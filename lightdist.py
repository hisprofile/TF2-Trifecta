import bpy, math
from bpy.types import *
from mathutils import *
class HISANIM_PT_LIGHTDIST(bpy.types.Panel):
    bl_label = "Light Optimizer"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_context = ''#.objectmode'
    bl_category = 'Tool'

    #framemodulo = bpy.props.IntProperty(default=1, min=1)

    def draw(self, context):
        s = self
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
        row.prop(context.scene, 'hisanimenablespread', text='Slower, Better Performing')
        row=layout.row()
        row.prop(context.scene, 'hisanimframemodulo')
        row.enabled = True if context.scene.hisanimenablespread else False
        layout.label(text=f'Active Lights: {GetActiveLights("ACTIVE")}/128 Max')
        layout.label(text=f'{GetActiveLights("OVERRIDDEN")} Overridden lights')

IsLight = lambda a: a.type=='LIGHT'

def IsHidden(a):
    if bpy.data.objects[a.name].hide_get() == True:
        return False
    else:
        return True

def IsOverriden(a):
    if a.get('LIGHTOVERRIDE') != None:
        return True
    else:
        return False

def GetActiveLights(stats):
    if stats == 'ACTIVE':
        return len(list(filter(IsHidden, list(filter(IsLight, bpy.data.objects)))))
    else:
        return len(list(filter(IsOverriden, list(filter(IsLight, bpy.data.objects)))))



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
#l[int((f() % t())*(len(l) / t())) : None if int(((f() + 1) % t())*(len(l) / t()))== 0 else int(((f() + 1) % t())*(len(l) / t())) ]



def f():
    return bpy.context.scene.frame_current

def t():
    return bpy.context.scene.hisanimframemodulo

def OptimizeLights(self = None, context = None):
    if bpy.context.scene.hisaenablelightdist == False:
        return None
    LIGHTS = list(filter(IsLight, bpy.data.objects))
    l = list(range(0, len(LIGHTS)))
    if bpy.context.scene.hisanimenablespread and bpy.context.screen.is_animation_playing:
        for i in l[int((f() % t())*(len(l) / t())) : None if int(((f() + 1) % t())*(len(l) / t()))== 0 else int(((f() + 1) % t())*(len(l) / t())) ]:
            if LIGHTS[i].data.get('LIGHTOVERRIDE'):
                continue
            if math.dist(bpy.context.scene.camera.location, LIGHTS[i].location) > bpy.context.scene.hisanimdrag.value*2 and not LIGHTS[i].data.type == 'SUN':
                LIGHTS[i].hide_set(True)
                LIGHTS[i].hide_render = True
                LIGHTS[i].data['HIDDEN'] = True
                continue
            else:
                LIGHTS[i].data['HIDDEN'] = False
                LIGHTS[i].hide_set(False)
                LIGHTS[i].hide_render = False
                continue
    else:
        for i in LIGHTS:
            if i.data.get('LIGHTOVERRIDE'):
                continue
            if math.dist(bpy.context.scene.camera.location, i.location) > bpy.context.scene.hisanimdrag.value*2 and not i.data.type == 'SUN':
                i.hide_set(True)
                i.hide_render = True
                i.data['HIDDEN'] = True
            else:
                i['HIDDEN'] = False
                i.hide_set(False)
                i.hide_render = False

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
        for i in list(filter(IsLight, bpy.data.objects)):
            i.hide_set(False)
            i.hide_render = False
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
    #bpy.types.Scene.hisanimframe = bpy.props.IntProperty(name=)
    bpy.types.Scene.hisanimdrag = bpy.props.PointerProperty(type=HISANIM_LIGHTDIST)
    bpy.app.handlers.frame_change_post.append(OptimizeLights)
    bpy.app.handlers.load_post.append(crossover)
    bpy.types.Scene.hisanimframemodulo = bpy.props.IntProperty(default=1, min=1, name='Frame Modulo', description='Have all the lights refresh every other amount of frames')
    bpy.types.Scene.hisanimenablespread = bpy.props.BoolProperty()
    #subscribe_to = bpy.types.Object, "location"
    
def unregister():
    for i in classes:
        bpy.utils.unregister_class(i)
    del bpy.types.Scene.hisanimframemodulo
    del bpy.types.Scene.hisanimlightdist
    del bpy.types.Scene.hisaenablelightdist
    del bpy.types.Scene.hisanimdrag
    del bpy.types.Scene.hisanimenablespread
    try:
        bpy.app.handlers.load_post.remove(crossover)
    except:
        pass
    try:
        bpy.app.handlers.frame_change_post.remove(OptimizeLights)
    except:
        pass