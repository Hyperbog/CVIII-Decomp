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
           offsetof(NestStudioMapping,sprites)==10368?0:1;
}
