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
class FaceRigAnimationSetFlags:
    def __init__(self, mirrorable=False, relatedAnim=""):
        self.mirrorable = mirrorable
        self.relatedAnim = relatedAnim


class FaceRigAnimationSetFrames:
    def __init__(self, idlePose=15, bPose=30, aPose=0):
        self.idlePose = idlePose
        self.aPose = aPose
        self.bPose = bPose


class FaceRigAnimationSet:
    def __init__(self, 
                name, 
                options=FaceRigAnimationSetFlags(), 
                frames=FaceRigAnimationSetFrames()
                ):
        self.name = name
        self.frames = frames
        self.options = options


class FaceRigMaterialOptions:
    def __init__(self, material_type = "", both_normals = False, alpha_enabled = False, alpha_mask = False):
        self.material_type = material_type
        self.both_normals = both_normals
        self.alpha_enabled = alpha_enabled
        self.alpha_mask = alpha_mask

