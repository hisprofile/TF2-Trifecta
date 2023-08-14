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
    props.loadout_data.clear()
    #print('updating')
    if props.stage == 'NONE':
        for key in getJson().keys():
            #print(key)
            new = props.loadout_data.add()
            new.name = key

class genericGroup(PropertyGroup):
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
    bl_label = 'Load Loadouts'
    bl_description = 'Load Loadouts'

    def execute(self, context):
        for item in bpy.types.Scene.loadout_temp:
            bpy.ops.hisanim.loadcosmetic(LOAD=item)
        props = bpy.context.scene.hisanimvars
        props.stage = 'NONE'
        update()
        return {'FINISHED'}

classes = [
    genericGroup,
    LOADOUT_OT_select,
    LOADOUT_OT_load
]

def register():
    for i in classes:
        register_class(i)

def unregister():
    for i in classes:
        unregister_class(i)