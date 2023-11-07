import bpy, json, os
from bpy.props import *
from bpy.types import (Operator, PropertyGroup)
from bpy.utils import register_class, unregister_class
from pathlib import Path


def jsonPath() -> str: # Get the .json library on the users machine
    addonPath = Path(__file__)
    addonDir = Path(addonPath).parent.parent
    jsonPath = os.path.join(addonDir, 'loadouts.json')
    return jsonPath


def jsonExists() -> bool: # If a .json pose library exists, return True. Else, return False.
    if os.path.exists(jsonPath()):
        return True
    else:
        return False


def getJson() -> dict: # Return the contents of the .json pose library in the form of a dictionary.
    with open(jsonPath(), 'r') as file:
        return json.loads(file.read())


def initJson() -> None: # Create an empty .json pose library
    jsonData = {
    }
    with open(jsonPath(), 'w+') as file:
        file.write(json.dumps(jsonData))
    return None


def writeJson(data: dict) -> None: # Take the dictionary data as a parameter, and write it in the .json file.
    with open(jsonPath(), 'w+') as file:
        file.write(json.dumps(data))

def update() -> None:
    props = bpy.context.scene.hisanimvars
    if props.stage == 'NONE':
        props.loadout_data.clear()
        for key in getJson().keys():
            new = props.loadout_data.add()
            new.name = key

class funny_funnygroup(PropertyGroup):
    name: StringProperty(default='')

class LOADOUT_OT_select(Operator):
    bl_idname = 'loadout.select'
    bl_label = 'Select'
    bl_description = 'Select this loadout'

    loadout: StringProperty(default='')

    def execute(self, context):
        props = bpy.context.scene.hisanimvars
        props.stage = 'DISPLAY'
        dictData = getJson()[self.loadout]
        props.loadout_data.clear()
        bpy.types.Scene.loadout_temp = []
        for i in dictData:
            new = props.loadout_data.add()
            new.name = i
            bpy.types.Scene.loadout_temp.append(i)

        return {'FINISHED'}
    
class LOADOUT_OT_load(Operator):
    bl_idname = 'loadout.load'
    bl_label = 'Load Loadout'
    bl_description = 'Loads Cosmetics'

    def execute(self, context):
        for item in bpy.types.Scene.loadout_temp:
            bpy.ops.hisanim.loadcosmetic(LOAD=item)
        props = bpy.context.scene.hisanimvars
        props.stage = 'NONE'
        update()
        return {'FINISHED'}
    
class LOADOUT_OT_rename(Operator):
    bl_idname = 'loadout.rename'
    bl_label = 'Rename'
    bl_description = 'Rename the current asset'

    name: StringProperty(default='')

    def execute(self, context):
        if self.name == '':
            self.report({'ERROR'}, "Cancelled: Name can't be blank!")
            return {'CANCELLED'}
        props = bpy.context.scene.hisanimvars
        lastName = props.loadout_data[props.loadout_index].name
        jsonData = getJson()
        if jsonData.get(self.name) != None:
            self.report({'ERROR'}, 'Cancelled: Name already taken!')
            return {'CANCELLED'}
        dictKeys = jsonData.keys()
        dictItems = list(jsonData.items())
        index = list(dictKeys).index(lastName)
        data = dictItems[index][1]
        dictItems.pop(index)
        dictItems.insert(index, (self.name, data))
        jsonData.clear()
        jsonData = {key: value for key, value in dictItems}
        writeJson(jsonData)
        return {'FINISHED'}

    def invoke(self, context, event):
        self.name = ''
        return context.window_manager.invoke_props_dialog(self)
    
    def draw(self, context):
        layout = self.layout
        layout.row().prop(self, 'name', text='Name')

class LOADOUT_OT_move(Operator):
    bl_idname = 'loadout.move'
    bl_label = 'Move'
    bl_description = 'Move this item'

    pos: IntProperty(name='Position')

    @classmethod
    def poll(cls, context):
        return (len(bpy.context.scene.hisanimvars.loadout_data) > 1) * (bpy.context.scene.hisanimvars.stage == 'NONE')

    def execute(self, context):
        props = bpy.context.scene.hisanimvars
        active = props.loadout_index
        if self.pos > 0:
            if active == 0: return {'CANCELLED'}
        else:
            if active == (len(props.loadout_data) - 1): return {'CANCELLED'}
        jsonData = getJson()
        items = list(jsonData.items())
        selected = items[active]
        items.pop(active)
        items.insert(min(max(active - self.pos, 0), len(props.loadout_data)), selected)
        jsonData = {key: value for key, value in items}

        writeJson(jsonData)
        update()
        props.loadout_index = active - self.pos
        return {'FINISHED'}
    
class LOADOUT_OT_remove(Operator):
    bl_idname = 'loadout.remove'
    bl_label = 'Remove'
    bl_description = 'Remove this item'

    @classmethod
    def poll(cls, context):
        return (len(bpy.context.scene.hisanimvars.loadout_data) != 0) * (bpy.context.scene.hisanimvars.stage == 'NONE')

    def invoke(self, context, event):
        if not self.poll(context):
            return {'CANCELLED'}
        context.window_manager.invoke_confirm(self, event)
        return {'FINISHED'}

    def execute(self, context):
        props = bpy.context.scene.hisanimvars
        jsonData = getJson()
        items = list(jsonData.items())
        active = props.loadout_index
        items.pop(active)
        jsonData = {key: value for key, value in items}
        writeJson(jsonData)
        update()
        return {'FINISHED'}

class LOADOUT_OT_refreshJson(Operator):
    bl_idname = 'loadout.refresh'
    bl_label = 'Refresh Pose Library'
    bl_description = 'Click to refresh contents of the pose library'

    def execute(self, context):
        update()
        return {'FINISHED'}

classes = [
    funny_funnygroup,
    LOADOUT_OT_select,
    LOADOUT_OT_load,
    LOADOUT_OT_rename,
    LOADOUT_OT_move,
    LOADOUT_OT_remove,
    LOADOUT_OT_refreshJson
]

def register():
    for i in classes:
        register_class(i)
    
    bpy.types.Scene.loadout_temp = []

    if not jsonExists():
        initJson()

def unregister():
    for i in classes:
        unregister_class(i)