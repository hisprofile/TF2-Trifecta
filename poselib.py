import bpy, json, os
from bpy.props import *
from bpy.types import (Operator, PropertyGroup)
from pathlib import Path
import shutil
#from .faceposer import get_frame
#from . import faceposer
#get_frame = faceposer.get_frame

def get_frame(context):
    return context.scene.frame_float if context.scene.show_subframe else context.scene.frame_current

def jsonPath() -> str: # Get the .json library on the users machine
    addonPath = Path(__file__)
    addonDir = Path(addonPath).parent.parent
    jsonPath = os.path.join(addonDir, 'poselib.json')
    return jsonPath

def defaultJsonPath() -> str:
    addon_path = os.path.dirname(__file__)
    default_json = os.path.join(addon_path, 'poselib_default_data.json')
    return default_json
    

def jsonExists() -> bool: # If a .json pose library exists, return True. Else, return False.
    if os.path.exists(jsonPath()):
        return True
    else:
        return False

latest_json_read = None
trigger_read = True
def getJson() -> dict: # Return the contents of the .json pose library in the form of a dictionary.
    global trigger_read
    global latest_json_read

    if trigger_read:
        with open(jsonPath(), 'r') as file:
            trigger_read = False
            latest_json_read = json.loads(file.read())
            return latest_json_read
    else:
        return latest_json_read


def initJson() -> None: # Create an empty .json pose library
    shutil.copyfile(defaultJsonPath(), jsonPath())
    return None


def writeJson(data: dict) -> None: # Take the dictionary data as a parameter, and write it in the .json file.
    global trigger_read
    trigger_read = True
    with open(jsonPath(), 'w+') as file:
        file.write(json.dumps(data))


def updateVCol() -> None: # Refresh the pose library
    global trigger_read
    trigger_read = True

    C = bpy.context
    scn = C.scene
    props = scn.poselibVars
    Fprops = scn.hisanimvars

    if Fprops.merc == '': return None
    lib = getJson()
    lib = lib[Fprops.merc]

    props.visemesCol.clear()
    for n, vis in enumerate(lib.keys()):
        new = props.visemesCol.add()
        new.name = vis
        new.index = n
    props.activeViseme = max(min(props.activeViseme, len(props.visemesCol) - 1 ), 0)
    return None


def mix(a, b, factor) -> float:
    return a*(1-factor)+b*factor

class visemes(PropertyGroup): # Simple property group to display the names of saved poses
    name: StringProperty(default='')
    index: IntProperty()

class dictVis(PropertyGroup):
    # Property group for all the flex controllers mentioned
    # in a saved posed.
    def noUse(self, value):
        C = bpy.context
        scn = C.scene
        obj = scn.hisanimvars.activeface
        data = obj.data
        props = scn.poselibVars
        if self.use: data[self.path] = mix(self.original, self.value, props.value)
        else: data[self.path] = self.original
        data.update()

    name: StringProperty(default='')
    value: FloatProperty(default=0.0, options=set())
    original: FloatProperty(default=0.0, options=set())
    use: BoolProperty(default=True, update=noUse, options=set())
    path: StringProperty(default='')

class poselibVars(PropertyGroup):
    # Variables for the addon
    def applyVisemes(self = None, value = None) -> None:
        if self == None: self = bpy.context.scene.poselibVars
        C = bpy.context
        scn = C.scene
        Fprops = scn.hisanimvars
        props = scn.poselibVars
        obj = Fprops.activeface
        data = obj.data

        for vis in props.dictVisemes:
            if data.get(vis.path) == None:
                continue

            if vis.name.startswith('!'):
                data[vis.path] = mix(vis.original, 0.0 if self.reset else vis.original, self.value)
                continue

            if not vis.use:
                data[vis.path] = vis.original
                continue

            data[vis.path] = mix(vis.original, vis.value, self.value)
            continue

        data.update()

    '''
    To Woha:
    The Pose Library contains three stages: Selection, Addition, and Application.

    When the Selection stage is active, the pose library will show all saved poses for
    a class. Each pose listed has an arrow button which, when pressed, will set the
    active stage to Application.

    When the Application stage is active, the addon will get the flex controllers contained
    by the selected pose, and iterate through them. Each iteration will be saved under
    the dictVisemes Collection Property (see below) with the attributes given in the
    dictVis class (see above), of which there are four. The flex controller's name to display,
    its saved value in the selected pose, its original value before the Application stage
    became active, and a toggle whether to use it in the final result. A mix slider will
    also be shown, where the user can mix between the original pose and the saved pose.

    When the Addition stage is active, the addon will prompt the user with a list of
    flex controllers to save. Anything checked will be saved. Any slider that does not
    equal 0 will be set to save automatically. Otherwise, the slider will be ignored.
    Once the user has entered a name for the pose, the addon will allow them to save it.
    '''

    visemesCol: CollectionProperty(type=visemes)
    dictVisemes: CollectionProperty(type=dictVis)
    activeViseme: IntProperty(default=0, options=set())
    activeItem: IntProperty(default=0, name='', options=set())
    visemeName: StringProperty(default='')
    stage: EnumProperty(
        items=(
        ('SELECT', 'Selection', '', '', 0),
        ('ADD', 'Add', '', '', 1),
        ('APPLY', 'Application', '', '', 2)
        ),
        name = 'Stages'
    )
    name: StringProperty(default='', name='Name')
    adding: BoolProperty(default=False, options=set())
    value: FloatProperty(default=1.0, name='Mix', min=0.0, max=1.0, update=applyVisemes, options=set())
    keyframe: BoolProperty(default = True, name='Keyframe')
    keyframe_unchanged: BoolProperty(default=False, name='Keyframe Unchanged', description='Keyframe flex controllers that have the same value before and after the application', options=set())
    reset: BoolProperty(default = False, name='Reset All', update=applyVisemes, description='Applies the preset after resetting the face')
    sort: BoolProperty(default=True, name='Sort', options=set())

class POSELIB_OT_refreshJson(Operator):
    bl_idname = 'poselib.refresh'
    bl_label = 'Refresh Pose Library'
    bl_description = 'Click to refresh contents of the pose library'

    def execute(self, context):
        updateVCol()
        return {'FINISHED'}

class POSELIB_OT_cancel(Operator):
    bl_idname = 'poselib.cancel'
    bl_label = 'Cancel'
    bl_description = 'Cancel the current operation'

    bl_options = {'UNDO'}

    def execute(self, context):
        C = context
        scn = C.scene
        Fprops = scn.hisanimvars
        props = scn.poselibVars

        obj = Fprops.activeface
        if obj == None:
            return {'CANCELLED'}
        data = obj.data
        props.stage = 'SELECT'
        props.adding = False
        for slider in Fprops.sliders:
            slider.use = False
            if slider.split:
                data[slider.R] = slider.originalval
                data[slider.L] = slider.originalvalL
            else:
                data[slider.name] = slider.originalval
        data.update()
        return {'FINISHED'}

class POSELIB_OT_cancelApply(Operator):
    bl_idname = 'poselib.cancelapply'
    bl_label = 'Cancel'
    bl_description = 'Cancel application'

    bl_options = {'UNDO'}

    def execute(self, context):
        C = context
        scn = C.scene
        Fprops = scn.hisanimvars
        props = scn.poselibVars

        obj = Fprops.activeface
        if obj == None:
            return {'CANCELLED'}
        
        data = obj.data
        data = Fprops.activeface.data
        if props.stage == 'SELECT': return {'CANCELLED'}
        props.stage = 'SELECT'

        for vis in props.dictVisemes:
            if vis.name.startswith('!'):
                data[vis.path] = vis.original
                continue
            data[vis.path] = vis.original

        props.dictVisemes.clear()
        data.update()
        return {'FINISHED'}

class POSELIB_OT_prepareAdd(Operator):
    bl_idname = 'poselib.prepareadd'
    bl_label = 'Add Pose'
    bl_description = 'Add a new face pose to the pose library'

    @classmethod
    def poll(cls, context):
        Fprops = context.scene.hisanimvars
        return not Fprops.needs_override 

    def execute(self, context):
        C = context
        scn = C.scene

        Fprops = scn.hisanimvars
        props = scn.poselibVars

        obj = Fprops.activeface
        data = obj.data

        props.stage = 'ADD'
        props.adding = False
        Fprops.sliderindex = 0

        for slider in Fprops.sliders:
            slider.use = False
            if slider.split:
                slider.originalval = data[slider.R]
                slider.originalvalL = data[slider.L]
                if data[slider.R] != 0 or data[slider.L] != 0:
                    slider.use = True
                if not slider.use:
                    data[slider.R] = 0.0
                    data[slider.L] = 0.0
            else:
                slider.originalval = data[slider.name]
                if data[slider.name] != 0:
                    slider.use = True
                if not slider.use:
                    data[slider.name] = 0.0
        props.adding = True
        data.update()
        
        return {'FINISHED'}
    
class POSELIB_OT_add(Operator):
    bl_idname = 'poselib.add'
    bl_label = 'Add Pose'
    bl_description = 'Add this pose'

    @classmethod
    def poll(cls, context):
        return context.scene.poselibVars.name != ''
    
    def invoke(self, context, event):
        C = context
        scn = C.scene
        Fprops = scn.hisanimvars
        props = scn.poselibVars
        jsonData = getJson()
        lib = jsonData[Fprops.merc]

        if lib.get(props.name) != None:
            return context.window_manager.invoke_props_dialog(self)
        else:
            return self.execute(context)

    def execute(self, context):
        C = context
        scn = C.scene
        Fprops = scn.hisanimvars
        props = scn.poselibVars

        obj = Fprops.activeface
        data = obj.data
        dictDat = {}

        for slider in filter(lambda a: a.use, Fprops.sliders):
            if slider.split:
                dictDat[slider.R] = round(data[slider.R], 4)
                dictDat[slider.L] = round(data[slider.L], 4)
            else:
                dictDat[slider.name] = round(data[slider.name], 4)


        jsonData = getJson()
        jsonData[Fprops.merc][props.name] = dictDat
        writeJson(jsonData)
        props.name = ''
        updateVCol()
        bpy.ops.poselib.cancel()
        return {'FINISHED'}
    
    def draw(self, context):
        self.layout.row().label(text='Entry exists. Overwrite?')

class POSELIB_OT_rename(Operator):
    bl_idname = 'poselib.rename'
    bl_label = 'Rename'
    bl_description = 'Rename the current asset'

    name: StringProperty(default='')

    def execute(self, context):
        if self.name == '':
            self.report({'ERROR'}, "Cancelled: Name can't be blank!")
            return {'CANCELLED'}
        props = context.scene.poselibVars
        Fprops = context.scene.hisanimvars
        lastName = props.visemesCol[props.activeViseme].name
        jsonData = getJson()
        dictMerc = jsonData.get(Fprops.merc)
        if dictMerc.get(self.name) != None:
            self.report({'ERROR'}, 'Cancelled: Name already taken!')
            return {'CANCELLED'}
        dictKeys = dictMerc.keys()
        dictItems = list(dictMerc.items())
        index = list(dictKeys).index(lastName)
        data = dictItems[index][1]
        dictItems.pop(index)
        dictItems.insert(index, (self.name, data))
        jsonData[Fprops.merc].clear()
        jsonData[Fprops.merc] = {key: value for key, value in dictItems}
        writeJson(jsonData)
        updateVCol()
        return {'FINISHED'}

    def invoke(self, context, event):
        self.name = ''
        return context.window_manager.invoke_props_dialog(self)
    
    def draw(self, context):
        layout = self.layout
        layout.row().prop(self, 'name', text='Name')

class POSELIB_OT_move(Operator):
    bl_idname = 'poselib.move'
    bl_label = 'Move'
    bl_description = 'Move this item'

    pos: IntProperty(name='Position')

    @classmethod
    def poll(cls, context):
        return len(context.scene.poselibVars.visemesCol) != 0

    def execute(self, context):
        props = context.scene.poselibVars
        Fprops = context.scene.hisanimvars
        active = props.activeViseme
        if self.pos > 0:
            if active == 0: return {'CANCELLED'}
        else:
            if active == (len(props.visemesCol) - 1): return {'CANCELLED'}
        jsonData = getJson()
        lib = jsonData[Fprops.merc]
        items = list(lib.items())
        selected = items[active]
        items.pop(active)
        items.insert(min(max(active - self.pos, 0), len(props.visemesCol)), selected)
        jsonData[Fprops.merc] = {key: value for key, value in items}

        writeJson(jsonData)
        updateVCol()
        props.activeViseme = active - self.pos
        return {'FINISHED'}

class POSELIB_OT_remove(Operator):
    bl_idname = 'poselib.remove'
    bl_label = 'Remove'
    bl_description = 'Remove this item'

    @classmethod
    def poll(cls, context):
        if len(context.scene.poselibVars.visemesCol) != 0:
            return True
        else:
            return False

    def invoke(self, context, event):
        #if not self.poll(context):
        #    return {'CANCELLED'}
        return context.window_manager.invoke_confirm(self, event)
        #return {'FINISHED'}

    def execute(self, context):
        props = context.scene.poselibVars
        Fprops = context.scene.hisanimvars
        jsonData = getJson()
        lib = jsonData[Fprops.merc]
        #items = list(lib.items())
        active = props.visemesCol[props.activeViseme].name
        #items.pop(active)
        del lib[active]
        #jsonData[Fprops.merc] = items # {key: value for key, value in items}
        writeJson(jsonData)
        #bpy.app.timers.register(updateVCol, first_interval=0.1)
        updateVCol()
        return {'FINISHED'}

class POSELIB_OT_prepareApply(Operator):
    bl_idname = 'poselib.prepareapply'
    bl_label = 'Apply'
    bl_description = 'Apply this viseme'

    bl_options = {'UNDO'}

    viseme: StringProperty(default='')

    def execute(self, context):
        C = context
        scn = C.scene
        Fprops = scn.hisanimvars
        props = scn.poselibVars

        obj = Fprops.activeface
        data = obj.data
        props.stage = 'APPLY'
        props.dictVisemes.clear()
        props.visemeName = self.viseme

        flexkeys = data.get('flexmap') or data.get('flexcontrollers')
        
        translation = {}

        jsonData = getJson()
        lib = jsonData[Fprops.merc][self.viseme]

        translation = {key[4:]: value for key, value in lib.items()}

        for key, value in flexkeys.items():
            if value == 'aaa_fs': continue
            
            new = props.dictVisemes.add()
            new.name = key
            new.path = value
            new.original = data.get(value)

            if translation.get(key, None) != None:
                new.name = key
                float_value = translation.get(key)
                if data.get(value) != None:
                    ui_settings = data.id_properties_ui(value).as_dict()
                    float_value = min(
                        max(
                            float_value,
                            ui_settings.get('min')
                        ),
                        ui_settings.get('max')
                    )

                new.value = float_value
            else:
                new.name = '!' + key

        poselibVars.applyVisemes(props, 'poop')
        return {'FINISHED'}

class POSELIB_OT_apply(Operator):
    bl_idname = 'poselib.apply'
    bl_label = 'Apply'
    bl_description = 'Apply this pose'

    bl_options = {'UNDO'}

    def execute(self, context):
        C = context
        scn = C.scene
        props = scn.poselibVars
        Fprops = scn.hisanimvars

        obj = Fprops.activeface
        data = obj.data
        props.stage = 'SELECT'

        if props.keyframe:
            for item in props.dictVisemes:
                if item.original == data[item.path] and not props.keyframe_unchanged: continue
                if props.reset and item.name.startswith('!'):
                    data.keyframe_insert(data_path=f'["{item.path}"]', frame=get_frame(context))
                if item.name.startswith('!'): continue
                data.keyframe_insert(data_path=f'["{item.path}"]', frame=get_frame(context))

        props.dictVisemes.clear()
        return {'FINISHED'}
    
def textBox(self, sentence, icon='NONE', line=56):
    layout = self.layout
    sentence = sentence.split(' ')
    mix = sentence[0]
    sentence.pop(0)
    broken = False
    while True:
        add = ' ' + sentence[0]
        if len(mix + add) < line:
            mix += add
            sentence.pop(0)
            if sentence == []:
                layout.row().label(text=mix, icon='NONE' if broken else icon)
                return None

        else:
            layout.row().label(text=mix, icon='NONE' if broken else icon)
            broken = True
            mix = sentence[0]
            sentence.pop(0)
            if sentence == []:
                layout.row().label(text=mix)
                return None

classes = (
    dictVis,
    visemes,
    poselibVars,
    POSELIB_OT_refreshJson,
    POSELIB_OT_cancel,
    POSELIB_OT_prepareAdd,
    POSELIB_OT_add,
    POSELIB_OT_rename,
    POSELIB_OT_move,
    POSELIB_OT_remove,
    POSELIB_OT_cancelApply,
    POSELIB_OT_prepareApply,
    POSELIB_OT_apply,
    )

def register():
    for i in classes:
        bpy.utils.register_class(i)
    if not jsonExists():
        initJson()

    bpy.types.Scene.poselibVars = PointerProperty(type=poselibVars)

def unregister():
    for i in reversed(classes):
        bpy.utils.unregister_class(i)
    del bpy.types.Scene.poselibVars