import bpy, math
from bpy.types import *
from mathutils import *
class HISANIM_PT_LIGHTDIST(bpy.types.Panel):
    bl_label = "Light Optimizer"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'scene'

    def draw(self, context):
        layout = self.layout
        layout.label(text='Optimize lights in a scene by disabling them based on how far away they are from the scene camera.')
        row = layout.row()
        row.prop(context.scene, 'hisaenablelightdist', text='Enable Light Optimization')
        row = layout.row()
        row.prop(context.scene.hisanimdrag, 'value')
        row.enabled = True if context.scene.hisaenablelightdist else False
        row = layout.row(align=True)
        row.operator('hisanim.lightoverride')
        row.operator('hisanim.removeoverrides')
        row.enabled = True if len(context.selected_objects) >= 1 else False
        row = layout.row()
        row.operator('hisanim.revertlights')
        row.enabled = False if context.scene.hisaenablelightdist else True
        row = layout.row()
        layout.label(text=f'Active Lights: {GetActiveLights("ACTIVE")}/128 Max')
        layout.label(text=f'{GetActiveLights("OVERRIDDEN")} Overridden lights')

def GetActiveLights(stats):
    lightcounter = 0
    if stats == 'ACTIVE':
        for i in bpy.data.lights:
            if bpy.data.objects[i.name].hide_get() == False:
                lightcounter += 1
    else:
        for i in bpy.data.lights:
            if i.get('LIGHTOVERRIDE') != None:
                lightcounter += 1
    return lightcounter


class HISANIM_OT_DRAGSUBSCRIBE(bpy.types.Operator):
    bl_idname = 'hisanim.dragsub'
    bl_label = ''
    stop: bpy.props.BoolProperty()

    def modal(self, context, event):
        if self.stop:
            context.scene.hisanimdrag.is_dragging = False
            bpy.data.objects.remove(bpy.data.objects['LIGHTDIST'])
            return {'FINISHED'}
        if event.value == 'RELEASE':
            self.stop = True

        return {'PASS_THROUGH'}
    def invoke(self, context, event):
        self.stop = False
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

def OptimizeLights(self = None, context = None):
    DO = bpy.data.objects
    if bpy.context.scene.hisaenablelightdist == False:
        return None
    for i in bpy.data.lights:
        if i.get('LIGHTOVERRIDE'):
            continue
        if math.dist(bpy.context.scene.camera.location, DO[i.name].location) > bpy.context.scene.hisanimdrag.value*2 and not i.type == 'SUN':
            DO[i.name].hide_set(True)
            DO[i.name].hide_render = True
        else:
            DO[i.name].hide_set(False)
            DO[i.name].hide_render = False

class HISANIM_OT_LIGHTOVERRIDE(bpy.types.Operator):
    bl_idname = 'hisanim.lightoverride'
    bl_label = 'Override Optimizer'
    bl_description = 'Lights that have an override property added to them will always show no matter how far away the camera is'

    def execute(self, context):
        for i in bpy.context.selected_objects:
            if i.type != "LIGHT" or i.data.get('LIGHTOVERRIDE') != None:
                continue
            i.data['LIGHTOVERRIDE'] = True
        return {'FINISHED'}

class HISANIM_OT_REMOVEOVERRIDES(bpy.types.Operator):
    bl_idname = 'hisanim.removeoverrides'
    bl_label = 'Remove Overrides'
    bl_description = 'Make a light hidable again by the Light Optimizer.'

    def execute(self, context):
        for i in bpy.context.selected_objects:
            if i.type != "LIGHT" or i.data.get('LIGHTOVERRIDE') == None:
                continue
            del i.data['LIGHTOVERRIDE']
        return {'FINISHED'}

class HISANIM_OT_REVERTLIGHTS(bpy.types.Operator):
    bl_idname = 'hisanim.revertlights'
    bl_label = 'Show All Lights'
    bl_description = 'Show all the lights that were left hidden by the optimizer'

    def execute(self, execute):
        for i in bpy.data.lights:
            bpy.data.objects[i.name].hide_set(False)
            bpy.data.objects[i.name].hide_render = False
        return {'FINISHED'}

def hisanimupdates(self, value):
    C = bpy.context
    if self.is_dragging:
        OptimizeLights()
        bpy.data.objects['LIGHTDIST'].scale = Vector((self.value*2, self.value*2, self.value*2))
    else:
        EMPTY = bpy.data.objects.new('LIGHTDIST', None)
        C.scene.collection.objects.link(EMPTY)
        EMPTY.empty_display_type = 'SPHERE'
        EMPTY.scale = Vector((self.value*2, self.value*2, self.value*2))
        EMPTY.location = C.scene.camera.location
        EMPTY.show_in_front = True
        OptimizeLights()
        self.is_dragging = True
        bpy.ops.hisanim.dragsub('INVOKE_DEFAULT')

class HISANIM_LIGHTDIST(bpy.types.PropertyGroup):
    value: bpy.props.FloatProperty(update=hisanimupdates, min=0.0, max=1000.0, step=25, default=25.0)
    is_dragging: bpy.props.BoolProperty()
classes = [HISANIM_PT_LIGHTDIST,
            HISANIM_OT_DRAGSUBSCRIBE,
            HISANIM_LIGHTDIST,
            HISANIM_OT_LIGHTOVERRIDE,
            HISANIM_OT_REMOVEOVERRIDES,
            HISANIM_OT_REVERTLIGHTS]

from bpy.app.handlers import persistent

@persistent
def crossover(dummy):
    bpy.app.handlers.frame_change_post.append(OptimizeLights)

#bpy.app.handlers.load_post.append(crossover)

def register():
    for i in classes:
        bpy.utils.register_class(i)
    bpy.types.Scene.hisanimlightdist = bpy.props.FloatProperty(min=0.0, default=25.0, step=0.1)#text='Max Light Distance', description='Lights outside of this distance will be disabled.', default=100.0)
    bpy.types.Scene.hisaenablelightdist = bpy.props.BoolProperty()#text='Enable Light Optimization', default=False)
    bpy.types.Scene.hisanimdrag = bpy.props.PointerProperty(type=HISANIM_LIGHTDIST)
    bpy.app.handlers.frame_change_post.append(OptimizeLights)
    bpy.app.handlers.load_post.append(crossover)
    #subscribe_to = bpy.types.Object, "location"
    
def unregister():
    for i in classes:
        bpy.utils.unregister_class(i)
    del bpy.types.Scene.hisanimlightdist
    del bpy.types.Scene.hisaenablelightdist
    del bpy.types.Scene.hisanimdrag
    try:
        bpy.app.handlers.load_post.remove(crossover)
    except:
        pass
    try:
        bpy.app.handlers.frame_change_post.remove(OptimizeLights)
    except:
        pass