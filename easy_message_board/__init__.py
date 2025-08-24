import bpy

will_unregster_sub_vers_warning = False

class EMB_PT_bad_version(bpy.types.Panel):
    bl_label = 'Easy Message Board'
    bl_category = 'Tool'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'

    def draw(self, context):
        layout = self.layout
        layout.label(text='Easy Message Board is only available for Blender 4.1 and up.')
        layout.label(text='As a result, you are unable to get notifications from the developer.')

def register():
    global will_unregster_sub_vers_warning
    if (bpy.app.version < (4, 1, 0)):
        if not bool(getattr(bpy.types, 'EMB_PT_bad_version', False)):
            bpy.utils.register_class(EMB_PT_bad_version)
            will_unregster_sub_vers_warning = True
        return
    else:
        from . import system
        system.register()

def unregister():
    global will_unregster_sub_vers_warning
    if (bpy.app.version < (4, 1, 0)):
        if will_unregster_sub_vers_warning:
            bpy.utils.unregister_class(EMB_PT_bad_version)
        return
    else:
        from . import system
        system.unregister()