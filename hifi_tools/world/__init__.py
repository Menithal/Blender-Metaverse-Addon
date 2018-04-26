if "bpy" in locals():
    import importlib
    importlib.reload(primitives)
    importlib.reload(material)
    importlib.reload(scene)
else:
    from . import (
        primitives,
        material,
        scene
    )
    import bpy
