
import bpy 

def of(selected, type: str):
    selection = []

    for select in selected:
        if select.type == type:
            selection.append(select)

    return selection