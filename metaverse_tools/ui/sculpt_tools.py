import bpy


classes = ()
module_register, module_unregister = bpy.utils.register_classes_factory(classes)

def register_operators():
    module_register()


def unregister_operators():
    module_unregister()