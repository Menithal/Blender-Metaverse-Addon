
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

# Helper script for Extrating details of the Armature data

import json
import bpy


def matrix4_to_dict(m):
    return [vec4_to_list(m[0]),
        vec4_to_list(m[1]),
        vec4_to_list(m[2]),
        vec4_to_list(m[3])]

def vec4_to_list(v):
    return [v[0],v[1],v[2],v[3]]


def vec_to_list(v):
    return [v.x,v.y,v.z]

def build_armature(bone, tree):
    
    print(bone.name)
    rotation = matrix4_to_dict(bone.matrix)
    
    print(rotation)
    head = vec_to_list(bone.head)
    tail = vec_to_list(bone.tail)
    current_tree = {
        "name": bone.name,
        "rotation": rotation,
        "head": head,
        "tail": tail,
        "connect": bone.use_connect,
        "children": []
    }
        
    for child in bone.children:
        build_armature(child, current_tree["children"])
    
    tree.append(current_tree)
    return tree    
    

armature = bpy.context.object.data

print("---------------------------")
print("---------------------------")
print("---------------------------")

if bpy.context.active_object:
    bpy.ops.object.mode_set(mode = 'EDIT')
    
    print(armature.edit_bones[0].name)
    if len(armature.edit_bones) > 0:
        test = build_armature( armature.edit_bones[0], [])
        print(test)


bpy.ops.object.mode_set(mode = 'OBJECT')

#for bone in armature.bones:
#    rotation = quat_to_dict(bone.matrix.to_4x4().to_quaternion())
#    
#    head = vec_to_dict(bone.head)
#    tail = vec_to_dict(bone.tail)
    
#    print(bone.name, rotation, head, tail)
    
    