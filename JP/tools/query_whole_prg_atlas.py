#!/usr/bin/env python3
from __future__ import annotations
import argparse, csv, json
from pathlib import Path

def parse_num(s: str) -> int:
    s=s.strip().lower()
    if s.startswith('$'): return int(s[1:],16)
    if s.startswith('0x'): return int(s,16)
    return int(s,10)

def rows(path):
    with Path(path).open(encoding='utf-8',newline='') as f:
        yield from csv.DictReader(f,delimiter='\t')

def main():
    ap=argparse.ArgumentParser(description='Query generated whole-PRG candidate indexes without re-decoding the ROM.')
    ap.add_argument('atlas', help='generated atlas directory')
    sp=ap.add_subparsers(dest='cmd',required=True)
    p=sp.add_parser('ram'); p.add_argument('address'); p.add_argument('--writes-only',action='store_true')
    p=sp.add_parser('jsr'); p.add_argument('target')
    sp.add_parser('e7fb')
    p=sp.add_parser('bank'); p.add_argument('number')
    args=ap.parse_args(); root=Path(args.atlas)
    if args.cmd=='bank':
        n=parse_num(args.number); m=json.loads((root/'manifest.json').read_text())
        b=next(x for x in m['banks'] if x['bank']==n)
        print(json.dumps(b,indent=2)); return
    if args.cmd=='e7fb':
        for r in rows(root/'e7fb_call_candidates.tsv'):
            print(f"PRG{int(r['bank']):02d}+${r['offset']}  {r['views']}")
        return
    if args.cmd=='ram':
        a=parse_num(args.address)
        for r in rows(root/'memory_access_candidates.tsv'):
            if int(r['base'],16)!=a: continue
            if args.writes_only and r['access'] not in ('write','readwrite'): continue
            print(f"PRG{int(r['bank']):02d}+${r['offset']} {r['views']}  {r['bytes']:<6} {r['mnemonic']} {r['mode']}  {r['access']} {r['region']}")
        return
    if args.cmd=='jsr':
        t=parse_num(args.target)
        for r in rows(root/'control_flow_candidates.tsv'):
            if r['mnemonic']!='JSR' or not r['target']: continue
            if int(r['target'],16)==t:
                print(f"PRG{int(r['bank']):02d}+${r['offset']} {r['view']}:${r['cpu']}  {r['bytes']} JSR ${t:04X}")
        return
if __name__=='__main__': main()
