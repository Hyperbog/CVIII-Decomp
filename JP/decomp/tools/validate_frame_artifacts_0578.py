#!/usr/bin/env python3
"""JP0578: validate bounded frame hashes and 256x240 screenshot from NESRecomp.

Artifacts are evidence of hardware state advancing, NOT original NES parity.
The hash line format comes from pinned upstream runner/cyc/cyc_host.c.
"""
from __future__ import annotations
import argparse,hashlib,json,re,sys
from pathlib import Path

FRAME=re.compile(
    r"^(\d+) trace=([0-9a-fA-F]{16}) mem=([0-9a-fA-F]{16}) "
    r"PC=([0-9a-fA-F]{4}) A=([0-9a-fA-F]{2}) X=([0-9a-fA-F]{2}) "
    r"Y=([0-9a-fA-F]{2}) S=([0-9a-fA-F]{2}) P=([0-9a-fA-F]{2}) "
    r"int=\d+ cycles=(\d+) hw=([0-9a-fA-F]{16})$"
)
PNG=b"\x89PNG\r\n\x1a\n"

def verify(hash_path:Path,png_path:Path,frames:int)->dict:
    if not 1<=frames<=12000:raise ValueError("frame limit outside 1..12000")
    raw=hash_path.read_bytes()
    entries=[line for line in raw.decode("ascii").splitlines() if line]
    if len(entries)!=frames:
        raise ValueError(f"frame hashes count {len(entries)} differs from requested {frames}")
    parsed=[]
    for line in entries:
        m=FRAME.fullmatch(line)
        if not m:raise ValueError("malformed original NESRecomp frame hash record")
        parsed.append(m)
    index=[int(m.group(1)) for m in parsed]
    if any(index[i+1]!=index[i]+1 for i in range(len(index)-1)):
        raise ValueError("missing or duplicated frame hash index")
    cycles=[int(m.group(10)) for m in parsed]
    if any(cycles[i+1]<=cycles[i] for i in range(len(cycles)-1)):
        raise ValueError("NESRecomp frame hashes did not advance CPU cycles")
    png=png_path.read_bytes()
    if len(png)<33 or png[:8]!=PNG or png[12:16]!=b"IHDR":
        raise ValueError("last frame is not a PNG image")
    width=int.from_bytes(png[16:20],"big")
    height=int.from_bytes(png[20:24],"big")
    if (width,height)!=(256,240):
        raise ValueError(f"expected 256x240 NES last frame, got {width}x{height}")
    return {
        "frame_hash_file":str(hash_path),"frame_hash_sha256":hashlib.sha256(raw).hexdigest(),
        "frame_records":len(parsed),"first_frame_index":index[0],
        "last_frame_index":index[-1],
        "first_cpu_pc":parsed[0].group(4).upper(),
        "last_cpu_pc":parsed[-1].group(4).upper(),
        "first_cpu_cycles":cycles[0],"last_cpu_cycles":cycles[-1],
        "distinct_memory_hashes":len({m.group(3) for m in parsed}),
        "distinct_picture_state_guaranteed":False,
        "screenshot":str(png_path),
        "screenshot_sha256":hashlib.sha256(png).hexdigest(),
        "png_width":width,"png_height":height,
        "independent_original_gameplay_parity":False
    }

def synthetic_png():
    # PNG signature + 13-byte IHDR + checksum (not a full encoded picture).
    return PNG+bytes((0,0,0,13))+b"IHDR"+(256).to_bytes(4,"big")+\
        (240).to_bytes(4,"big")+bytes((8,6,0,0,0))+bytes(4)

def fake_hash_lines(n:int)->str:
    return "".join(
        f"{i} trace={i+11:016x} mem={i+21:016x} "
        f"PC=E000 A=00 X=00 Y=00 S=FD P=24 int=00 "
        f"cycles={30000*(i+1)} hw={i+31:016x}\n" for i in range(n)
    )

def smoke():
    import tempfile
    with tempfile.TemporaryDirectory(prefix="jp0578-") as w:
        folder=Path(w);hashes=folder/"hashes.txt";shot=folder/"last.png"
        hashes.write_text(fake_hash_lines(3),encoding="ascii")
        shot.write_bytes(synthetic_png())
        report=verify(hashes,shot,3)
        assert report["frame_records"]==3 and report["last_cpu_cycles"]==90000
        hashes.write_text(fake_hash_lines(2),encoding="ascii")
        try:verify(hashes,shot,3)
        except ValueError:pass
        else:raise AssertionError("missing frame hash accepted")
        hashes.write_text(fake_hash_lines(3).replace("PC=E000","PC=???",1))
        try:verify(hashes,shot,3)
        except ValueError:pass
        else:raise AssertionError("invalid PC in frame hash accepted")
        hashes.write_text(fake_hash_lines(3),encoding="ascii")
        shot.write_bytes(b"not-a-PNG")
        try:verify(hashes,shot,3)
        except ValueError:pass
        else:raise AssertionError("invalid screenshot accepted")
    print("PASS JP0578 original-frame artifact parser; truncated hash / PNG fail closed")

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--smoke",action="store_true")
    p.add_argument("--hash-out",type=Path)
    p.add_argument("--screenshot",type=Path)
    p.add_argument("--frames",type=int,default=3)
    a=p.parse_args()
    if a.smoke:smoke()
    else:
        if not a.hash_out or not a.screenshot:
            p.error("supply --hash-out FILE and --screenshot PNG")
        print(json.dumps(verify(a.hash_out,a.screenshot,a.frames),sort_keys=True))
if __name__=="__main__":
    try:main()
    except (ValueError,OSError,UnicodeError,AssertionError) as e:
        print("JP0578 FAIL "+str(e),file=sys.stderr);raise SystemExit(2)
