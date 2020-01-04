
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
# Copyright 2019 Matti 'Menithal' Lahtinen
import bpy


def get_selected_or_all():
    selected = bpy.context.selected_objects
    if len(selected) < 1:
        selected = bpy.context.view_layer.objects
    return selected

# https://blenderartists.org/t/how-to-know-if-an-operator-is-registered/638803/4
def operator_exists(idname):
    from bpy.ops import op_as_string
    try:
        op_as_string(idname)
        return True
    except:
        return False


def move_bone_layer(bone, layer):
    print(layer, (1 == layer, 2 == layer, 3 == layer, 4 == layer, 5 == layer, 6 == layer, 7 == layer, 8 == layer, 9 == layer, 10 == layer,
                        11 == layer, 12 == layer, 13 == layer, 14 == layer, 15 == layer, 16 == layer, 17 == layer, 18 == layer, 19 == layer,  20 == layer,
                        21 == layer, 22 == layer, 23 == layer, 24 == layer, 25 == layer, 26 == layer, 27 == layer, 28 == layer, 29 == layer,  30 == layer,
                        31 == layer, 32 == layer))
    bone.layers = (1 == layer, 2 == layer, 3 == layer, 4 == layer, 5 == layer, 6 == layer, 7 == layer, 8 == layer, 9 == layer, 10 == layer,
                        11 == layer, 12 == layer, 13 == layer, 14 == layer, 15 == layer, 16 == layer, 17 == layer, 18 == layer, 19 == layer,  20 == layer,
                        21 == layer, 22 == layer, 23 == layer, 24 == layer, 25 == layer, 26 == layer, 27 == layer, 28 == layer, 29 == layer,  30 == layer,
                        31 == layer, 32 == layer)