/* JP0732: the generated-game developer build patches the private external
 * mapper and PPU with read-only observation callbacks. The standalone,
 * no-ROM-at-build gameplay backend deliberately DOES NOT patch the engine.
 * Those audit options are rejected in cviii_edition.c for this backend.
 * Registration is inert; normal cycle-accurate CPU/PPU hardware is untouched.
 */
#include "../enhanced/cviii_chr_fetch_0600.h"
#include "../enhanced/cviii_nt_trace_0606.h"
void cviii_chr_fetch_set_hook(CviiiChrFetchHook callback) {
    (void)callback;
}
void cviii_nt_set_hook(CviiiNtHook callback) {
    (void)callback;
}
