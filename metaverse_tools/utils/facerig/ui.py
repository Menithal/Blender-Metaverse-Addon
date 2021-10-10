import bpy
import metaverse_tools.utils.facerig.ui as facerig




classes = (
)

module_register, module_unregister = bpy.utils.register_classes_factory(
    classes)

def register_operators():
    module_register()
    facerig.module_register()


def unregister_operators():
    module_unregister()
    facerig.module_unregister()
