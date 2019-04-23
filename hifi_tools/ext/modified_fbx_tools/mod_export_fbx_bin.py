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

# <pep8 compliant>

# Overides parts of io_scene_fbx
# Original copyright (C) Campbell Barton, Bastien Montagne

# HifiShaderWrapper / Stingray Modifications by Matti 'Anthony' Lahtinen

import array
import math
import os
import time

from hifi_tools.utils.materials import HifiShaderWrapper, get_hifi_shader_node
from itertools import chain

import bpy
import bpy_extras
from bpy_extras import node_shader_utils

from mathutils import Vector, Matrix


import io_scene_fbx
from io_scene_fbx import encode_bin, data_types, fbx_utils
from io_scene_fbx.fbx_utils import (
    # Constants.
    FBX_VERSION, 
    FBX_MATERIAL_VERSION, FBX_TEXTURE_VERSION,
    BLENDER_OTHER_OBJECT_TYPES, BLENDER_OBJECT_TYPES_MESHLIKE,
    # Miscellaneous utils.
    PerfMon,
    units_blender_to_fbx_factor,
    similar_values, similar_values_iter,
    # Mesh transform helpers.
    vcos_transformed_gen,
    # UUID from key.
    get_fbx_uuid_from_key,
    # Key generators.
    get_blenderID_key, 
    get_blender_mesh_shape_key, get_blender_mesh_shape_channel_key,
    get_blender_empty_key,
    get_blender_nodetexture_key,
    # FBX element data.
    elem_empty,
    elem_data_single_int32, elem_data_single_int64,
    elem_data_single_string, elem_data_single_string_unicode,
    # FBX element properties.
    elem_properties,
    # FBX element properties handling templates.
    elem_props_template_init, elem_props_template_set, elem_props_template_finalize,
    # Templates.
    FBXTemplate,
    # Objects.
    ObjectWrapper, fbx_name_class,
    # Top level.
    FBXExportSettingsMedia, FBXExportSettings, FBXExportData,
)

from io_scene_fbx.export_fbx_bin import (
    fbx_template_def_globalsettings,
    fbx_template_def_model,
    fbx_template_def_null,
    fbx_template_def_light,
    fbx_template_def_camera,
    fbx_template_def_bone,
    fbx_template_def_geometry,
    fbx_template_def_material,
    fbx_template_def_texture_file,
    fbx_template_def_video,
    fbx_template_def_pose,
    fbx_template_def_deformer,
    fbx_template_def_animstack,
    fbx_template_def_animlayer,
    fbx_template_def_animcurvenode,
    fbx_template_def_animcurve,
    fbx_data_element_custom_properties,
    fbx_data_empty_elements,
    fbx_data_object_elements,
    fbx_data_light_elements,
    fbx_data_camera_elements,
    fbx_data_mesh_elements,
    _gen_vid_path,
    fbx_data_video_elements,
    fbx_data_armature_elements,
    fbx_data_leaf_bone_elements,
    fbx_data_animation_elements,
    PRINCIPLED_TEXTURE_SOCKETS_TO_FBX,
    fbx_skeleton_from_armature,
    fbx_generate_leaf_bones,
    fbx_animations,
    fbx_scene_data_cleanup,
    fbx_header_elements,
    fbx_documents_elements,
    fbx_references_elements,
    fbx_definitions_elements,
    fbx_connections_elements,
    fbx_takes_elements,
    )

# Save fbx_objects_elements, save_single, save



# Mapping Blender -> FBX (principled_socket_name, fbx_name).
EXTENDED_PRINCIPLED_TEXTURE_SOCKETS_TO_FBX = (
    # Hifi takes alpha from the diffuse!, so no need to attach
    ("color_map", b"tex_color_map"),
    ("metallic_map", b"tex_metallic_map"),
    ("normal_map", b"tex_normal_map"),
    ("roughness_map", b"tex_roughness_map"),
    ("emissive_map", b"tex_emissive_map"), 
)

def fbx_epbdsf_data_material_elements(root, ma, scene_data):
    """
    Write the Material data block.
    """

    ambient_color = (0.0, 0.0, 0.0)
    if scene_data.data_world:
        ambient_color = next(iter(scene_data.data_world.keys())).color

    ma_wrap = HifiShaderWrapper(ma, is_readonly=True)
    ma_key, _objs = scene_data.data_materials[ma]
    ma_type = b"Phong"

    fbx_ma = elem_data_single_int64(root, b"Material", get_fbx_uuid_from_key(ma_key))
    fbx_ma.add_string(fbx_name_class(ma.name.encode(), b"Material"))
    fbx_ma.add_string(b"")

    elem_data_single_int32(fbx_ma, b"Version", FBX_MATERIAL_VERSION)
    elem_data_single_string(fbx_ma, b"ShadingModel", ma_type)
    elem_data_single_int32(fbx_ma, b"MultiLayer", 0)

    tmpl = elem_props_template_init(scene_data.templates, b"Material")
    props = elem_properties(fbx_ma)
    
    # Absolutely not Standard, but Autodesk doesnt give a fuck apparently about what FBX Standard really is anymore.
    # Lets Cheat and shim some FBX Stingray features in until Hifi supports proper GLTF stuff.
    # This Avoids also any issues with the hifi reading some stuff proper
    # Basically Forcing thee FBX Serializer to actually just think this is an PBS material, not a "Blender one."  


    elem_props_template_set(tmpl, props, "p_string", b"ShadingModel", ma_type.decode())


    elem_props_template_set(tmpl, props, "p_color", b"DiffuseColor", ma_wrap.base_color)
    # Not in Principled BSDF, so assuming always 1
    elem_props_template_set(tmpl, props, "p_number", b"DiffuseFactor", 1.0)

    elem_props_template_set(tmpl, props, "p_color", b"EmissiveColor", ma_wrap.base_color)
    elem_props_template_set(tmpl, props, "p_number", b"EmissiveFactor", 1.0)
    
    
    # --------
    # https://github.com/highfidelity/hifi/blob/d88bee89e4204c5dd167e0e10ff8ba3d91a26696/libraries/fbx/src/FBXSerializer.cpp
    # -------- 
    ## Additionally there is tex_ao_map and ambientcolor / ambientfactor that neesd to investigate, someday. TODO: -matti
    elem_props_template_set(tmpl, props, "p_color", b"AmbientColor", ambient_color)
    elem_props_template_set(tmpl, props, "p_number", b"AmbientFactor", 0.0)

    #elem_props_template_set(tmpl, props, "p_color", b"TransparentColor", ma_wrap.base_color)
    #elem_props_template_set(tmpl, props, "p_number", b"TransparencyFactor", ma_wrap.transparency)
    #elem_props_template_set(tmpl, props, "p_number", b"Opacity", 1.0 - ma_wrap.transparency)

    elem_props_template_set(tmpl, props, "p_vector_3d", b"NormalMap", (0.0, 0.0, 0.0))
    
    if ma_wrap.normal_map is not None:
        elem_props_template_set(tmpl, props, "p_bool", b"Maya|use_normal_map", True)
   
    # TODO: Perhaps Additional someday ? -matti
    elem_props_template_set(tmpl, props, "p_color", b"SpecularColor",(1.0, 1.0, 1.0))
    elem_props_template_set(tmpl, props, "p_number", b"SpecularFactor", 0.0)
    # elem_props_template_set(tmpl, props, "p_number", b"SpecularFactor", ma_wrap.specular / 2.0)

    elem_props_template_set(tmpl, props, "p_color", b"DiffuseColor", ma_wrap.base_color)
    elem_props_template_set(tmpl, props, "p_color", b"Maya|base_color", ma_wrap.base_color)
    
    if ma_wrap.color_map is not None:
        elem_props_template_set(tmpl, props, "p_bool", b"Maya|use_color_map", True)

    elem_props_template_set(tmpl, props, "p_number", b"Roughness", ma_wrap.roughness)
    elem_props_template_set(tmpl, props, "p_number", b"Maya|roughness", ma_wrap.roughness)
    shininess = (1.0 - ma_wrap.roughness) * 10
    shininess *= shininess
    elem_props_template_set(tmpl, props, "p_number", b"Shininess", shininess)
    elem_props_template_set(tmpl, props, "p_number", b"ShininessExponent", shininess)

    if ma_wrap.roughness_map is not None:
        elem_props_template_set(tmpl, props, "p_bool", b"Maya|use_roughness_map", True)

    elem_props_template_set(tmpl, props, "p_number", b"Metallic", ma_wrap.metallic)
    elem_props_template_set(tmpl, props, "p_number", b"Maya|metallic", ma_wrap.metallic)
    
    if ma_wrap.metallic_map is not None:
        elem_props_template_set(tmpl, props, "p_bool", b"Maya|use_metallic_map", True)

    elem_props_template_set(tmpl, props, "p_color", b"Emissive", ma_wrap.emissive)
    elem_props_template_set(tmpl, props, "p_color", b"Maya|emissive", ma_wrap.emissive)
    elem_props_template_set(tmpl, props, "p_number", b"Maya|emissive_intensity", 1.0) #TODO: - matti Not apparently used by Hifi atm
    
    if ma_wrap.emissive_map is not None:
        elem_props_template_set(tmpl, props, "p_bool", b"Maya|use_emissive_map", True)
        
    elem_props_template_finalize(tmpl, props)


    # Custom properties.
    if scene_data.settings.use_custom_props:
        fbx_data_element_custom_properties(props, ma)


def fbx_epbdsf_data_texture_file_elements(root, blender_tex_key, scene_data):
    """
    Write the (file) Texture data block.
    """
    # XXX All this is very fuzzy to me currently...
    #     Textures do not seem to use properties as much as they could.
    #     For now assuming most logical and simple stuff.

    ma, sock_name = blender_tex_key
    
    ma_wrap = HifiShaderWrapper(ma, is_readonly=True)
    tex_key, _fbx_prop = scene_data.data_textures[blender_tex_key]

    tex = getattr(ma_wrap, sock_name)
    img = tex.image
    fname_abs, fname_rel = _gen_vid_path(img, scene_data)

    fbx_tex = elem_data_single_int64(root, b"Texture", get_fbx_uuid_from_key(tex_key))
    fbx_tex.add_string(fbx_name_class(sock_name.encode(), b"Texture"))
    fbx_tex.add_string(b"")

    elem_data_single_string(fbx_tex, b"Type", b"TextureVideoClip")
    elem_data_single_int32(fbx_tex, b"Version", FBX_TEXTURE_VERSION)
    elem_data_single_string(fbx_tex, b"TextureName", fbx_name_class(sock_name.encode(), b"Texture"))
    elem_data_single_string(fbx_tex, b"Media", fbx_name_class(img.name.encode(), b"Video"))
    elem_data_single_string_unicode(fbx_tex, b"FileName", fname_abs)
    elem_data_single_string_unicode(fbx_tex, b"RelativeFilename", fname_rel)

    alpha_source = 0  # None
    if img.use_alpha:
        # ~ if tex.texture.use_calculate_alpha:
            # ~ alpha_source = 1  # RGBIntensity as alpha.
        # ~ else:
            # ~ alpha_source = 2  # Black, i.e. alpha channel.
        alpha_source = 2  # Black, i.e. alpha channel.
    # BlendMode not useful for now, only affects layered textures afaics.
    mapping = 0  # UV.
    uvset = None
    if tex.texcoords == 'ORCO':  # XXX Others?
        if tex.projection == 'FLAT':
            mapping = 1  # Planar
        elif tex.projection == 'CUBE':
            mapping = 4  # Box
        elif tex.projection == 'TUBE':
            mapping = 3  # Cylindrical
        elif tex.projection == 'SPHERE':
            mapping = 2  # Spherical
    elif tex.texcoords == 'UV':
        mapping = 0  # UV
        # Yuck, UVs are linked by mere names it seems... :/
        # XXX TODO how to get that now???
        # uvset = tex.uv_layer
    wrap_mode = 1  # Clamp
    if tex.extension == 'REPEAT':
        wrap_mode = 0  # Repeat

    tmpl = elem_props_template_init(scene_data.templates, b"TextureFile")
    props = elem_properties(fbx_tex)
    elem_props_template_set(tmpl, props, "p_enum", b"AlphaSource", alpha_source)
    elem_props_template_set(tmpl, props, "p_bool", b"PremultiplyAlpha",
                            img.alpha_mode in {'STRAIGHT'})  # Or is it PREMUL?
    elem_props_template_set(tmpl, props, "p_enum", b"CurrentMappingType", mapping)
    if uvset is not None:
        elem_props_template_set(tmpl, props, "p_string", b"UVSet", uvset)
    elem_props_template_set(tmpl, props, "p_enum", b"WrapModeU", wrap_mode)
    elem_props_template_set(tmpl, props, "p_enum", b"WrapModeV", wrap_mode)
    elem_props_template_set(tmpl, props, "p_vector_3d", b"Translation", tex.translation)
    elem_props_template_set(tmpl, props, "p_vector_3d", b"Rotation", (-r for r in tex.rotation))
    elem_props_template_set(tmpl, props, "p_vector_3d", b"Scaling", (((1.0 / s) if s != 0.0 else 1.0) for s in tex.scale))
    # UseMaterial should always be ON imho.
    elem_props_template_set(tmpl, props, "p_bool", b"UseMaterial", True)
    elem_props_template_set(tmpl, props, "p_bool", b"UseMipMap", False)
    elem_props_template_finalize(tmpl, props)

    # No custom properties, since that's not a data-block anymore.

# Contains PrincipledBSDFWrapper
def fbx_data_material_elements(root, ma, scene_data):
    """
    Write the Material data block.
    """
    epbdsf_node = get_hifi_shader_node(ma)
    if epbdsf_node is not None:
        fbx_epbdsf_data_material_elements(root, ma, scene_data)
    else:
        io_scene_fbx.export_fbx_bin.fbx_data_material_elements(root, ma, scene_data)
        

# Contains PrincipledBSDFWrapper
def fbx_data_texture_file_elements(root, blender_tex_key, scene_data):
    """
    Write the (file) Texture data block.
    """
    ma, sock_name = blender_tex_key
    
    epbdsf_node = get_hifi_shader_node(ma)
    if epbdsf_node is not None:
        fbx_epbdsf_data_texture_file_elements(root, blender_tex_key, scene_data)
    else:
        io_scene_fbx.export_fbx_bin.fbx_data_texture_file_elements(root, (ma, sock_name), scene_data)


# Contains PrincipledBSDFWrapper
def fbx_data_from_scene(scene, depsgraph, settings):
    """
    Do some pre-processing over scene's data...
    """
    objtypes = settings.object_types
    dp_objtypes = objtypes - {'ARMATURE'}  # Armatures are not supported as dupli instances currently...
    perfmon = PerfMon()
    perfmon.level_up()

    # ##### Gathering data...

    perfmon.step("FBX export prepare: Wrapping Objects...")

    # This is rather simple for now, maybe we could end generating templates with most-used values
    # instead of default ones?
    objects = {}  # Because we do not have any ordered set...
    for ob in settings.context_objects:
        if ob.type not in objtypes:
            continue
        ob_obj = ObjectWrapper(ob)
        objects[ob_obj] = None
        # Duplis...
        for dp_obj in ob_obj.dupli_list_gen(depsgraph):
            if dp_obj.type not in dp_objtypes:
                continue
            objects[dp_obj] = None

    perfmon.step("FBX export prepare: Wrapping Data (lamps, cameras, empties)...")

    data_lights = {ob_obj.bdata.data: get_blenderID_key(ob_obj.bdata.data)
                   for ob_obj in objects if ob_obj.type == 'LIGHT'}
    # Unfortunately, FBX camera data contains object-level data (like position, orientation, etc.)...
    data_cameras = {ob_obj: get_blenderID_key(ob_obj.bdata.data)
                    for ob_obj in objects if ob_obj.type == 'CAMERA'}
    # Yep! Contains nothing, but needed!
    data_empties = {ob_obj: get_blender_empty_key(ob_obj.bdata)
                    for ob_obj in objects if ob_obj.type == 'EMPTY'}

    perfmon.step("FBX export prepare: Wrapping Meshes...")

    data_meshes = {}
    for ob_obj in objects:
        if ob_obj.type not in BLENDER_OBJECT_TYPES_MESHLIKE:
            continue
        ob = ob_obj.bdata
        use_org_data = True
        org_ob_obj = None

        # Do not want to systematically recreate a new mesh for dupliobject instances, kind of break purpose of those.
        if ob_obj.is_dupli:
            org_ob_obj = ObjectWrapper(ob)  # We get the "real" object wrapper from that dupli instance.
            if org_ob_obj in data_meshes:
                data_meshes[ob_obj] = data_meshes[org_ob_obj]
                continue

        is_ob_material = any(ms.link == 'OBJECT' for ms in ob.material_slots)

        if settings.use_mesh_modifiers or ob.type in BLENDER_OTHER_OBJECT_TYPES or is_ob_material:
            # We cannot use default mesh in that case, or material would not be the right ones...
            use_org_data = not (is_ob_material or ob.type in BLENDER_OTHER_OBJECT_TYPES)
            tmp_mods = []
            if use_org_data and ob.type == 'MESH':
                # No need to create a new mesh in this case, if no modifier is active!
                for mod in ob.modifiers:
                    # For meshes, when armature export is enabled, disable Armature modifiers here!
                    # XXX Temp hacks here since currently we only have access to a viewport depsgraph...
                    if mod.type == 'ARMATURE' and 'ARMATURE' in settings.object_types:
                        tmp_mods.append((mod, mod.show_render, mod.show_viewport))
                        mod.show_render = False
                        mod.show_viewport = False
                    if mod.show_render or mod.show_viewport:
                        use_org_data = False
            if not use_org_data:
                tmp_me = ob.to_mesh(
                    depsgraph,
                    apply_modifiers=settings.use_mesh_modifiers)
                data_meshes[ob_obj] = (get_blenderID_key(tmp_me), tmp_me, True)
            # Re-enable temporary disabled modifiers.
            for mod, show_render, show_viewport in tmp_mods:
                mod.show_render = show_render
                mod.show_viewport = show_viewport
        if use_org_data:
            data_meshes[ob_obj] = (get_blenderID_key(ob.data), ob.data, False)

        # In case "real" source object of that dupli did not yet still existed in data_meshes, create it now!
        if org_ob_obj is not None:
            data_meshes[org_ob_obj] = data_meshes[ob_obj]

    perfmon.step("FBX export prepare: Wrapping ShapeKeys...")

    # ShapeKeys.
    data_deformers_shape = {}
    geom_mat_co = settings.global_matrix if settings.bake_space_transform else None
    for me_key, me, _free in data_meshes.values():
        if not (me.shape_keys and len(me.shape_keys.key_blocks) > 1):  # We do not want basis-only relative skeys...
            continue
        if me in data_deformers_shape:
            continue

        shapes_key = get_blender_mesh_shape_key(me)
        # We gather all vcos first, since some skeys may be based on others...
        _cos = array.array(data_types.ARRAY_FLOAT64, (0.0,)) * len(me.vertices) * 3
        me.vertices.foreach_get("co", _cos)
        v_cos = tuple(vcos_transformed_gen(_cos, geom_mat_co))
        sk_cos = {}
        for shape in me.shape_keys.key_blocks[1:]:
            shape.data.foreach_get("co", _cos)
            sk_cos[shape] = tuple(vcos_transformed_gen(_cos, geom_mat_co))
        sk_base = me.shape_keys.key_blocks[0]

        for shape in me.shape_keys.key_blocks[1:]:
            # Only write vertices really different from org coordinates!
            # XXX FBX does not like empty shapes (makes Unity crash e.g.), so we have to do this here... :/
            shape_verts_co = []
            shape_verts_idx = []

            sv_cos = sk_cos[shape]
            ref_cos = v_cos if shape.relative_key == sk_base else sk_cos[shape.relative_key]
            for idx, (sv_co, ref_co) in enumerate(zip(sv_cos, ref_cos)):
                if similar_values_iter(sv_co, ref_co):
                    # Note: Maybe this is a bit too simplistic, should we use real shape base here? Though FBX does not
                    #       have this at all... Anyway, this should cover most common cases imho.
                    continue
                shape_verts_co.extend(Vector(sv_co) - Vector(ref_co))
                shape_verts_idx.append(idx)
            if not shape_verts_co:
                continue
            channel_key, geom_key = get_blender_mesh_shape_channel_key(me, shape)
            data = (channel_key, geom_key, shape_verts_co, shape_verts_idx)
            data_deformers_shape.setdefault(me, (me_key, shapes_key, {}))[2][shape] = data

    perfmon.step("FBX export prepare: Wrapping Armatures...")

    # Armatures!
    data_deformers_skin = {}
    data_bones = {}
    arm_parents = set()
    for ob_obj in tuple(objects):
        if not (ob_obj.is_object and ob_obj.type in {'ARMATURE'}):
            continue
        fbx_skeleton_from_armature(scene, settings, ob_obj, objects, data_meshes,
                                   data_bones, data_deformers_skin, data_empties, arm_parents)

    # Generate leaf bones
    data_leaf_bones = []
    if settings.add_leaf_bones:
        data_leaf_bones = fbx_generate_leaf_bones(settings, data_bones)

    perfmon.step("FBX export prepare: Wrapping World...")

    # Some world settings are embedded in FBX materials...
    if scene.world:
        data_world = {scene.world: get_blenderID_key(scene.world)}
    else:
        data_world = {}

    perfmon.step("FBX export prepare: Wrapping Materials...")

    # TODO: Check all the material stuff works even when they are linked to Objects
    #       (we can then have the same mesh used with different materials...).
    #       *Should* work, as FBX always links its materials to Models (i.e. objects).
    #       XXX However, material indices would probably break...
    data_materials = {}
    for ob_obj in objects:
        # If obj is not a valid object for materials, wrapper will just return an empty tuple...
        for ma_s in ob_obj.material_slots:
            ma = ma_s.material
            if ma is None:
                continue  # Empty slots!
            # Note theoretically, FBX supports any kind of materials, even GLSL shaders etc.
            # However, I doubt anything else than Lambert/Phong is really portable!
            # Note we want to keep a 'dummy' empty material even when we can't really support it, see T41396.
            ma_data = data_materials.setdefault(ma, (get_blenderID_key(ma), []))
            ma_data[1].append(ob_obj)

    perfmon.step("FBX export prepare: Wrapping Textures...")

    # Note FBX textures also hold their mapping info.
    # TODO: Support layers?
    data_textures = {}
    # FbxVideo also used to store static images...
    data_videos = {}
    # For now, do not use world textures, don't think they can be linked to anything FBX wise...
    for ma in data_materials.keys():
        has_extended_pricipled = get_hifi_shader_node(ma)
        ma_wrap = None
        sockets = None
        if has_extended_pricipled is not None:
            print("Do Stuff")
            ma_wrap = HifiShaderWrapper(ma, is_readonly=True)
            sockets = EXTENDED_PRINCIPLED_TEXTURE_SOCKETS_TO_FBX
        else:
            # Note: with nodal shaders, we'll could be generating much more textures, but that's kind of unavoidable,
            #       given that textures actually do not exist anymore in material context in Blender...
            ma_wrap = node_shader_utils.PrincipledBSDFWrapper(ma, is_readonly=True)
            sockets = PRINCIPLED_TEXTURE_SOCKETS_TO_FBX

        for sock_name, fbx_name in sockets:
            tex = getattr(ma_wrap, sock_name)
            if tex is None or tex.image is None:
                continue
            blender_tex_key = (ma, sock_name)
            data_textures[blender_tex_key] = (get_blender_nodetexture_key(*blender_tex_key), fbx_name)

            img = tex.image
            vid_data = data_videos.setdefault(img, (get_blenderID_key(img), []))
            vid_data[1].append(blender_tex_key)

    perfmon.step("FBX export prepare: Wrapping Animations...")

    # Animation...
    animations = ()
    animated = set()
    frame_start = scene.frame_start
    frame_end = scene.frame_end
    if settings.bake_anim:
        # From objects & bones only for a start.
        # Kind of hack, we need a temp scene_data for object's space handling to bake animations...
        tmp_scdata = FBXExportData(
            None, None, None,
            settings, scene, depsgraph, objects, None, None, 0.0, 0.0,
            data_empties, data_lights, data_cameras, data_meshes, None,
            data_bones, data_leaf_bones, data_deformers_skin, data_deformers_shape,
            data_world, data_materials, data_textures, data_videos,
        )
        animations, animated, frame_start, frame_end = fbx_animations(tmp_scdata)

    # ##### Creation of templates...

    perfmon.step("FBX export prepare: Generating templates...")

    templates = {}
    templates[b"GlobalSettings"] = fbx_template_def_globalsettings(scene, settings, nbr_users=1)

    if data_empties:
        templates[b"Null"] = fbx_template_def_null(scene, settings, nbr_users=len(data_empties))

    if data_lights:
        templates[b"Light"] = fbx_template_def_light(scene, settings, nbr_users=len(data_lights))

    if data_cameras:
        templates[b"Camera"] = fbx_template_def_camera(scene, settings, nbr_users=len(data_cameras))

    if data_bones:
        templates[b"Bone"] = fbx_template_def_bone(scene, settings, nbr_users=len(data_bones))

    if data_meshes:
        nbr = len({me_key for me_key, _me, _free in data_meshes.values()})
        if data_deformers_shape:
            nbr += sum(len(shapes[2]) for shapes in data_deformers_shape.values())
        templates[b"Geometry"] = fbx_template_def_geometry(scene, settings, nbr_users=nbr)

    if objects:
        templates[b"Model"] = fbx_template_def_model(scene, settings, nbr_users=len(objects))

    if arm_parents:
        # Number of Pose|BindPose elements should be the same as number of meshes-parented-to-armatures
        templates[b"BindPose"] = fbx_template_def_pose(scene, settings, nbr_users=len(arm_parents))

    if data_deformers_skin or data_deformers_shape:
        nbr = 0
        if data_deformers_skin:
            nbr += len(data_deformers_skin)
            nbr += sum(len(clusters) for def_me in data_deformers_skin.values() for a, b, clusters in def_me.values())
        if data_deformers_shape:
            nbr += len(data_deformers_shape)
            nbr += sum(len(shapes[2]) for shapes in data_deformers_shape.values())
        assert(nbr != 0)
        templates[b"Deformers"] = fbx_template_def_deformer(scene, settings, nbr_users=nbr)

    # No world support in FBX...
    """
    if data_world:
        templates[b"World"] = fbx_template_def_world(scene, settings, nbr_users=len(data_world))
    """

    if data_materials:
        templates[b"Material"] = fbx_template_def_material(scene, settings, nbr_users=len(data_materials))

    if data_textures:
        templates[b"TextureFile"] = fbx_template_def_texture_file(scene, settings, nbr_users=len(data_textures))

    if data_videos:
        templates[b"Video"] = fbx_template_def_video(scene, settings, nbr_users=len(data_videos))

    if animations:
        nbr_astacks = len(animations)
        nbr_acnodes = 0
        nbr_acurves = 0
        for _astack_key, astack, _al, _n, _fs, _fe in animations:
            for _alayer_key, alayer in astack.values():
                for _acnode_key, acnode, _acnode_name in alayer.values():
                    nbr_acnodes += 1
                    for _acurve_key, _dval, acurve, acurve_valid in acnode.values():
                        if acurve:
                            nbr_acurves += 1

        templates[b"AnimationStack"] = fbx_template_def_animstack(scene, settings, nbr_users=nbr_astacks)
        # Would be nice to have one layer per animated object, but this seems tricky and not that well supported.
        # So for now, only one layer per anim stack.
        templates[b"AnimationLayer"] = fbx_template_def_animlayer(scene, settings, nbr_users=nbr_astacks)
        templates[b"AnimationCurveNode"] = fbx_template_def_animcurvenode(scene, settings, nbr_users=nbr_acnodes)
        templates[b"AnimationCurve"] = fbx_template_def_animcurve(scene, settings, nbr_users=nbr_acurves)

    templates_users = sum(tmpl.nbr_users for tmpl in templates.values())

    # ##### Creation of connections...

    perfmon.step("FBX export prepare: Generating Connections...")

    connections = []

    # Objects (with classical parenting).
    for ob_obj in objects:
        # Bones are handled later.
        if not ob_obj.is_bone:
            par_obj = ob_obj.parent
            # Meshes parented to armature are handled separately, yet we want the 'no parent' connection (0).
            if par_obj and ob_obj.has_valid_parent(objects) and (par_obj, ob_obj) not in arm_parents:
                connections.append((b"OO", ob_obj.fbx_uuid, par_obj.fbx_uuid, None))
            else:
                connections.append((b"OO", ob_obj.fbx_uuid, 0, None))

    # Armature & Bone chains.
    for bo_obj in data_bones.keys():
        par_obj = bo_obj.parent
        if par_obj not in objects:
            continue
        connections.append((b"OO", bo_obj.fbx_uuid, par_obj.fbx_uuid, None))

    # Object data.
    for ob_obj in objects:
        if ob_obj.is_bone:
            bo_data_key = data_bones[ob_obj]
            connections.append((b"OO", get_fbx_uuid_from_key(bo_data_key), ob_obj.fbx_uuid, None))
        else:
            if ob_obj.type == 'LIGHT':
                light_key = data_lights[ob_obj.bdata.data]
                connections.append((b"OO", get_fbx_uuid_from_key(light_key), ob_obj.fbx_uuid, None))
            elif ob_obj.type == 'CAMERA':
                cam_key = data_cameras[ob_obj]
                connections.append((b"OO", get_fbx_uuid_from_key(cam_key), ob_obj.fbx_uuid, None))
            elif ob_obj.type == 'EMPTY' or ob_obj.type == 'ARMATURE':
                empty_key = data_empties[ob_obj]
                connections.append((b"OO", get_fbx_uuid_from_key(empty_key), ob_obj.fbx_uuid, None))
            elif ob_obj.type in BLENDER_OBJECT_TYPES_MESHLIKE:
                mesh_key, _me, _free = data_meshes[ob_obj]
                connections.append((b"OO", get_fbx_uuid_from_key(mesh_key), ob_obj.fbx_uuid, None))

    # Leaf Bones
    for (_node_name, par_uuid, node_uuid, attr_uuid, _matrix, _hide, _size) in data_leaf_bones:
        connections.append((b"OO", node_uuid, par_uuid, None))
        connections.append((b"OO", attr_uuid, node_uuid, None))

    # 'Shape' deformers (shape keys, only for meshes currently)...
    for me_key, shapes_key, shapes in data_deformers_shape.values():
        # shape -> geometry
        connections.append((b"OO", get_fbx_uuid_from_key(shapes_key), get_fbx_uuid_from_key(me_key), None))
        for channel_key, geom_key, _shape_verts_co, _shape_verts_idx in shapes.values():
            # shape channel -> shape
            connections.append((b"OO", get_fbx_uuid_from_key(channel_key), get_fbx_uuid_from_key(shapes_key), None))
            # geometry (keys) -> shape channel
            connections.append((b"OO", get_fbx_uuid_from_key(geom_key), get_fbx_uuid_from_key(channel_key), None))

    # 'Skin' deformers (armature-to-geometry, only for meshes currently)...
    for arm, deformed_meshes in data_deformers_skin.items():
        for me, (skin_key, ob_obj, clusters) in deformed_meshes.items():
            # skin -> geometry
            mesh_key, _me, _free = data_meshes[ob_obj]
            assert(me == _me)
            connections.append((b"OO", get_fbx_uuid_from_key(skin_key), get_fbx_uuid_from_key(mesh_key), None))
            for bo_obj, clstr_key in clusters.items():
                # cluster -> skin
                connections.append((b"OO", get_fbx_uuid_from_key(clstr_key), get_fbx_uuid_from_key(skin_key), None))
                # bone -> cluster
                connections.append((b"OO", bo_obj.fbx_uuid, get_fbx_uuid_from_key(clstr_key), None))

    # Materials
    mesh_material_indices = {}
    _objs_indices = {}
    for ma, (ma_key, ob_objs) in data_materials.items():
        for ob_obj in ob_objs:
            connections.append((b"OO", get_fbx_uuid_from_key(ma_key), ob_obj.fbx_uuid, None))
            # Get index of this material for this object (or dupliobject).
            # Material indices for mesh faces are determined by their order in 'ma to ob' connections.
            # Only materials for meshes currently...
            # Note in case of dupliobjects a same me/ma idx will be generated several times...
            # Should not be an issue in practice, and it's needed in case we export duplis but not the original!
            if ob_obj.type not in BLENDER_OBJECT_TYPES_MESHLIKE:
                continue
            _mesh_key, me, _free = data_meshes[ob_obj]
            idx = _objs_indices[ob_obj] = _objs_indices.get(ob_obj, -1) + 1
            mesh_material_indices.setdefault(me, {})[ma] = idx
    del _objs_indices

    # Textures
    print("FBX Texture Prep")
    for (ma, sock_name), (tex_key, fbx_prop) in data_textures.items():
        ma_key, _ob_objs = data_materials[ma]
        print(ma_key, _ob_objs, ma, sock_name, fbx_prop)
        # texture -> material properties
        connections.append((b"OP", get_fbx_uuid_from_key(tex_key), get_fbx_uuid_from_key(ma_key), fbx_prop))

    # Images
    for vid, (vid_key, blender_tex_keys) in data_videos.items():
        for blender_tex_key in blender_tex_keys:
            tex_key, _fbx_prop = data_textures[blender_tex_key]
            connections.append((b"OO", get_fbx_uuid_from_key(vid_key), get_fbx_uuid_from_key(tex_key), None))

    # Animations
    for astack_key, astack, alayer_key, _name, _fstart, _fend in animations:
        # Animstack itself is linked nowhere!
        astack_id = get_fbx_uuid_from_key(astack_key)
        # For now, only one layer!
        alayer_id = get_fbx_uuid_from_key(alayer_key)
        connections.append((b"OO", alayer_id, astack_id, None))
        for elem_key, (alayer_key, acurvenodes) in astack.items():
            elem_id = get_fbx_uuid_from_key(elem_key)
            # Animlayer -> animstack.
            # alayer_id = get_fbx_uuid_from_key(alayer_key)
            # connections.append((b"OO", alayer_id, astack_id, None))
            for fbx_prop, (acurvenode_key, acurves, acurvenode_name) in acurvenodes.items():
                # Animcurvenode -> animalayer.
                acurvenode_id = get_fbx_uuid_from_key(acurvenode_key)
                connections.append((b"OO", acurvenode_id, alayer_id, None))
                # Animcurvenode -> object property.
                connections.append((b"OP", acurvenode_id, elem_id, fbx_prop.encode()))
                for fbx_item, (acurve_key, default_value, acurve, acurve_valid) in acurves.items():
                    if acurve:
                        # Animcurve -> Animcurvenode.
                        connections.append((b"OP", get_fbx_uuid_from_key(acurve_key), acurvenode_id, fbx_item.encode()))

    perfmon.level_down()

    # ##### And pack all this!

    return FBXExportData(
        templates, templates_users, connections,
        settings, scene, depsgraph, objects, animations, animated, frame_start, frame_end,
        data_empties, data_lights, data_cameras, data_meshes, mesh_material_indices,
        data_bones, data_leaf_bones, data_deformers_skin, data_deformers_shape,
        data_world, data_materials, data_textures, data_videos,
    )


# Contains fbx_data_texture_file_elements, fbx_data_material_elements
# Same as in io_scene_fbx, but pointing to the new functions
def fbx_objects_elements(root, scene_data):
    """
    Data (objects, geometry, material, textures, armatures, etc.).
    """
    perfmon = PerfMon()
    perfmon.level_up()
    objects = elem_empty(root, b"Objects")

    perfmon.step("FBX export fetch empties (%d)..." % len(scene_data.data_empties))

    for empty in scene_data.data_empties:
        fbx_data_empty_elements(objects, empty, scene_data)

    perfmon.step("FBX export fetch lamps (%d)..." % len(scene_data.data_lights))

    for lamp in scene_data.data_lights:
        fbx_data_light_elements(objects, lamp, scene_data)

    perfmon.step("FBX export fetch cameras (%d)..." % len(scene_data.data_cameras))

    for cam in scene_data.data_cameras:
        fbx_data_camera_elements(objects, cam, scene_data)

    perfmon.step("FBX export fetch meshes (%d)..."
                 % len({me_key for me_key, _me, _free in scene_data.data_meshes.values()}))

    done_meshes = set()
    for me_obj in scene_data.data_meshes:
        fbx_data_mesh_elements(objects, me_obj, scene_data, done_meshes)
    del done_meshes

    perfmon.step("FBX export fetch objects (%d)..." % len(scene_data.objects))

    for ob_obj in scene_data.objects:
        if ob_obj.is_dupli:
            continue
        fbx_data_object_elements(objects, ob_obj, scene_data)
        for dp_obj in ob_obj.dupli_list_gen(scene_data.depsgraph):
            if dp_obj not in scene_data.objects:
                continue
            fbx_data_object_elements(objects, dp_obj, scene_data)

    perfmon.step("FBX export fetch remaining...")

    for ob_obj in scene_data.objects:
        if not (ob_obj.is_object and ob_obj.type == 'ARMATURE'):
            continue
        fbx_data_armature_elements(objects, ob_obj, scene_data)

    if scene_data.data_leaf_bones:
        fbx_data_leaf_bone_elements(objects, scene_data)

    for ma in scene_data.data_materials:
        fbx_data_material_elements(objects, ma, scene_data)

    print("Getting Tex Keys")
    for blender_tex_key in scene_data.data_textures:
        print(blender_tex_key)
        fbx_data_texture_file_elements(objects, blender_tex_key, scene_data)

    for vid in scene_data.data_videos:
        fbx_data_video_elements(objects, vid, scene_data)

    perfmon.step("FBX export fetch animations...")
    start_time = time.process_time()

    fbx_data_animation_elements(objects, scene_data)

    perfmon.level_down()


# ##### "Main" functions. #####

# This func can be called with just the filepath
def save_single(operator, scene, depsgraph, filepath="",
                global_matrix=Matrix(),
                apply_unit_scale=False,
                global_scale=1.0,
                apply_scale_options='FBX_SCALE_NONE',
                axis_up="Z",
                axis_forward="Y",
                context_objects=None,
                object_types=None,
                use_mesh_modifiers=True,
                use_mesh_modifiers_render=True,
                mesh_smooth_type='FACE',
                use_armature_deform_only=False,
                bake_anim=True,
                bake_anim_use_all_bones=True,
                bake_anim_use_nla_strips=True,
                bake_anim_use_all_actions=True,
                bake_anim_step=1.0,
                bake_anim_simplify_factor=1.0,
                bake_anim_force_startend_keying=True,
                add_leaf_bones=False,
                primary_bone_axis='Y',
                secondary_bone_axis='X',
                use_metadata=True,
                path_mode='AUTO',
                use_mesh_edges=True,
                use_tspace=True,
                embed_textures=False,
                use_custom_props=False,
                bake_space_transform=False,
                armature_nodetype='NULL',
                **kwargs
                ):

    # Clear cached ObjectWrappers (just in case...).
    ObjectWrapper.cache_clear()

    if object_types is None:
        object_types = {'EMPTY', 'CAMERA', 'LIGHT', 'ARMATURE', 'MESH', 'OTHER'}

    if 'OTHER' in object_types:
        object_types |= BLENDER_OTHER_OBJECT_TYPES

    # Default Blender unit is equivalent to meter, while FBX one is centimeter...
    unit_scale = units_blender_to_fbx_factor(scene) if apply_unit_scale else 100.0
    if apply_scale_options == 'FBX_SCALE_NONE':
        global_matrix = Matrix.Scale(unit_scale * global_scale, 4) @ global_matrix
        unit_scale = 1.0
    elif apply_scale_options == 'FBX_SCALE_UNITS':
        global_matrix = Matrix.Scale(global_scale, 4) @ global_matrix
    elif apply_scale_options == 'FBX_SCALE_CUSTOM':
        global_matrix = Matrix.Scale(unit_scale, 4) @ global_matrix
        unit_scale = global_scale
    else: # if apply_scale_options == 'FBX_SCALE_ALL':
        unit_scale = global_scale * unit_scale

    global_scale = global_matrix.median_scale
    global_matrix_inv = global_matrix.inverted()
    # For transforming mesh normals.
    global_matrix_inv_transposed = global_matrix_inv.transposed()

    # Only embed textures in COPY mode!
    if embed_textures and path_mode != 'COPY':
        embed_textures = False

    # Calculate bone correction matrix
    bone_correction_matrix = None  # Default is None = no change
    bone_correction_matrix_inv = None
    if (primary_bone_axis, secondary_bone_axis) != ('Y', 'X'):
        from bpy_extras.io_utils import axis_conversion
        bone_correction_matrix = axis_conversion(from_forward=secondary_bone_axis,
                                                 from_up=primary_bone_axis,
                                                 to_forward='X',
                                                 to_up='Y',
                                                 ).to_4x4()
        bone_correction_matrix_inv = bone_correction_matrix.inverted()


    media_settings = FBXExportSettingsMedia(
        path_mode,
        os.path.dirname(bpy.data.filepath),  # base_src
        os.path.dirname(filepath),  # base_dst
        # Local dir where to put images (medias), using FBX conventions.
        os.path.splitext(os.path.basename(filepath))[0] + ".fbm",  # subdir
        embed_textures,
        set(),  # copy_set
        set(),  # embedded_set
    )

    settings = FBXExportSettings(
        operator.report, (axis_up, axis_forward), global_matrix, global_scale, apply_unit_scale, unit_scale,
        bake_space_transform, global_matrix_inv, global_matrix_inv_transposed,
        context_objects, object_types, use_mesh_modifiers, use_mesh_modifiers_render,
        mesh_smooth_type, use_mesh_edges, use_tspace,
        armature_nodetype, use_armature_deform_only,
        add_leaf_bones, bone_correction_matrix, bone_correction_matrix_inv,
        bake_anim, bake_anim_use_all_bones, bake_anim_use_nla_strips, bake_anim_use_all_actions,
        bake_anim_step, bake_anim_simplify_factor, bake_anim_force_startend_keying,
        False, media_settings, use_custom_props,
    )

    import bpy_extras.io_utils

    print('\nFBX export starting... %r' % filepath)
    start_time = time.process_time()

    # Generate some data about exported scene...
    scene_data = fbx_data_from_scene(scene, depsgraph, settings)

    root = elem_empty(None, b"")  # Root element has no id, as it is not saved per se!

    # Mostly FBXHeaderExtension and GlobalSettings.
    fbx_header_elements(root, scene_data)

    # Documents and References are pretty much void currently.
    fbx_documents_elements(root, scene_data)
    fbx_references_elements(root, scene_data)

    # Templates definitions.
    fbx_definitions_elements(root, scene_data)

    # Actual data.
    fbx_objects_elements(root, scene_data)

    # How data are inter-connected.
    fbx_connections_elements(root, scene_data)

    # Animation.
    fbx_takes_elements(root, scene_data)

    # Cleanup!
    fbx_scene_data_cleanup(scene_data)

    # And we are down, we can write the whole thing!
    encode_bin.write(filepath, root, FBX_VERSION)

    # Clear cached ObjectWrappers!
    ObjectWrapper.cache_clear()

    # copy all collected files, if we did not embed them.
    if not media_settings.embed_textures:
        bpy_extras.io_utils.path_reference_copy(media_settings.copy_set)

    print('export finished in %.4f sec.' % (time.process_time() - start_time))
    return {'FINISHED'}


def save(operator, context,
         filepath="",
         use_selection=False,
         use_active_collection=False,
         batch_mode='OFF',
         use_batch_own_dir=False,
         **kwargs
         ):
    """
    This is a wrapper around save_single, which handles multi-scenes (or collections) cases, when batch-exporting
    a whole .blend file.
    """

    ret = {'FINISHED'}

    active_object = context.view_layer.objects.active

    org_mode = None
    if active_object and active_object.mode != 'OBJECT' and bpy.ops.object.mode_set.poll():
        org_mode = active_object.mode
        bpy.ops.object.mode_set(mode='OBJECT')

    if batch_mode == 'OFF':
        kwargs_mod = kwargs.copy()
        if use_active_collection:
            if use_selection:
                ctx_objects = tuple(obj
                                    for obj in context.view_layer.active_layer_collection.collection.all_objects
                                    if obj.select_get())
            else:
                ctx_objects = context.view_layer.active_layer_collection.collection.all_objects
        else:
            if use_selection:
                ctx_objects = context.selected_objects
            else:
                ctx_objects = context.view_layer.objects
        kwargs_mod["context_objects"] = ctx_objects

        ret = save_single(operator, context.scene, context.depsgraph, filepath, **kwargs_mod)
    else:
        # XXX We need a way to generate a depsgraph for inactive view_layers first...
        # XXX Also, what to do in case of batch-exporting scenes, when there is more than one view layer?
        #     Scenes have no concept of 'active' view layer, that's on window level...
        fbxpath = filepath

        prefix = os.path.basename(fbxpath)
        if prefix:
            fbxpath = os.path.dirname(fbxpath)

        if batch_mode == 'COLLECTION':
            data_seq = tuple((coll, coll.name, 'objects') for coll in bpy.data.collections if coll.objects)
        elif batch_mode in {'SCENE_COLLECTION', 'ACTIVE_SCENE_COLLECTION'}:
            scenes = [context.scene] if batch_mode == 'ACTIVE_SCENE_COLLECTION' else bpy.data.scenes
            data_seq = []
            for scene in scenes:
                if not scene.objects:
                    continue
                #                                      Needed to avoid having tens of 'Master Collection' entries.
                todo_collections = [(scene.collection, "_".join((scene.name, scene.collection.name)))]
                while todo_collections:
                    coll, coll_name = todo_collections.pop()
                    todo_collections.extend(((c, c.name) for c in coll.children if c.all_objects))
                    data_seq.append((coll, coll_name, 'all_objects'))
        else:
            data_seq = tuple((scene, scene.name, 'objects') for scene in bpy.data.scenes if scene.objects)

        # call this function within a loop with BATCH_ENABLE == False

        new_fbxpath = fbxpath  # own dir option modifies, we need to keep an original
        for data, data_name, data_obj_propname in data_seq:  # scene or collection
            newname = "_".join((prefix, bpy.path.clean_name(data_name))) if prefix else bpy.path.clean_name(data_name)

            if use_batch_own_dir:
                new_fbxpath = os.path.join(fbxpath, newname)
                # path may already exist... and be a file.
                while os.path.isfile(new_fbxpath):
                    new_fbxpath = "_".join((new_fbxpath, "dir"))
                if not os.path.exists(new_fbxpath):
                    os.makedirs(new_fbxpath)

            filepath = os.path.join(new_fbxpath, newname + '.fbx')

            print('\nBatch exporting %s as...\n\t%r' % (data, filepath))

            if batch_mode in {'COLLECTION', 'SCENE_COLLECTION', 'ACTIVE_SCENE_COLLECTION'}:
                # Collection, so that objects update properly, add a dummy scene.
                scene = bpy.data.scenes.new(name="FBX_Temp")
                src_scenes = {}  # Count how much each 'source' scenes are used.
                for obj in getattr(data, data_obj_propname):
                    for src_sce in obj.users_scene:
                        src_scenes[src_sce] = src_scenes.setdefault(src_sce, 0) + 1
                    scene.collection.objects.link(obj)

                # Find the 'most used' source scene, and use its unit settings. This is somewhat weak, but should work
                # fine in most cases, and avoids stupid issues like T41931.
                best_src_scene = None
                best_src_scene_users = -1
                for sce, nbr_users in src_scenes.items():
                    if (nbr_users) > best_src_scene_users:
                        best_src_scene_users = nbr_users
                        best_src_scene = sce
                scene.unit_settings.system = best_src_scene.unit_settings.system
                scene.unit_settings.system_rotation = best_src_scene.unit_settings.system_rotation
                scene.unit_settings.scale_length = best_src_scene.unit_settings.scale_length

                scene.update()
                # TODO - BUMMER! Armatures not in the group wont animate the mesh
            else:
                scene = data

            kwargs_batch = kwargs.copy()
            kwargs_batch["context_objects"] = getattr(data, data_obj_propname)

            save_single(operator, scene, scene.view_layers[0].depsgraph, filepath, **kwargs_batch)

            if batch_mode in {'COLLECTION', 'SCENE_COLLECTION', 'ACTIVE_SCENE_COLLECTION'}:
                # Remove temp collection scene.
                bpy.data.scenes.remove(scene)

    if active_object and org_mode:
        context.view_layer.objects.active = active_object
        if bpy.ops.object.mode_set.poll():
            bpy.ops.object.mode_set(mode=org_mode)

    return ret
