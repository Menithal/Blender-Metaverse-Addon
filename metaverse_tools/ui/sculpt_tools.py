import bpy


class SCULPT_PT_MVT_TOOL_Panel(bpy.types.Panel):
    """ Panel for Sculpt related tools """
    bl_label = "Remesh Quicks"

    bl_region_type = "TOOLS"
    bl_space_type = "VIEW_3D"
    @classmethod
    def poll(self, context):
        return context.mode == "SCULPT"


    def draw(self, context):
        layout = self.layout

        row = layout.row()
        row.operator(
            SCULPT_OT_MVT_TOOL_Decrease_Res_5.bl_idname, 
            emboss=False)
        row.operator(
            SCULPT_OT_MVT_TOOL_Decrease_Res_10.bl_idname, 
            emboss=False)
        row = layout.row()
        row.operator(
            SCULPT_OT_MVT_TOOL_Increase_Res_10.bl_idname,
            emboss=False)
        row.operator(
            SCULPT_OT_MVT_TOOL_Increase_Res_5.bl_idname,
            emboss=False)
        return None

class SCULPT_OT_MVT_TOOL_Increase_Res_10(bpy.types.Operator):
    """ Simple utility increasing resolution and doing a remesh """
    bl_idname = "metaverse_toolset.sculpt_increase_res_remesh_10"
    bl_label = "+10"

    def execute(self, context):
        bpy.context.object.data.remesh_voxel_size = bpy.context.object.data.remesh_voxel_size + 0.1
        bpy.ops.object.voxel_remesh()
        return {'FINISHED'}


        
class SCULPT_OT_MVT_TOOL_Decrease_Res_10(bpy.types.Operator):
    """ Simple utility decrease resolution and doing a remesh """
    bl_idname = "metaverse_toolset.sculpt_decrease_res_remesh_10"
    bl_label = "-10"

    def execute(self, context):
        bpy.context.object.data.remesh_voxel_size = bpy.context.object.data.remesh_voxel_size - 0.1
        bpy.ops.object.voxel_remesh()
        return {'FINISHED'}


class SCULPT_OT_MVT_TOOL_Increase_Res_5(bpy.types.Operator):
    """ Simple utility increasing resolution and doing a remesh """
    bl_idname = "metaverse_toolset.sculpt_increase_res_remesh_5"
    bl_label = "+5"

    def execute(self, context):
        bpy.context.object.data.remesh_voxel_size = bpy.context.object.data.remesh_voxel_size + 0.05
        bpy.ops.object.voxel_remesh()
        return {'FINISHED'}

        
class SCULPT_OT_MVT_TOOL_Decrease_Res_5(bpy.types.Operator):
    """ Simple utility decrease resolution and doing a remesh """
    bl_idname = "metaverse_toolset.sculpt_decrease_res_remesh_5"
    bl_label = "-5"

    def execute(self, context):
        bpy.context.object.data.remesh_voxel_size = bpy.context.object.data.remesh_voxel_size - 0.05
        bpy.ops.object.voxel_remesh()
        return {'FINISHED'}



classes = (
    SCULPT_PT_MVT_TOOL_Panel,
    SCULPT_OT_MVT_TOOL_Increase_Res_5,
    SCULPT_OT_MVT_TOOL_Decrease_Res_5,
    SCULPT_OT_MVT_TOOL_Decrease_Res_10,
    SCULPT_OT_MVT_TOOL_Increase_Res_10

)
module_register, module_unregister = bpy.utils.register_classes_factory(classes)

def register_operators():
    module_register()


def unregister_operators():
    module_unregister()