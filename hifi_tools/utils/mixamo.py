import bpy

from hifi_tools.utils import materials, mesh

def convert_mixamo_avatar_hifi():

    if not bpy.data.is_saved:
        print("Select a Directory")
        bpy.ops.hifi_error.save_file('INVOKE_DEFAULT')
        return
    
    bpy.ops.wm.console_toggle()
    print("Converting Mixamo Avatar to be Blender- High Fidelity compliant")
    print("Searching for  mixamo:: prefix bones")

    for obj in bpy.data.objects:
        if obj.type == "ARMATURE":
            for bone in obj.data.edit_bones:
                print(" - Renaming", bone.name)
                bone.name = bone.name.replace("mixamo::","")
        
        if obj.type == "MESH":
            print("Cleaning unused vertex groups")
            mesh.clean_unused_vertex_groups(obj)

    print("Texture pass")
    materials.pack_images(bpy.data.images)
    materials.unpack_images(bpy.data.images)
    
    materials.convert_images_to_mask(bpy.data.images)
                
    bpy.ops.file.make_paths_absolute()

    bpy.ops.wm.console_toggle()

