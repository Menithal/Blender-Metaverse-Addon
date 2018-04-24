import bpy
import os
import uuid

from hifi_tools.utils.bones import find_armature, retarget_armature
from hifi_tools.utils.mesh import get_mesh_from
from hifi_tools.utils.materials import get_images_from

prefix_joint_maps = {
    "Hips": "jointRoot",
    "Head": "jointHead",
    "RightHand": "jointRightHand",
    "LeftHand": "jointLeftHand",
    "Neck": "jointNeck",
    "LeftEye": "jointLeftEye",
    "RightEye": "jointRightEye",
    "Spine": "jointLean"
}

prefix_free_joints = [
    "LeftArm",
    "LeftForeArm",
    "RightArm",
    "RightForeArm"
]

prefix_name = "name = $\n"
prefix_type = "type = body+head\n"
prefix_scale = "scale = $\n"
prefix_texdir = "texdir = $\n"
prefix_filename = "filename = $\n"


def fst_export(context, selected):

    # file = open
    uuid_gen = uuid.uuid5(uuid.NAMESPACE_DNS, context.name)
    scene_id = str(uuid_gen)

    print("Exporting file to filepath", context.filepath)

    path = os.path.dirname(os.path.realpath(context.filepath)) + '/'

    texture_path = os.path.dirname(
        os.path.realpath(context.filepath)) + '/textures/'

    avatar_file = scene_id + ".fbx"
    avatar_filepath = path + avatar_file

    joint_maps = prefix_joint_maps.keys()
    print(joint_maps, selected)
    armature = find_armature(selected)

    if armature is None:
        print(" Could not find Armature in selection or scene")
        return {"CANCELLED"}

    f = open(context.filepath, "w")

    # selected_only
    mode = bpy.context.area.type
    try:

        bpy.context.area.type = 'VIEW_3D'

        f.write(prefix_name.replace('$', context.name))
        f.write(prefix_type)
        f.write(prefix_scale.replace('$', str(context.scale)))
        if not context.embed:
            f.write(prefix_texdir.replace('$', scene_id + '.fbm/'))
        f.write(prefix_filename.replace('$', avatar_file))

        # Writing these in separate loops because they need to done in order.
        for bone in armature.data.bones:
            if bone.name in joint_maps:
                print("Writing joint map",
                      prefix_joint_maps[bone.name] + " = " + bone.name)
                f.write("joint = " + prefix_joint_maps[bone.name] + " = " + bone.name + "\n")

        for bone in armature.data.bones:
            if bone.name in prefix_free_joints:
                print("Writing joint index", "freeJoint = " + bone.name + "\n")
                f.write("freeJoint = " + bone.name + "\n")
                
        retarget_armature({"apply": True}, selected)

        if bpy.context.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')
        
        bpy.ops.object.select_all(action='DESELECT')

        for select in selected:
            select.select = True

        bpy.ops.export_scene.fbx(filepath=avatar_filepath, version='BIN7400', embed_textures=context.embed, path_mode='COPY',
                                 use_selection=True, axis_forward='-Z', axis_up='Y')

    except Exception as e:
        print('Could not write to file.', e)

        f.close()
        bpy.context.area.type = mode
        return {"CANCELLED"}

    f.close()
    bpy.context.area.type = mode

    return {"FINISHED"}
    # FST Exporter
