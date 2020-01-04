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

from metaverse_tools.utils.helpers import materials, mesh
from metaverse_tools.utils.bones import bones_builder

# POSSIBLY DEPRICATED... :( Custom Avatar should be able to do the same thing but better.


def convert_mixamo_avatar_hifi():
    if not bpy.data.is_saved:
        print("Select a Directory")
        bpy.ops.metaverse_toolset_messages.remind_save('INVOKE_DEFAULT')
        return

    try:
        bpy.ops.wm.console_toggle()
    except:
        print("Console was toggled")

    print("Converting Mixamo Avatar to be Blender- High Fidelity compliant")
    print("Searching for  mixamo:: prefix bones")
    bones_builder.remove_all_actions()

    for obj in bpy.context.view_layer.objects:
        if obj.type == "ARMATURE":

            bones_builder.scale_helper(obj)

            for bone in obj.data.edit_bones:
                print(" - Renaming", bone.name)
                bone.name = bone.name.replace("mixamo::", "")

        if obj.type == "MESH":
            print("Cleaning unused vertex groups")
            mesh.clean_unused_vertex_groups(obj)

    # for material in bpy.data.materials:
    #    materials.flip_material_specular(material)

    print("Texture pass")
    materials.convert_to_png(bpy.data.images)
    materials.convert_images_to_mask(bpy.data.images)

    # materials.cleanup_alpha(bpy.data.materials)
    bpy.ops.file.make_paths_absolute()

    try:
        bpy.ops.wm.console_toggle()
    except:
        print("Console was toggled")
