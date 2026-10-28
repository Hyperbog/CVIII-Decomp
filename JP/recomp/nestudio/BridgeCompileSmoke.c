/* Compile-only, ROM-free NEStudio host bridge contract.
 * Tests real Windows C compatibility without a private NES executable.
 * Runtime host functions are supplied by the actual owner C11 build.
 */
#include <stddef.h>
#include <stdint.h>
static void save_settings(void) {}
#include "../native/enhanced/cviii_nestudio_host_bridge.h"
int main(void)
{
    return sizeof(NestStudioLight)==80 &&
           sizeof(NestStudioSprite)==24 &&
           offsetof(NestStudioMapping,lights)==128 &&
           offsetof(NestStudioMapping,sprites)==10368 &&
           sizeof(NestStudioOriginalObject)==44 &&
           offsetof(NestStudioMapping,oam_phase)==11904 &&
           offsetof(NestStudioMapping,original_objects)==11912 &&
           offsetof(NestStudioMapping,original_dialogue)==13144 &&
           offsetof(NestStudioMapping,owner_for_oam)==13176 &&
           offsetof(NestStudioMapping,selected_original_mask)==13448 &&
           offsetof(NestStudioMapping,ec47_trace)==13468 &&
           offsetof(NestStudioMapping,ec47_queue_length)==13528 &&
           offsetof(NestStudioMapping,ec47_queue_bytes)==13536 &&
           offsetof(NestStudioMapping,lighting_scene)==13792 &&
           sizeof(NestStudioLightExtra)==56 &&
           sizeof(NestStudioKitBrief)==56 &&
           sizeof(NestStudioStyleBrief)==100 &&
           sizeof(NestStudioMaskBrief)==32 &&
           sizeof(NestStudioParticleBrief)==116 &&
           sizeof(NestStudioWeatherBrief)==104 &&
           offsetof(NestStudioMapping,light_extra)==13864 &&
           offsetof(NestStudioMapping,kits)==21032 &&
           offsetof(NestStudioMapping,styles)==21704 &&
           offsetof(NestStudioMapping,masks)==23304 &&
           offsetof(NestStudioMapping,particles)==25352 &&
           offsetof(NestStudioMapping,weather)==29064 &&
           offsetof(NestStudioMapping,command_text)==29896 &&
           sizeof(NestStudioMapping)==29944 &&
           NEST_VERSION==6 ?0:1;
}
