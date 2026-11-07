#include "cviii_jp_effect_state_0667.h"
#include <string.h>
static unsigned width(uint8_t op){
    if((op&0xf0u)==0xd0u)return 4u;
    if(op>=0xe0u && op<=0xe5u)return 1u;
    if(op==0xe6u)return 2u; /* original $83F8 INY, read parameter, $840B INY */
    if(op==0xebu)return 0u; /* variable: validated below */
    switch(op){
        case 0xe7u:case 0xe8u:case 0xe9u:case 0xeau:case 0xecu:case 0xeeu:return 2u;
        default:return 0u;
    }
}
bool cviii_jp0667_effect(const uint8_t *before,size_t n,
                         const CviiiJp0667Effect *e,
                         uint8_t *after,size_t m,uint8_t *consumed)
{
    if(!before || !e || !after || !consumed || before==after ||
       n!=CVIII_JP0667_RAM || m!=CVIII_JP0667_RAM || e->mode>=5u)
        return false;
    unsigned w=e->opcode==0xebu?(e->arguments[0]==0u?2u:3u):width(e->opcode);
    if(w==0u || e->argument_count!=w-1u)return false;
    uint8_t ram[CVIII_JP0667_RAM];memcpy(ram,before,sizeof(ram));
    const unsigned x=e->mode;
    const uint8_t a=e->arguments[0],b=e->arguments[1],c=e->arguments[2];
    if((e->opcode&0xf0u)==0xd0u){
        ram[0x0112u+x]=(uint8_t)(e->opcode&15u);
        ram[0x017eu+x]=(uint8_t)(a&0xf0u);
        ram[0x0175u+x]=(uint8_t)(a&15u);
        ram[0x01b7u+x]=b;
        ram[0x0187u+x]=(b&0x80u)?0u:ram[0x0175u+x];
        ram[0x03d9u+x]=(uint8_t)(c&15u);
        ram[0x03deu+x]=(uint8_t)(c>>4);
    }else if(e->opcode<=0xe5u){
        ram[0x018eu+x]&=0x7fu;
        ram[0x01a3u+x]=(uint8_t)(e->opcode&15u);
    }else switch(e->opcode){
        case 0xe6u:
            ram[0x0112u+x]=(ram[0x018eu+x]&0x80u)?(uint8_t)(a&15u):a;
            break;
        case 0xe7u:
            if((ram[0x018eu+x]&0x80u)!=0u || (a>>4)>9u)return false;
            ram[0x01b7u+x]=a;ram[0x018eu+x]&=0x7fu;break;
        case 0xe8u:
            ram[0x03d9u+x]=(uint8_t)(a&15u);
            ram[0x03deu+x]=(uint8_t)(a>>4);
            break;
        case 0xe9u:
            if(!a){
                ram[0x018eu+x]&=0xdfu;
                ram[0x03e8u+x]=0u;
            }else if((a&15u)==0u){
                ram[0x017eu+x]=a;
            }else{
                ram[0x03e8u+x]=a;
                ram[0x018eu+x]|=0x20u;
            }
            break;
        case 0xeau:
            ram[0x01a8u+x]=(uint8_t)((a<<1)|(a&0x80u));
            break;
        case 0xebu:
            if(!a)ram[0x018eu+x]&=0xefu;
            else{
                ram[0x06a5u+x]=(uint8_t)(a-0x50u);
                ram[0x018eu+x]|=0x10u;
                unsigned rep=b>>4;
                unsigned unit=ram[0x0112u+x];
                unsigned acc=unit,carry=0u;
                if(rep==0u)acc=0u;
                else for(unsigned i=1u;i<rep;++i){
                    unsigned sum=acc+unit+carry;
                    acc=sum&255u;carry=sum>>8;
                }
                ram[0x03edu+x]=(uint8_t)acc;
                ram[0x03f7u+x]=(uint8_t)(b&15u);
            }
            break;
        case 0xecu:
            if((ram[0x018eu+x]&0x80u)!=0u) {
                if((a&15u)==0u){ram[0x06b4u+x]=0x80u;}
                else if((a&15u)<4u){ram[0x06b4u+x]=(uint8_t)(0x40u|(a&15u));ram[0x06b9u+x]=0u;}
                else {ram[0x06b4u+x]=(uint8_t)(0x50u|((a&15u)-3u));ram[0x06b9u+x]=0u;}
            }else{
                if(a==0u)ram[0x06b4u+x]=0x80u;
                else if(a<4u){ram[0x06b4u+x]=(uint8_t)(a|0x40u);ram[0x06b9u+x]=0u;}
                else {ram[0x06b4u+x]=(uint8_t)(0x50u|(a-3u));ram[0x06b9u+x]=0u;}
            }
            break;
        case 0xeeu:ram[0x01beu]=a;break;
        default:return false;
    }
    memcpy(after,ram,sizeof(ram));*consumed=(uint8_t)w;
    return true;
}
