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
# Created by Matti 'Menithal' Lahtinen

import bpy
import re

from math import pi
from mathutils import Quaternion, Matrix, Vector, Euler
from hifi_tools.utils import mesh

from hifi_tools.armature.skeleton import structure as base_armature

corrected_axis = {
    "GLOBAL_NEG_Z": ["Shoulder", "Arm", "Hand", "Thumb"],
    "GLOBAL_NEG_Y": ["Spine", "Head", "Hips", "Leg", "Foot", "Toe", "Eye"]
}

bone_parent_structure = {
    "LeftToe": "LeftFoot",
    "RightToe": "RightFoot",
    "LeftFoot": "LeftLeg",
    "RightFoot": "RightLeg",
    "LeftLeg": "LeftUpLeg",
    "RightLeg": "RightUpLeg",
    "LeftUpLeg": "Hips",
    "RightUpLeg": "Hips",
    "Spine1": "Spine",
    "Spine2": "Spine1",
    "Spine": "Hips",
    "Neck": "Spine2",
    "Head": "Neck",
    "LeftShoulder": "Spine2",
    "RightShoulder": "Spine2",
    "LeftArm": "LeftShoulder",
    "RightArm": "RightShoulder",
    "LeftForeArm": "LeftArm",
    "RightForeArm": "RightArm",
    "LeftHand": "LeftForeArm",
    "RightHand": "RightForeArm",
    "RightEye": "Head",
    "LeftEye": "Head"
}


physical_re = re.compile("^sim")

number_re = re.compile("\\d+")
number_text_re = re.compile(".+(\\d+).*")
blender_copy_re = re.compile("\.001$")
end_re = re.compile("_end$")

def combine_bones(selected_bones, active_bone, active_object):
    print("----------------------")
    print("Combining Bones", len(selected_bones),
          "-", active_bone, "-", active_object)
    edit_bones = list(active_object.data.edit_bones)
    meshes = mesh.get_mesh_from(active_object.children)
    names_to_combine = []

    print("Removing Selected Bones first:")
    for bone in selected_bones:
        if bone.name != active_bone.name:
            print("Now Removing ", bone.name)
            children = list(bone.children)
            names_to_combine.append(bone.name)

            active_object.data.edit_bones.remove(
                bone)  # TODO: REmoval is broken :(
            for child in children:
                child.use_connect = True

    print("Combining weights.")
    bpy.ops.object.mode_set(mode='OBJECT')
    for name in names_to_combine:
        if name != active_bone.name:
            for me in meshes:
                bpy.context.scene.objects.active = me
                mesh.mix_weights(active_bone.name, name)
                me.vertex_groups.remove(me.vertex_groups.get(name))

    bpy.context.scene.objects.active = active_object
    bpy.ops.object.mode_set(mode='EDIT')
    print("Done")


# TODO: Fix Naming Convention!
def scale_helper(obj):
    if obj.dimensions.y > 2.4:
        print("Avatar too large > 2.4m, maybe incorrect? setting height to 1.9m. You can scale avatar inworld, instead")

        bpy.ops.object.mode_set(mode='OBJECT')
        scale = 1.9/obj.dimensions.y
        obj.dimensions = obj.dimensions * scale
        bpy.context.scene.objects.active = obj
        bpy.ops.object.transform_apply(
            location=False, rotation=False, scale=True)

        bpy.ops.object.mode_set(mode='POSE')
        bpy.ops.pose.select_all(action='SELECT')
        bpy.ops.pose.transforms_clear()

        bpy.ops.object.mode_set(mode='OBJECT')


def remove_all_actions():
    for action in bpy.data.actions:
        bpy.data.actions.remove(action)


def find_armatures(selection):
    armatures = []
    for selected in selection:
        if selected.type == "ARMATURE":
            armatures.append(selected)

    return armatures


def find_armature(selection):
    for selected in selection:
        if selected.type == "ARMATURE":
            return selected
    return None


def clean_up_bone_name(bone_name, remove_clones = True):
    if remove_clones:
        bone_name = blender_copy_re.sub("", bone_name)

    bone_name = bone_name.capitalize().replace('.', '_')
    # Remove .001 blender suffic First remove every dot with _ to remove confusion

    #bone_name = end_re.sub("", bone_name)
    
    split = bone_name.split("_")
    if "end" in split:
        end = True
    else:
        end = False
        
    length = len(split)
    last = None
    new_bone_split = []
    for idx, val in enumerate(split):
        if val is "r":
            new_bone_split.append("Right")
        elif val is "l":
            new_bone_split.append("Left")
        elif number_text_re.match(val):
            nr = number_text_re.match(val)
            group = nr.groups()
            if end:
                last = str(int(group[0]) + 1)
            else:
                last = group[0]
        elif number_re.match(val):  # value is a number, before the last
            print ("Idx", idx, length)
            if idx < length:
                print ("Storing")
                last = val.capitalize()
        elif val.lower() != "end":
            print(val)
            new_bone_split.append(val.capitalize())

    if last is not None:
        if end:
            new_bone_split.append( str(int(last) + 1))
        else:
            new_bone_split.append(last)

    return "".join(new_bone_split)


def set_selected_bones_physical(bones):
    for bone in bones:
        if physical_re.search(bone.name) is None:
            bone.name = "sim" + clean_up_bone_name(bone.name)


def remove_selected_bones_physical(bones):
    for bone in bones:
        if physical_re.search(bone.name) is not None:
            bone.name = physical_re.sub("", bone.name)


def correct_bone_parents(bones):
    keys = bone_parent_structure.keys()
    for bone in bones:
        if bone.name == "Hips":
            bone.parent = None
        else:
            parent = bone_parent_structure.get(bone.name)
            if parent is not None:
                parent_bone = bones.get(parent)
                if parent_bone is not None:
                    bone.parent = parent_bone


def correct_bone_rotations(obj):
    name = obj.name
    if "Eye" in name:
        bone_head = Vector(obj.head)
        bone_head.z += 0.05
        obj.tail = bone_head
        obj.roll = 0

    elif "Hips" == name:
        bone_head = Vector(obj.head)
        bone_tail = Vector(obj.tail)

        if bone_head.z > bone_tail.z:
            obj.head = bone_tail
            obj.tail = bone_head
        else:
            print("Hips already correct")
    elif "RightHandThumb" in name:
        obj.roll = 70 * pi/180
    elif "LeftHandThumb" in name:
        obj.roll = -70 * pi/180
    else:
        axises = corrected_axis.keys()
        correction = None
        found = False

        for axis in axises:
            corrections = corrected_axis.get(axis)
            for correction in corrections:
                if correction in name:
                    print("Found correction", name, axis)
                    bpy.ops.object.mode_set(mode='EDIT')
                    bpy.ops.armature.select_all(action="DESELECT")
                    obj.select = True
                    bpy.ops.armature.calculate_roll(type=axis)
                    bpy.ops.armature.select_all(action="DESELECT")
                    found = True
                    break
            if found:
                break


def has_armature_as_child(me):
    for child in me.children:
        if child.type == "ARMATURE":
            return True
    return False


def translate_bones(Translator, bones):
    for idx, bone in enumerate(bones):
        bone.hide = False
        bone.hide_select = False

        translated = Translator.translate(bone.name)
        bone.name = translated


def delete_bones(edit_bones, bones_to_remove):
    for removal_bone in bones_to_remove:
        if removal_bone is not None:
            print(" Remove Bone:", removal_bone)
            edit_bones.remove(removal_bone)


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

        print("----------------------")
        print("Creating Base Armature")
        print("----------------------")
        # Reset mode to Object, just to be sure

        if bpy.context.active_object:
            bpy.ops.object.mode_set(mode='OBJECT')

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


def correct_scale_rotation(obj, rotation):
    current_context = bpy.context.area.type
    bpy.context.area.type = 'VIEW_3D'
    # set context to 3D View and set Cursor
    bpy.context.space_data.cursor_location[0] = 0.0
    bpy.context.space_data.cursor_location[1] = 0.0
    bpy.context.space_data.cursor_location[2] = 0.0
    bpy.context.area.type = current_context
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT')
    obj.select = True
    bpy.context.scene.objects.active = obj
    bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    obj.scale = Vector((100, 100, 100))
    str_angle = -90 * pi/180
    if rotation:
        obj.rotation_euler = Euler((str_angle, 0, 0), 'XYZ')
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    obj.scale = Vector((0.01, 0.01, 0.01))
    if rotation:
        obj.rotation_euler = Euler((-str_angle, 0, 0), 'XYZ')


def navigate_armature(data, current_rest_node, world_matrix, parent, parent_node):
    name = current_rest_node["name"]
    bone = data.get(name)
    if(bone):
        bone.rotation_mode = "QUATERNION"
        destination_matrix = current_rest_node["matrix_local"].copy()
        inv_destination_matrix = destination_matrix.inverted()
        matrix = bone.matrix
        if parent:
            parent_matrix = parent.matrix.copy()
            parent_inverted = parent_matrix.inverted()
            parent_destination = parent_node["matrix_local"].copy()
        else:
            parent_matrix = Matrix()
            parent_inverted = Matrix()
            parent_destination = Matrix()
        smat = inv_destination_matrix * \
            (parent_destination * (parent_inverted * matrix))
        bone.rotation_quaternion = smat.to_quaternion().inverted()
        for child in current_rest_node["children"]:
            navigate_armature(data, child, world_matrix,
                              bone, current_rest_node)
    else:
        bone = parent
        for child in current_rest_node["children"]:
            navigate_armature(data, child, world_matrix, bone, parent_node)


def retarget_armature(options, selected, selected_only=False):

    armature = find_armature(selected)
    print("selected", selected, "armature", armature)
    if armature is not None:
        # Center Children First
        print(bpy.context.mode, armature)
        if bpy.context.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')

        print("Deselect all")
        bpy.ops.object.select_all(action='DESELECT')
        print("Selected")

        bpy.context.scene.objects.active = armature
        armature.select = True
        # Make sure to reset the bones first.
        bpy.ops.object.transform_apply(
            location=False, rotation=True, scale=True)
        print("Selecting Bones")

        bpy.ops.object.mode_set(mode='POSE')
        bpy.ops.pose.select_all(action='SELECT')
        bpy.ops.pose.transforms_clear()
        bpy.ops.pose.select_all(action='DESELECT')

        print("---")

        # Now lets do the repose to rest
        world_matrix = armature.matrix_world
        bones = armature.pose.bones

        for bone in base_armature:
            print("Iterating Bones", bone["name"])
            navigate_armature(bones, bone, world_matrix, None, None)

        print("Moving Next")
        # Then apply everything
        if options['apply']:

            print("Applying Scale")
            if bpy.context.mode != 'OBJECT':
                bpy.ops.object.mode_set(mode='OBJECT')

            print("Correcting Scale and Rotations")
            correct_scale_rotation(armature, True)

            print(" Correcting child rotations and scale")
            for child in armature.children:
                if selected_only is False or child.select:
                    correct_scale_rotation(child, False)

            bpy.context.scene.objects.active = armature

        armature.select = True

        if bpy.context.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')

        print("Done")
    else:
        # Judas proofing:
        print("No Armature, select, throw an exception")
        raise Exception("You must have an armature to continue")
