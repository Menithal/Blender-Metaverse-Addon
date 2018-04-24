import bpy
import os
import hifi_tools.files.fst.writer as FSTWriter
import hifi_tools.utils.bones as bones

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

class FSTWriterOperator(bpy.types.Operator, ExportHelper):
    bl_idname = "export_avatar.hifi_fbx_fst"
    bl_label = "Export Hifi Avatar"
    bl_options = {'UNDO'}

    directory = StringProperty()
    filename_ext = ".fst"

    filter_glob = StringProperty(default="*.fst", options={'HIDDEN'})
    selected_only = BoolProperty(
        default=False, name="Selected Only", description="Selected Only")

    embed = BoolProperty(default=False, name="Embed Textures",
                         description="Embed Textures to Exported Model")

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "selected_only")
        layout.prop(self, "embed")

    def execute(self, context):
        if not self.filepath:
            raise Exception("filepath not set")

        to_export = None

        if self.selected_only:
            to_export = list(bpy.context.selected_objects)
        else:
            to_export = list(bpy.data.objects)

        self.scale = 1 # Add scene scale here

        FSTWriter.fst_export(self, to_export)

        return {'FINISHED'}
