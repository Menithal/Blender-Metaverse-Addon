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

from metaverse_tools.utils.facerig.models import FaceRigMaterialOptions
from metaverse_tools.utils.facerig.statics import SHADER_DOUBLE_SIDED_NORMALS, SHADER_MASK, SHADER_BLENDING
from metaverse_tools.utils.facerig.models import *

def set_facerig_material_name(base_model_name:str, material_name:str, options:FaceRigMaterialOptions = FaceRigMaterialOptions()):
    current_name = base_model_name + "_" + options.material_type + "_" + material_name

    if(options.both_normals):
        current_name = current_name + SHADER_DOUBLE_SIDED_NORMALS
    
    if (options.alpha_enabled):
        if (options.alpha_mask):
            current_name = current_name + SHADER_MASK
        else:
            current_name = current_name + SHADER_BLENDING
    
    return current_name.lower()


def apply_constraints(bone: PoseBone, constraints: [FaceRigBoneConstraints]):

    pass