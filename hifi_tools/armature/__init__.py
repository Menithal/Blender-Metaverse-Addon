if "bpy" in locals():
    import importlib
    
    importlib.reload(panel)
    importlib.reload(skeleton)

else:
    from . import (
        panel,
        skeleton
    )

    import bpy
