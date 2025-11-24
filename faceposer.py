import bpy, random, time, pickle
from bpy.app.handlers import persistent
from . import poselib, mercdeployer, loadout
from math import floor, ceil

from bpy.types import Operator
from bpy.props import *

upperFace = ['BrowInV', 'BrowOutV', 'Frown', 'InnerSquint',
                'OuterSquint', 'ScalpD', 'CloseLid',
                'multi_CloseLid']

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
        for point in curv.keyframe_points:
            if get_frame(context) == point.co.x:
                return True
        return False
else:
    def has_key(context, obj, slider) -> bool:
        data = obj.data
        if not (anim_data := getattr(data, 'animation_data', None)):
            return False
        if not (action := getattr(anim_data, 'action', None)):
            return None
        
        curv = action.fcurves.find(f'["{slider}"]')
        if curv == None: return False
        for point in curv.keyframe_points:
            if get_frame(context) == point.co.x:
                return True
        return False

def get_frame(context):
    return context.scene.frame_float if context.scene.show_subframe else context.scene.frame_current

@persistent
def updatefaces(scn = None):
    '''
    Everytime an object gets selected, run this. However, if it is not
    recognized as a head, do nothing. If a face is selected,
    cycle through its keys and create sliders from them. Then, use those
    sliders to manipulate the keys.
    '''
    #loadout.update()
    props = bpy.context.scene.hisanimvars
    props.needs_override = True
    props.enable_faceposer = False
    context = bpy.context
    if not hasattr(context, 'object'): return
    if context.object == None: return
    if context.object.data == None: return
    data = context.object.data
    
    if data.get('aaa_fs') == None:
        return None
    props.enable_faceposer = True
    if data.animation_data != None:
        if data.animation_data.drivers.find('["aaa_fs"]') != None: props.enable_faceposer = False
    if data.get('flexcontrollers') == None:
        data['flexcontrollers'] = {key[4:]: key for key in data.keys() if type(data[key]) == float}

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
    props.activeface = bpy.context.object
    if props.activeface != props.lastactiveface:
        props.sliders.clear()
        k = sorted(data.keys())
        z = list(zip(range(len(k)), k))
        for i in range(len(data.keys())):
            if type(data[z[i][1]]) != float: continue
            newdata = data.id_properties_ui(z[i][1]).as_dict()
            if 'left' in z[i][1]:
                continue
            if type(data[z[i][1]]) == bytes: continue
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
        poselib.updateVCol()
    
    props.lastactiveface = props.activeface # use this to see if a new face has been selected. if the same face has been selected twice, do nothing.
    

class HISANIM_OT_SLIDEKEYFRAME(Operator):
    bl_idname = 'hisanim.keyslider'
    bl_label = 'Keyframe Slider'
    bl_description = 'Keyframe this slider'
    delete: bpy.props.BoolProperty(default=False)
    slider: bpy.props.StringProperty()
    def execute(self, context):
        props = context.scene.hisanimvars
        slider = props.sliders[self.slider]
        is_keyed_on_frame = has_key(context, context.object, self.slider)
        data = bpy.context.object.data
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
    slider = bpy.props.StringProperty()
    stop: bpy.props.BoolProperty(default = False)

    '''This operator decides what will happen to the sliders once
    the user stops manipulating them. It only deals with keyframing and resetting.
    If the sliders were changed and auto keyframing is enabled, keyframe.
    If one slider was cancelled, then all were cancelled, and reset
    the face to its original position.'''

    def resetsliders(self, sliders, context):
        face = context.object
        for i in sliders:
            if i.split:
                face.data[i.R] = i.originalval
                face.data[i.L] = i.originalvalL
            else:
                face.data[i.name] = i.originalval
        face.data.update()

    def modal(self, context, event):
        props = context.scene.hisanimvars
        face = context.object
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
    if props.updating: return None # allow slider values to be reset back to 0 without undergoing any updates
    if props.dragging: # do this every time after once
        self.changed = True
        if not self.split:
            props.activeface.data[self.name] = min(max(self.originalval + self.value, self.mini), self.maxi)
            if not self in scn.activesliders: scn.activesliders.append(self) # add sliders to a list of sliders being changed by the user
        else:
            Rmult = MAP(props.LR, -1, 0.0, 0.0, 1.0, True)
            Lmult = MAP(props.LR, 1.0, 0.0, 0.0, 1.0, True)
            props.activeface.data[self.R] = min(max(self.originalval + (self.value * Rmult), self.mini), self.maxi)
            props.activeface.data[self.L] = min(max(self.originalvalL + (self.value * Lmult), self.mini), self.maxi)
            if not self in scn.activesliders: scn.activesliders.append(self) # add sliders to a list of sliders being changed by the user
        
        bpy.context.object.data.update() # update the face with the new face values

    else: # do this once
        for slide in props.sliders:
            if not slide.split:
                slide.originalval = bpy.context.object.data[slide.name]
            else:
                slide.originalval = bpy.context.object.data[slide.R]
                slide.originalvalL = bpy.context.object.data[slide.L]
        # define original values to add off of and produce a final result. an original value is the value of a slider before manipulating took place.
        # all must be initialized if one were to move, as the previous method did not work
        props.dragging = True
        if not props.callonce: bpy.ops.hisanim.resetslider('INVOKE_DEFAULT')
        props.callonce = True
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

    def Use(self, value):
        if not bpy.context.scene.poselibVars.adding: return None
        data = bpy.context.object.data
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
    use: bpy.props.BoolProperty(default=False, update=Use, options=set())

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
        bpy.context.scene.activesliders.clear()
        bpy.ops.hisanim.resetslider('INVOKE_DEFAULT', stop=True)
        return {'FINISHED'}

class HISANIM_OT_RANDOMIZEFACE(Operator):
    bl_idname = 'hisanim.randomizeface'
    bl_label = 'Randomize Face'
    bl_description = 'Randomize the values of the facial sliders'
    bl_options = {'UNDO', 'REGISTER'}
    seed: bpy.props.IntProperty(default=0)
    time: bpy.props.IntProperty(default=0)

    def execute(self, context):
        props = context.scene.hisanimvars
        data = context.object.data
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
        
        bpy.context.object.data.update()
        return {'FINISHED'}
    
    def invoke(self, context, event):
        self.time = int(time.time())
        self.seed = 0
        self.execute(context) 
        return bpy.context.window_manager.invoke_props_popup(self, event)
    
    def draw(self, context):
        layout = self.layout
        layout.row().prop(self, 'seed', text='Seed')

class HISANIM_OT_resetface(Operator):
    bl_idname = 'hisanim.resetface'
    bl_label = 'Reset Face'
    bl_description = 'Reset all sliders to 0.0'
    bl_options = {'UNDO'}

    def execute(self, context):
        props = context.scene.hisanimvars
        data = context.object.data
        for x, i in enumerate(data.keys()):
            if i == 'aaa_fs' or i == 'skdata':
                continue
            if type(data[i]) != float: continue
            data[i] = 0.0
            if props.keyframe:
                data.keyframe_insert(data_path=f'["{i}"]', frame=get_frame(context))
        
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
        data = context.object.data
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
    amount: bpy.props.FloatProperty()

    def execute(self, context):
        props = bpy.context.scene.hisanimvars
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

        mod_tally = 0
        for obj in bpy.context.selected_objects:
            D = obj.data
            if D.get('skdata') != None: continue
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
        def apply_values(item, data: dict):
            for key, value in sorted(data.items(), key=lambda a: 0 if a[0] == 'id_type' else 1):
                if isinstance(value, (list, dict, tuple, set)): continue
                #input((item, key, value))
                setattr(item, key, value)
        for obj in context.selected_objects:
            if obj.type != 'MESH': continue
            D = obj.data
            skdata: bpy.types.Key = D.shape_keys
            drivers: list[bpy.types.FCurve] = getattr(skdata.animation_data, 'drivers', None)
            if drivers == None: continue

            for driv in drivers:
                if driv.data_path.endswith('HA!'):
                    driv.data_path = driv.data_path[:-3]
                    driv.driver.expression = driv.driver.expression

            '''if (drivers_list := skdata.get('drivers')) == None: continue

            for path, driver in drivers_list:
                if (existing := drivers.find(path)):
                    drivers.remove(existing)
                driver = driver.to_dict()
                #input(driver)
                new_driver: bpy.types.FCurve = drivers.new(path)
                new_driver: bpy.types.Driver = new_driver.driver
                apply_values(new_driver, driver)
                variables = driver['variables']
                for var in variables:
                    new_var = new_driver.variables.new()
                    apply_values(new_var, var)
                    targets = var['targets']
                    for n, targ in enumerate(targets):
                        apply_values(new_var.targets[n], targ)

            del skdata['drivers']'''


            '''if D.get('skdata') == None: continue
            if D.shape_keys == None: continue
            kb = D.shape_keys.key_blocks
            data = pickle.loads(obj.data['skdata'])
            for key in data.keys():
                if (skey := kb.get(key)) == None: continue
                dat = data[key]
                driv = skey.driver_add('value')
                driv.driver.expression = dat['expression']
                for v in dat['variables']:
                    var = driv.driver.variables.new()
                    var.type = 'SINGLE_PROP'
                    var.name = v['name']
                    var.targets[0].id_type = 'MESH'
                    var.targets[0].id = obj.data
                    var.targets[0].data_path = v['data_path']

                    if v.get('arm'):
                        var.targets[0].id_type = 'OBJECT'
                        var.targets[0].id = bpy.data.objects[v['obj']]

            del obj.data['skdata']'''

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
        context.object.data['merc'] = self.merc_list
        props.merc = self.merc_list
        poselib.updateVCol()
        return {'FINISHED'}
    
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)
    
    def draw(self, context):
        self.layout.prop(self, 'merc_list')

class HISANIM_OT_refresh_face(Operator):
    bl_idname = 'faceposer.refresh'
    bl_label = 'Refresh Face Drivers'
    bl_description = 'Use this tool if parts of the face do not work'

    def execute(self, context):
        script = context.object.get('script')
        if script == None and context.object.parent != None:
            script = context.object.parent.get('script')
        if script != None:
            script.as_module()
            if context.preferences.filepaths.use_scripts_auto_execute == False:
                self.report({'WARNING'}, 'Enable "Auto Run Python Scripts" in "Preferences > Save & Load" if you want this process to be automatic!')
        else:
            self.report({'WARNING'}, 'Failed to find face script for face! Try executing manually!')
        
        for driver in context.object.data.shape_keys.animation_data.drivers:
            driver.driver.expression = driver.driver.expression
        return {'FINISHED'}

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
    HISANIM_OT_refresh_face
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