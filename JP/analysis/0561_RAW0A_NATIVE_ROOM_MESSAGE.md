# JP 0561 — source-level C++ translation of original $B8CC room-message selector

The original ROM's **audited** bank raw0A $B8CC–$B908 6502 sequence
is converted into the direct host-C++ `Room0aMessageSelector0561`
(`JP/native/bank0a/room_message_native_0561.hpp`).

Original opcode control flow:
- RAM $07F6 or RAM $0781 nonzero selects message pointer group 1,
  otherwise group 0.
- Table root $B909/$B90B indexes $B90D or $B917 respectively.
- RAM $07A0 selects 0..4 among five message pointers per group.
- RAM $07A5 indexes the message stream; $FF terminates.
- Nonterminal path calls fixed-bank $EC47 and then increments $07A5.
  Terminal path returns with carry set; the nonterminal return clears carry.

**The new C++ selector handles only the source-derived table indexing,
byte selection and terminal condition.** Actual fixed-bank $EC47
rendering/copy behavior is an explicitly unresolved dependency,
not a mocked game implementation. Original bytes are supplied from
a private physical raw0A source image at runtime, not committed.

The code checks the 2 original group roots, 10 pointer locations,
22 source-backed message bytes, all $FF termination conditions,
and bounds for each byte within its own message. The new ROM-free
`jp_room_message_native_0561` test uses a synthetic 10-message,
22-byte table and invalid-pointer/terminator cases.

The existing bank0A native driver now validates the same source
in a separate ROM-backed gate alongside the 135-case selector path;
original-ROM backed execution is still performed locally, not
in copyright-restricted CI.

This is semantic **original ASM → readable C++** for a complete
bounded selector, not a full playable game or newly proven code reachability.
It does not add ROM bytes, opcode dispatch starts, strict PRG
coverage or VPP points. VPP 27/100, strict 49,504/262,144,
compiled instruction sites 4,261.

Next: recover source-level semantics of the $EC47 text/render call,
state producers for $07A0/$07A5, and additional bank0A routines.
