#ifndef CVIII_ROOM_NATIVE_HOST_0660_H
#define CVIII_ROOM_NATIVE_HOST_0660_H
#include "cviii_room_native_bridge_0660.h"
/* Attach only when all required NESRecomp observers are free; no chaining
 * across unknown plugins. Original CPU always executes unchanged. */
int cviii_bridge0660_attach(CviiiRoomNativeBridge0660 *bridge);
void cviii_bridge0660_boundary(CviiiRoomNativeBridge0660 *bridge);
#endif