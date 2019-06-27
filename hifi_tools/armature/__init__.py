
from . import (
    hifi_skeleton,
    vrc_skeleton
)

import bpy
from enum import Enum


class SkeletonTypes(Enum):
    HIFI = (hifi_skeleton.structure, 67)
    VRC = (vrc_skeleton.structure, 55)

    def __init__(self, structure, count, ):
        self.structure = structure
        self.count = count

    @staticmethod
    def get_type_from_armature(obj):
        if obj.type != "ARMATURE":
            return None

        

        if len(obj.data.bones) < 55:
            return None

        if obj.data.bones.index("Chest"):
            return SkeletonTypes.VRC

        return SkeletonTypes.HIFI

