
import bpy
from metaverse_tools.utils.helpers import mesh

class MESH_PT_MVT_TOOLSET(bpy.types.Panel):
    """ Panel for Mesh related tools """
    bl_label = "Mesh Tools"

    bl_region_type = "TOOLS"
    bl_space_type = "VIEW_3D"

    @classmethod
    def poll(self, context):
        return len(context.selected_objects) >= 1 and context.active_object is not None and context.active_object.type == "MESH"

    def draw(self, context):
        layout = self.layout

        layout.operator(
            MESH_OT_MVT_TOOL_Merge_Modifiers_Shapekey.bl_idname, icon='MODIFIER_DATA',  emboss=False)
        layout.operator(
            MESH_OT_MVT_TOOL_Clean_Unused_Vertex_Groups.bl_idname, icon='NORMALS_VERTEX',  emboss=False)
        layout.operator(
            OBJECT_OT_MVT_TOOL_Boolean_Unite.bl_idname, icon='SELECT_EXTEND',  emboss=False)
        return None

# boolean_union_objects

class MESH_OT_MVT_TOOL_Message_Processing(bpy.types.Operator):
    """ This Operator is used show yes indeed we are doing something.
    """
    bl_idname = "metaverse_toolset_messages.processing"
    bl_label = ""
    bl_options = {'REGISTER', 'INTERNAL'}

    def invoke(self, context, even):
        print("Invoked")
        wm = context.window_manager
        return wm.invoke_popup(self, width=400, height=600)

    def execute(self, context):
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        row.label(text="Notice:", icon="QUESTION")
        row = layout.row()
        row.label(
            text="Processing: This may take a while. Click Out to see when done")


class MESH_OT_MVT_TOOL_Message_Done(bpy.types.Operator):
    """ This Operator is used show we are done
    """
    bl_idname = "metaverse_toolset_messages.done"
    bl_label = ""
    bl_options = {'REGISTER', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        return True

    def invoke(self, context, even):
        print("Invoked")
        wm = context.window_manager
        return wm.invoke_popup(self, width=400, height=600)

    def execute(self, context):
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        row.label(text="Done!", icon="FILE_TICK")


class MESH_OT_MVT_TOOL_Merge_Modifiers_Shapekey(bpy.types.Operator):
    """ Helper Operator to attempt to merge modifiers onto Mesh with Shapekeys using Przemysław Bągard's ApplyModifierForObjectWithShapeKeys modified for 2.8 """
    bl_idname = "metaverse_toolset.merge_modifiers_on_shapekeys"
    bl_label = "Merge Modifiers & Shapekeys"

    bl_space_type = "VIEW_3D"

    @classmethod
    def poll(self, context):
        return context.active_object is not None and context.active_object.type == "MESH" and context.active_object.data.shape_keys is not None and len(context.active_object.data.shape_keys.key_blocks) > 0

    def execute(self, context):
        bpy.ops.object.apply_modifier_for_object_with_shape_keys(
            'INVOKE_DEFAULT')

        return {"FINISHED"}


class MESH_OT_MVT_TOOL_Clean_Unused_Vertex_Groups(bpy.types.Operator):
    """ Helper Operator to clean a mesh from unused vertex groups (groups that have not been bound to armature)"""
    bl_idname = "metaverse_toolset.clean_unused_vertex_groups"
    bl_label = "Clean Unused Vertex Groups"

    bl_space_type = "VIEW_3D"

    @classmethod
    def poll(self, context):
        return context.active_object is not None and context.active_object.type == "MESH" and len(context.active_object.vertex_groups) > 0

    def execute(self, context):
        mesh.clean_unused_vertex_groups(context.active_object)
        return {"FINISHED"}


class OBJECT_OT_MVT_TOOL_Boolean_Unite(bpy.types.Operator):
    """ Quick Helper Button to merge with Boolean Operation objects  """
    bl_label = "Boolean Unite"
    bl_idname = "metaverse_toolset.boolean_operate_unite_selected_to_active"
    bl_space_type = "VIEW_3D"

    @classmethod
    def poll(self, context):
        return len(context.selected_objects) > 1 and context.active_object is not None and context.active_object.type == "MESH"

    def execute(self, context):
        mesh.boolean_union_objects(context.active_object, context.selected_objects)
        return {"FINISHED"}



classes = (
    MESH_PT_MVT_TOOLSET,
    MESH_OT_MVT_TOOL_Message_Done,
    MESH_OT_MVT_TOOL_Message_Processing,
    MESH_OT_MVT_TOOL_Merge_Modifiers_Shapekey,
    MESH_OT_MVT_TOOL_Clean_Unused_Vertex_Groups,
    OBJECT_OT_MVT_TOOL_Boolean_Unite
)

module_register, module_unregister = bpy.utils.register_classes_factory(
    classes)


def register_operators():
    module_register()


def unregister_operators():
    module_unregister()