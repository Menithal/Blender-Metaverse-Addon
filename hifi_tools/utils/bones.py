import bpy
import re
from math import pi
from mathutils import Vector


corrected_axis = {
    "GLOBAL_NEG_Z": ["Shoulder", "Arm", "Hand", "Thumb"],
    "GLOBAL_NEG_Y": ["Spine", "Head", "Hips", "Leg", "Foot", "Toe", "Eye"]
}

bone_parent_structure = {
    #Bone : Parent
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
