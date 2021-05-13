from . import (
    bones_builder,
    mmd,
    mixamo,
    custom,
)

import math
from mathutils import Matrix, Vector, Euler



def euler_to_degrees(euler) -> (Vector, str):
    vector = Vector()
    vector.x = math.degrees(euler.x)
    vector.y = math.degrees(euler.y)
    vector.z = math.degrees(euler.z)
    return (vector, euler.order)