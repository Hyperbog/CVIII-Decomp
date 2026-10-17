# JP 0570 — synthetic mapper24 VRC6 IRQ isolation regression

A review of the first 0569 synthetic cartridge found that the loop
`JMP $E02E` spans $E02E–$E030, while its IRQ handler was
written at $E030, overwriting that JMP's operand. The prior
upstream cycle runner completing 3 frames did **not** detect this
synthetic fixture control-flow defect.

The synthetic ROM generator now moves its IRQ handler to $E080,
NMI to $E090, updates the respective vectors, checks the complete
three-byte loop instruction on every verification, and includes
a negative test that corrupts the JMP high byte. The corrected
original-free cartridge must pass a new pinned external C11
mapper24 runtime build and execution.

Neither synthetic cycle tests nor a process exit of zero proves
Mesen parity of the original retail game, and neither adds strict
PRG or VPP certification. VPP27/100, 49,504/262,144 strict,
4,261 original compiled sites unchanged.
