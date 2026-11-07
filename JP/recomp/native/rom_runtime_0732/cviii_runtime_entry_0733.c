/* JP0733 - launch-time identity gate for the code-independent game host.
 *
 * The upstream NESRecomp entry point is renamed at compilation, never
 * patched or vendored. The original Japanese ROM is authenticated BEFORE
 * the first CPU/PPU cycle. Enhanced receives the same private owner path
 * for resource extraction; no original bytes enter the executable.
 */
#include "../enhanced/cviii_runtime_resources_0727.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int cviii_upstream_main_0733(int argc, char **argv);

static int authentic_rom(const char *path)
{
    static const unsigned char japanese[32]={
        0x95,0x8a,0x4b,0x5e,0x95,0xe8,0x0a,0xcb,
        0x2c,0x71,0xa4,0x3e,0x9e,0xf2,0xe9,0x14,
        0x44,0xf3,0xd0,0x97,0xae,0x9d,0x4e,0xeb,
        0x74,0x7f,0x0d,0xac,0x8a,0xbe,0x7a,0x28
    };
    if (!path || !*path) return 0;
    FILE *f=fopen(path,"rb");
    if (!f)return 0;
    unsigned char *rom=(unsigned char *)malloc(CVIII_RUNTIME_ROM_BYTES_0727);
    if(!rom){fclose(f);return 0;}
    size_t n=fread(rom,1,CVIII_RUNTIME_ROM_BYTES_0727,f);
    int extra=fgetc(f),error=ferror(f);
    fclose(f);
    int valid=!error && extra==EOF &&
              n==CVIII_RUNTIME_ROM_BYTES_0727;
    if(valid){
        unsigned char hash[32];
        cviii_sha256_0727(rom,n,hash);
#ifdef CVIII_JP0733_TEST_SYNTHETIC_ROM
        /* Test executables ONLY. Release binaries never define this flag.
         * A synthetic VRC6 program is required for public CI tests. */
        valid=rom[0]=='N'&&rom[1]=='E'&&rom[2]=='S'&&
              rom[3]==0x1a&&rom[4]==16u&&rom[5]==16u&&
              (((unsigned)rom[6]>>4)|((unsigned)rom[7]&0xf0u))==24u;
#else
        valid=memcmp(hash,japanese,32)==0;
#endif
    }
    free(rom);
    return valid;
}

int main(int argc,char **argv)
{
    if(argc==2 && (!strcmp(argv[1],"--help") ||
                   !strcmp(argv[1],"-h"))) {
        return cviii_upstream_main_0733(argc,argv);
    }
    if(argc<2 || !argv[1] || argv[1][0]=='-') {
        fputs("CVIII JP0733: supply the original Japanese ROM as the first argument\n",
              stderr);
        return 2;
    }
    if(!authentic_rom(argv[1])) {
        fputs("CVIII JP0733: ROM rejected (expected original Japanese VRC6 cartridge)\n",
              stderr);
        return 3;
    }
    /* Host executes the original 6502 bytes using its mapper-24 interpreter;
     * Enhanced receives this validated path but cannot mutate the guest ROM.
     * If a caller already set --stage1-world-rom, replace it with the
     * authenticated launch source by appending the authoritative argument.
     */
    char **args=(char **)calloc((size_t)argc+3u,sizeof *args);
    if(!args)return 4;
    for(int i=0;i<argc;i++)args[i]=argv[i];
    args[argc]="--stage1-world-rom";
    args[argc+1]=argv[1];
    int result=cviii_upstream_main_0733(argc+2,args);
    free(args);
    return result;
}
