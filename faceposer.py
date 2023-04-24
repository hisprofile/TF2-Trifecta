import bpy, random
from bpy.app.handlers import persistent

upperFace = ['BrowInV', 'BrowOutV', 'Frown', 'InnerSquint',
             'OuterSquint', 'ScalpD', 'CloseLid',
             'multi_CloseLid']

midFace = ['NoseV', 'NostrilFlare', 'CheekV', 'CheekH']

lowerFace = ['JawV', 'JawD', 'JawH', 'LipsV', 'LipUpV',
             'LipLoV', 'FoldLipUp', 'FoldLipLo', 'PuckerLipLo',
             'PuckerLipUp', 'PuffLipUp', 'PuffLipLo',
             'Smile', 'multi_Smile', 'Platysmus', 'LipCnrTwst',
             'Dimple']

facesections = [upperFace, midFace, lowerFace]

def MAP(x,a,b,c,d, clamp=None):
    y=(x-a)/(b-a)*(d-c)+c
    
    if clamp:
        return min(max(y, c), d)
    else:
        return y
    
@persistent
def updatefaces(scn = None):
    '''
    Everytime an object gets selected, run this. However, if it is not
    recognized as a head, do nothing. If a face is selected,
    cycle through its keys and create sliders from them. Then, use those
    sliders to manipulate the keys.
    '''

    props = bpy.context.scene.hisanimvars
    try:
        data = bpy.context.object.data
        data.get('')
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
            if 'right' in z[i][1]: # if the slider is one half of another, make it recognized as a half, and define both haves
                # in the slider.
                new.split = True
                new.R = z[i][1]
                new.L = z[i+1][1]
                new.realvalue = False
                new.name = z[i][1]
                NAME = new.name.split('_')[-1]
                for sectstr, sect in zip(['UPPER', 'MID', 'LOWER'], facesections):
                    if NAME in sect:
                        new.Type = sectstr
                        break
            else:
                name = new.name[4:]
                for sectstr, sect in zip(['UPPER', 'MID', 'LOWER'], facesections):
                    if name in sect:
                        new.Type = sectstr
                        break
    
    props.lastactiveface = props.activeface # use this to see if a new face has been selected. if the same face has been selected twice, do nothing.

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
            
            return {'FINISHED'}

        if event.value == 'RELEASE':
            self.stop = True
            bpy.context.scene.hisanimvars.dragging = False # allow sliders to initialize original values again
            context.scene.hisanimvars.dragging = False
            props.updating = True
            for i in context.scene.hisanimvars.sliders:
                if i.changed:
                    if context.scene.tool_settings.use_keyframe_insert_auto:
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

        return {'PASS_THROUGH'}
    def invoke(self, context, event):
        self.stop = False
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

def slideupdate(self, value):
    props = bpy.context.scene.hisanimvars
    if props.updating: return None
    if props.dragging: # do this every time after once
        self.changed = True
        ignore = False if props.activeslider != self.name else True
        if not self.split:
            props.activeface.data[self.name] = min(max(self.originalval + (self.value * props.sensitivity), self.mini), self.maxi)
        else:
            Rmult = MAP(props.LR, 0.0, 0.5, 0.0, 1.0, True)
            Lmult = MAP(props.LR, 1.0, 0.5, 0.0, 1.0, True)
            props.activeface.data[self.R] = min(max(self.originalval + (self.value * props.sensitivity * Rmult), self.mini), self.maxi)
            props.activeface.data[self.L] = min(max(self.originalvalL + (self.value * props.sensitivity * Lmult), self.mini), self.maxi)
        if props.activeslider == '': props.activeslider = self.name
        props.activeface.data.update()
        print(props.activeslider)
    else: # do this once
        '''if not self.split:
            self.originalval = props.activeface.data[self.name]
        else:
            self.originalval = props.activeface.data[self.R]
            self.originalvalL = props.activeface.data[self.L]'''
        for slide in props.sliders:
            #print(slide)
            if not slide.split:
                slide.originalval = bpy.context.object.data[slide.name]
            else:
                slide.originalval = bpy.context.object.data[slide.R]
                slide.originalvalL = bpy.context.object.data[slide.L]
        # define original values to add off of and produce a final result. an original value is the value of a slider before manipulating took place.
        
        #print(self.name)
        props.dragging = True
        if not props.callonce: bpy.ops.hisanim.resetslider('INVOKE_DEFAULT')
        props.callonce = True
    #print(self.name)
    return None

class faceslider(bpy.types.PropertyGroup):

    def set_lock(self, value):
        obj = bpy.context.object
        if (locklist := obj.data.get('locklist')) == None:
            obj.data['locklist'] = {}
            locklist = obj.data['locklist']
        if not self.split:
            if (lockstate := locklist.get(self.name)) == None:
                locklist[self.name] = True
                return None
            locklist[self.name] = 1 - lockstate
            return None
        else:
            if (lockstate := locklist.get(self.R)) == None:
                locklist[self.R] = True
                return None
            locklist[self.R] = 1 - lockstate
            return None
        
    def set_lockL(self, value):
        obj = bpy.context.object
        if (locklist := obj.data.get('locklist')) == None:
            obj.data['locklist'] = {}
            locklist = obj.data['locklist']
        if (lockstate := locklist.get(self.L)) == None:
            locklist[self.L] = True
            return None
        locklist[self.L] = 1 - lockstate
        return None
    
    def get_lock(self):
        obj = bpy.context.object
        if (locklist := obj.data.get('locklist')) == None: return False
        locklist = obj.data['locklist']
        if (lockstate := locklist.get(self.name)) == None: return False
        return lockstate
    
    def get_lockL(self):
        obj = bpy.context.object
        if (locklist := obj.data.get('locklist')) == None: return False
        locklist = obj.data['locklist']
        if (lockstate := locklist.get(self.L)) == None: return False
        return lockstate

    name: bpy.props.StringProperty()
    value: bpy.props.FloatProperty(name='', default=0.0, update=slideupdate, min=-1, max=1, options=set())
    split: bpy.props.BoolProperty(name='')
    mini: bpy.props.FloatProperty(options=set())
    maxi: bpy.props.FloatProperty(options=set())
    originalval: bpy.props.FloatProperty(options=set())
    originalvalL: bpy.props.FloatProperty(options=set())
    realvalue: bpy.props.BoolProperty(default=True, options=set())
    R: bpy.props.StringProperty()
    L: bpy.props.StringProperty()
    changed: bpy.props.BoolProperty(default=False, options=set())
    Type: bpy.props.EnumProperty(items=(
        ('NONE', 'None', '', '', 0),
        ('UPPER', 'Upper Face', '', '', 1),
        ('MID', 'Mid Face', '', '', 2),
        ('LOWER', 'Lower Face', '', '', 3)
        ),
        name='type', options=set()
    )
    locked: bpy.props.BoolProperty(name='', default = False, set=set_lock, get=get_lock, options=set())
    lockedL: bpy.props.BoolProperty(default = False, name='', set=set_lockL, get=get_lockL, options=set())

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

class HISANIM_OT_RANDOMIZEFACE(bpy.types.Operator):
    bl_idname = 'hisanim.randomizeface'
    bl_label = 'Randomize Face'
    bl_description = 'Randomize the values of the facial sliders'
    bl_options = {'UNDO'}
    reset: bpy.props.BoolProperty(default=False)

    def execute(self, context):
        props = context.scene.hisanimvars
        data = context.object.data
        for i in data.keys():
            if i == 'aaa_fs':
                continue
            if (locklist := data.get('locklist')) != None:
                if locklist.get(i) == True: continue
            try:
                prop = data.id_properties_ui(i).as_dict()
            except:
                continue
            min = prop.get('min')
            max = prop.get('max')
            randval = random.random() 
            randval = MAP(randval, 0, 1, min, max) * (1- self.reset) * props.randomstrength
            if props.randomadditive and not self.reset:
                data[i] = data[i] + randval
            else:
                data[i] = randval
            
            if props.keyframe:
                data.keyframe_insert(data_path=f'["{i}"]')
        
        props.activeface.data.update()

        return {'FINISHED'}
    
class HISANIM_OT_KEYEVERY(bpy.types.Operator):
    bl_idname = 'hisanim.keyeverything'
    bl_label = 'Key Every Slider'
    bl_description = 'Add a keyframe to every slider on this frame.'
    bl_options = {'UNDO'}

    def execute(self, context):
        data = bpy.context.object.data
        for i in data.keys():
            try:
                prop = data.id_properties_ui(i).as_dict()
            except:
                continue
            data.keyframe_insert(data_path=f'["{i}"]')
        
        return {'FINISHED'}

classes = [
    faceslider,
    HISANIM_OT_SLIDERESET,
    HISANIM_OT_FIXFACEPOSER,
    HISANIM_OT_SLIDEKEYFRAME,
    HISANIM_OT_RANDOMIZEFACE,
    HISANIM_OT_KEYEVERY
]

def register():
    for i in classes:
        bpy.utils.register_class(i)
    bpy.app.handlers.depsgraph_update_post.append(updatefaces)

def unregister():
    for i in reversed(classes):
        bpy.utils.unregister_class(i)
    bpy.app.handlers.depsgraph_update_post.remove(updatefaces)