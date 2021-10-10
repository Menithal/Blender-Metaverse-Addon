
import bpy
from metaverse_tools.utils.animation.action import *

class ACTION_PT_MVT_TOOLSET(bpy.types.Panel):
    """ Panel for Dopesheet related tools """
    bl_label = "General Action Tools"

    bl_space_type = "DOPESHEET_EDITOR"
    bl_region_type = "UI"

    def draw(self, context):
        layout = self.layout
        layout.operator(ACTION_OT_MVT_Split_Mirrored.bl_idname)

        return None


class ACTION_OT_MVT_Split_Mirrored(bpy.types.Operator):
    """ Helper Operator Make split animations from sets of combined animations """
    bl_idname = "metaverse_toolset.split_mirroable_actions"
    bl_label = "Split Mirrorable Actions"

    bl_space_type = "DOPESHEET_EDITOR"

    def execute(self, context):
        split_all_actions(bpy.context.active_object, bpy.data.actions)
        return {"FINISHED"}


classes = (
    ACTION_PT_MVT_TOOLSET,
    ACTION_OT_MVT_Split_Mirrored
)

module_register, module_unregister = bpy.utils.register_classes_factory(
    classes)

def register_operators():
    module_register()


def unregister_operators():
    module_unregister()
