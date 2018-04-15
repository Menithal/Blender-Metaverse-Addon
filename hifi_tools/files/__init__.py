if "bpy" in locals():
    import importlib
    importlib.reload(hifi_json)
else:
    from . import (
        hifi_json
    )
    import bpy
