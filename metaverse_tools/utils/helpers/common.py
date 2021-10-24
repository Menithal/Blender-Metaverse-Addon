
import bpy 

ops = bpy.ops

# Filtered selection
def of(selected, type: str):
    selection = []

    for select in selected:
        if select.type == type:
            print("append " + select.name)
            selection.append(select)

    return selection

def object_active(obj):
    bpy.context.view_layer.objects.active = obj

def object_active_selected(obj):
    select(obj)
    bpy.context.view_layer.objects.active = obj

# bpy ops deselect helper
def deselect_all():
    mode = bpy.context.mode

    # This is a fairly hefty if, but this is for dev sanity remembering all the modes the app might be in.
    if mode == 'EDIT_MESH':
        ops.mesh.select_all(action = 'DESELECT')
    elif mode == 'EDIT_ARMATURE':
        ops.armature.select_all(action = 'DESELECT')
    elif mode == 'POSE':
        ops.pose.select_all(action = 'DESELECT')
    elif mode == 'OBJECT':
        ops.object.select_all(action = 'DESELECT')
    else: # Everything else is not to be supported as those operations are not something we will use with MVT
        return False 

    return True

# bpy ops select helper
def select(selected_original):
    # This is a fairly hefty if, but this is for dev sanity remembering all the modes the app might be in.
    
    if selected_original is None:
        return False
    if not isinstance(selected_original, list): 
        selected = [selected_original]
    else:
        selected = selected_original

    if not deselect_all():
        return False
    elif len(selected) == 0:
        return False 
   
    for select in selected:
        try:
            select.select_set(True)
        except e:
            print("Error trying to select", select.name)

    return True


def context_selected():
    context = bpy.context
    mode = context.mode

    # This is a fairly hefty if, but this is for dev sanity remembering all the modes the app might be in.
    if mode == 'EDIT_MESH':
        #needs object 
        ops.mesh.select_all(action = 'DESELECT')
    elif mode == 'EDIT_ARMATURE':
        return context.selected_bones
    elif mode == 'POSE':
        return context.selected_pose_bones
    elif mode == 'OBJECT':
        return context.selected_objects