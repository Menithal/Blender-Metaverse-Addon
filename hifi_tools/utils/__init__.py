if "bpy" in locals():
    import importlib
    importlib.reload(helpers)
    importlib.reload(mmd)
else:
    from . import (
        helpers,
        mmd
    )
    import bpy
