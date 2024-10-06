bl_info = {
    "name" : "The TF2 Trifecta",
    "description" : "A tool dedicated towards the creation of TF2 Content in Blender",
    "author" : "hisanimations",
    "version" : (3, 1, 1),
    "blender" : (3, 5, 0),
    "location" : "View3d > TF2-Trifecta",
    "support" : "COMMUNITY",
    "category" : "Porting",
    "doc_url": "https://github.com/hisprofile/TF2-Trifecta/blob/main/README.md"
}

import os, glob
from bpy.props import *
from bpy.types import *
from mathutils import *
from bpy.app.handlers import persistent
import importlib, sys
from . import (bonemerge, mercdeployer, icons,
                updater, newuilist, preferences,
                wardrobe, panel, faceposer,
                poselib, loadout)
pack_path = os.path.dirname(__file__)
for filename in [*glob.glob('**.py', root_dir=pack_path), *glob.glob('**/*.py', root_dir=pack_path)]:
    #print(filename)
    if filename == os.path.basename(__file__): continue
    module = sys.modules.get("{}.{}".format(__name__,filename[:-3]))
    if module: importlib.reload(module)

def register():
    #loadout.register()
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
    
    mercdeployer.unregister()
    icons.unregister()
    updater.unregister()
    newuilist.unregister()
    preferences.unregister()
    wardrobe.unregister()
    bonemerge.unregister()
    panel.unregister()
    poselib.unregister()
    #loadout.unregister()


if __name__ == '__main__':
    register()