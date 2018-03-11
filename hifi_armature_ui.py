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

# TODO: Experiemntal Adding Armature to Scene and Sync.


import bpy
import sys
from hifi_armature import structure as base_armature
from mathutils import Quaternion, Vector, Euler, Matrix

if "bpy" in locals():
    import importlib
    if "hifi_armature" in locals():
        importlib.reload(hifi_armature)

def list_tuple(l):
    if len(l) == 4:
        return(l[0], l[1], l[2], l[3])
    
    return (l[0], l[1], l[2])
    

def list_vector(l):
    t = list_tuple(l)
    print(t, l)
    return Vector(t)
    
    
def list_matrix(v):
    return Matrix( (v[0], v[1], v[2], v[3]))


def build_armature_structure(data, current_node, parent):

    name = current_node["name"] 
    bpy.ops.armature.bone_primitive_add(name=name)
    # Refresh Bone Tree after Addition
    #bpy.ops.object.mode_set(mode='POSE')
    #bpy.ops.object.mode_set(mode='EDIT')
    
    current_bone_index = data.edit_bones.find(name)
    current_bone = data.edit_bones[current_bone_index]
    
    current_bone.parent = parent
        
    current_bone.head = list_vector(current_node["head"])
    current_bone.tail = list_vector(current_node["tail"])
    mat = list_matrix(current_node['rotation'])
    current_bone.matrix = mat
    
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
            
        print ("Adding Armature" )
        bpy.ops.object.add(type="ARMATURE", enter_editmode=True)
        
        current_armature = bpy.context.active_object
        
        current_armature.name = "HifiArmature"
        
        for root_bone in base_armature:
            build_armature_structure(current_armature.data, root_bone, None) 
           
        #bpy.ops.object.mode_set(mode = 'OBJECT')    

    except Exception as detail:
        print('Error', detail)

    finally:
        bpy.context.area.type = current_view
        

build_skeleton()
