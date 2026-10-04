#include "collision_math.hpp"

// Intentionally header-driven: these primitives are constexpr so the same
// exact 8-bit behavior can be used in tests and future native object/collision
// lifts without host-width promotion changing semantics.
