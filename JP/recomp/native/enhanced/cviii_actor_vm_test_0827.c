/* JP0827: isolated 6502 VM with original-ROM parity when an owner
 * ROM path is supplied. CI runs ROM-free instruction fixtures. Never
 * republishes proprietary raw ROM bytes or private savestates. */
#include "cviii_actor_vm_0827.h"
#include "cviii_contact_effects_0821.h"
#include "cviii_wide_instance_0826.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
static void test(int yes,const char *name){
 if(!yes){fprintf(stderr,"FAIL JP0827 VM: %s\n",name);exit(1);}
}
static void put(uint8_t *bank,unsigned pc,uint8_t value){
 bank[pc-0x8000u]=value;
}
static void synthetic(void){
 uint8_t bank[16384]={0},ram[2048]={0};
 CviiiActorVM0827 vm={0};
 /* Independent private guest stack; synthetic CALL/RET permitted ONLY
  * within the bounded bank0B original-code address whitelist. */
 put(bank,0xb486u,0x20u);put(bank,0xb487u,0xa0u);
 put(bank,0xb488u,0xb4u);put(bank,0xb489u,0x60u);
 put(bank,0xb4a0u,0xa9u);put(bank,0xb4a1u,0x42u);
 put(bank,0xb4a2u,0x85u);put(bank,0xb4a3u,0x10u);
 put(bank,0xb4a4u,0x60u);
 test(cviii_vm_init_0827(&vm,ram,1u,0xb486u) &&
      cviii_vm_run_0827(&vm,bank,32u) &&
      vm.stop_kind==CVIII_VM_STOP_RTS_0827 &&
      vm.stop_pc==0xb489u && vm.a==0x42u &&
      vm.ram[0x10u]==0x42u && ram[0x10u]==0u &&
      vm.sp==0xfdu && !vm.depth && vm.ram_writes==1u,
      "private 2A03 JSR/RTS, zeropage, registers and untouched guest");
 memset(bank,0,sizeof bank);
 put(bank,0xb486u,0x20u);put(bank,0xb487u,0x49u);
 put(bank,0xb488u,0xe2u);
 test(cviii_vm_init_0827(&vm,ram,1u,0xb486u) &&
      cviii_vm_run_0827(&vm,bank,16u) &&
      vm.stop_kind==CVIII_VM_STOP_EXTERNAL_0827 &&
      vm.stop_pc==0xb486u && vm.external_target==0xe249u &&
      vm.ram_writes==0u && vm.sp==0xfdu,
      "unapproved original E249 must trap before any CPU/audio effects");
 memset(bank,0,sizeof bank);
 put(bank,0xb486u,0x02u);
 test(cviii_vm_init_0827(&vm,ram,1u,0xb486u) &&
      !cviii_vm_run_0827(&vm,bank,16u) &&
      vm.stop_kind==CVIII_VM_STOP_OPCODE_0827 &&
      !vm.ram_writes,"unknown opcode fails closed");
 memset(bank,0,sizeof bank);
 put(bank,0xb486u,0xbdu);put(bank,0xb487u,0x00u);
 put(bank,0xb488u,0x20u);
 test(cviii_vm_init_0827(&vm,ram,1u,0xb486u) &&
      !cviii_vm_run_0827(&vm,bank,16u) &&
      vm.stop_kind==CVIII_VM_STOP_BUS_0827,
      "private CPU never accesses PPU register or unsupported bus");
 memset(bank,0,sizeof bank);
 put(bank,0xb486u,0x4cu);put(bank,0xb487u,0x86u);
 put(bank,0xb488u,0xb4u);
 test(cviii_vm_init_0827(&vm,ram,1u,0xb486u) &&
      !cviii_vm_run_0827(&vm,bank,6u) &&
      vm.stop_kind==CVIII_VM_STOP_BUDGET_0827 &&
      vm.instructions==6u,"hostile infinite loop bounded at six instructions");
 test(!cviii_vm_init_0827(&vm,ram,0u,0xb486u) &&
      !cviii_vm_init_0827(&vm,ram,1u,0xb620u),
      "invalid original actors or entry PCs are refused");
}
static void original(const char *path){
 FILE *file=fopen(path,"rb");
 test(file!=NULL,"original Japanese ROM file opens");
 uint8_t bank[16384]={0};
 test(fseek(file,16L+11L*16384L,SEEK_SET)==0 &&
      fread(bank,1,sizeof bank,file)==sizeof bank,
      "read private physical original PRG raw0B");
 fclose(file);
 test(bank[0xb486u-0x8000u]==0xbdu &&
      bank[0xb525u-0x8000u]==0xa9u &&
      bank[0xb53cu-0x8000u]==0x20u,
      "B486/B525 owner-original opcode entry identity");
 static uint8_t ram[2048];
 const unsigned actor=1u;
 unsigned checked=0;
 for(unsigned type=0;type<256u;type++)
 for(unsigned shield=0;shield<2u;shield++)
 for(unsigned hit=0;hit<16u;hit++)
 for(unsigned hp=0;hp<16u;hp++){
    memset(ram,0,sizeof ram);
    ram[0x54eu+actor]=(uint8_t)type;
    ram[0x470u+actor]=(uint8_t)(shield?2u:0u);
    ram[0x669u+actor]=(uint8_t)((hit<<4u)|7u);
    ram[0x67bu+actor]=(uint8_t)hp;
    uint8_t before[2048];memcpy(before,ram,sizeof ram);
    CviiiB486Effect0821 pred={0};
    CviiiActorVM0827 vm={0};
    test(cviii_effect_b486_prefix_0821(ram,actor,&pred),
         "independent existing B486 prefix model");
    test(cviii_vm_init_0827(&vm,ram,actor,0xb486u) &&
         cviii_vm_run_0827(&vm,bank,96u),
         "original-ROM VM B486 must stop at bounded exit");
    test(vm.x==actor && vm.ram[0x669u+actor]==pred.new_0669 &&
         vm.ram[0x67bu+actor]==pred.new_067b,
         "original 6502 RAM postconditions match B486 C11 model");
    const unsigned stop=pred.stop_pc==0xb525u ? 0xb53cu:pred.stop_pc;
    test(vm.stop_pc==stop,"exact original ROM B486/B525 stop PC");
    if(stop==0xb53cu){
        CviiiB525Prefix0826 first={0};
        test(cviii_b525_prefix_0826(ram,actor,&first) &&
             vm.stop_kind==CVIII_VM_STOP_EXTERNAL_0827 &&
             vm.external_target==0xe249u &&
             vm.a==first.sound_id,
             "original B525 selects exact sound on private 2A03 CPU");
    }else if(stop==0xb4bcu){
        test(vm.stop_kind==CVIII_VM_STOP_EXTERNAL_0827 &&
             vm.external_target==0xe249u &&
             vm.a==0x24u,
             "original B4BC hurt-sound call must stop before E249");
    }else if(stop==0xb4d4u){
        test(vm.stop_kind==CVIII_VM_STOP_RTS_0827,
             "original B486 early return is real RTS");
    }else{
        test(vm.stop_kind==CVIII_VM_STOP_BOUNDARY_0827,
             "unknown original effect branch must fail closed");
    }
    test(memcmp(ram,before,sizeof ram)==0,
         "entire actual guest RAM untouched by reentrant execution");
    checked++;
 }
 printf("PASS JP0827 %u original-bank B486/B525 traces vs C11, CPU RAM isolated\n",
        checked);
}
int main(int argc,char **argv){
 synthetic();
 puts("PASS JP0827 ROM-free CPU RAM, stack, external call and budget isolation");
 if(argc>1)original(argv[1]);
 return 0;
}
