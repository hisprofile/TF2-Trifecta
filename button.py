import bpy

from . import dload
#import google.auth
#from .google import auth
#from . import auth
#from . import gdown
#from .google_drive_downloader import GoogleDriveDownloader as gdd
#from .pydrive2.auth import GoogleAuth
#from .pydrive2.drive import GoogleDrive
from . import dload
#gauth = GoogleAuth()
#gauth.LocalWebserverAuth()
from . import PATHS
#drive = GoogleDrive(gauth)
class T_PT_BUTTON(bpy.types.Panel):
    bl_label = "TF2 Trifecta Updater"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'scene'
    #bl_category = "Bonemerge"

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.operator('hisanim.button')

class B_OT_BUTTON(bpy.types.Operator):
    bl_idname = 'hisanim.button'
    bl_label = 'button'
    bl_description = 'button'

    def execute(self, context):
        print('hi')
        print(PATHS.FPATHS)
        #gdd.download_file_from_google_drive(file_id='1pnw7Kp4PwA-9IMujJUNwr8l_cW7AODax', dest_path=r'C:/Users/matth\AppData/Roaming/Blender Foundation/Blender/3.3/scripts/addons/TF2-Trifecta')
        #gdown.download('https://drive.google.com/file/d/1pnw7Kp4PwA-9IMujJUNwr8l_cW7AODax/')
        #download_file(real_file_id='1pnw7Kp4PwA-9IMujJUNwr8l_cW7AODax')
        #dload.save('https://bitbucket.org/hisanimations/tf2collection/raw/main/scoutcosmetics.blend')
        print('finished')
        return {'FINISHED'}

def register():
    bpy.utils.register_class(T_PT_BUTTON)
    bpy.utils.register_class(B_OT_BUTTON)
def unregister():
    bpy.utils.unregister_class(T_PT_BUTTON)
    bpy.utils.unregister_class(B_OT_BUTTON)