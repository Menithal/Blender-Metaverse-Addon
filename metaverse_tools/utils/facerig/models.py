# -*- coding: utf-8 -*-
# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####
# Copyright 2020 Matti 'Menithal' Lahtinen

# TODO: Should Probably Universal 
import enum

class FaceRigAnimationSetFlags:
    def __init__(self, mirrorable:bool=False, relatedAnim:str=""):
        self.mirrorable = mirrorable
        self.relatedAnim = relatedAnim


class FaceRigAnimationSetFrames:
    def __init__(self, idlePose:int=15, bPose:int=30, aPose:int=0):
        self.idlePose = idlePose
        self.aPose = aPose
        self.bPose = bPose


class FaceRigAnimationSet:
    def __init__(self, 
                name:str, 
                options:FaceRigAnimationSetFlags = FaceRigAnimationSetFlags(), 
                frames:FaceRigAnimationSetFrames = FaceRigAnimationSetFrames()
                ):
        self.name = name
        self.frames = frames
        self.options = options


class FaceRigMaterialOptions:
    def __init__(self, material_type:str = "", both_normals:bool = False, alpha_enabled:bool = False, alpha_mask:bool = False):
        self.material_type = material_type
        self.both_normals = both_normals
        self.alpha_enabled = alpha_enabled
        self.alpha_mask = alpha_mask


class FaceRigConstraintType(enum.Enum):
    ROTATION_X = "rotation_x"
    ROTATION_Y = "rotation_y"
    ROTATION_Z = "rotation_z"


# TODO: robably could do a universal class Min Max stuff?
class FaceRigBoneValueConstraint:
    def __init__(self, constraint_type: FaceRigConstraintType, max_value, min_value = None):
        self.type: FaceRigConstraintType = constraint_type
        if(min_value == None):
            self.min: float = -max_value
        else:
            self.min: float = max_value

        self.max: float = max_value


# TODO: Probably could do a universal class for typing later? Seems fairly common
class FaceRigBoneConstraints:
    def __init__(self, name):
        self.name = name
        self.constraints: [FaceRigBoneValueConstraint] = []

    def append_constraint(self, constraint: FaceRigBoneValueConstraint = None):
        self.constraints.append(constraint)
        return self