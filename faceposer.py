import bpy
from bpy.app.handlers import persistent
from . import mercdeployer

@persistent
def updatefaces(scn = None):
    props = bpy.context.scene.hisanimvars
    try:
        data = bpy.context.object.data
    except:
        return None
    if data.get('aaa_fs') == None: return None
    props.activeface = bpy.context.object

    if props.activeface != props.lastactiveface:
        props.sliders.clear()
        k = data.keys()
        z = list(zip(range(len(k)), k))
        for i in range(len(data.keys())):
            try:
                newdata = data.id_properties_ui(z[i][1]).as_dict()
            except:
                continue
            if 'left' in z[i][1]:
                continue
            mini = newdata.get('min')
            maxi = newdata.get('max')
            new = props.sliders.add()
            new.name = z[i][1]
            new.mini = mini
            new.maxi = maxi
            if 'right' in z[i][1]:
                new.split = True
                new.R = z[i][1]
                new.L = z[i+1][1]
                new.realvalue = False
                new.name = z[i][1]
    props.lastactiveface = props.activeface

class HISANIM_OT_SLIDEKEYFRAME(bpy.types.Operator):
    bl_idname = 'hisanim.keyslider'
    bl_label = 'Keyframe Slider'
    bl_description = 'Keyframe this slider'

    delete: bpy.props.BoolProperty(default=False)
    slider: bpy.props.StringProperty()
    def execute(self, context):
        props = context.scene.hisanimvars
        slider = props.sliders[self.slider]
        data = bpy.context.object.data
        if slider.split:
            if self.delete:
                data.keyframe_delete(data_path=f'["{slider.R}"]')
                data.keyframe_delete(data_path=f'["{slider.L}"]')
            else:
                data.keyframe_insert(data_path=f'["{slider.R}"]')
                data.keyframe_insert(data_path=f'["{slider.L}"]')
        else:
            if self.delete:
                data.keyframe_delete(data_path=f'["{slider.name}"]')
            else:
                data.keyframe_insert(data_path=f'["{slider.name}"]')

        return {'FINISHED'}
        

class HISANIM_OT_SLIDERESET(bpy.types.Operator):
    bl_idname = 'hisanim.resetslider'
    bl_label = ''
    slider = bpy.props.StringProperty()
    stop: bpy.props.BoolProperty(default = False)

    def modal(self, context, event):
        props = context.scene.hisanimvars
        face = bpy.context.object
        if self.stop:
            bpy.context.scene.hisanimvars.dragging = False
            #bpy.context.scene.hisanimvars.sliders[bpy.context.scene.hisanimvars.activeslider].value = 0
            context.scene.hisanimvars.dragging = False
            props.updating = True
            for i in context.scene.hisanimvars.sliders:
                if context.scene.tool_settings.use_keyframe_insert_auto:
                    if i.changed:
                        if i.split:
                            if i.originalval != face.data[i.R]:
                                face.data.keyframe_insert(data_path=f'["{i.R}"]')
                            if i.originalvalL != face.data[i.L]:
                                face.data.keyframe_insert(data_path=f'["{i.L}"]')
                        else:
                            if i.originalval != face.data[i.name]:
                                face.data.keyframe_insert(data_path=f'["{i.name}"]')
                            
                i.value = 0
                i.changed = False
            props.activeslider = ''
            
            props.updating = False
            props.callonce = False
            return {'FINISHED'}

        if event.value == 'RELEASE':
            self.stop = True

        return {'PASS_THROUGH'}
    def invoke(self, context, event):
        self.stop = False
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

def slideupdate(self, value):
    props = bpy.context.scene.hisanimvars
    if props.updating: return None
    if props.dragging:
        self.changed = True
        ignore = False if props.activeslider != self.name else True
        if not self.split:
            props.activeface.data[self.name] = min(max(self.originalval + (self.value * props.sensitivity), self.mini), self.maxi)
        else:
            Rmult = mercdeployer.MAP(props.LR, 0.0, 0.5, 0.0, 1.0, True)
            Lmult = mercdeployer.MAP(props.LR, 1.0, 0.5, 0.0, 1.0, True)
            props.activeface.data[self.R] = min(max(self.originalval + (self.value * props.sensitivity * Rmult), self.mini), self.maxi)
            props.activeface.data[self.L] = min(max(self.originalvalL + (self.value * props.sensitivity * Lmult), self.mini), self.maxi)
        #pass
        #for driv in props.activeface.data.shape_keys.animation_data.drivers:
            #driv.driver.expression = driv.driver.expression
        props.activeface.data.update()
        props.activeslider = self.name
    else:
        if not self.split:
            self.originalval = props.activeface.data[self.name]
        else:
            self.originalval = props.activeface.data[self.R]
            self.originalvalL = props.activeface.data[self.L]
        #if self.split: self.originalvalL = self.originalval
        props.activeslider = self.name
        #print(self.name)
        props.dragging = True
        if not props.callonce: bpy.ops.hisanim.resetslider('INVOKE_DEFAULT')
        props.callonce = True
    #print(self.name)
    return None

class faceslider(bpy.types.PropertyGroup):
    #def set_val():

    name: bpy.props.StringProperty()
    value: bpy.props.FloatProperty(name='', default=0.0, update=slideupdate, min=-1, max=1)
    split: bpy.props.BoolProperty(name='')
    mini: bpy.props.FloatProperty()
    maxi: bpy.props.FloatProperty()
    originalval: bpy.props.FloatProperty()
    originalvalL: bpy.props.FloatProperty()
    realvalue: bpy.props.BoolProperty(default=True)
    R: bpy.props.StringProperty()
    L: bpy.props.StringProperty()
    changed: bpy.props.BoolProperty(default=False)

class HISANIM_OT_FIXFACEPOSER(bpy.types.Operator):
    bl_idname = 'hisanim.fixfaceposer'
    bl_label = 'Fix Face Poser'
    bl_description = 'If something seems off, click this'

    @classmethod
    def poll(cls, context):
        return context.scene.hisanimvars.dragging

    def execute(self, context):
        props = context.scene.hisanimvars
        props.dragging = False
        props.activeslider = ''
        bpy.ops.hisanim.resetslider('INVOKE_DEFAULT', stop=True)
        return {'FINISHED'}

classes = [
    faceslider,
    HISANIM_OT_SLIDERESET,
    HISANIM_OT_FIXFACEPOSER,
    HISANIM_OT_SLIDEKEYFRAME
]

def register():
    for i in classes:
        bpy.utils.register_class(i)
    bpy.app.handlers.depsgraph_update_post.append(updatefaces)

def unregister():
    for i in classes:
        bpy.utils.unregister_class(i)
    bpy.app.handlers.depsgraph_update_post.remove(updatefaces)