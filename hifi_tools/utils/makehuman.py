# -*- coding: utf-8 -*-

import csv
import bpy
import re
import os
from math import pi
import copy
from mathutils import Vector
from hifi_tools.utils import materials, mesh, bones

bones_to_correct = [
	"LeftToeBase",
	"RightToeBase"
]

bones_to_correct_rolls = [
	30,
	-30
]

bones_to_correct_position = [
    ("Hips",       "tail"),
    ("Spine",      "head"),
    ("Spine",      "tail"),
    ("Spine1",     "head"),
    ("Spine1",     "tail"),
    ("Spine2",     "head"),
    ("Spine2",     "tail"),
    ("RightUpLeg", "head"),
    ("RightUpLeg", "tail"),
    ("LeftUpLeg",  "head"),
    ("LeftUpLeg",  "tail"),
    ("RightLeg",   "head"),
    ("RightLeg",   "tail"),
    ("LeftLeg",    "head"),
    ("LeftLeg",    "tail"),
    ("LeftFoot",   "head"),
    ("RightFoot",  "head")
]

finger_correction = {

}


#####################################################
# Armature Fixes:


def correct_toe_rotations(obj):
    #if "Eye" in obj.name:
    #    print("   ", obj.name)
    #    bone_head = Vector(obj.head)
    #    bone_head.z += 0.12
    #    obj.tail = bone_head
    #    obj.roll = 0
    #elif "Hips" == obj.name:
    #    bone_head = Vector(obj.head)
    #    bone_tail = Vector(obj.tail)
    #    if bone_head.z > bone_tail.z:
    #        obj.head = bone_tail
    #        obj.tail = bone_head
    #    else:
    #        print("Hips already correct")
    #else:
    for idx, name in enumerate(bones_to_correct):
        if name in obj.name:
            print("   Updating Roll of", obj.name, "with",
                  bones_to_correct_rolls[idx], "current", obj.roll)
            obj.roll = bones_to_correct_rolls[idx] * (pi/180)

def correct_bone_positions(bones):

    hips = bones.get("Hips")
    root = Vector(hips.head)
	
    for dest_name, end in bones_to_correct_position:
        dest = bones.get(dest_name)
        dest_head = Vector(dest.head)
        dest_tail = Vector(dest.tail)
        print(end)
        if end == "head":
            print("Set head")
            dest_head.y = root.y
            dest.head = dest_head
        elif end == "tail":
            print("set tail")
            dest_tail.y = root.y
            dest.tail = dest_tail

def clean_up_bones(obj):
    _to_remove = []

    pose_bones = obj.pose.bones

    bpy.ops.object.mode_set(mode='EDIT')
    updated_context = bpy.data.objects[obj.name]
    edit_bones = updated_context.data.edit_bones

    bpy.ops.object.mode_set(mode='OBJECT')
    for bone in obj.data.bones:
        pose_bone = pose_bones.get(bone.name)

        # Oddly needed to get the edit bone reference
        bpy.ops.object.mode_set(mode='EDIT')
        edit_bone = edit_bones.get(bone.name)

        print(" Bone ", bone.name)

        if pose_bone is not None and edit_bone is not None:
            print(" + Setting Pose Mode for", pose_bone)
            
            print(" - Removing Constraints from", pose_bone.name)
            for constraint in pose_bone.constraints:
            	pose_bone.constraints.remove(constraint)
            
            print(" # Check Rotations")
            bones.correct_bone_rotations(edit_bone)
            correct_toe_rotations(edit_bone)

    bpy.ops.object.mode_set(mode='EDIT')
    correct_bone_positions(updated_context.data.edit_bones)
	
    bpy.ops.object.mode_set(mode='OBJECT')

    return _to_remove


def convert_bones(obj):
    bones = obj.data.bones

    print("Cleaning Up Bones")
    clean_up_bones(obj)




def has_armature_as_child(me):
    for child in me.children:
        if child.type == "ARMATURE":
            return True
    return False


#####################################################
# Mesh Fixes:


# --------------------

def convert_makehuman_avatar_hifi():
    # Should Probably have a confirmation dialog when using this.
    original_type = bpy.context.area.type
    bpy.context.area.type = 'VIEW_3D'

    # Change mode to object mode

    marked_for_purge = []
    marked_for_deletion = []

    bpy.ops.object.mode_set(mode='OBJECT')
    for scene in bpy.data.scenes:
        for obj in scene.objects:
            bpy.ops.object.select_all(action='DESELECT')
            if obj is not None:
                obj.select = True
                bpy.context.scene.objects.active = obj

                # Delete joints and rigid bodies items. Perhaps later convert this to flow.
                print("Reading", obj.name)
                if obj.name == "joints" or obj.name == "rigidbodies":
                    marked_for_purge.append(obj)

                elif obj.type == "EMPTY" and obj.parent is None:
                    marked_for_deletion.append(obj)

                elif obj.type == 'ARMATURE':
                    convert_bones(obj)

                elif obj.type == 'MESH' and obj.parent is not None and obj.parent.type == 'ARMATURE':
                    bpy.ops.object.mode_set(mode='OBJECT')
                    print(" Cleaning up Materials now. May take a while ")
                    materials.clean_materials(obj.material_slots)
                    for material_slot in obj.material_slots:
                        material_slot.material.specular_intensity = 0
                        material_slot.material.specular_hardness = 1


    bpy.ops.object.select_all(action='DESELECT')
    for deletion in marked_for_deletion:
        deletion.select = True
        bpy.context.scene.objects.active = deletion
        bpy.ops.object.delete()

    bpy.context.area.type = original_type