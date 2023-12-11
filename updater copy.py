import bpy, os, shutil, shutil, glob, json, zipfile, threading, time
from pathlib import Path
from . import dload, icons, mercdeployer
from urllib import request
import requests

from bpy.types import Operator, PropertyGroup
from bpy.props import *

global blend_files
global files
#bpy
files = ['scout', 'soldier', 'pyro', 'demo', 'heavy', 'engineer', 'medic', 'sniper', 'spy']
classes = mercdeployer.classes
allclasses = ['allclass', 'allclass2', 'allclass3']

def format_size(size_in_bytes):
    """
    Convert size in bytes to a human-readable format.
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_in_bytes < 1024.0:
            return f"{size_in_bytes:.2f} {unit}"
        size_in_bytes /= 1024.0

class HISANIM_PT_UPDATER(bpy.types.Panel): # the panel for the TF2 Collection Updater
    bl_label = "TF2 Trifecta"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'scene'
    def draw(self, context):
        addon_fp = os.path.abspath(Path(__file__).parent)
        props = bpy.context.scene.trifecta_updateprops
        layout = self.layout
        self.layout.icon
        #layout.label(text='Update Class Cosmetics')
        #layout.row().prop(context.scene, 'my_progress')
        if props.active:
            row = layout.row()
            row.label(text=props.stage)
            row.label(text=str(format_size(props.size)))
            row.progress(text='', type='RING', factor=props.var)
        else:
            layout.row().label(text=props.stage)
        op = layout.row().operator('trifecta.update')
        op.id = '1-Npd2KupzpzmoMvXfl1-KWwPnoADODVj'
        op.filepath = addon_fp
        op.operation = 'ZIP'
        row = layout.row()
        row.alert = True
        row.label(text='Updating assets has been temporarily removed.')
        '''
        for i in files:
            OPER = row.operator('hisanim.clsupdate', text='Update ' + i, icon_value=icons.id(f'tfupdater'))
            OPER.UPDATE = i
            row = layout.row()
        layout.label(text='Update Allclass Cosmetics')
        row = layout.row()
        for i in allclasses:
            OPER = row.operator('hisanim.allclsupdate', text='Update '+ i, icon_value=icons.id('tfupdater'))
            OPER.UPDATE = i
            row = layout.row()
        
        layout.label(text='Note! Allclass will take much longer!')
        row = layout.row()
        layout.label(text='Update/Replace Rigs')  
        row = layout.row()
        row.operator('hisanim.mercupdate', text='Standard Rigs')
        layout.label(text='The default rigs by hisanimations. Supports the Face Poser tool.')
        row = layout.row()
        row.operator('hisanim.hectorisupdate')
        layout.label(text='Face Panel + Phonemes Rigs by Hectoris919')
        row = layout.row()
        row.operator('hisanim.eccentricupdate')
        layout.label(text='Face Panel by Eccentric')
        layout.label(text='Open the console to view progress!')
        '''
        row = layout.row()
        row.operator('hisanim.addonupdate', icon_value=icons.id('tfupdater'))
        layout.row().operator('hisanim.relocatepaths', text='Redefine Library Paths', icon='FILE_REFRESH')
        row = layout.row()
        row.prop(context.scene.hisanimvars, 'savespace')
        layout.row().prop(context.preferences.addons[__package__].preferences, 'quickswitch')

class HISANIM_OT_CLSUPDATE(Operator):
    bl_idname = 'hisanim.clsupdate'
    bl_label = 'Update Class'
    bl_description = 'Press to update class'
    UPDATE: bpy.props.StringProperty(default='')
    def execute(self, context):
        prefs = bpy.context.preferences.addons[__package__].preferences
        #RefreshPaths() # refresh paths, just cause
        switch = False
        if (GET := prefs.hisanim_paths.get(self.UPDATE)) == None:
            self.report({'INFO'}, f'No valid path for {self.UPDATE} found!')
            return {'CANCELLED'}
        PATH = GET.path
        if not os.path.exists(PATH):
            if os.path.exists(Path(PATH).parents[0]):
                switch = True
                DLOADTO = Path(PATH).parents[0]
            else:
                self.report({'INFO'}, f'Entry for {self.UPDATE} exists, but path is not valid!')
                return {'CANCELLED'}
        else:
            DLOADTO = Path(PATH).parents[0]
        if switch == False:
            print(f"Deleting old file from {GET.path}...")
            if os.path.exists(GET.path):
                os.remove(GET.path)
                print('Deleted!')
            else:
                print("Nothing to delete!")
        LINK = f'https://gitlab.com/hisprofile/the-tf2-collection/raw/main/{self.UPDATE}cosmetics.zip'
        print(f'Downloading {self.UPDATE} from Gitlab...')
        dload.save(LINK)
        print(f'{self.UPDATE}.zip downloaded!')
        print('Updating master.json...')
        dload.save('https://gitlab.com/hisprofile/the-tf2-collection/raw/main/master.json', overwrite=True)#, DLOADTO)
        print('Updated!')
        print('Moving to asset library path...')
        shutil.move(str(Path(__file__).parent) + f"/{self.UPDATE}cosmetics.zip", DLOADTO)
        print('Moved!')
        print('Extracting .zip file...')
        zipfile.ZipFile(os.path.join(DLOADTO, f'{self.UPDATE}cosmetics.zip'), 'r').extractall(DLOADTO)
        print('Extracted!')
        print('Removing .zip file...')
        os.remove(os.path.join(DLOADTO, f'{self.UPDATE}cosmetics.zip'))
        print('Removed!')
        print(f'Updating {self.UPDATE} complete!')
        return {'FINISHED'}

class HISANIM_OT_ALLCLSUPDATE(Operator):
    bl_idname = 'hisanim.allclsupdate'
    bl_label = 'Update Class'
    bl_description = 'Press to update class'
    UPDATE: bpy.props.StringProperty(default='')
    def execute(self, context):
        prefs = bpy.context.preferences.addons[__package__].preferences
        switch = False
        if (GET := prefs.hisanim_paths.get(self.UPDATE)) == None:
            self.report({'INFO'}, f'No valid path for {self.UPDATE} found!')
            return {'CANCELLED'}
        PATH = GET.path
        if not os.path.exists(PATH):
            if os.path.exists(Path(PATH).parents[0]):
                switch = True
                DLOADTO = Path(PATH).parents[0]
            else:
                self.report({'INFO'}, f'Entry for {self.UPDATE} exists, but path is not valid!')
                return {'CANCELLED'}
        else:
            DLOADTO = GET.path[:GET.path.rfind('/')+1]
        #print(DLOADTO)
        if switch == False:
            print(f"Deleting old file from {GET.path}...")
            if os.path.exists(GET.path):
                os.remove(GET.path)
                print('Deleted!')
            else:
                print("Nothing to delete!")
        if switch == False:
            print(f"Deleting old file from {GET}...")
            if os.path.exists(GET):
                os.remove(GET)
                print('Deleted!')
            else:
                print("Nothing to delete!")
        LINK = f'https://gitlab.com/hisprofile/the-tf2-collection/raw/main/{self.UPDATE}.zip'
        print(f'Downloading {self.UPDATE} from Gitlab...')
        dload.save(LINK)
        print(f'{self.UPDATE}.zip downloaded!')
        print('Updating master.json...')
        dload.save('https://gitlab.com/hisprofile/the-tf2-collection/raw/main/master.json', overwrite=True)#, DLOADTO)
        print('Updated!')
        print('Moving to asset library path...')
        shutil.move(str(Path(__file__).parent) + f"/{self.UPDATE}.zip", DLOADTO)
        print('Moved!')
        print('Extracting .zip file...')
        zipfile.ZipFile(os.path.join(DLOADTO, f'{self.UPDATE}.zip'), 'r').extractall(DLOADTO)
        print('Extracted!')
        print('Removing .zip file...')
        os.remove(os.path.join(DLOADTO, f'{self.UPDATE}.zip'))
        print('Removed!')
        print(f'Updating {self.UPDATE} complete!')
        return {'FINISHED'}

class HISANIM_OT_MERCUPDATE(Operator):
    bl_idname = 'hisanim.mercupdate'
    bl_label = 'Standard Mercs'
    bl_description = "Download hisanimations' TF2 rigs, the default rigs to use"

    def execute(self, execute):
        prefs = bpy.context.preferences.addons[__package__].preferences
        #DLOADTO = bpy.context.preferences.filepaths.asset_libraries['TF2-V3'].path + "/"
        if (GET := prefs.hisanim_paths.get('rigs')) == None:
            self.report({'INFO'}, 'No entry for rigs!')
            return {'CANCELLED'}
        GET = GET.path
        print('Deleting old .blend files...')
        for i in glob.glob("*.blend", root_dir=GET):
            os.remove(os.path.join(GET, i))
            print(f'Deleted {i}..')
        DLOADTO = GET
        print(f"Downloading hisanimations' rigs...")
        dload.save('https://gitlab.com/hisprofile/the-tf2-collection/raw/main/TF2-V3.zip')
        print('''hisanimations' port downloaded!''')
        print('Moving to asset library path...')
        shutil.move(str(Path(__file__).parent) + f"/TF2-V3.zip", DLOADTO)
        print('Moved!')
        print('Extracting .zip file...')
        zipfile.ZipFile(os.path.join(DLOADTO, 'TF2-V3.zip'), 'r').extractall(DLOADTO)
        print('Extracted!')
        print('Removing .zip flie...')
        os.remove(os.path.join(DLOADTO, 'TF2-V3.zip'))
        print('Removed!')
        print("Downloaded hisanimations' port!")
        return {'FINISHED'}

class HISANIM_OT_HECTORISUPDATE(Operator):
    bl_idname = 'hisanim.hectorisupdate'
    bl_label = 'Face Panel + Phonemes Rigs'
    bl_description = "Download Hectoris919's version of hisanimation's port, complete with a face rig and phonemes"

    def execute(self, execute):
        prefs = bpy.context.preferences.addons[__package__].preferences
        try:
            githubResponse = request.urlopen("https://gitlab.com/hisprofile/the-tf2-collection/raw/main/TF2-HECTORIS.zip")
        except:
            self.report({'ERROR'}, 'Not ready yet!')
            return {'CANCELLED'}
        if (GET := prefs.hisanim_paths.get('rigs')) == None:
            self.report({'INFO'}, 'No entry for rigs!')
            return {'CANCELLED'}
        GET = GET.path
        print('Deleting old .blend files...')
        for i in glob.glob("*.blend", root_dir=GET):
            os.remove(os.path.join(GET, i))
            print(f'Deleted {i}..')
        DLOADTO = GET
        print(f"Downloading Hectoris919's rigs...")
        dload.save('https://gitlab.com/hisprofile/the-tf2-collection/raw/main/TF2-HECTORIS.zip')
        print('''hisanimations' port downloaded!''')
        print('Moving to asset library path...')
        shutil.move(str(Path(__file__).parent) + f"/TF2-HECTORIS.zip", DLOADTO)
        print('Moved!')
        print('Extracting .zip file...')
        zipfile.ZipFile(os.path.join(DLOADTO, 'TF2-HECTORIS.zip'), 'r').extractall(DLOADTO)
        print('Extracted!')
        print('Removing .zip flie...')
        os.remove(os.path.join(DLOADTO, 'TF2-HECTORIS.zip'))
        print('Removed!')
        print("Downloaded Hectoris919's port!")
        return {'FINISHED'}
    
class HISANIM_OT_ECCENTRICUPDATE(Operator):
    bl_idname = 'hisanim.eccentricupdate'
    bl_label = 'Face Panel'
    bl_description = "Download Eccentric's TF2 rigs, used with a face panel"

    def execute(self, execute):
        prefs = bpy.context.preferences.addons[__package__].preferences
        #DLOADTO = bpy.context.preferences.filepaths.asset_libraries['TF2-V3'].path + "/"
        if (GET := prefs.hisanim_paths.get('rigs')) == None:
            self.report({'INFO'}, 'No entry for rigs!')
            return {'CANCELLED'}
        GET = GET.path
        print('Deleting old .blend files...')
        for i in glob.glob("*.blend", root_dir=GET):
            os.remove(os.path.join(GET, i))
            print(f'Deleted {i}..')
        DLOADTO = GET
        print(f"Downloading Eccentric's rigs...")
        dload.save('https://gitlab.com/hisprofile/the-tf2-collection/raw/main/TF2-V3_FACE_RIG.zip')
        print('''Eccentric's version downloaded!''')
        print('Moving to asset library path...')
        shutil.move(str(Path(__file__).parent) + f"/TF2-V3_FACE_RIG.zip", DLOADTO)
        print('Moved!')
        print('Extracting .zip file...')
        zipfile.ZipFile(os.path.join(DLOADTO, 'TF2-V3_FACE_RIG.zip'), 'r').extractall(DLOADTO)
        print('Extracted!')
        print('Removing .zip flie...')
        os.remove(os.path.join(DLOADTO, 'TF2-V3_FACE_RIG.zip'))
        print('Removed!')
        print("Downloaded Eccentric's version!")
        return {'FINISHED'}
    
class HISANIM_OT_ADDONUPDATER(Operator):
    bl_idname = 'hisanim.addonupdate'
    bl_label = 'Update Addon'
    bl_description = "Get the latest version of the addon. Updater made by Herwork and hisanimations"

    def execute(self, context):
        PATH = Path(__file__).parent.parent
        print("Fetching new download URL from GitHub")
        # Getting the new release URL from GitHub REST API
        try:
            githubResponse = request.urlopen("https://api.github.com/repos/hisprofile/TF2-Trifecta/releases")
            request
        except:
            self.report({'ERROR'}, 'Network failure! Unable to download file!')
            return {'CANCELLED'}
        gitData = githubResponse.read()
        # Decoding the urllib contents to JSON format
        encode = githubResponse.info().get_content_charset('utf-8')
        data = json.loads(gitData.decode(encode))
        newRelease = dict(data[0]).get("assets")
        assetsData = dict(newRelease[0])
        addonPath = Path(__file__).parent
        tempPath = os.path.join(Path(__file__).parent.parent, 'TRIFECTATEMP')
        downPath = os.path.join(Path(__file__).parent, 'Newvers.zip')
        if not os.path.exists(tempPath):
            os.mkdir(tempPath)
        
        for file in glob.glob("*", root_dir=addonPath):
            shutil.move(os.path.join(addonPath, file), os.path.join(tempPath, file))
        
        URL = assetsData.get("browser_download_url")
        
        try:
            request.urlretrieve(URL, downPath)
        except:
            self.report({'ERROR'}, 'Network failure! Unable to download file!')
            for file in glob.glob("*", root_dir=tempPath):
                shutil.move(os.path.join(tempPath, file), os.path.join(addonPath, file))
            return {'CANCELLED'}
        if not os.path.exists(downPath):
            self.report({'ERROR'}, 'File downloaded, but not where it should be.. weird..')
            for file in glob.glob("*", root_dir=tempPath):
                shutil.move(os.path.join(tempPath, file), os.path.join(addonPath, file))
            return {'CANCELLED'}
        
        zipfile.ZipFile(downPath).extractall(addonPath)
        moveFrom = os.path.join(addonPath, 'TF2-Trifecta')

        for file in glob.glob("*", root_dir=moveFrom):
            shutil.move(os.path.join(moveFrom, file), os.path.join(addonPath, file))
        
        shutil.rmtree(tempPath)
        os.remove(downPath)
        shutil.rmtree(moveFrom)
        class HISANIM_OT_reloadAddon(Operator):
            bl_idname = 'temp.reloadaddon'
            bl_label = 'Reload Addon'
            bl_description = 'Press to reload the TF2-Trifecta'

            def execute(self, context):
                bpy.ops.preferences.addon_enable(module=__package__)
                bpy.utils.unregister_class(HISANIM_PT_tempPanel)
                bpy.utils.unregister_class(HISANIM_OT_reloadAddon)
                self.report({'INFO'}, 'Addon successfully updated!')
                return {'FINISHED'}
            
        class HISANIM_PT_tempPanel(bpy.types.Panel):
            bl_label = 'Reload Addon'
            bl_parent_id = 'HISANIM_PT_UPDATER'
            bl_space_type = 'PROPERTIES'
            bl_region_type = 'WINDOW'
            bl_context = 'scene'

            def draw(self, context):
                layout = self.layout
                row = layout.row()
                row.operator('temp.reloadaddon')
                row = layout.row()
                row.alert = True
                row.label(icon='ERROR')
                row.label(text='Blender may crash!')
        
        bpy.utils.register_class(HISANIM_OT_reloadAddon)
        bpy.utils.register_class(HISANIM_PT_tempPanel)
        self.report({'INFO'}, 'Addon downloaded! Press "Reload Addon" to apply changes.')
        return {'FINISHED'}

def download_file_from_google_drive(file_id, destination, chunk_size=32768):
    url = "https://docs.google.com/uc?export=download"

    session = requests.Session()
    params = {'id': file_id, 'confirm': 1}
    response = session.get(url, params=params, stream=True)
    #save_response_content(response, destination, chunk_size):

    #for i, chunk_size_ in save_response_content(response, destination, chunk_size):
        #yield i, chunk_size_
    return None

def download_file_from_google_drive_blank():
    try:
        C = bpy.context
        scn = C.scene
        props = scn.trifecta_updateprops
        prefs = C.preferences.addons[__package__].preferences
        props.active = True


        ### Download Properties ###
        url = "https://docs.google.com/uc?export=download"
        file_id = '1-Npd2KupzpzmoMvXfl1-KWwPnoADODVj'
        destination = os.path.join(props.filepath, 'rigs.zip')
        chunk_size=32768
        session = requests.Session()
        params = {'id': file_id, 'confirm': 1}
        response = session.get(url, params=params, stream=True)
        wm = bpy.context.window_manager

        ### Start Download ###
        if response.status_code != 200:
            props.stop = True
            props.fail = response.status_code
            return None
        with open(destination, "wb") as f:
            for i, chunk in enumerate(response.iter_content(chunk_size)):
                    if chunk:  # filter out keep-alive new chunks
                        try:
                            props.size = i*chunk_size
                        except Exception as e:
                            print(e)
                            pass
                        f.write(chunk)
        f.close()
        props.size = os.stat(destination)[6]
        if props.operation == 'ZIP': # ZIP is alias for downloading rig sets
            props.stage = 'Moving...'
            rigs = prefs.rigs[scn.trifectarigs]
            props.file = os.path.join(rigs.path, 'rigs.zip')
            file = destination
            newpath = Path(rigs.path)

            if Path(props.file).exists():
                os.remove(Path(props.file))

            file = shutil.move(destination, newpath)

            props.stage = 'Extracting...'
            zipfile.ZipFile(file).extractall(newpath)

            props.stage = 'Removing...'
            os.remove(file)
        
        if props.operation == 'BLEND':
            prefs.hisanim_paths[props.asset]

        props.finished = True
    except:
        props.stop = True
        raise
    return None

def get_confirm_token(response):
    for key, value in response.cookies.items():
        if key.startswith('download_warning'):
            return value

    return None


def save_response_content(response, destination, chunk_size):
    print('fart')
    with open(destination, "wb") as f:
        for i, chunk in enumerate(response.iter_content(chunk_size)):
            if chunk:  # filter out keep-alive new chunks
                f.write(chunk)
                print(i)
                yield i, chunk_size


'''if __name__ == '__main__':
    file_id = '...'
    destination = '...'
    for i, chunk_size in download_file_from_google_drive(file_id, destination):
        print(i, chunk_size)'''

class updateProps(PropertyGroup):
    id: StringProperty(name='ID')
    active: BoolProperty(default=False)
    file: StringProperty(name='File')
    filepath:StringProperty(name='Filepath', subtype='FILE_PATH')
    newpath: StringProperty(name='New path', subtype='FILE_PATH')
    finished: BoolProperty(default=False)
    stop:BoolProperty(default=False)
    progress: FloatProperty(default=False)
    var: FloatProperty(default=0.0)
    size: FloatProperty(default=0.0)
    fail: IntProperty(default=0)
    operation: EnumProperty(items=(
        ('BLEND', '', '', 0),
        ('ZIP', '', '', 1)
    ), name='Operation')
    stage: StringProperty(default='')
    asset: StringProperty(default='')
    '''stage: EnumProperty(items=(
        ('DOWNLOADING', 'Downlading...', '', '', 0),
        ('MOVING', 'Moving...', '', '', 1),
        ('EXTRACTING', 'Extracting...', '', '', 2),
        ('REMOVING', 'Removing...', '', '', 3)
        ), name='Stage'
    )'''


class TRIFECTA_OT_downloader(Operator):
    bl_idname = 'trifecta.update'
    bl_label = 'Grab File'
    _timer = None
    start = 0
    progress: FloatProperty(default=0.0)
    id: StringProperty(name='ID')
    file: StringProperty(name='File')
    filepath:StringProperty(name='Filepath', subtype='FILE_PATH')
    newpath: StringProperty(name='New path', subtype='FILE_PATH')
    asset: StringProperty(default='')
    operation: EnumProperty(items=(
        ('BLEND', '', '', 0),
        ('ZIP', '', '', 1)
    ), name='Operation')
    def modal(self, context, event):
        props = context.scene.trifecta_updateprops
        prefs = context.preferences.addons[__package__].preferences
        wm = context.window_manager

        if props.stop:
            props.stop = False
            props.active = False
            wm.event_timer_remove(self._timer)
            #self.cancel(context)
            self.report({'WARNING'}, f"Cancelling! Code: {props.fail}")
            return {'CANCELLED'}

        if not props.active:
            thread = threading.Thread(target=download_file_from_google_drive_blank)
            thread.start()
            #bpy.app.timers.register(download_file_from_google_drive_blank)

        if props.finished:
            props.active = False
            props.finished=False
            self.report({'INFO'}, 'Finished downloading!')
            wm.event_timer_remove(self._timer)
            bpy.context.area.tag_redraw()
            return {'FINISHED'}

        #if event.type in {'RIGHTMOUSE', 'ESC'}:
            #self.cancel(context)
            #return {'CANCELLED'}

        if event.type == 'TIMER':
            wm.name = wm.name
            #props.var = (props.var + 0.1) % 1
            bpy.context.area.tag_redraw()
            # change theme color, silly!

        if props.stage == 'Downloading...':
            props.var = round(time.time(), 3) % 1

        if props.stage == 'Moving...':
            print(os.stat(props.newpath)[6], props.newpath)
            if os.stat(props.newpath)[6] == 0:
                props.var = 0.0
            else:
                print(os.stat(props.newpath)[6])
                props.var = props.size/os.stat(props.newpath)[6]

        #if time.time() - self.time > 5:
            #return {'CANCELLED'}

            #context.my_progress 
        #bpy.context.area.tag_redraw()
        return {'PASS_THROUGH'}

    def execute(self, context):
        props = bpy.context.scene.trifecta_updateprops
        props.stage = 'Downloading...'
        props.id = self.id
        props.filepath = self.filepath
        props.operation = self.operation
        props.asset = self.asset
        wm = context.window_manager
        self._timer = wm.event_timer_add(0.1, window=context.window)
        self.time = time.time()
        wm.modal_handler_add(self)
        return {'RUNNING_MODAL'}
    
    def invoke(self, context, event):
        if self.operation == 'ZIP':
            return context.window_manager.invoke_props_dialog(self)
        return self.execute(context)
        #context.window_manager.invoke
    
    def draw(self, context):
        layout = self.layout
        layout.row().label(text='farp')
        layout.prop(context.scene, 'trifectarigs')
        return None

bpyClasses = [HISANIM_PT_UPDATER,
              HISANIM_OT_CLSUPDATE,
              HISANIM_OT_ALLCLSUPDATE,
              HISANIM_OT_MERCUPDATE,
              HISANIM_OT_HECTORISUPDATE,
              HISANIM_OT_ADDONUPDATER, 
              HISANIM_OT_ECCENTRICUPDATE,
              TRIFECTA_OT_downloader,
              updateProps
              ]

def register():
    for operator in bpyClasses:
        bpy.utils.register_class(operator)
    bpy.types.Scene.trifecta_updateprops = PointerProperty(type=updateProps)
    bpy.types.Scene.my_progress = FloatProperty(default=0.0, name='ffff')
def unregister():
    for operator in bpyClasses:
        bpy.utils.unregister_class(operator)
    del bpy.types.Scene.trifecta_updateprops