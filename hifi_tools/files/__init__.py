if "bpy" in locals():
    import importlib
    importlib.reload(hifi_json)
    importlib.reload(fst)
else:
    from . import (
        hifi_json,
        fst
    )
    import bpy
