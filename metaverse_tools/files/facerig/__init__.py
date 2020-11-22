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
import bpy
import os
import os.path as ntpath

from bpy_extras.io_utils import (
    ExportHelper
)

from metaverse_tools.utils.facerig.statics import *
from metaverse_tools.utils.bones.bones_builder import find_armature, clear_pose
from bpy.props import (
    StringProperty,
    BoolProperty,
    FloatProperty,
    EnumProperty
)


class EXPORT_OT_MVT_TOOLSET_Writer_Facerig_Bundle_DAE(bpy.types.Operator, ExportHelper):
    """ This Operator exports Facerig dae bundles"""

    bl_idname = "metaverse_toolset.export_facerig"
    bl_label = "Export FaceRig Avatar Bundle"
    bl_options = {'UNDO'}

    directory: StringProperty()
    filename_ext = ".dae"

    # TODO: instead create a new directory instead of a file.
    filter_glob: StringProperty(default="*.dae", options={'HIDDEN'}) 

    def execute(self, context):
        if not self.filepath:
            raise Exception("filepath not set")
        
        # Export Main Dae
        print(context.selected_objects)
        
        armature = find_armature(context.selected_objects)

        if armature is None:
            return {'CANCELLED'}


        if bpy.data.actions["idle1"] is  None:
            return {'CANCELLED'}

        # bpy.context.active_object.animation_data.action
        # Lets Export
        # generalMovement Folder
        
        # Create Folders.
        armature.animation_data.action = bpy.data.actions["idle1"]
        filename = ntpath.basename(self.filepath).replace('.dae', "")
        
        directory = ntpath.join(os.path.dirname(
            os.path.realpath(self.filepath)), filename)

        mkdir_if_not_exist(directory)

        anim_directory = ntpath.join(directory, "anim")

        mkdir_if_not_exist(anim_directory)

        actual_model_file = ntpath.join(directory,filename + ".dae")

        export_collada_file(actual_model_file)

        bpy.ops.object.select_all(action="DESELECT")
        armature.select_set(True)

        for action in bpy.data.actions:
            name = action.name
            clear_pose([armature])
            armature.animation_data.action = action
            
            if name in general_movement_names:
                directory = ntpath.join(anim_directory, general_movement_directory )
                mkdir_if_not_exist(directory)
            elif name in eye_and_eyebrows_names:
                directory = ntpath.join(anim_directory, eye_and_eyebrows_directory )
                mkdir_if_not_exist(directory)
            elif name in mouth_and_nose_names:
                directory = ntpath.join(anim_directory, mouth_and_nose_directory )
                mkdir_if_not_exist(directory)

            if directory is not None:
                action_file = ntpath.join(directory, name)
                export_collada_file(action_file, True)


        # bpy.ops.wm.collada_export(filepath='/Users/dave/test.dae', check_existing=False, filter_blender=False, filter_image=False, filter_movie=False, filter_python=False, filter_font=False, filter_sound=False, filter_text=False, filter_btx=False, filter_collada=True, filter_folder=True, filemode=8)
        # bpy.context.active_object.animation_data.action.groups to get current action's active stuff
        #
        clear_pose([armature])
        return {'FINISHED'}

def mkdir_if_not_exist(directory):
    if os.path.isdir(directory) == False:
        print("making missing directory " + directory)    
        os.mkdir(directory)


def export_collada_file(filepath, selected = False):
    print("export collada file " + filepath)
    bpy.ops.wm.collada_export(filepath=filepath, check_existing=False, selected=selected, include_all_actions = False )


#  bpy.context.active_object.animation_data.action.groups
# bpy.context.active_object.animation_data.action.groups['RightLip'].items(
