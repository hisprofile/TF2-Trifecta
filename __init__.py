bl_info = {
    "name" : "The TF2 Trifecta",
    "description" : "A tool dedicated towards the creation of TF2 Content in Blender",
    "author" : "hisanimations",
    "version" : (2, 7, 0),
    "blender" : (3, 5, 0),
    "location" : "View3d > TF2-Trifecta",
    "support" : "COMMUNITY",
    "category" : "Porting",
    "doc_url": "https://github.com/hisprofile/TF2-Trifecta/blob/main/README.md"
}

import os
from bpy.props import *
from bpy.types import *
from mathutils import *
from bpy.app.handlers import persistent
import importlib, sys
from . import (bonemerge, mercdeployer, icons,
                updater, newuilist, preferences,
                wardrobe, panel, faceposer,
                poselib, loadout)

def register():
    loadout.register()
    faceposer.register()
    wardrobe.register()
    mercdeployer.register()
    icons.register()
    updater.register()
    newuilist.register()
    preferences.register()
    bonemerge.register()
    panel.register()
    poselib.register()


def unregister():
    faceposer.unregister()
    wardrobe.unregister()
    mercdeployer.unregister()
    icons.unregister()
    updater.unregister()
    newuilist.unregister()
    preferences.unregister()
    bonemerge.unregister()
    panel.unregister()
    poselib.unregister()
    loadout.unregister()


if __name__ == '__main__':
    register()