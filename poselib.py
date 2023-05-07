import bpy, json, os
from bpy.props import *
from bpy.types import (Context, Operator, Panel, PropertyGroup)
from pathlib import Path
from . import mercdeployer

def jsonPath() -> str:
    addonPath = Path(__file__)
    addonDir = Path(addonPath).parent.parent
    jsonPath = os.path.join(addonDir, 'poselib.json')
    return jsonPath


def jsonExists() -> bool:
    if os.path.exists(jsonPath()):
        return True
    else:
        return False


def getJson() -> dict:
    with open(jsonPath(), 'r') as file:
        return json.loads(file.read())
    

def initJson() -> None:
    jsonData = {
        'scout' : {},
        'soldier' : {},
        'demo' : {},
        'heavy' : {},
        'engineer' : {},
        'medic' : {},
        'sniper' : {},
        'spy' : {}
    }

    with open(jsonPath(), 'w+') as file:
        file.write(json.dumps(jsonData))
    return None


def writeJson(data: dict) -> None:
    with open(jsonPath(), 'w+') as file:
        file.write(json.dumps(data))


def updateVCol() -> None:
    C = bpy.context
    obj = C.object
    scn = C.scene
    props = scn.poselibVars
    Fprops = scn.hisanimvars
    lib = getJson()
    lib = lib[Fprops.merc]

    props.visemesCol.clear()
    for vis in lib.keys():
        new = props.visemesCol.add()
        new.name = vis
    props.activeViseme = min(props.activeViseme, len(props.visemesCol))
    if len(props.visemesCol) != 0: props.visemeName = props.visemesCol[props.activeViseme].name
    return None


def mix(a, b, factor) -> float:
    return a*(1-factor)+b*factor


class visemes(PropertyGroup):
    
    def updateName(self, value) -> None:
        props = bpy.context.scene.poselibVars
        Fprops = bpy.context.scene.hisanimvars
        lastName = props.visemeName
        newName = self.name

        jsonData = getJson()
        dictData = jsonData[Fprops.merc][lastName]
        del jsonData[Fprops.merc][lastName]
        jsonData[Fprops.merc][newName] = dictData
        writeJson(jsonData)

    name: StringProperty(default='')#, update=updateName)

class dictVis(PropertyGroup):
    name: StringProperty(default='')
    value: FloatProperty(default=0.0)
    original: FloatProperty(default=0.0)
    use: BoolProperty(default=True)

class poselibVars(PropertyGroup):
    def lastName(self, value) -> None:
        self.visemeName = self.visemesCol[self.activeViseme].name

    def applyVisemes(self, value) -> None:
        C = bpy.context
        obj = C.object
        data = obj.data
        scn = C.scene
        Fprops = scn.hisanimvars
        props = scn.poselibVars

        for vis in props.dictVisemes:
            if not vis.use:
                data[vis.name] = vis.original
                continue
            data[vis.name] = mix(vis.original, vis.value, value)
            continue


    visemesCol: CollectionProperty(type=visemes)
    dictVisemes: CollectionProperty(type=dictVis)
    activeViseme: IntProperty(default=0, update=lastName)
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
    adding: BoolProperty(default=False)
    value: FloatProperty(default=1.0, name='Mix', min=0.0, max=1.0)

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

    def execute(self, context):
        C = bpy.context
        obj = C.object
        data = obj.data
        scn = C.scene
        Fprops = scn.hisanimvars
        props = scn.poselibVars
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

    def execute(self, context):
        C = bpy.context
        obj = C.object
        data = obj.data
        scn = C.scene
        Fprops = scn.hisanimvars
        props = scn.poselibVars

        for vis in props.dictVisemes:
            data[vis.name] = vis.original

class POSELIB_OT_prepareAdd(Operator):
    bl_idname = 'poselib.prepareadd'
    bl_label = 'Add Pose'
    bl_description = 'Add a new face pose to the pose library'

    def execute(self, context):
        C = bpy.context
        obj = C.object
        data = obj.data
        scn = C.scene
        Fprops = scn.hisanimvars
        props = scn.poselibVars
        props.stage = 'ADD'
        props.adding = False
        #bpy.types.SpaceView3D.draw_handler_add(SP3Dhandle, (self, context), 'WINDOW', 'POST_PIXEL')

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
        return bpy.context.scene.poselibVars.name != ''
    
    def invoke(self, context, event):
        C = bpy.context
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
        C = bpy.context
        obj = C.object
        data = obj.data
        scn = C.scene
        Fprops = scn.hisanimvars
        props = scn.poselibVars
        dictDat = {}

        for slider in filter(lambda a: a.use, Fprops.sliders):
            if slider.split:
                dictDat[slider.R] = data[slider.R]
                dictDat[slider.L] = data[slider.L]
            else:
                dictDat[slider.name] = data[slider.name]


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
        props = bpy.context.scene.poselibVars
        Fprops = bpy.context.scene.hisanimvars
        lastName = props.visemesCol[props.activeViseme].name
        jsonData = getJson()
        dictMerc = jsonData.get(Fprops.merc)
        if dictMerc.get(self.name) != None:
            self.report({'ERROR'}, 'Cancelled: Name already taken!')
            return {'CANCELLED'}
        dictKeys = dictMerc.keys()
        dictItems = list(dictMerc.items())
        index = list(dictKeys).index(lastName)
        jsonData[Fprops.merc].clear()

        for num, val in enumerate(list(dictItems)):
            print(num, val)
            key, value = val
            if num == index:
                jsonData[Fprops.merc][self.name] = value
            else:
                jsonData[Fprops.merc][key] = value
        writeJson(jsonData)
        updateVCol()
        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)
    
    def draw(self, context):
        layout = self.layout
        layout.row().label(text='Rename:')
        layout.row().prop(self, 'name')

class POSELIB_OT_move(Operator):
    bl_idname = 'poselib.move'
    bl_label = 'Move'
    bl_description = 'Move this item'

    pos: IntProperty(name='Position')

    @classmethod
    def poll(cls, context):
        return len(bpy.context.scene.poselibVars.visemesCol) != 0

    def execute(self, context):
        props = bpy.context.scene.poselibVars
        Fprops = bpy.context.scene.hisanimvars
        active = props.activeViseme
        print(active, len(props.visemesCol))
        if self.pos > 0:
            if active == 0:
                return {'CANCELLED'}
        else:
            if active == (len(props.visemesCol) - 1):
                return {'CANCELLED'}
        jsonData = getJson()
        lib = jsonData[Fprops.merc]
        items = list(lib.items())
        selected = items[active]
        items.pop(active)
        items.insert(min(max(active - self.pos, 0), len(props.visemesCol)), selected)
        print(items)
        jsonData[Fprops.merc] = {key: value for key, value in items}

        writeJson(jsonData)
        updateVCol()
        props.activeViseme = active - self.pos
        return {'FINISHED'}

class POSELIB_OT_remove(Operator):
    bl_idname = 'poselib.remove'
    bl_label = 'Remove'
    bl_description = 'Remove this item'

    def execute(self, context):
        props = bpy.context.scene.poselibVars
        Fprops = bpy.context.scene.hisanimvars
        jsonData = getJson()
        lib = jsonData[Fprops.merc]
        items = list(lib.items())
        active = props.activeViseme
        items.pop(active)
        jsonData[Fprops.merc] = {key: value for key, value in items}
        writeJson(jsonData)
        updateVCol()
        return {'FINISHED'}

class POSELIB_OT_prepareApply(Operator):
    bl_idname = 'poselib.prepareapply'

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
            POSELIB_OT_remove
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