import bpy

def apply_armature_restpose(context):
    active = context.active_object
  
    if active.type != "ARMATURE":  
        print("Armature was not found")
        return

    for child in active.children:
        modifiers = child.modifiers
        # Find Modifier that is the Armature
        print("Trying to find Armature modifier in Child " + child.name)
        armature_modifiers = [modifier for modifier in modifiers if modifier.type == "ARMATURE"]
        if len(armature_modifiers) == 0:
            print("Could not find armature modifier for " + child.name)
            continue
        
        context.view_layer.objects.active = child
        
        armature_modifier = armature_modifiers[0]
        
        print("Modifier found, name is "  + armature_modifier.name)
        bpy.ops.object.modifier_copy(modifier=armature_modifier.name)
        
        active_modifier = child.modifiers.active

        success = bpy.ops.object.apply_modifier_for_object_with_shape_keys( my_enum=armature_modifier.name, disable_armatures=False)
        if success:
            active_modifier.name = armature_modifier.name
            child.select_set(False)
            print("Succesfully merged modifier in " + child.name)
            continue

        context.view_layer.objects.active = active
        print("Could not merge modifier for " + child.name + " - Skipping")
        return
    
    context.view_layer.objects.active = active
    bpy.ops.object.mode_set(mode="POSE")

    active.select_set(False)
    bpy.ops.pose.armature_apply()
    # Armature is selected
    # Change mode to Pose
    # apply restpose to armature
    
            
        