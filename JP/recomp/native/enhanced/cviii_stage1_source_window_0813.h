/* JP0813: original raw0A:$8213-$8254 admission, observer-only.
 * No original data, guest writes, actor allocation or AI simulation. */
#ifndef CVIII_STAGE1_SOURCE_WINDOW_0813_H
#define CVIII_STAGE1_SOURCE_WINDOW_0813_H
#include <stdint.h>
typedef struct {
    uint8_t admitted;    /* Original $8213-$8254 reaches JSR $8275. */
    uint8_t local_axis;  /* Original $8248 output ($02+$37)&$FF. */
} CviiiStage1Admission0813;
static inline CviiiStage1Admission0813 cviii_stage1_admit_0813(
    uint16_t object_axis, uint16_t camera_axis)
{
    CviiiStage1Admission0813 out={0,0};
    uint8_t obj_lo=(uint8_t)object_axis, obj_hi=(uint8_t)(object_axis>>8);
    uint8_t cam_lo=(uint8_t)camera_axis, cam_hi=(uint8_t)(camera_axis>>8);
    unsigned borrow=obj_lo<cam_lo;
    uint8_t low=(uint8_t)(obj_lo-cam_lo);
    uint8_t high=(uint8_t)(obj_hi-cam_hi-borrow);
    if(high&0x80u)return out; /* $8220 BMI */
    uint8_t page=(uint8_t)(obj_hi-cam_hi); /* $8223, independent SEC */
    if(page!=0) {
        if(page!=1u)return out; /* $822C BNE */
        borrow=low<0x10u;
        low=(uint8_t)(low-0x10u); /* $8231 SBC #$10 */
        high=(uint8_t)(high-borrow); /* $8237 DEC $03 */
    }
    if(high || low>=0xb9u)return out; /* $8239-$8241 */
    out.admitted=1u;
    out.local_axis=(uint8_t)(low+0x37u);
    return out;
}
#endif
