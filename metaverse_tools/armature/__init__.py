
from . import (
    hifi_skeleton,
    vrc_skeleton,
    tu_skeleton
)

import bpy
from enum import Enum

class SkeletonTypes(Enum):
    HIFI = (hifi_skeleton.structure, 67)
    VRC = (vrc_skeleton.structure, 55)
    TU = (tu_skeleton.structure, 61)

    def __init__(self, structure, count, ):
        self.structure = structure
        self.count = count

    @staticmethod
    def get_type_from_armature(obj):
        if obj.type != "ARMATURE":
            return None

        if len(obj.data.bones) < 55:
            return None
        
        # TODO: Better Detection Methods Later using skeletons.

        if obj.data.bones.find("Chest"):
            return SkeletonTypes.VRC

        if obj.data.bones.find("Spine2") or obj.data.bones.find("HeadTop_End"):
            return SkeletonTypes.HIFI

        for skeleton_type in SkeletonTypes:
            if len(obj.data.bones) == skeleton_type.count:
                return skeleton_type

        return None


