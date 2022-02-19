
from operator import truediv
import bpy

def get_curve_length(curve):
  depsgraph = bpy.context.evaluated_depsgraph_get()
  curveLength = sum (s.calc_length() for s in curve.evaluated_get(depsgraph).data.splines)
  return curveLength


def make_mesh_per_curve(curves, mesh, axis, duplicate=False):
  meshlayer = mesh+"-curves"
  if bpy.data.collections.get(meshlayer) is None:
    bpy.context.scene.collection.children.link(bpy.data.collections.new(meshlayer))

  mesh_collection = bpy.data.collections.get(meshlayer)

  for curve in curves:
    length = get_curve_length(curve)
    copied_curve = bpy.data.objects[mesh].copy()
    copied_curve.name = mesh + '-copy'
    copied_curve.dimensions.z = length*1.1
    if duplicate:
        co = copied_curve.data.copy()
        copied_curve.data = co
    
    mesh_collection.objects.link(copied_curve)
    modifier = copied_curve.modifiers.new("Curve", "CURVE")
    modifier.object = curve
    modifier.deform_axis = axis
    modifier.show_in_editmode = True
    modifier.show_on_cage = True


def get_meshes(self, context):
    obj = []
    count = 0
    for ob in context.scene.objects:
        if ob.type == 'MESH':
            if(ob.visible_get()):
                obj.append((ob.name, ob.name, "MESH"))
                count += 1

    return obj 



class CURVE_OT_MVT_TOOLSET_Hair_Mesh_To_Curves(bpy.types.Operator):
    bl_idname = "metaverse_toolset.duplicate_mesh_to_curves"
    bl_label = "Duplicate Mesh to Curves"
    
    bl_region_type = "TOOLS"
    bl_space_type = "VIEW_3D"
    bl_options = {'REGISTER', 'UNDO'}
    
    target_mesh: bpy.props.EnumProperty(
        name="Select Mesh", items=get_meshes)
    direction: bpy.props.EnumProperty(
        name="Direction", items=(('POS_X', 'X','AXIS_SIDE'),
        ('NEG_X','-X','AXIS_SIDE'),
        ('POS_Y','Y','AXIS_TOP'),
        ('NEG_Y','-Y','AXIS_TOP'),
        ('POS_Z','Z','AXIS_FRONT'),
        ('NEG_Z','-Z','AXIS_FRONT')))
    duplicate_data: bpy.props.BoolProperty()
    
    @classmethod
    def poll(self,context):
        return context.selected_objects is not None and len(context.selected_objects)  >= 1
    
    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=400)
    

    def execute(self, context):
        make_mesh_per_curve(context.selected_objects, self.target_mesh, self.direction, self.duplicate_data)
        return {'FINISHED'}


class CURVE_PT_MVT_TOOLSET(bpy.types.Panel):
    """  """
    bl_label = "Curve Tools"

    bl_region_type = "TOOLS"
    bl_space_type = "VIEW_3D"

    @classmethod
    def poll(self, context):
        return len(context.selected_objects) >= 1 and context.active_object is not None and context.active_object.type == "CURVE"

    def draw(self, context):
        layout = self.layout

        layout.operator(
            CURVE_OT_MVT_TOOLSET_Hair_Mesh_To_Curves.bl_idname, icon='MODIFIER_DATA',  emboss=False)
       
        return None

classes = [
    CURVE_PT_MVT_TOOLSET,
    CURVE_OT_MVT_TOOLSET_Hair_Mesh_To_Curves
]
    

module_register, module_unregister = bpy.utils.register_classes_factory(classes)
