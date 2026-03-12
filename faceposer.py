import bpy, random, time, pickle
from bpy.app.handlers import persistent
from . import poselib, mercdeployer, loadout
from math import floor, ceil

from bpy.types import Operator
from bpy.props import *
import numpy as np

upperFace = ['BrowInV', 'BrowOutV', 'Frown', 'InnerSquint',
                'OuterSquint', 'ScalpD', 'CloseLid',
                'multi_CloseLid', 'eyes_updown', 'eyes_LR']

midFace = ['NoseV', 'NostrilFlare', 'CheekV', 'CheekH']

lowerFace = ['JawV', 'JawD', 'JawH', 'LipsV', 'LipUpV',
                'LipLoV', 'FoldLipUp', 'FoldLipLo', 'PuckerLipLo',
                'PuckerLipUp', 'PuffLipUp', 'PuffLipLo',
                'Smile', 'multi_Smile', 'Platysmus', 'LipCnrTwst',
                'Dimple', 'TongueV', 'TongueH', 'TongueCurl',
                'TongueD', 'TongueWide', 'TongueNarrow',
                'TongueFunnel']

facesections = [upperFace, midFace, lowerFace]

def MAP(x,a,b,c,d, clamp=None):
    y=(x-a)/(b-a)*(d-c)+c
    
    if clamp:
        return min(max(y, c), d)
    else:
        return y

def get_frame(context):
    return context.scene.frame_float if context.scene.show_subframe else context.scene.frame_current

if bpy.app.version >= (4, 4, 0):
    def has_key(context, obj, slider) -> bool:
        from bpy_extras import anim_utils
        data = obj.data
        if not (anim_data := getattr(data, 'animation_data', None)):
            return False
        action = getattr(anim_data, 'action', None)
        action_slot = getattr(anim_data, 'action_slot', None)
        channelbag = anim_utils.action_get_channelbag_for_slot(action, action_slot)
        
        if not channelbag:
            return False

        curv = channelbag.fcurves.find(f'["{slider}"]')
        if curv == None: return False

        points: bpy.types.FCurveKeyframePoints = curv.keyframe_points
        p_array = np.zeros(len(points)*2, dtype=np.float32)
        points.foreach_get('co', p_array)
        p_array = p_array.reshape((-1, 2))[:, 0]

        return get_frame(context) in p_array
else:
    def has_key(context, obj, slider) -> bool:
        data = obj.data
        if not (anim_data := getattr(data, 'animation_data', None)):
            return False
        if not (action := getattr(anim_data, 'action', None)):
            return False
        
        curv = action.fcurves.find(f'["{slider}"]')

        points: bpy.types.FCurveKeyframePoints = curv.keyframe_points
        p_array = np.zeros(len(points)*2, dtype=np.float32)
        points.foreach_get('co', p_array)
        p_array = p_array.reshape((-1, 2))[:, 0]

        return get_frame(context) in p_array

single_run = False

def protect_single(func):
    global single_run
    def inner(a=None, b=None):
        global single_run
        return_val = func()
        if return_val == False:
            single_run = False
    return inner

last_select = None

@persistent
@protect_single
def updatefaces(scn = None):
    global single_run
    global last_select
    '''
    Everytime an object gets selected, run this. However, if it is not
    recognized as a head, do nothing. If a face is selected,
    cycle through its keys and create sliders from them. Then, use those
    sliders to manipulate the keys.
    '''
    if single_run:
        return True
    single_run = True

    props = bpy.context.scene.hisanimvars
    pose_props = bpy.context.scene.poselibVars
    context = bpy.context
    obj = context.object
    if obj == last_select:
        return False
    last_select = obj

    if not hasattr(context, 'object'): return False

    if obj == None:
        if props.activeface is None:
            props.enable_faceposer = False
        return False
    
    data = obj.data
    if data == None: return False
    
    if data.get('aaa_fs') == None:
        return False
    
    props.enable_faceposer = True
    props.needs_override = True
    
    if data.animation_data != None:
        if data.animation_data.drivers.find('["aaa_fs"]') != None:
            props.enable_faceposer = False

    for i in mercdeployer.mercs:
        if i in data.name:
            props.merc = i
            props.needs_override = False
            break
    else:
        if data.get('merc'):
            props.merc = data['merc']
        else:
            props.merc = ''

    if obj == props.activeface:
        return False
    if pose_props.stage == 'ADD':
        bpy.ops.poselib.cancel()
    if pose_props.stage == 'APPLY':
        bpy.ops.poselib.cancelapply()
    # face poser system 2.0 baybeee
    if (flexcontrollers := data.get('flexcontrollers')) and (flexmap := data.get('flexmap')):
        flexcontrollers: dict = flexcontrollers.to_dict()
        flexmap: dict = flexmap.to_dict()
        sliders = props.sliders
        sliders.clear()

        for flex_ui_name, flex_data in flexcontrollers.items():
            #is stereo
            if flex_data['type'] & 0b01:
                left_prop = flexmap[flex_data['left']]
                right_prop = flexmap[flex_data['right']]

                right_prop_ui_settings = data.id_properties_ui(right_prop).as_dict()

                min = right_prop_ui_settings.get('min')
                max = right_prop_ui_settings.get('max')

                new = sliders.add()
                new.realvalue = False

                new.name = flex_ui_name
                new.display_name = flex_ui_name
                new.split = True
                new.L = left_prop
                new.R = right_prop
                new.mini = min
                new.maxi = max

            else:
                cont_prop = flexmap[flex_data['controller']]
                cont_prop_ui_settings = data.id_properties_ui(cont_prop).as_dict()

                min = cont_prop_ui_settings.get('min')
                max = cont_prop_ui_settings.get('max')

                new = sliders.add()
                new.display_name = flex_data['controller']
                new.name = cont_prop
                new.mini = min
                new.maxi = max

                if abs(max - min)/2 > 1.0:
                    new.realvalue = False

            for sectstr, sect in zip(['UPPER', 'MID', 'LOWER'], facesections):
                if flex_ui_name in sect:
                    new.Type = sectstr
                    break
            # has nway
            if flex_data['type'] & 0b10:
                multi_prop = flexmap[flex_data['nway']]
                multi_prop_ui_settings = data.id_properties_ui(multi_prop).as_dict()

                min = multi_prop_ui_settings.get('min')
                max = multi_prop_ui_settings.get('max')

                new = sliders.add()
                new.display_name = flex_data['nway']
                new.name = multi_prop
                new.mini = min
                new.maxi = max

                for sectstr, sect in zip(['UPPER', 'MID', 'LOWER'], facesections):
                    if flex_data['nway'] in sect:
                        new.Type = sectstr
                        break

    else:
        sliders = props.sliders
        sliders.clear()

        if (flex_controllers_map := data.get('flexcontrollers', None)) == None:
            def filter_func(name: str):
                split = name.split('_')
                if len(split) < 2:
                    return False
                if len(split[0]) != 3:
                    return False
                if split[0].isalpha() and split[0].islower():
                    return True
                return False


            keys = sorted(
                filter(
                    filter_func,
                    data.keys()
                )
            )

            flex_controllers_map = {key[4:]: key for key in keys}
            data['flexcontrollers'] = flex_controllers_map

        key_processing: list[str] = list(flex_controllers_map.keys())

        while key_processing:
            flex = key_processing.pop(0)

            l_case = flex.startswith('left_')
            r_case = flex.startswith('right_')
            if l_case or r_case:
                if l_case:
                    other_flex = flex.replace('left_', 'right_')
                    left_flex = flex
                    right_flex = other_flex
                else:
                    other_flex = flex.replace('right_', 'left_')
                    right_flex = flex
                    left_flex = other_flex

                if not other_flex in key_processing:
                    print('TF2-Trifecta Face Poser: failed to find a pair for', flex)
                    continue

                key_processing.remove(other_flex)
                
                flex_mapped = flex_controllers_map[flex]
                display_name = flex.split('_')[-1]
                flex_ui_settings = data.id_properties_ui(flex_mapped).as_dict()

                min = flex_ui_settings.get('min')
                max = flex_ui_settings.get('max')

                new = sliders.add()
                new.split = True
                new.name = flex_mapped
                new.display_name = display_name
                new.L = flex_controllers_map[left_flex]
                new.R = flex_controllers_map[right_flex]
                new.mini = min
                new.maxi = max
                # never show real value, as we always want to use the stereo slider controls by default
                new.realvalue = False
                
                for sectstr, sect in zip(['UPPER', 'MID', 'LOWER'], facesections):
                    if display_name in sect:
                        new.Type = sectstr
                        break

            else:
                flex_mapped = flex_controllers_map[flex]
                display_name = flex
                flex_ui_settings = data.id_properties_ui(flex_mapped).as_dict()

                min = flex_ui_settings.get('min')
                max = flex_ui_settings.get('max')

                new = sliders.add()
                new.display_name = display_name
                new.name = flex_mapped
                new.mini = min
                new.maxi = max
                new.realvalue = max <= 1.0
                
                for sectstr, sect in zip(['UPPER', 'MID', 'LOWER'], facesections):
                    if display_name in sect:
                        new.Type = sectstr
                        break

    poselib.updateVCol()
    props.activeface = obj
    return False
    #props.lastactiveface = props.activeface # use this to see if a new face has been selected. if the same face has been selected twice, do nothing.
    

class HISANIM_OT_SLIDEKEYFRAME(Operator):
    bl_idname = 'hisanim.keyslider'
    bl_label = 'Keyframe Slider'
    bl_description = 'Keyframe this slider'
    delete: BoolProperty(default=False)
    slider: StringProperty()

    bl_options = {'UNDO'}

    def execute(self, context):
        props = context.scene.hisanimvars
        slider = props.sliders[self.slider]
        if slider.split:
            is_keyed_on_frame = has_key(context, props.activeface, slider.R) and has_key(context, props.activeface, slider.L)
        else:
            is_keyed_on_frame = has_key(context, props.activeface, self.slider)
        data = props.activeface.data
        if slider.split:
            if is_keyed_on_frame:
                data.keyframe_delete(data_path=f'["{slider.R}"]', frame=get_frame(context))
                data.keyframe_delete(data_path=f'["{slider.L}"]', frame=get_frame(context))
            else:
                data.keyframe_insert(data_path=f'["{slider.R}"]', frame=get_frame(context))
                data.keyframe_insert(data_path=f'["{slider.L}"]', frame=get_frame(context))
        else:
            if is_keyed_on_frame:
                data.keyframe_delete(data_path=f'["{slider.name}"]', frame=get_frame(context))
            else:
                data.keyframe_insert(data_path=f'["{slider.name}"]', frame=get_frame(context))

        return {'FINISHED'}
        

class HISANIM_OT_SLIDERESET(Operator):
    bl_idname = 'hisanim.resetslider'
    bl_label = ''
    slider = StringProperty()
    stop: BoolProperty(default = False)

    '''This operator decides what will happen to the sliders once
    the user stops manipulating them. It only deals with keyframing and resetting.
    If the sliders were changed and auto keyframing is enabled, keyframe.
    If one slider was cancelled, then all were cancelled, and reset
    the face to its original position.'''

    def resetsliders(self, sliders, context):
        props = context.scene.hisanimvars
        face = props.activeface
        for i in sliders:
            if i.split:
                face.data[i.R] = i.originalval
                face.data[i.L] = i.originalvalL
            else:
                face.data[i.name] = i.originalval
        face.data.update()

    def modal(self, context, event):
        props = context.scene.hisanimvars
        #face = context.object
        face = props.activeface
        scn = context.scene
        if self.stop:
            return {'FINISHED'}

        if event.value == 'RELEASE':
            self.stop = True
            props.dragging = False # allow sliders to initialize original values again
            props.updating = True

            for i in scn.activesliders:
                if i.split:
                    if (i.originalval == face.data[i.R] or i.originalvalL == face.data[i.L]) and i.value == 0:
                        # if at least one slider was reset back to its original value, then reset all
                        self.resetsliders(scn.activesliders, context)
                        break
                else:
                    if i.originalval == face.data[i.name] and i.value == 0:
                        # if at least one slider was reset back to its original value, then reset all
                        self.resetsliders(scn.activesliders, context)
                        break
            else: # if the previous for loop did not break, then nothing was cancelled/reset. keyframe if auto-keyframing is enabled.
                if context.scene.tool_settings.use_keyframe_insert_auto:
                    for i in scn.activesliders:
                        if i.split:
                            face.data.keyframe_insert(data_path=f'["{i.R}"]', frame=get_frame(context))
                            face.data.keyframe_insert(data_path=f'["{i.L}"]', frame=get_frame(context))
                        else:
                            face.data.keyframe_insert(data_path=f'["{i.name}"]', frame=get_frame(context))

            for i in scn.activesliders:                
                i.value = 0
                i.changed = False

            context.scene.activesliders.clear()
            props.updating = False
            props.callonce = False
        return {'PASS_THROUGH'}
    
    def invoke(self, context, event):
        self.stop = False
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

def slideupdate(self, value):
    scn = bpy.context.scene
    props = bpy.context.scene.hisanimvars
    face = props.activeface
    if props.updating: return None # allow slider values to be reset back to 0 without undergoing any updates
    if props.dragging: # do this every time after once
        #magnitude = max((self.maxi - self.mini) / 2, 1.0)
        magnitude = abs(self.maxi)
        self.changed = True
        if not self.split:
            props.activeface.data[self.name] = min(max(self.originalval + self.value*magnitude, self.mini), self.maxi)
            if not self in scn.activesliders: scn.activesliders.append(self) # add sliders to a list of sliders being changed by the user
        else:
            Rmult = MAP(props.LR, -1, 0.0, 0.0, 1.0, True)
            Lmult = MAP(props.LR, 1.0, 0.0, 0.0, 1.0, True)
            props.activeface.data[self.R] = min(max(self.originalval + (self.value * Rmult * magnitude), self.mini), self.maxi)
            props.activeface.data[self.L] = min(max(self.originalvalL + (self.value * Lmult * magnitude), self.mini), self.maxi)
            if not self in scn.activesliders: scn.activesliders.append(self) # add sliders to a list of sliders being changed by the user
        
        face.data.update() # update the face with the new face values

    else: # do this once
        for slide in props.sliders:
            if not slide.split:
                slide.originalval = face.data[slide.name]
            else:
                slide.originalval = face.data[slide.R]
                slide.originalvalL = face.data[slide.L]
        # define original values to add off of and produce a final result. an original value is the value of a slider before manipulating took place.
        # all must be initialized if one were to move, as the previous method did not work
        props.dragging = True
        if not props.callonce: bpy.ops.hisanim.resetslider('INVOKE_DEFAULT')
        props.callonce = True
    return None

class faceslider(bpy.types.PropertyGroup):

    def set_lock(self, value):
        obj = bpy.context.scene.hisanimvars.activeface
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
        obj = bpy.context.scene.hisanimvars.activeface
        if (locklist := obj.data.get('locklist')) == None:
            obj.data['locklist'] = {}
            locklist = obj.data['locklist']
        if (lockstate := locklist.get(self.L)) == None:
            locklist[self.L] = True
            return None
        locklist[self.L] = 1 - lockstate
        return None
    
    def get_lock(self):
        obj = bpy.context.scene.hisanimvars.activeface
        if (locklist := obj.data.get('locklist')) == None: return False
        locklist = obj.data['locklist']
        if not self.split:
            if (lockstate := locklist.get(self.name)) == None: return False
        else:
            if (lockstate := locklist.get(self.R)) == None: return False
        return lockstate
    
    def get_lockL(self):
        obj = bpy.context.scene.hisanimvars.activeface
        if (locklist := obj.data.get('locklist')) == None: return False
        locklist = obj.data['locklist']
        if (lockstate := locklist.get(self.L)) == None: return False
        return lockstate

    def Use(self, value):
        if not bpy.context.scene.poselibVars.adding: return None
        data = bpy.context.scene.hisanimvars.activeface.data
        if self.split:
            if self.use:
                data[self.R] = self.originalval
                data[self.L] = self.originalvalL
            else:
                data[self.R] = 0.0
                data[self.L] = 0.0
        else:
            if self.use:
                data[self.name] = self.originalval
            else:
                data[self.name] = 0.0
        data.update()


    display_name: StringProperty(name='Display Name', default='')
    name: StringProperty()
    value: FloatProperty(name='', default=0.0, update=slideupdate, min=-1, max=1, options=set(), description='Sliders are additive, and will be reset!')
    split: BoolProperty(name='')
    mini: FloatProperty(options=set())
    maxi: FloatProperty(options=set())
    originalval: FloatProperty(options=set())
    originalvalL: FloatProperty(options=set())
    realvalue: BoolProperty(default=True, options=set())
    R: StringProperty()
    L: StringProperty()
    changed: BoolProperty(default=False, options=set())
    Type: EnumProperty(items=(
        ('NONE', 'None', '', '', 0),
        ('UPPER', 'Upper Face', '', '', 1),
        ('MID', 'Mid Face', '', '', 2),
        ('LOWER', 'Lower Face', '', '', 3)
        ),
        name='type', options=set()
    )
    locked: BoolProperty(name='', default = False, set=set_lock, get=get_lock, options=set())
    lockedL: BoolProperty(default = False, name='', set=set_lockL, get=get_lockL, options=set())
    use: BoolProperty(default=False, update=Use, options=set())

class HISANIM_OT_FIXFACEPOSER(Operator):
    bl_idname = 'hisanim.fixfaceposer'
    bl_label = 'Fix Face Poser'
    bl_description = 'If something seems off, click this'

    @classmethod
    def poll(cls, context):
        return context.scene.hisanimvars.dragging

    def execute(self, context):
        props = context.scene.hisanimvars
        props.dragging = False
        context.scene.activesliders.clear()
        bpy.ops.hisanim.resetslider('INVOKE_DEFAULT', stop=True)
        return {'FINISHED'}

class HISANIM_OT_RANDOMIZEFACE(Operator):
    bl_idname = 'hisanim.randomizeface'
    bl_label = 'Randomize Face'
    bl_description = 'Randomize the values of the facial sliders'
    bl_options = {'UNDO', 'REGISTER'}
    seed: IntProperty(default=0)
    time: IntProperty(default=0)

    def execute(self, context):
        props = context.scene.hisanimvars
        data = props.activeface.data
        for x, i in enumerate(data.keys()):
            if i == 'aaa_fs':
                continue
            if (locklist := data.get('locklist')) != None:
                if locklist.get(i) == True: continue
            if type(data[i]) != float: continue
            prop = data.id_properties_ui(i).as_dict()
            min = prop.get('min')
            max = prop.get('max')
            random.seed(self.time + self.seed + x)
            randval = random.random() 
            randval = MAP(randval, 0, 1, min, max) * props.randomstrength
            if props.randomadditive:
                data[i] = data[i] + randval
            else:
                data[i] = randval
            
            if props.keyframe:
                data.keyframe_insert(data_path=f'["{i}"]', frame = get_frame(context))
        
        props.activeface.data.update()
        return {'FINISHED'}
    
    def invoke(self, context, event):
        self.time = int(time.time())
        self.seed = 0
        self.execute(context) 
        return context.window_manager.invoke_props_popup(self, event)
    
    def draw(self, context):
        layout = self.layout
        layout.row().prop(self, 'time', text='Time')
        layout.row().prop(self, 'seed', text='Seed')

class HISANIM_OT_resetface(Operator):
    bl_idname = 'hisanim.resetface'
    bl_label = 'Reset Face'
    bl_description = 'Reset all sliders to 0.0'
    bl_options = {'UNDO'}

    def execute(self, context):
        props = context.scene.hisanimvars
        data = props.activeface.data
        if data.get('flexmap'):
            flexes = list(data['flexmap'].values())
        elif data.get('flexcontrollers'):
            flexes = list(data['flexcontrollers'].values())

        for flex in flexes:
            if flex == 'aaa_fs':
                continue
            data[flex] = 0.0
            if props.keyframe:
                data.keyframe_insert(data_path=f'["{flex}"]', frame=get_frame(context))
        
        data.update()
        return {'FINISHED'}

class HISANIM_OT_KEYEVERY(Operator):
    bl_idname = 'hisanim.keyeverything'
    bl_label = 'Key Every Slider'
    bl_description = 'Add a keyframe to every slider on this frame'
    bl_options = {'UNDO'}

    def execute(self, context):
        props = context.scene.hisanimvars
        sliders = props.sliders
        data = props.activeface.data
        for i in sliders:
            item = i
            if props.up or props.mid or props.low:
                if item.Type == 'NONE':
                    continue

                if item.Type == 'UPPER':
                    if not props.up:
                        continue
                
                if item.Type == 'MID':
                    if not props.mid:
                        continue

                if item.Type == 'LOWER':
                    if not props.low:
                        continue
            if i.split:
                data.keyframe_insert(data_path=f'["{i.L}"]', frame=get_frame(context))
                data.keyframe_insert(data_path=f'["{i.R}"]', frame=get_frame(context))
                continue
            data.keyframe_insert(data_path=f'["{i.name}"]', frame=get_frame(context))
        
        return {'FINISHED'}
    
class HISANIM_OT_adjust(Operator):
    bl_idname = 'hisanim.adjust'
    bl_label = 'Adjust'
    bl_description = 'Adjust the LR weight by 0.1'
    amount: FloatProperty()

    def execute(self, context):
        props = context.scene.hisanimvars
        val = round(props.LR * 10, 1)
        if val % 1 == 0:
            props.LR = val/10 + self.amount
            return {'FINISHED'}
        if self.amount > 0.0:
            props.LR = ceil(val)/10
        else:
            props.LR = floor(val)/10
        return {'FINISHED'}
    
class HISANIM_OT_optimize(Operator):
    bl_idname = 'hisanim.optimize'
    bl_label = 'Optimize Merc'
    bl_description = 'Optimize scene performance by deleting shape key drivers. Disable facial movements'
    bl_options = {'UNDO'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=390)

    def execute(self, context):
        driv_props = bpy.types.Driver.bl_rna.properties
        var_props = bpy.types.DriverVariable.bl_rna.properties
        targ_props = bpy.types.DriverTarget.bl_rna.properties
        props = context.scene.hisanimvars
        #props = context.scene.hisanimvars

        mod_tally = 0
        for obj in set(context.selected_objects + [props.activeface]):
            data = obj.data
            if data.get('flexcontrollers') == None: continue
            #if data.get('skdata') != None: continue
            if obj.type != 'MESH':
                continue
            shapekey = {}
            skdata: bpy.types.Key = obj.data.shape_keys
            drivers = getattr(skdata.animation_data, 'drivers', None)
            if drivers == None: continue
            drivers_list = []

            for n, key in enumerate(skdata.key_blocks[1:]):
                if (driver := drivers.find(key.path_from_id('value'))) == None: continue
                driver.data_path += 'HA!'

            '''
            for n, key in enumerate(skdata.key_blocks[1:]):
                if (driver := drivers.find(key.path_from_id('value'))) == None: continue
                driv_template = dict()
                driv: bpy.types.Driver = driver.driver
                for prop in driv_props:
                    if prop.is_readonly: continue
                    driv_template[prop.identifier] = getattr(driv, prop.identifier)
                variables = list()

                for var in driv.variables:
                    variable = dict()
                    for prop in var_props:
                        if prop.is_readonly: continue
                        variable[prop.identifier] = getattr(var, prop.identifier)
                    targets = list()
                    for targ in var.targets:
                        target = dict()
                        for prop in targ_props:
                            if prop.is_readonly: continue
                            target[prop.identifier] = getattr(targ, prop.identifier)
                        targets.append(target)
                    variable['targets'] = targets
                    variables.append(variable)
                driv_template['variables'] = variables
                drivers_list.append((key.path_from_id('value'), driv_template))
                drivers.remove(driver)
            skdata['drivers'] = drivers_list
            '''
                    
            if (mod := obj.modifiers.get('wrinkle')) == None:
                mod_tally += 1
                self.report({'WARNING'}, f'Failed to disable wrinkle node group on "{obj.name}"!')
            else:
                mod.show_viewport = False
        if mod_tally > 0:
            pass
            self.report({'WARNING'}, f'{mod_tally} wrinkle node group(s) failed to disable in viewport. Resolve manually. Check INFO')
        return {'FINISHED'}
    
    def draw(self, context):
        self.layout.label(text='Flex controllers will not work at the cost of improved performance. Confirm?')
    
class HISANIM_OT_restore(Operator):
    bl_idname = 'hisanim.restore'
    bl_label = 'Restore Merc'
    bl_description = 'Restores facial features of mercenary. Harms performance'
    bl_options = {'UNDO'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=390)

    def execute(self, context):
        mod_tally = 0
        props = context.scene.hisanimvars
        for obj in set(context.selected_objects + [props.activeface]):
            if obj.type != 'MESH': continue
            D = obj.data
            skdata: bpy.types.Key = D.shape_keys
            drivers: list[bpy.types.FCurve] = getattr(skdata.animation_data, 'drivers', None)
            if drivers == None: continue

            for driv in drivers:
                if driv.data_path.endswith('HA!'):
                    driv.data_path = driv.data_path[:-3]
                    driv.driver.expression = driv.driver.expression

            if (mod := obj.modifiers.get('wrinkle')) == None:
                mod_tally += 1
                self.report({'WARNING'}, f'Failed to enable wrinkle node group on "{obj.name}"!')
            else:
                mod.show_viewport = True

        if mod_tally > 0:
            self.report({'WARNING'}, f'{mod_tally} wrinkle node group(s) failed to disable in viewport. Resolve manually. Check INFO')

        return {'FINISHED'}

    def draw(self, context):
        self.layout.label(text='Face movement will be restored at the cost of slower performance. Confirm?')

class HISANIM_OT_override(Operator):
    bl_idname = 'faceposer.override'
    bl_label = 'Set Pose Library'
    #bl_description = ''

    merc_list: EnumProperty(
        items=(
            ('scout', 'Scout', '', '', 0),
            ('soldier', 'Soldier', '', '', 1),
            ('demo', 'Demo', '', '', 2),
            ('heavy', 'Heavy', '', '', 3),
            ('engineer', 'Engineer', '', '', 4),
            ('medic', 'Medic', '', '', 5),
            ('sniper', 'Sniper', '', '', 6),
            ('spy', 'Spy', '', '', 7),
        ),
        name = 'Mercs',
        default='scout'
    )

    def execute(self, context):
        props = context.scene.hisanimvars
        obj = props.activeface
        obj.data['merc'] = self.merc_list
        props.merc = self.merc_list
        poselib.updateVCol()
        return {'FINISHED'}
    
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)
    
    def draw(self, context):
        self.layout.prop(self, 'merc_list')

classes = [
    #faceslider,
    HISANIM_OT_SLIDERESET,
    HISANIM_OT_FIXFACEPOSER,
    HISANIM_OT_SLIDEKEYFRAME,
    HISANIM_OT_RANDOMIZEFACE,
    HISANIM_OT_resetface,
    HISANIM_OT_KEYEVERY,
    HISANIM_OT_adjust,
    HISANIM_OT_optimize,
    HISANIM_OT_restore,
    HISANIM_OT_override,
]

def register():
    for i in classes:
        bpy.utils.register_class(i)
    bpy.app.handlers.depsgraph_update_post.append(updatefaces)
    bpy.types.Scene.activesliders = [] # used to store all sliders being changed by the user.

def unregister():
    for i in reversed(classes):
        bpy.utils.unregister_class(i)
    bpy.app.handlers.depsgraph_update_post.remove(updatefaces)
    del bpy.types.Scene.activesliders