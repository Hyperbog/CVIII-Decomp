#!/usr/bin/env python3
"""Validate a passive Mesen2 JP0711 CHR/palette trace; no liveness inference."""
import argparse
import hashlib
import json
import re
from collections import Counter
from pathlib import Path

ROM_SHA256 = "958a4b5e95e80acb2c71a43e9ef2e91444f3d097ae9d4eeb747f0dac8abe7a28"
ROM_LEN = 393232
HEX = re.compile(r"^[0-9a-fA-F]+$")
PAGE_HEX = re.compile(r"^(?:[0-9a-fA-F]{2}|--){8}$")
ALLOWED_WRITE = set(range(0x2000,0x2008)) | {0xB003} | set(range(0xD000,0xD004)) | set(range(0xE000,0xE004))

def require(ok, message):
    if not ok:
        raise ValueError(message)

def original_sha1s(rom):
    require(len(rom)==ROM_LEN and rom[:4]==b"NES\x1a" and
            hashlib.sha256(rom).hexdigest()==ROM_SHA256,
            "not the exact owner-supplied original Japanese ROM")
    require(rom[4]==16 and rom[5]==16 and
            ((rom[6]>>4)|(rom[7]&0xF0))==24,
            "not the original mapper24 256KiB PRG/128KiB CHR layout")
    return {hashlib.sha1(rom).hexdigest(), hashlib.sha1(rom[16:]).hexdigest()}

def parse(lines, accepted_hashes):
    entries=[line.strip() for line in lines if line.strip().startswith("JP0711_")]
    require(len(entries)>=3, "missing trace records")
    header=entries[0].split()
    require(len(header)==3 and header[:2]==["JP0711_BEGIN","1"],
            "missing or unsupported trace header")
    require(header[2].lower() in accepted_hashes, "Mesen ROM SHA1 does not authenticate with provided JP ROM")
    ending=entries[-1].split()
    require(len(ending)==3 and ending[0]=="JP0711_END","missing clean script-ended footer")
    expected_events,expected_frames=map(int,ending[1:])
    require(0<=expected_events<=50000 and 1<=expected_frames<=10000,
            "invalid or empty capture census")
    evt=0
    frame=0
    last_cycle=-1
    palette_count=Counter()
    chr_count=Counter()
    selectors=Counter()
    writes=Counter()
    changes=[]
    previous=None
    known_page_frames=0
    for line in entries[1:-1]:
        f=line.split()
        require(f[0] in ("JP0711_EVENT","JP0711_FRAME"),
                "aborted, reset, state-loaded, truncated or unknown Mesen trace: "+f[0])
        if f[0]=="JP0711_EVENT":
            require(len(f)==8,"invalid register-write record")
            n,fr,cyc=[int(x) for x in f[1:4]]
            pc,phys,addr,val=[int(x,16) for x in f[4:]]
            require(n==evt+1 and fr==frame and cyc>=last_cycle,
                    "event order/frame/cycle regression")
            require(0<=pc<=0xFFFF and (phys==0xFFFFF or 0<=phys<262144)
                    and addr in ALLOWED_WRITE and 0<=val<=255,
                    "invalid physical PC/register/bank/value")
            evt=n
            writes[f"{addr:04X}"]+=1
            last_cycle=cyc
        else:
            require(len(f)==10,"invalid completed-frame record")
            fr,cyc=int(f[1]),int(f[2])
            banks,palette=f[3],f[4]
            flags=[int(x,16) for x in f[5:]]
            require(fr==frame and cyc>=last_cycle,"non-monotonic completed frame/cycle")
            require(PAGE_HEX.fullmatch(banks) is not None,"not eight physically validated CHR page slots")
            pages=[banks[i:i+2] for i in range(0,16,2)]
            require(all(p=="--" or int(p,16)<=127 for p in pages),"CHR bank outside 128 1KiB original pages")
            require(len(palette)==64 and HEX.fullmatch(palette) is not None,
                    "incorrect 32-byte palette")
            pb=bytes.fromhex(palette)
            require(all(v<=63 for v in pb),"illegal NES palette index")
            require(all(pb[a]==pb[a+16] for a in (0,4,8,12)),
                    "PPU palette aliases are not equal; capture/API mismatch")
            require(len(flags)==5 and all(0<=v<=255 for v in flags),"stage-state RAM values invalid")
            key=tuple(flags[:3])
            selectors["%02X/%02X/%02X"%key]+=1
            palette_count[palette]+=1
            chr_count[banks]+=1
            known_page_frames+=int(any(v!="--" for v in pages))
            if previous and (banks,palette,key)!=previous:
                changes.append({"frame":fr,
                                "chr_mapping_changed":banks!=previous[0],
                                "palette_changed":palette!=previous[1],
                                "state_triple_changed":key!=previous[2]})
            previous=(banks,palette,key)
            frame+=1
            last_cycle=cyc
    require(evt==expected_events and frame==expected_frames,
            "footer census does not equal complete event/frame count")
    require(known_page_frames>0,"no verified source CHR-ROM page mappings")
    return {
       "format":"JP0711-mesen-physical-chr-palette/v1",
       "original_rom_sha256":ROM_SHA256,
       "capture_kind":"original_emulator_debugger_capture_unverified_natural_stage",
       "complete":True, "frames":frame, "register_writes":evt,
       "ppu_chrrom_mapped_frames":known_page_frames,
       "unique_chr_page_layouts":len(chr_count),
       "unique_palette_snapshots":len(palette_count),
       "selector_triples_observed":dict(sorted(selectors.items())),
       "register_write_counts":dict(sorted(writes.items())),
       "state_or_visual_transitions":changes[:1000],
       "state_or_visual_transition_count":len(changes),
       "warnings":[
         "RAM $34/$35/$36 triples are observed, not certified Stage 1-01 room identities.",
         "Frame-end CHR/palette snapshots do not establish every scanline/dot mapping.",
         "Register callbacks observe CPU writes, not guaranteed PPU fetch or visible pixel events.",
         "No room adjacency, RGB calibration, or original-vs-native rendered-frame parity claimed."
       ]
    }

def smoke():
    pal=bytearray((i*5+1)&63 for i in range(32))
    for x in (0,4,8,12):
        pal[x+16]=pal[x]
    p=pal.hex().upper()
    fixture=["JP0711_BEGIN 1 "+"0"*40,
             "JP0711_EVENT 1 0 10 8000 00000 D000 05",
             "JP0711_FRAME 0 20 0001020304050607 "+p+" 00 00 00 00 01",
             "JP0711_FRAME 1 50 0001020304050607 "+p+" 00 00 00 00 01",
             "JP0711_END 1 2"]
    result=parse(fixture,{"0"*40})
    require(result["frames"]==2 and result["unique_chr_page_layouts"]==1,
            "synthetic good case failed")
    for label,alter in [
        ("wrong-hash",lambda a:a.__setitem__(0,"JP0711_BEGIN 1 "+"1"*40)),
        ("wrong-bank",lambda a:a.__setitem__(2,a[2].replace("0001020304050607","8001020304050607"))),
        ("bad-palette",lambda a:a.__setitem__(2,a[2].replace(p,"GG"*32))),
        ("missing-footer",lambda a:a.pop()),
        ("state-loaded",lambda a:a.insert(-1,"JP0711_STATE_LOADED")),
        ("event-sequence",lambda a:a.__setitem__(1,a[1].replace("EVENT 1","EVENT 2"))),
        ("wrong-census",lambda a:a.__setitem__(-1,"JP0711_END 2 2"))
    ]:
        changed=fixture.copy()
        alter(changed)
        try: parse(changed,{"0"*40})
        except (ValueError, IndexError): pass
        else: raise AssertionError("admitted "+label)
    print("PASS JP0711 ROM-free 2-frame synthetic capture and 7 tamper-negative gates")

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--smoke",action="store_true")
    ap.add_argument("--rom",type=Path,help="owner's exact original Japanese .nes")
    ap.add_argument("--trace",type=Path,help="private Mesen2 log saved after stopping Lua")
    ap.add_argument("--out",type=Path,help="private aggregate JSON, not a geometry asset")
    a=ap.parse_args()
    if a.smoke: smoke()
    if a.trace or a.rom:
        require(a.rom is not None and a.trace is not None,"--rom and --trace are both required")
        shas=original_sha1s(a.rom.read_bytes())
        report=parse(a.trace.read_text(encoding="utf-8").splitlines(),shas)
        if a.out:a.out.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n",encoding="utf-8")
        print(json.dumps({k:report[k] for k in ("frames","register_writes",
                                                "unique_chr_page_layouts",
                                                "unique_palette_snapshots",
                                                "selector_triples_observed")},indent=2))
    elif not a.smoke:ap.error("use --smoke or --rom and --trace")
if __name__=="__main__": main()
