/* JP0731: private owner-local content loader probe.
 * The executable is ROM-independent at build time. It accepts the original
 * Japanese cartridge only when explicitly provided at runtime.
 * Prints resource COUNTS, not any copyrighted game data or artwork.
 */
#include "cviii_runtime_resources_0727.h"
#include <stdio.h>
#include <stdlib.h>
int main(int argc,char **argv)
{
    if(argc<2 || argc>3) {
        fprintf(stderr,"Usage: cviii_content_probe_0731 <original-JP-ROM> [private-cache-path]\n");
        return 2;
    }
    CviiiStage1Atlas0724 *atlas=(CviiiStage1Atlas0724 *)calloc(1,sizeof *atlas);
    if(!atlas) return 3;
    CviiiChrIndex chr={0};
    CviiiResourceStatus0727 result=cviii_game_resources_cached_open_0729(
        argv[1],argc==3 ? argv[2] : NULL,atlas,&chr);
    if(result!=CVIII_RESOURCE_READY_0727) {
        fprintf(stderr,"Source rejected by runtime loader: %d\n",(int)result);
        free(atlas);
        return 4;
    }
    if(!atlas->loaded || !chr.allocation || !chr.raw || !chr.pixels) {
        cviii_chr_index_free(&chr);free(atlas);return 5;
    }
    printf("CVIII ROM content ready: Stage1 rooms=%u, tile positions=%u, CHR patterns=%u, schema=%u\n",
           (unsigned)CVIII_STAGE1_ROOMS_0724,
           (unsigned)CVIII_STAGE1_TILES_0724,
           (unsigned)(CVIII_CHR_RAW_BYTES/16u),
           (unsigned)CVIII_RUNTIME_STAGE1_SCHEMA_0727);
    cviii_chr_index_free(&chr);
    free(atlas);
    return 0;
}
