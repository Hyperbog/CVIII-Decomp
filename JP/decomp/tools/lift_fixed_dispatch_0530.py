#!/usr/bin/env python3
"""Restore authenticated JP fixed-bank 04FE/04FF/0500 6502 graphs.

Uses historical original ROM SHA-pinned interval certificates and exact dispatch
pointer table targets. Never linearly decodes unclassified bytes. Never
promotes strict coverage, and does not infer producer-domain liveness.
"""
from __future__ import annotations
from collections import deque
import hashlib
import audit_nmi_fixed_scheduler_banked as proof

HIST04FE=[
 (0xE366,0xE434,'b1bb37d98f9d0c9992ec2c9bc0c8a99cb3a1a2db8eb9359ecdc686ed1a7d6f46'),
 (0xE436,0xE577,'faa4c0e4033694f4e0bbadc1ac18fb500d3b746c8c1c1c46bb9523124c9ba3f9'),
 (0xE62D,0xE632,'40038e39a56b11e71412ead62b2574002c961973fe122d0aaca3b89f0ac0d52c'),
 (0xE63D,0xE648,'0b6bd8d5b060c86180149316236f21750165b786917ccf3dcd636db5071a8d34'),
 (0xE710,0xE718,'42e14ed3d9e6686c8e5b7b2f9c4639ddeafdc43a2156d6776c3ca07754096dd5'),
 (0xE7A7,0xE814,'77fdf616b9dcf810b95d87fbad15f22842b277c8a28e7bc6b0911084e493bdb2'),
 (0xE827,0xE831,'fe9dab3a7ce1bb29399af19923cf2e12165f9d17a0ed4bd6bebce71da6410060'),
 (0xEB44,0xEB6B,'7a534ebcac80d8c2e919184621381e3b944ae0ee161d474705cfe5cb199760c6'),
 (0xEB82,0xEBF7,'e69aaaa7f343f00621a23d78aab2b018057a6ba29ac50d07aa1c34bc8ed287e8'),
 (0xF390,0xF3DD,'534f1b3ff2e7b25348a1a4c66479018ec9153d63b3e9f9b964f9e07483905b15'),
 (0xF6AE,0xF6E4,'d79b617b7e27190b6556464a37cc024a1837e949ebe9446d12815da908233dfb'),
]
HIST04FF=[
 (0xF3DD,0xF6AE,'371c27c08f71624463d2c63097938a30fa57253bd073d2554d454111708f6852'),
 (0xF6E4,0xF706,'cd2f26e03fcfab69f12aec4fbe3ff9571f8a2633b3c84eb4365a0d8e777378c5'),
 (0xF713,0xF724,'4bc45df46fbab59efc9b70eb7d577001b8474818f921b86e618b43c4653c8300'),
 (0xF739,0xF782,'b8cc2cdf6b04eb86ff7693b53c006afb6710098252d7a921e199c22355d462ac'),
 (0xF792,0xF7B7,'b564a74ff4c6ba3a55b76472c1462ff1b915f0c333c8dc54ccae3b9a76d1e5e1'),
 (0xF7CF,0xF800,'13b6de6ba1671ce00afec40ee8b7886d6ed9126a6261b5a090a15f0cc73b1574'),
]
HIST0500=[
 (0xF706,0xF713,'8745c6e3d3acdd90bf3b1cafaf32f9e981a606070ba5d2b365cace8f56fa3025'),
 (0xF724,0xF739,'41cad7c7b722c299f4111083f871fd996a0cfa517bd990d3b37ddce6ac30072e'),
 (0xF782,0xF792,'17bbb4663de8e617686c27ab5ad5554a69c0062d9c8bff1d353fd6487028546b'),
 (0xF7B7,0xF7CF,'0d93fcf865fdae96f01a0640e3769924b558f1cb0aaa0dbe7d2fedfdf17462be'),
 (0xF800,0xFAA0,'6dea651f93c64d59355c4180907677d367bb705ed84cbfa6ec59da79009028a8'),
 (0xFAAA,0xFB96,'5d32479e3af38c5477b4a3c076b3c3d0a0bd07f4c572a35a115bd6e347720402'),
]
BANK31=31*0x2000
BR={x.lower() for x in proof.BR}
ENDS={x.lower() for x in proof.TERM}

def lift(prg:bytes):
    assert len(prg)==262144
    fixed=prg[BANK31:BANK31+8192]
    def read(pc,n):
        assert 0xe000<=pc<0x10000 and pc+n<=0x10000
        return fixed[pc-0xe000:pc+n-0xe000]
    def table(pc,n,digest):
        raw=read(pc,n*2)
        assert hashlib.sha256(raw).hexdigest()==digest,(hex(pc),'table SHA mismatch')
        return [int.from_bytes(raw[i:i+2],'little') for i in range(0,n*2,2)]
    for stage,intervals,total in [('04FE',HIST04FE,957),('04FF',HIST04FF,931),('0500',HIST0500,982)]:
        assert sum(b-a for a,b,_ in intervals)==total
        for a,b,h in intervals:
            assert hashlib.sha256(read(a,b-a)).hexdigest()==h,(stage,hex(a))

    t_first=table(0xE363,16,'def43bbd8730858236b66f0cbfebec9d050c05a29ab90db176a3a4b3da186089')
    t_nested=table(0xF39D,32,'81d06cd79d64c3d4cfe14bbefa851e74e748536f723636abaf82870ec065d22f')
    # Nested true digest appears in the original 04FE history; the source
    # test will independently fingerprint every admitted stage interval.
    def dec(pc):
        op=read(pc,1)[0]
        if op not in proof.OPS:raise ValueError(f'Unrecognized opcode ${op:02X} at ${pc:04X}')
        mn,mode,n=proof.OPS[op]
        raw=read(pc,n)
        arg=None if n==1 else raw[1] if n==2 else int.from_bytes(raw[1:3],'little')
        if mode=='rel':arg=(pc+2+(arg if arg<128 else arg-256))&0xffff
        return mn.lower(),mode,n,arg
    def walk(roots,in_domain,call_jsr=True,skip_e7fb=False,special=None,stop=None):
        q=deque(roots);seen={};inline=[]
        while q:
            pc=q.popleft()
            if pc in seen or not in_domain(pc) or (stop and stop(pc)):continue
            mn,mode,n,arg=dec(pc)
            seen[pc]=(mn,mode,n,arg)
            nxt=pc+n
            def put(t):
                if in_domain(t):q.append(t)
            if mn in ENDS:continue
            if mn in BR:put(nxt);put(arg)
            elif mn=='jmp':
                if mode!='ind':put(arg)
            elif mn=='jsr':
                if special and pc in special:
                    for t in special[pc]:put(t)
                elif skip_e7fb and arg==0xe7fb:
                    inline.append(pc)
                else:
                    put(nxt)
                    if call_jsr:put(arg)
            else:put(nxt)
        return seen,inline
    whole=lambda x:0xe000<=x<0x10000
    first,inline=walk([*t_first,0xE7FB],whole,skip_e7fb=True)
    assert len(first)==450 and inline==[0xF39A],('04FE original graph',len(first),inline)
    in04ff=lambda x:0xF3DD<=x<0xF800
    ff,inline_ff=walk([x for x in t_nested if in04ff(x)],in04ff)
    assert len(ff)==401 and not inline_ff,('04FF historical graph',len(ff),inline_ff)

    t68_1=table(0xF84E,16,'88065baa658136181547132c1ee61481724cba01f76f0f5aed837a91aa06e549')
    t68_2=table(0xF96A,10,'9db34975a37e416e832cc543ae63858c0fa17e5a7b0b5f6f6070a96974838aea')
    old=set(x for a,b,_ in HIST04FE+HIST04FF for x in range(a,b))
    allowed=set(x for a,b,_ in HIST0500 for x in range(a,b))
    in0500=lambda x:x in allowed and x not in old
    # Original 0500 decoder may enter 04FF-prior span; the original proof
    # stops there and the first two historical graphs supply those bytes.
    roots=[0xF800,0xF831,0xF839,0xF841,0xF849,0xF965]
    zero,inline_zero=walk(roots,in0500,special={0xF84B:t68_1,0xF967:t68_2})
    assert len(zero)==414 and not inline_zero,('0500 original graph',len(zero),inline_zero)

    # First table's $E363-$E365 belonged to even earlier physical certificates;
    # include complete, independently SHA-verified symbolically named pointers.
    data_regions=[(0xE363,t_first),(0xF39D,t_nested),(0xF84E,t68_1),
                  (0xF96A,t68_2),(0xFB31,list(int.from_bytes(read(0xFB31+i,2),'little') for i in (0,2,4)))]
    assert hashlib.sha256(read(0xFB31,6)).hexdigest()=='92e4f972206296cbd33f41e211a71edf949a5c4fd5c5f03e9d530f7cd3f78165'
    data_mask={x for a,values in data_regions for x in range(a,a+2*len(values))}
    def covered(seen):return {x for pc,(_,_,n,_) in seen.items() for x in range(pc,pc+n)}
    for stage,intervals,seen in [('04FE',HIST04FE,first),('04FF',HIST04FF,ff),('0500',HIST0500,zero)]:
        admitted={x for a,b,_ in intervals for x in range(a,b)}
        code=covered({pc:ins for pc,ins in seen.items() if all(x in admitted for x in range(pc,pc+ins[2]))})
        if code | (admitted & data_mask)!=admitted or code & data_mask:
            missing=admitted-code-data_mask
            conflict=code & data_mask
            raise ValueError(f'{stage} non-reassembled certificate: missing {len(missing)} {list(sorted(missing))[:12]}, table overlap {len(conflict)}')
    # Keep only audited original physical spans and original instruction starts.
    admitted_all={x for a,b,_ in HIST04FE+HIST04FF+HIST0500 for x in range(a,b)}
    source={}
    for graph in (first,ff,zero):
        for pc,ins in graph.items():
            used=set(range(pc,pc+ins[2]))
            if used<=admitted_all:
                if pc in source and source[pc]!=ins:raise ValueError('Conflicting graph decoding')
                source[pc]=ins
    code_bytes=covered(source)
    assert not code_bytes & data_mask
    assert len(code_bytes)+len(data_mask)==len(code_bytes|data_mask)
    tables=[]
    for pc,values in data_regions:
        lines=[f'; Original bounded pointer table ${pc:04X}',f'DispatchTable_{pc:04X}:']
        lines.extend('    .word '+','.join(f'${v:04X}' for v in values[i:i+8]) for i in range(0,len(values),8))
        tables.append({'a':pc,'b':pc+2*len(values),'src':f'04FE/0500 original pointer table ${pc:04X}','lines':lines})
    return source,tables,{'04FE_graph_instruction_starts_including_dispatch_body':len(first),'04FF_instructions':len(ff),
        '0500_instructions':len(zero),'new_mnemonic_instructions':len(source),
        'new_mnemonic_bytes':len(code_bytes),'new_explicit_data_bytes':len(data_mask),
        'new_symbolic_bytes':len(code_bytes)+len(data_mask)}
