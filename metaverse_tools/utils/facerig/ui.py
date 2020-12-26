import bpy
import metaverse_tools.utils.facerig.ui as facerig


class ACTION_PT_MVT_Facerig_Tools(bpy.types.Panel):
    """ Panel for Dopespheer related tools """
    bl_label = "Facerig/Animaze Tools"

    bl_space_type = "DOPESHEET_EDITOR"
    bl_region_type = "UI"

    def draw(self, context):
        layout = self.layout

        layout.operator(ACTION_OT_MVT_Generate_Facerig_Movements.bl_idname)
        return None

class ACTION_OT_MVT_Generate_Facerig_Movements(bpy.types.Operator):
    """ Helper Operator to generate facerig / Animaze avatar movements """
    bl_idname = "metaverse_toolset.generate_movement_actions"
    bl_label = "Split Mirrorable Actions"

    bl_space_type = "DOPESHEET_EDITOR"

    def execute(self, context):
        #split_all_actions(bpy.context.active_object, bpy.data.actions)
        return {"FINISHED"}



classes = (
    ACTION_PT_MVT_Facerig_Tools,
    ACTION_OT_MVT_Generate_Facerig_Movements
)

module_register, module_unregister = bpy.utils.register_classes_factory(
    classes)

def register_operators():
    module_register()
    facerig.module_register()


def unregister_operators():
    module_unregister()
    facerig.module_unregister()
