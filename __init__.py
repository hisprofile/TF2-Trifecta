bl_info = {
    "name" : "The TF2 Trifecta",
    "description" : "A group of three addons: Wardrobe, Merc Deployer, and Bonemerge.",
    "author" : "hisanimations",
    "version" : (2, 1, 3),
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
for filename in [f for f in os.listdir(os.path.dirname(os.path.realpath(__file__))) if f.endswith(".py") ]:
    if filename == os.path.basename(__file__): continue
    module = sys.modules.get("{}.{}".format(__name__,filename[:-3]))
    if module: importlib.reload(module)
# borrowed from BST
from . import (bonemerge, mercdeployer, icons,
                updater, newuilist, preferences,
                wardrobe, panel, faceposer,
                poselib)

def register():
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


if __name__ == '__main__':
    register()