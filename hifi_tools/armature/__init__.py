if "bpy" in locals():
    import importlib
    
    importlib.reload(panel)
    importlib.reload(repose)

else:
    from . import (
        panel,
        repose
    )

    import bpy
