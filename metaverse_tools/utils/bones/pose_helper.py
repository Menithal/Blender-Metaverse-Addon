
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

# Copyright 2020 Matti 'Menithal' Lahtinen
## Tools for managing pose related stuff

import bpy
import copy
from metaverse_tools.utils.bpyutil import list_has_item
from metaverse_tools.utils.bones.bones_builder import BoneMirrorableInfo, get_bone_side_and_mirrored


def purge_constraints(from_selected):
    for pose_bone in from_selected:
        constraints = pose_bone.constraints
        for constraint in constraints:
            constraints.remove(constraint)


def add_local_pose_constraint_bone(parent, to_selected_bones, follow, constraint_type, influence_by_distance = False):

    constraints_list = []
    for pose_bone in to_selected_bones:
        constraint = pose_bone.constraints.new(constraint_type)
        constraint.name = constraint_type + "_" + pose_bone.name + "_TO_" + follow.name
        constraint.target = parent
        constraint.subtarget = follow.name

        constraint.target_space = "LOCAL_WITH_PARENT"
        constraint.owner_space = "LOCAL_WITH_PARENT"
        constraints_list.append(constraint)

    if influence_by_distance:
        smallest = -1
        largest = -1
        # Get range
        target_ebone = parent.data.bones[follow.name]
        for bone in to_selected_bones:
            ebone = parent.data.bones[bone.name]
            
            distance = (target_ebone.tail - ebone.tail).length
            if smallest == -1 or smallest > distance:
                smallest = distance
            
            if largest == -1 or distance > largest:
                largest = distance

        # Got the smallest value, now use that for influence
        for ind,pose_bone in enumerate(to_selected_bones):
            ebone = parent.data.bones[pose_bone.name]
            
            # Get influence amount by reducing smallest amount from largest and the distance
            
            influence = 1 - (((target_ebone.tail - ebone.tail).length - smallest) / (largest))
            constraints = pose_bone.constraints
            
            constraints[ind].influence = influence


def mirror_location_or_rotation(source_constraint, target_constraints):
    if source_constraint.type == "COPY_LOCATION" or source_constraint.type == "COPY_ROTATION":
        new_constraint = target_constraints.new(source_constraint.type)
        new_constraint.target = source_constraint.target

        if source_constraint.target.type == "ARMATURE":
            constraint_bone_info = get_bone_side_and_mirrored(source_constraint.subtarget)

            # Is the name mirrorable?
            if constraint_bone_info is not None:
                new_constraint.subtarget = constraint_bone_info.mirror_name
            else:
                new_constraint.subtarget = source_constraint.subtarget

        new_constraint.target_space = source_constraint.target_space
        new_constraint.owner_space = source_constraint.owner_space
        new_constraint.use_x = source_constraint.use_x
        new_constraint.use_y = source_constraint.use_y
        new_constraint.use_z = source_constraint.use_z
        new_constraint.influence = source_constraint.influence
        new_constraint.name = source_constraint.name

        return new_constraint
    
    return None

def copy_limit_constraints(active_pose_bone, pose_bones):
    source_constraints = [ e for e in active_pose_bone.constraints]
    for pose_bone in pose_bones:
        if active_pose_bone != pose_bone:
            target_constraints = pose_bone.constraints
            for constraint in source_constraints:
                if constraint.type == "LIMIT_LOCATION" or constraint.type == "LIMIT_ROTATION":
                    copy_limit_constraint(constraint, target_constraints)

        

def copy_limit_constraint(source_constraint, target_constraints):
    new_constraint = target_constraints.new(source_constraint.type)
    
    if source_constraint.type == "LIMIT_LOCATION":
        new_constraint.use_min_x = source_constraint.use_min_x
        new_constraint.use_max_x = source_constraint.use_max_x

        new_constraint.use_min_y = source_constraint.use_min_y
        new_constraint.use_max_y = source_constraint.use_max_y

        new_constraint.use_min_z = source_constraint.use_min_z
        new_constraint.use_max_z = source_constraint.use_max_z
        
  
    elif source_constraint.type == "LIMIT_ROTATION":
        new_constraint.use_limit_x = source_constraint.use_limit_x
        new_constraint.use_limit_y = source_constraint.use_limit_y
        new_constraint.use_limit_z = source_constraint.use_limit_z
  

    new_constraint.min_x = source_constraint.min_x
    new_constraint.max_x = source_constraint.max_x
    
    new_constraint.min_y = source_constraint.min_y
    new_constraint.max_y = source_constraint.max_y
        
    new_constraint.min_z = source_constraint.min_z
    new_constraint.max_z = source_constraint.max_z

    new_constraint.use_transform_limit = source_constraint.use_transform_limit
    new_constraint.owner_space = source_constraint.owner_space

    return new_constraint



# Later expand to other axis too.
def mirror_limits(source_constraint, target_constraints, axis='X'):
    
    new_constraint = copy_limit_constraint(source_constraint, target_constraints)
    
    if source_constraint.type == "LIMIT_LOCATION":
        new_constraint.min_x = -source_constraint.max_x
        new_constraint.max_x = -source_constraint.min_x

    elif source_constraint.type == "LIMIT_ROTATION":
        new_constraint.min_y = -source_constraint.max_y
        new_constraint.max_y = -source_constraint.min_y

    return new_constraint


# TODO> Check for duplicates before adding new.
def mirror_pose_constraints(parent, selected_pose_bones):
    for pose_bone in selected_pose_bones:
        bone_info = get_bone_side_and_mirrored(pose_bone.name)

        if bone_info is not None:
            target = bone_info.mirror_name
        else:
            target = pose_bone.name
            
        target_constraints = parent.pose.bones[target].constraints
        
        # make sure not to impact what is being changed.

        copied_list = [ e for e in pose_bone.constraints]

        for constraint in copied_list:
            
            if constraint.type == "COPY_LOCATION" or constraint.type == "COPY_ROTATION":
                new_constraint = mirror_location_or_rotation(constraint, target_constraints)
                new_constraint.name = new_constraint.name.replace("Left","tefLx").replace("Right","Left").replace("tefLx", "Left")

            elif constraint.type == "LIMIT_ROTATION" or constraint.type == "LIMIT_LOCATION":
                new_constraint = mirror_limits(constraint, target_constraints)
                new_constraint.name = new_constraint.name.replace("Left","tefLx").replace("Right","Left").replace("tefLx", "Left")
                #boop
            else:
                print(constraint.type + "  is unsupported for X-mirroring")


def normalize_influence_for(constraints, of_type, amount=1.0):
    total_value = 0
    filtered_constraints = []
    for constraint in constraints:
        if constraint.type == of_type:
            print("Found")
            total_value += constraint.influence
            filtered_constraints.append(constraint)
    
    if len(filtered_constraints) <= 1:
        print("Not sufficient constraints to normalize")
        return False

    for constraint in filtered_constraints:
        constraint.influence = ((constraint.influence) / total_value) * amount


def remove_duplicate_constraints(constraints):
    constraints_list = []
    duplicates = []

    targetable_constraints = ["COPY_LOCATION", "COPY_ROTATION", "COPY_SCALE", "COPY_TRANSFORMS"]
    #constraint_types = get_constraint_types(constraints)
    for constraint in constraints:
        name = constraint.type
        if list_has_item(targetable_constraints, constraint.type):
            if constraint.target is not None:
                if constraint.target.type == "ARMATURE" and constraint.subtarget is not None:
                    name += "-" + constraint.target.name + "-" + constraint.subtarget.name
                elif constraint.target.type == "ARMATURE":
                    name += "-" + constraint.target.name
        
        if list_has_item(constraints_list, name):
            duplicates.append(constraint)
        else:
            constraints_list.append(name)
    
    for duplicate in duplicates:
        constraints.remove(duplicate)
        

def get_constraint_types(constraints):
    constraint_types = []
    for constraint in constraints:
        if not list_has_item(constraint_types, constraint.type):
            constraint_types.append(constraint.type)
    
    return constraint_types


def normalize_constraints_rotation(pose_bones, amount = 1.0):
    for pose_bone in pose_bones:
        types = get_constraint_types(pose_bone.constraints)
        for constraint_type in types:
            normalize_influence_for(pose_bone.constraints, constraint_type, amount)


def set_pose_bone_rotation_lock(pose_bones, mode):
    for pose_bone in pose_bones:
        pose_bone.lock_rotation_w = mode
        pose_bone.lock_rotation[0] = mode
        pose_bone.lock_rotation[1] = mode
        pose_bone.lock_rotation[2] = mode


def set_pose_bone_translations_lock(pose_bones, mode):
    for pose_bone in pose_bones:
        pose_bone.lock_location[0] = mode
        pose_bone.lock_location[1] = mode
        pose_bone.lock_location[2] = mode


def clone_locks(target, pose_bones):
    for pose_bone in pose_bones:
        pose_bone.lock_location[0] = target.lock_location[0]
        pose_bone.lock_location[1] = target.lock_location[1]
        pose_bone.lock_location[2] = target.lock_location[2]

        pose_bone.lock_rotation_w =  target.lock_rotation_w
        pose_bone.lock_rotation[0] = target.lock_rotation[0]
        pose_bone.lock_rotation[1] = target.lock_rotation[1]
        pose_bone.lock_rotation[2] = target.lock_rotation[2]



def copy_custom_shape(active_pose_bone, pose_bones):
    for pose_bone in pose_bones:
        pose_bone.custom_shape = active_pose_bone.custom_shape
        
        bpy.context.object.data.bones[pose_bone.name].show_wire = bpy.context.object.data.bones[active_pose_bone.name].show_wire

        pose_bone.use_custom_shape_bone_size = active_pose_bone.use_custom_shape_bone_size
        pose_bone.custom_shape_scale = active_pose_bone.custom_shape_scale
        pose_bone.custom_shape_transform =  active_pose_bone.custom_shape_transform



def clear_custom_shape(pose_bones):
    for pose_bone in pose_bones:
        pose_bone.custom_shape = None
        pose_bone.use_custom_shape_bone_size = True
        pose_bone.custom_shape_scale = 1.0
        pose_bone.custom_shape_transform =  None

        bpy.context.object.data.bones[pose_bone.name].show_wire = False