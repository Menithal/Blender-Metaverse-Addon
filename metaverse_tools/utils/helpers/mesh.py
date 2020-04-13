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
# Copyright 2019 Matti 'Menithal' Lahtinen
import bpy
import copy


def get_mesh_from(selected):
    meshes = []

    for select in selected:
        if select.type == "MESH":
            meshes.append(select)

    return meshes


def mix_weights(a, b):
    print("  Mixing", a, b)
    bpy.ops.object.modifier_add(type='VERTEX_WEIGHT_MIX')

    bpy.context.object.modifiers["VertexWeightMix"].vertex_group_a = a
    bpy.context.object.modifiers["VertexWeightMix"].vertex_group_b = b
    bpy.context.object.modifiers["VertexWeightMix"].mix_mode = 'ADD'
    bpy.context.object.modifiers["VertexWeightMix"].mix_set = 'OR'

    bpy.ops.object.modifier_move_up(modifier="VertexWeightMix")
    bpy.ops.object.modifier_move_up(modifier="VertexWeightMix")
    bpy.ops.object.modifier_move_up(modifier="VertexWeightMix")
    bpy.ops.object.modifier_move_up(modifier="VertexWeightMix")

    bpy.ops.object.modifier_apply(apply_as='DATA', modifier="VertexWeightMix")


def clean_unused_vertex_groups(obj):
    # This part is generic:
    bpy.ops.object.mode_set(mode='OBJECT')
    vertex_groups = copy.copy(obj.vertex_groups.values())

    empty_vertex = []

    for vertex in obj.data.vertices:
        if len(vertex.groups) < 0:
            empty_vertex.append(vertex)

        index = vertex.index

        has_use = []
        for group in vertex_groups:
            try:
                obj.vertex_groups[group.name].weight(index)
                if group not in has_use:
                    has_use.append(group)
            except RuntimeError:
                pass

        for used in has_use:
            vertex_groups.remove(used)

    print(" Removing Unused Bones")

    parent = obj.parent
    _to_remove_bones = []
    if parent is not None and parent.type == "ARMATURE":

        obj.select_set(state=False)

        bpy.context.view_layer.objects.active = parent
        parent.select_set(state=True)
        mapped = [(x.name) for x in vertex_groups]

        bpy.ops.object.mode_set(mode='EDIT')
        print(" Iterating edit bones", len(parent.data.edit_bones))
        for edit_bone in parent.data.edit_bones:
            if edit_bone.name in mapped and edit_bone.name != "HeadTop":
                print("  - Removing Unused Bone", edit_bone.name)
                _to_remove_bones.append(edit_bone)

        for bone_to_remove in _to_remove_bones:
            parent.data.edit_bones.remove(bone_to_remove)

    print(" Found ", len(vertex_groups),
          " without weights, cleaning up", obj.parent)
    for group in vertex_groups:
        print("  - Removing Vertex Groups ", group)
        obj.vertex_groups.remove(group)

    bpy.ops.object.mode_set(mode='OBJECT')
    print(" Found", len(empty_vertex), " Unused Vertices")

    bpy.context.view_layer.objects.active = obj


def get_shape_keys(mesh):
    if mesh.type != "MESH":
        raise "Object was not a mesh"

    return mesh.data.shape_keys.key_blocks


def generate_empty_shapekeys(obj, target_shapekey_list):
    print("generate_empty_shapekeys", obj)
    shape_keys = get_shape_keys(obj)
    for key in target_shapekey_list:
        print(key, shape_keys.find(key))
        if shape_keys.find(key) is -1:
            bpy.ops.object.shape_key_clear()
            obj.shape_key_add(name=key)

def boolean_union_objects(active, meshes):
        # Now if above is a mesh type to do join / boolean operations on
        for mesh in meshes:
            if mesh is not active:
                # Material Combinator to pre-combine materials prior to applying boolean operator or joining objects together
                # This allows the materials to be maintained even if they are joined.
                # for each material the child's blender objects have
                for material in mesh.data.materials.values():
                    # and if the material is set, and is not yet set for the parent, add an instance of the material to the parent
                    if material is not None and material not in bpy.context.object.data.materials.values():
                        bpy.context.object.data.materials.append(material)
                # If the scene wants to use boolean operators, this overrides join children (as it is a method to join children)
            
                bpy.ops.object.modifier_add(type='BOOLEAN')
                # Set name for modifier to keep track of it.
                name = mesh.name + '-Boolean'
                bpy.context.object.modifiers["Boolean"].name = name
                bpy.context.object.modifiers[name].operation = 'UNION'
                bpy.context.object.modifiers[name].object = mesh
                bpy.ops.object.modifier_apply(
                    apply_as='DATA', modifier=name)
                # Clean up the child object from the blender scene.
                bpy.data.objects.remove(mesh)
                # TODO: Set Child.blender_object as the blender object of the parent to maintain links



def sort_shapekeys(obj, target_shapekey_list):
    print("sort_shapekeys", obj)
    shape_keys = get_shape_keys(obj)
    print(shape_keys)
    name_list = [sk.name for sk in shape_keys]
    moved = 0

    for key in reversed(target_shapekey_list):
        try:
            
            index = name_list.index(key)
            bpy.context.object.active_shape_key_index = index + moved
            bpy.ops.object.shape_key_move(type='TOP')
            moved += 1
            # Simple upkeep for indexes from changing. They are ALWAYS added to top first, so technically "gone"
            name_list.pop(index)
        except Exception as e:
            print("Could not find shapekey ", key, " Skipping: Full: ", e)
