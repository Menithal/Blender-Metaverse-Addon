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

# Adding Armature related functions to the Blender Hifi Tool set
# 

import bpy
import sys
from .hifi_armature_data import structure as base_armature
from .hifi_armature_repose import retarget_armature, correct_scale_rotation
from mathutils import Quaternion, Vector, Euler, Matrix

if "bpy" in locals():
    import importlib
    if "hifi_armature_repose" in locals():
        importlib.reload(hifi_armature_repose)

def list_tuple(l):
    if len(l) == 4:
        return(l[0], l[1], l[2], l[3])
    
    return (l[0], l[1], l[2])
    

def list_vector(l):
    t = list_tuple(l)
    return Vector(t)
    
    
def list_matrix(v):
    return Matrix( (v[0], v[1], v[2], v[3]))


def build_armature_structure(data, current_node, parent):

    name = current_node["name"] 
    bpy.ops.armature.bone_primitive_add(name=name)
    
    current_bone_index = data.edit_bones.find(name)
    current_bone = data.edit_bones[current_bone_index]
    
    current_bone.parent = parent
        
    current_bone.head = current_node["head"]
    current_bone.tail = current_node["tail"]
    mat = current_node['matrix']
    current_bone.matrix = mat
    
    if current_node["connect"]:
        current_bone.use_connect = True
        
    for child in current_node["children"]:
        build_armature_structure(data, child, current_bone)
    
    return current_bone


def build_skeleton():
    current_view = bpy.context.area.type

    try:
        bpy.context.area.type = 'VIEW_3D'
        # set context to 3D View and set Cursor
        bpy.context.space_data.cursor_location[0] = 0.0
        bpy.context.space_data.cursor_location[1] = 0.0
        bpy.context.space_data.cursor_location[2] = 0.0
        
        print ( "----------------------")
        print ( "Creating Base Armature")
        print ( "----------------------")
        # Reset mode to Object, just to be sure
        
        if bpy.context.active_object:
            bpy.ops.object.mode_set(mode = 'OBJECT')
            
        bpy.ops.object.add(type="ARMATURE", enter_editmode=True)
        
        current_armature = bpy.context.active_object
        
        current_armature.name = "HifiArmature"
        
        for root_bone in base_armature:
            build_armature_structure(current_armature.data, root_bone, None) 
           
        correct_scale_rotation(bpy.context.active_object, True)

    except Exception as detail:
        print('Error', detail)

    finally:
        bpy.context.area.type = current_view


class HifiArmaturePanel(bpy.types.Panel):
    bl_idname = "armature_toolset.hifi"
    bl_label = "Hifi Metaverse Toolset"
    
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "High Fidelity"
    
    
    @classmethod
    def poll(self, context):
        return context.mode == "OBJECT"
    
    def draw(self, context):
        layout = self.layout
        layout.operator(HifiArmatureCreateOperator.bl_idname)
        layout.operator(HifiArmaturePoseOperator.bl_idname)
        layout.operator(HifiArmatureRetargetPoseOperator.bl_idname)
        return None


class HifiArmatureCreateOperator(bpy.types.Operator):
    bl_idname = "armature_toolset_create_base_rig.hifi"
    bl_label = "Add HiFi Armature"
    
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "High Fidelity"
    
    def execute(self, context):
        build_skeleton()        
        return {'FINISHED'}


class HifiArmatureRetargetPoseOperator(bpy.types.Operator):
    bl_idname = "armature_toolset_retarget.hifi"
    bl_label = "Retarget Avatar Pose / Fix Avatar"
    
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "High Fidelity"
    
    def execute(self, context):
        retarget_armature({'apply': True})
        return {'FINISHED'}


class HifiArmaturePoseOperator(bpy.types.Operator):
    bl_idname = "armature_toolset_pose.hifi"
    bl_label = "Test with Hifi Avatar rest Pose"
    
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "High Fidelity"
    
    def execute(self, context):
        retarget_armature({'apply': False})
        return {'FINISHED'}



classes = [
    HifiArmaturePanel,
    HifiArmatureCreateOperator,
    HifiArmatureRetargetPoseOperator,
    HifiArmaturePoseOperator
]

def armature_create_menu_func(self,context):
    self.layout.operator(HifiArmatureCreateOperator.bl_idname,
        text="Add HiFi Armature",
        icon="ARMATURE_DATA")


def armature_ui_register():
    for cls in classes:    
        bpy.utils.register_class(cls)
    
    bpy.types.INFO_MT_armature_add.append(armature_create_menu_func)

def armature_ui_unregister(): 
    for cls in classes:    
        bpy.utils.unregister_class(cls)
    
    bpy.types.INFO_MT_armature_add.remove(armature_create_menu_func)

if __name__ == "__main__":
    armature_ui_register()