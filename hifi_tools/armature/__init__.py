if "bpy" in locals():
    import importlib
    
    importlib.reload(panel)
    importlib.reload(repose)
    importlib.reload(skeleton)

else:
    from . import (
        panel,
        repose,
        skeleton
    )

    import bpy
