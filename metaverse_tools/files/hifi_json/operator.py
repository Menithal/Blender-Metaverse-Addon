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
import os

from metaverse_tools.files.hifi_json.loader import load_file
from metaverse_tools.files.hifi_json.writer import write_file

from bpy_extras.io_utils import (
    ImportHelper,
    ExportHelper
)
from bpy.props import (
    StringProperty,
    BoolProperty,
    FloatProperty,
    EnumProperty
)

class EXPORT_OT_MVT_TOOLSET_Message_Error_Missing_ATP_Override(bpy.types.Operator):
    """ This Operator to show an error that the ATP Override is missing from export
    """
    bl_idname = "metaverse_toolset_messages.export_missing_atp_override"
    bl_label = "You must either select ATP export or override a baseURL for your host (be it marketplace or your own)"
    bl_options = {'REGISTER', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        return True

    def invoke(self, context, even):
        print("Invoked")
        wm = context.window_manager
        return wm.invoke_popup(self, width=400, height=300)

    def execute(self, context):
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        row.label(text="Warning:", icon="ERROR")
        row = layout.row()
        row.label(text="You must either select ATP export ")
        row = layout.row()
        row.label(text=" or override a baseURL for your host")
        row = layout.row()
        row.label(text=" (be it marketplace or your own)")


class EXPORT_OT_MVT_TOOLSET_Writer_FBX_JSON(bpy.types.Operator, ExportHelper):
    """ This Operator to show an error that the ATP Override is missing from export
    """
    bl_idname = "metaverse_toolset.export_fbx_json"
    bl_label = "Export HiFi Scene"
    bl_options = {'UNDO'}

    filename_ext = ".hifi.json"

    directory: StringProperty()
    filter_glob: StringProperty(default="*.hifi.json", options={'HIDDEN'})

    atp: BoolProperty(default=False, name="Use ATP / Upload to domain",
                      description="Use ATP instead of Marketplace / upload assets to domain")
    use_folder: BoolProperty(default=True, name="Use Folder",
                             description="Upload Files as a folder instead of individually")

    url_override: StringProperty(default="", name="Marketplace / Base Url",
                                 description="Set Marketplace / URL Path here to override")
    clone_scene: BoolProperty(default=False, name="Clone Scene prior to export", description="Clones the scene and performs the automated export functions on the clone instead of the original. " +
                              "WARNING: instancing will not work, and ids will no longer be the same, for future features.")
    remove_trailing: BoolProperty(
        default=False, name="Remove Trailing .### from names")

    def draw(self, context):
        layout = self.layout

        layout.prop(self, "atp")

        if not self.atp:
            layout.label(
                text="Url Override: Add Marketplace / URL to make sure that the content can be reached.")
            layout.prop(self, "url_override")
        else:
            layout.prop(self, "use_folder")

        layout.label(
            text="Clone scene: Performs automated actions on a cloned scene instead of the original.")
        layout.prop(self, "clone_scene")
        layout.prop(self, "remove_trailing")

    def execute(self, context):
        if not self.filepath:
            raise Exception("filepath not set")

        if not self.url_override and not self.atp:
            
            bpy.ops.metaverse_toolset_messages.export_missing_atp_override('INVOKE_DEFAULT')
            return {'CANCELLED'}
           # raise Exception("You must Use ATP or Set the Marketplace / base URL to make sure that the content can be reached after you upload it. ATP currently not supported")

        write_file(self)

        return {'FINISHED'}

class EXPORT_OT_MVT_TOOLSET_Writer_GLTF_JSON(bpy.types.Operator, ExportHelper):
    """ This Operator to show an error that the ATP Override is missing from export
    """
    bl_idname = "metaverse_toolset.export_gltb_json"
    bl_label = "Export HiFi Scene"
    bl_options = {'UNDO'}

    filename_ext = ".hifi.json"

    directory: StringProperty()
    filter_glob: StringProperty(default="*.hifi.json", options={'HIDDEN'})

    atp: BoolProperty(default=False, name="Use ATP / Upload to domain",
                      description="Use ATP instead of Marketplace / upload assets to domain")
    use_folder: BoolProperty(default=True, name="Use Folder",
                             description="Upload Files as a folder instead of individually")

    url_override: StringProperty(default="", name="Marketplace / Base Url",
                                 description="Set Marketplace / URL Path here to override")
    clone_scene: BoolProperty(default=False, name="Clone Scene prior to export", description="Clones the scene and performs the automated export functions on the clone instead of the original. " +
                              "WARNING: instancing will not work, and ids will no longer be the same, for future features.")
    remove_trailing: BoolProperty(
        default=False, name="Remove Trailing .### from names")

    def draw(self, context):
        layout = self.layout

        layout.prop(self, "atp")

        if not self.atp:
            layout.label(
                text="Url Override: Add Marketplace / URL to make sure that the content can be reached.")
            layout.prop(self, "url_override")
        else:
            layout.prop(self, "use_folder")

        layout.label(
            text="Clone scene: Performs automated actions on a cloned scene instead of the original.")
        layout.prop(self, "clone_scene")
        layout.prop(self, "remove_trailing")

    def execute(self, context):
        if not self.filepath:
            raise Exception("filepath not set")

        if not self.url_override and not self.atp:
            
            bpy.ops.metaverse_toolset_messages.export_missing_atp_override('INVOKE_DEFAULT')
            return {'CANCELLED'}
           # raise Exception("You must Use ATP or Set the Marketplace / base URL to make sure that the content can be reached after you upload it. ATP currently not supported")

        write_file(self, True)

        return {'FINISHED'}



class IMPORT_OT_MVT_TOOLSET_Scene_From_JSON(bpy.types.Operator, ImportHelper):
    """ Import a metaverse_toolset.json.svo scene into Blender. Works only for Primitives for now.
    """
    # Load a Hifi File
    bl_idname = "metaverse_toolset.import_scene_from_json"
    bl_label = "Import Hifi Json"
    bl_options = {"UNDO", "PRESET"}

    directory: StringProperty()

    filename_ext = ".json"
    filter_glob: StringProperty(default="*.json", options={'HIDDEN'})

    uv_sphere: BoolProperty(
        name="Use UV Sphere",
        description="Uses UV Sphere instead of Quad Sphere",
        default=False,
    )

    join_children: BoolProperty(
        name="Join Mesh Children",
        description="Joins Child Mesh with their parents to form a single object. Instead of keeping everything separate",
        default=True,
    )

    merge_distance: FloatProperty(
        name="Merge Distance",
        description="Merge close vertices together",
        min=0.0, max=1.0,
        default=0.001,
    )

    delete_interior_faces: BoolProperty(
        name="Delete interior Faces",
        description="If Mesh is made whole with Merge, make sure to remove interior faces",
        default=True,
    )

    use_boolean_operation: EnumProperty(
        items=(('NONE', "None", "Do not use boolean operations"),
               ('CARVE', "Carve", "EXPERIMENTAL: Use CARVE boolean Operation to join mesh"),
               ('BMESH', "BMesh", "EXPERIMENTAL: Use BMESH boolean Operation to join mesh")),
        name="Boolean",
        description="EXPERIMENTAL: Enable Boolean Operation when joining parents",
    )

    def draw(self, context):
        layout = self.layout

        sub = layout.column()

        sub.prop(self, "uv_sphere")
        sub.prop(self, "join_children")

        sub.prop(self, "merge_distance")

        sub.prop(self, "delete_interior_faces")
        sub.prop(self, "use_boolean_operation")
        sub.prop(self, "use_gltf")

    def execute(self, context):
        keywords = self.as_keywords(ignore=("filter_glob", "directory"))
        return load_file(self, context, **keywords)
