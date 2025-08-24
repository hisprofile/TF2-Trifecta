import bpy, os, shutil, shutil, glob, json, zipfile, threading, time, requests
from pathlib import Path
from . import icons, mercdeployer
from .preferences import ids, rigs_ids
from .panel import TRIFECTA_OT_genericText, textBox
from . import bl_info
from urllib import request
from math import sin
from bpy.types import Context, Operator, PropertyGroup
from bpy.props import *
from datetime import datetime
import uuid
import requests
import ast

global blend_files
global files
#bpy

area = None
Queue = list()
current_iter = None

mercs = [
    'scout_cosmetics',   
    'soldier_cosmetics', 
    'pyro_cosmetics',    
    'demo_cosmetics' ,   
    'heavy_cosmetics',   
    'engineer_cosmetics',
    'medic_cosmetics',   
    'sniper_cosmetics',  
    'spy_cosmetics',     
]

all_class = [
    'allclass1',
    'allclass2',
    'allclass3',
    'allclass4',
]

weapons = [
    'weapons1',
    'weapons2',
    'weapons3',
]

misc = [
    'taunts_items',
    '_resources'
]

runonce = True

release_notes = dict()
new_version = False
online_vers = None

#assets = mercs + all_class + weapons + misc
assets = set(map(lambda a: a+'.blend', ids.keys()))

textchars = bytearray({7,8,9,10,12,13,27} | set(range(0x20, 0x100)) - {0x7f})
is_binary_string = lambda bytes: bool(bytes.translate(None, textchars))

class SmallDownload(Exception):
    "Download too small, assuming download failed!"

    def __init__(self, message="Download too small, assuming download failed!"):
        self.message = message
        super().__init__(self.message)
    pass

class InvalidResponse(Exception):
    "Response code was not 200! Failed!"

    def __init__(self, message="Response code was not 200! Failed!"):
        self.message = message
        super().__init__(self.message)
    pass

class InvalidDownload(Exception):
    "Download was not .blend/.zip. Failed!"

    def __init__(self, message="Download was not .blend/.zip. Failed!"):
        self.message = message
        super().__init__(self.message)
    pass

class UserCancelled(Exception):
    "User cancelled task!"

    def __init__(self, message="User cancelled task!"):
        self.message = message
        super().__init__(self.message)
    pass

def MAP(x,a,b,c,d, clamp=None):
    y=(x-a)/(b-a)*(d-c)+c
    
    if clamp:
        return min(max(y, c), d)
    else:
        return y

def get_day_factor():
    now = datetime.now()
    midnight = now.replace(hour=0, minute=0, second=0, microsecond=0)
    seconds_in_a_day = 24 * 60 * 60  # 24 hours * 60 minutes * 60 seconds
    elapsed_seconds = (now - midnight).total_seconds()
    day_factor = elapsed_seconds / seconds_in_a_day
    return day_factor

def format_size(size_in_bytes):
    """
    Convert size in bytes to a human-readable format.
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_in_bytes < 1024.0:
            return f"{size_in_bytes:.2f} {unit}"
        size_in_bytes /= 1024.0

def getRigs(self, context):
    prefs = context.preferences.addons[__package__].preferences
    rig_list = list()
    for n, data in enumerate(rigs_ids.items()):
        key, value = data
        rig_list.append((value[0], key, value[1], '', n))
    return rig_list

class HISANIM_PT_UPDATER(bpy.types.Panel): # the panel for the TF2 Collection Updater
    bl_label = "TF2 Trifecta"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'scene'
    def draw(self, context):
        version = bpy.app.version
        prefs = context.preferences.addons[__package__].preferences
        addon_fp = os.path.abspath(Path(__file__).parent)
        props = bpy.context.scene.trifecta_updateprops
        layout = self.layout
        if props.running:
            row = layout.row(align=True)
            row.alignment = 'LEFT'
            row.label(text=props.stage)
            row.label(text=f'{format_size(props.size)}/{format_size(props.download_size)}')
            data = current_iter[1]
            task = current_iter[0]
            file_name = data[0]
            tasks = Queue[1]
            row.label(text=f'{file_name}, {task+1}/{tasks}')
            if version >= (4, 0, 0):
                row.progress(text='', type='RING', factor=props.progress)
            else:
                row.label(text='.'*int(((time.time()*3)%3) + 1))
        else:
            layout.row().operator('wm.url_open', text='Installation Documentation', icon='URL').url = 'https://github.com/hisprofile/blenderstuff/blob/main/Guides/TF2%20Blender/!TF2-Trifecta%20Installation.md'
            layout.row().operator('wm.url_open', text='TF2 Items Folder', icon='URL').url = 'https://drive.google.com/open?id=1JFzUvfiiBF8ukpL50ewZDct98E96oNmL&usp=drive_fs'
            layout.row().operator('wm.url_open', text='Rigs', icon='URL').url = 'https://drive.google.com/open?id=1DF6S3lmqA8xtIMflWhzV242OrUnP62ws&usp=drive_fs'
        box = layout.box()
        box.label(text='Update Class Cosmetics')
        id_items = ids.items()
        col = box.column()
        for item in mercs:
            op = col.row().operator('trifecta.get_blend', text=f'Download {item.title()}', icon_value=icons.id('tfupdater'))
            op.text = f'''Blender will momentarily pause after downloading the file to validate it.
Downloading {item}.blend. Continue?'''
            op.size = '56,56'
            op.icons = 'ERROR,QUESTION'
            op.width = 350
            op.item_name = item
            op.item_id = ids[item]

        box = layout.box()
        box.label(text='Update Allclass Cosmetics')
        col = box.column()
        for item in all_class:
            op = col.row().operator('trifecta.get_blend', text=f'Download {item.title()}', icon_value=icons.id('tfupdater'))
            op.text = f'''Blender will momentarily pause after downloading the file to validate it.
Downloading {item}.blend. Continue?'''
            op.size = '56,56'
            op.icons = 'ERROR,QUESTION'
            op.width = 350
            op.item_name = item
            op.item_id = ids[item]

        box = layout.box()
        box.label(text='Update Weapons')
        col = box.column()
        for item in weapons:
            op = col.row().operator('trifecta.get_blend', text=f'Download {item.title()}', icon_value=icons.id('tfupdater'))
            op.text = f'''Blender will momentarily pause after downloading the file to validate it.
Downloading {item}.blend. Continue?'''
            op.size = '56,56'
            op.icons = 'ERROR,QUESTION'
            op.width = 350
            op.item_name = item
            op.item_id = ids[item]

        box = layout.box()
        box.label(text='Update Misc.')
        col = box.column()
        for item in misc:
            op = col.row().operator('trifecta.get_blend', text=f'Download {item.title()}', icon_value=icons.id('tfupdater'))
            op.text = f'''Blender will momentarily pause after downloading the file to validate it.
Downloading {item}.blend. Continue?'''
            op.size = '56,56'
            op.icons = 'ERROR,QUESTION'
            op.width = 350
            op.item_name = item
            op.item_id = ids[item]

        extra_assets = set(map(lambda a: a.name, prefs.blends)) - assets
        extra_assets = filter(lambda a: bool(a[1]), map(lambda a: (a, getattr(prefs.blends.get(a), 'drive_id', None)), extra_assets))
        extra_assets = list(extra_assets)

        if extra_assets != []:
            box = layout.box()
            box.label(text='Update Extra')
            col = box.column()
            for name, drive_id in extra_assets:
                name: str
                op = col.row().operator('trifecta.get_blend', text=f'Download {name.title()}', icon_value=icons.id('tfupdater'))
                op.text = f'''Blender will momentarily pause after downloading the file to validate it.
    Downloading {name}. Continue?'''
                op.size = '56,56'
                op.icons = 'ERROR,QUESTION'
                op.width = 350
                op.item_name = name.rsplit('.blend', maxsplit=1)[0]
                op.item_id = drive_id

        box = layout.box()
        box.label(text='Download Rigs')
        op = box.row().operator('trifecta.get_rig', text='Download Rigs', icon_value=icons.id('tfupdater'))
        op.text = '''hisanimations', Eccentric's, and ThatLazyArtist's rigs all differ based on how the face is posed. Only hisanimations' and TLA's rigs support facial cosmetics.
hisanimations' rigs have faces that can be posed through the Face Poser tool, and have a control scheme similar to that of SFM/Garry's Mod. Therefore, it is recommended to people who have used said control scheme.
Eccentric's rigs have control points overlayed on the face, resembling a control scheme akin to the industrial standard.
ThatLazyArtist's rigs have a panel above the head with sliders to pose the face.
The MvM Robots rigs are complete with Rigify and FK rigs.
The Ragdoll rigs are what they say they are. They come with a tool panel in the Items tab to help users use them. Legacy rigs should be bonemerged onto these rigs.'''
        op.size='56,58,56,56,56,56'
        op.icons='BLANK1,BLANK1,BLANK1,BLANK1,BLANK1,BLANK1'
        op.width = 350

        box = layout.box()
        box.label(text='Install TF2 Items')
        op = box.row().operator('trifecta.download_all', text='Install TF2 Items', icon_value=icons.id('tfupdater'))
        op.text = '''It's possible the download will fail due to not having a consistent way of downloading from Google Drive. Open the link to the folder to download the files if this doesn't work.
The TF2-Trifecta will validate the files once the download is complete. Open the console if you wish to view progress.
It's recommended to not do anything intensive while the TF2-Trifecta is downloading the files.'''
        op.size='56,56,56'
        op.icons='ERROR,CONSOLE,ERROR'
        op.width=350
        box.row().label(text='Path should be empty if downloading for the first time.')
        row = box.row()
        row.alignment = 'EXPAND'
        row.label(text='TF2 Items Path:')
        row.prop(prefs, 'items_path', text='')

        row = layout.row()
        box = layout.box()
        box.label(text='Update Addon')
        if new_version:
            if tuple(release_notes['version']) == online_vers:
                box.label(text=f'New version: {".".join(map(str, release_notes["version"]))}')
                text = release_notes['text'].split('\n')
                col = box.column()
                for sentence, icon, size in zip(text, ['REC']*len(text), [60]*len(text)):
                    textBox(col, sentence, icon, size)
            else:
                box.label(text=f'New version: {".".join(map(str, online_vers))}')
                box.label(text=f'Read the release notes here:')
                bbox = box.box()
                bbox.operator('wm.url_open', text='GitHub Releases').url = 'https://github.com/hisprofile/TF2-Trifecta/releases'

        box.operator('hisanim.addonupdate', icon_value=icons.id('tfupdater'))
        layout.row().operator('hisanim.relocatepaths', text='Redefine Library Paths', icon='FILE_REFRESH')
        row = layout.row()

#def startup():
#    global runonce
#    if runonce == False:
#        return None
#    runonce = False
#    bpy.ops.hisanim.check_update('EXEC_DEFAULT')
#    bpy.ops.hisanim.startup_msg('EXEC_DEFAULT')
#    bpy.app.timers.unregister(startup)
#    return None

#def notify_update():
#    bpy.ops.hisanim.notify_user('INVOKE_DEFAULT')
#    bpy.app.timers.unregister(notify_update)
#    return None

#class HISANIM_OT_notify_user(Operator):
#    bl_idname = 'hisanim.notify_user'
#    bl_label = 'Notify User'
#    _timer = None
#
#    def modal(self, context, event):
#        if event.type == 'TIMER':
#            self.report({'INFO'}, 'New TF2-Trifecta update available! Scene Properties > TF2-Trifecta')
#            return {'FINISHED'}
#        return {'RUNNING_MODAL'}
#    
#    def execute(self, context):
#        wm = context.window_manager
#        self._timer = wm.event_timer_add(0.1, window=context.window)
#        wm.modal_handler_add(self)
#        return {'RUNNING_MODAL'}
        

#class HISANIM_OT_check_update(Operator):
#    bl_idname = 'hisanim.check_update'
#    bl_label = 'Check for Update'
#    _timer = None
#
#    def cancel(self, context: Context):
#    
#    def execute(self, context):
#        global release_notes
#        global new_version
#        global online_vers
#
#        prefs = context.preferences.addons[__package__].preferences
#        if not prefs.update_notice: return {'CANCELLED'}
#        try:
#            data = requests.get('https://api.github.com/repos/hisprofile/TF2-Trifecta/releases')
#            release_notes = requests.get('https://raw.githubusercontent.com/hisprofile/blenderstuff/refs/heads/main/online/release_notes.json')
#        except:
#            return {'CANCELLED'}
#        data = data.content.decode()
#        release_notes = release_notes.content.decode()
#
#        try:
#            data_json = json.loads(data)
#            notes_json = ast.literal_eval(release_notes)
#        except Exception as e:
#            print(e)
#            return {'CANCELLED'}
#        if not isinstance(data_json, list):
#            return {'CANCELLED'}
#        if not isinstance(notes_json, dict):
#            return {'CANCELLED'}
#        release_notes = dict(notes_json)
#
#        online_vers = data_json[0]['tag_name']
#        online_vers = online_vers.strip('v')
#        online_vers = tuple(map(int, online_vers.split('.')))
#        #release_notes['version'] = online_vers
#        vers = bl_info['version']
#        if online_vers > vers:# and (tuple(notes_json['version']) == online_vers):
#            new_version = True
#            bpy.app.timers.register(notify_update, first_interval=2)
#        return {'FINISHED'}
        


#class HISANIM_OT_PROMPT(TRIFECTA_OT_genericText):
#    bl_idname = 'hisanim.prompt'
#    bl_label = 'TF2-Trifecta Message Notice'
#
#    def draw_extra(self, context):
#        prefs = context.preferences.addons[__package__].preferences
#        layout = self.layout
#        layout.prop(prefs, 'hide_update_msg', text='Hide Future Prompts')

#class HISANIM_OT_STARTUP_UPDATE(Operator):
#    bl_idname = 'hisanim.startup_msg'
#    bl_label = 'Startup Update'
#
#    def execute(self, context):
#        prefs = context.preferences.addons[__package__].preferences
#        if prefs.hide_update_msg: return {'CANCELLED'}
#        PATH = Path(__file__).parent
#        update_msg = os.path.join(PATH, 'update_msg.json')
#        try:
#            data = requests.get('https://raw.githubusercontent.com/hisprofile/blenderstuff/refs/heads/main/online/trifecta_update_message.json')
#        except:
#            return {'CANCELLED'}
#        
#        data = data.content.decode()
#
#        try:
#            data_json = ast.literal_eval(data)
#        except:
#            return {'CANCELLED'}
#        
#        if not isinstance(data_json, dict):
#            return {'CANCELLED'}
#        
#        if not os.path.exists(update_msg):
#            with open(update_msg, 'w+') as file:
#                file.write(json.dumps(data_json))
#            return {'FINISHED'}
#        else:
#            with open(update_msg, 'r') as file:
#                data_json_exists = json.loads(file.read())
#        
#        new_id = data_json.get('id', -1)
#        old_id = data_json_exists.get('id', -1)
#
#        if new_id == old_id: return {'CANCELLED'}
#
#        with open(update_msg, 'w+') as file:
#            file.write(json.dumps(data_json))
#
#        text = data_json.get('text')
#        icons = data_json.get('icons')
#        size = data_json.get('size')
#
#        if not text:
#            return {'CANCELLED'}
#
#        text_lines = text.split('\n')
#        if icons == None:
#            icons = ','.join(['NONE']*len(text_lines))
#        else:
#            icons_split = icons.split(',')
#        
#            if len(icons_split) != len(text_lines):
#                fill = len(text_lines) - len(icons_split)
#                icons += ',' + ','.join(['BLANK1']*fill)
#
#        if size == None:
#            size = ','.join(['56']*len(text_lines))
#        else:
#            size_split = size.split(',')
#        
#            if len(size_split) != len(text_lines):
#                fill = len(text_lines) - len(size_split)
#                size += ',' + ','.join(['56']*fill)
#        
#        bpy.ops.hisanim.prompt('INVOKE_DEFAULT', text=text, icons=icons, size=size)
#        return {'FINISHED'}

class HISANIM_OT_ADDONUPDATER(Operator):
    bl_idname = 'hisanim.addonupdate'
    bl_label = 'Update Addon'
    bl_description = "Get the latest version of the addon. Updater made by Herwork and hisanimations"

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)

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
                row.label(text='Blender may crash! Be sure to restart Blender!')
        
        bpy.utils.register_class(HISANIM_OT_reloadAddon)
        bpy.utils.register_class(HISANIM_PT_tempPanel)
        self.report({'INFO'}, 'Addon downloaded! Press "Reload Addon" to apply changes.')
        return {'FINISHED'}

class updateProps(PropertyGroup):
    id: StringProperty(name='ID')
    active: BoolProperty(default=False)
    file: StringProperty(name='File')
    filepath:StringProperty(name='Filepath', subtype='DIR_PATH')
    newpath: StringProperty(name='New path', subtype='DIR_PATH')
    finished: BoolProperty(default=False)
    stop:BoolProperty(default=False)
    fstop: BoolProperty(default=False)
    progress: FloatProperty(default=0.0)
    var: FloatProperty(default=0.0)
    size: FloatProperty(default=0.0)
    fail: IntProperty(default=0)
    operation: EnumProperty(items=(
        ('BLEND', 'Blend', '', '', 0),
        ('ZIP', 'Zip', '', '', 1)
    ), name='Operation')
    stage: StringProperty(default='')
    asset: StringProperty(default='')
    running: BoolProperty(default=False)
    error: StringProperty(default='')
    updateAll: BoolProperty(default=False)
    updateAllRig: BoolProperty(default=False)
    download_size: IntProperty(default=0)

    ### Rig download properties ###

    newRigEntry: BoolProperty(default=False, name='Create New Rig-Set')
    newRigName: StringProperty(default='Rigs', name='Rig-Set Name')
    newRigPath: StringProperty(default='', subtype='DIR_PATH', name='Rig-Set Path')
    tf2ColPath: StringProperty(default='', subtype='DIR_PATH', name='TF2 Collection Path')
    tf2ColRig: BoolProperty(default=False, name='Include Rigs')
    iter: IntProperty(default=0, max=13)

def download_file_from_google_drive_blank(context, operator: Operator):
    try:
        #C = bpy.context
        C = context # safer to use context from operator
        scn = C.scene
        props = scn.trifecta_updateprops
        prefs = C.preferences.addons[__package__].preferences
        props.active = True
        props.size = 0.0
        props.progress = 0.0
        props.download_size = 0
        bak = ''
        time.sleep(0.5)

        current_task = current_iter[1]
        file_name = current_task[0]
        blend_name = file_name+'.blend'
        file_id = current_task[1]
        operation = current_task[2]

        ### Download Properties ###
        #url = "https://docs.google.com/uc?export=download"
        url = 'https://drive.usercontent.google.com/download?'
        #https://drive.usercontent.google.com/download?id=1cAP7NY1x_IHVQQtnWwjFNstQKjXp-Qlu?confirm=t&uuid=a908a383-e795-4d21-974d-73c8e49a2d6f
        chunk_size=32768
        session = requests.Session()
        #params = {'id': file_id, 'confirm': 't', 'authuser': 0}
        params = {'id': file_id, 'confirm': 't', 'uuid': str(uuid.uuid4())}
        response = session.get(url, params=params, stream=True)
        #print(response.headers.get('Content-Length', 1))
        props.download_size = int(response.headers.get('Content-Length', 1))
        #raise SmallDownload

        ##d = response

        wm = bpy.context.window_manager

        # Start Download ###
        if response.status_code != 200:
            props.stop = True
            props.fail = response.status_code
            raise InvalidResponse
        
        if operation == 'ZIP':
            rigs = prefs.rigs[scn.hisanimvars.rigs]
            destination = os.path.join(rigs.path, 'rigs.zip')
            folder = rigs.path
            
            rigs_backup = os.path.join(folder, 'bak')
            os.makedirs(rigs_backup)
            for file in glob.glob('*.blend', root_dir=folder):#os.listdir(folder):
                shutil.move(os.path.join(folder, file), os.path.join(folder, 'bak', file))

        if operation == 'BLEND':
            folder = prefs.items_path
            destination = os.path.join(folder, blend_name)
            if os.path.exists(destination):
                bak = shutil.move(destination, os.path.join(folder, 'bak.blend'))        

        with open(destination, "wb") as file:
            for i, chunk in enumerate(response.iter_content(chunk_size)):
                    if props.fstop:
                        raise UserCancelled
                    if chunk:  # filter out keep-alive new chunks
                        try:
                            props.size = i*chunk_size
                            props.progress = props.size/props.download_size
                        except Exception as e:
                            print(e)
                            pass
                        file.write(chunk)
        file.close()

        open_file = open(destination, 'rb')
        if is_binary_string(open_file.read(1024)):
            open_file.close()
            pass
        else:
            open_file.close()
            operator.report({'ERROR'}, f'Got an .html file instead of desired result!')
            operator.report({'INFO'}, 'This usually occurs when Google would rather you download the file through their website, or if the quota for the wanted file is full. In either case, open the link to the items folder on Drive and try getting it there.')
            raise InvalidDownload

        filesize = os.stat(destination)[6]

        '''
        If the file size is less than 2mb, then it's probably gone to waste. Obviously the best thing to do would be to verify via
        checksum, but I don't really have a way to implement that in way that's constantly up to date with the files.
        '''

        props.size = filesize

        if operation == 'ZIP': # ZIP is alias for downloading rig sets
            props.stage = 'Extracting...'

            with zipfile.ZipFile(destination, 'r') as zip:
                info = zip.infolist()
                obj_count = len(info)
                for n, file_info in enumerate(info):
                    props.progress = obj_count / (n + 1)
                    #if bpy.context.screen != None:
                    #    for area in bpy.context.screen.areas:
                    #        if area.type == 'PROPERTIES':
                    #            area.tag_redraw()
                    file_path = os.path.join(folder, file_info.filename)
                    zip.extract(file_info, folder)

            props.stage = 'Removing...'
            #props.var = 1.0
            os.remove(destination)

            shutil.rmtree(rigs_backup)
        
        if operation == 'BLEND':
            if (blend_entry := prefs.blends.get(blend_name)) == None:
                new_blend = prefs.blends.add()
                new_blend.name = blend_name
                new_blend.validated = False
                new_blend.path = destination
            else:
                blend_entry.validated = False
            if bak != '':
                os.remove(bak)

    except Exception as E:
        props.stop = True
        props.error = str(E)

        if operation == 'ZIP':# and Path(destination).exists():
            if os.path.exists(destination):
                os.remove(destination)
            for file in os.listdir(rigs_backup):
                shutil.move(os.path.join(rigs_backup, file), os.path.join(folder, file))
            shutil.rmtree(rigs_backup)
            pass

        if operation == 'BLEND':
            if os.path.exists(destination):
                os.remove(destination)
            if bak != '': shutil.move(bak, destination)
    props.active = False
    return None

class TRIFECTA_OT_DOWNLOAD_QUEUE(Operator):
    bl_idname = 'trifecta.download_queue'
    bl_label = 'Download Queue'
    bl_description = 'Go through a queue of items to download'

    _timer = None
    _time = None
    _count = None
    _wait_validated = None
    _start_at = 0

    @classmethod
    def poll(cls, context):
        props = context.scene.trifecta_updateprops
        return not props.running

    def modal(self, context, event):
        global current_iter
        props = context.scene.trifecta_updateprops
        prefs = context.preferences.addons[__package__].preferences
        wm = context.window_manager
        props.running = True

        if props.stop:
            props.fstop = False
            props.stop = False
            props.active = False
            props.running = False
            props.finished = False
            props.updateAll = False
            wm.event_timer_remove(self._timer)
            area.tag_redraw()
            self.report({'WARNING'}, f"Cancelling! Code: {props.fail}, Error: {props.error}. Read INFO")
            return {'CANCELLED'}
        
        if (self._wait_validated) and (time.time() > self._start_at):
            bpy.ops.trifecta.scan('EXEC_DEFAULT', scan_all=True, revalidate=False)
            self.report({'INFO'}, 'All files validated!')
            props.running = False
            return {'FINISHED'}

        if (not props.active) and (not self._wait_validated):
            try:
                current_iter = next(Queue[0])
                self._count += 1
            except StopIteration:
                props.fstop = False
                props.stop = False
                props.active = False
                props.finished = False
                props.updateAll = False
                props.running = False
                
                self.report({'INFO'}, 'Queue Cleared!')
                for blend in prefs.blends:
                    if blend.validated == False:
                        self._wait_validated = True
                        self._time = time.time()
                        self._start_at = time.time() + 2
                        props.stage = 'Validating...'
                        self.report({'INFO'}, 'Please wait for files to be validated!')
                        return {'PASS_THROUGH'}
                return {'FINISHED'}
            props.active = True
            thread = threading.Thread(target=download_file_from_google_drive_blank,
                        args=(context, self),
                        daemon=True
                        )
            thread.start()

        if event.type in {'ESC'}:
            props.fstop = True
            #thread.join(1)

        if event.type == 'TIMER':
            area.tag_redraw()
        
        return {'PASS_THROUGH'}


    def execute(self, context):
        global area
        global Queue
        area = context.area

        props = bpy.context.scene.trifecta_updateprops
        prefs = context.preferences.addons[__package__].preferences

        props.active = False
        props.fstop = False
        props.running = False
        props.active = False
        props.finished = False
        props.size = 0.0
        props.stage = 'Downloading...'
        props.error = 'User Cancelled'
        props.fail = 0

        wm = context.window_manager
        self._time = time.time()
        self._count = 0
        self._wait_validated = False
        self._start_at = 0
        self.report({'INFO'}, 'Press ESC to cancel!')
        self._timer = wm.event_timer_add(1/30, window=context.window)
        wm.modal_handler_add(self)
        return {'RUNNING_MODAL'}
    
class TRIFECTA_OT_GET_RIG(TRIFECTA_OT_genericText):
    bl_idname = 'trifecta.get_rig'
    bl_label = 'Download Rig Set'
    bl_description = 'Download a set of rigs'

    rigs: EnumProperty(
        items=getRigs,
        name='Rig-Set',
        description='Choose a set of rigs to download'
    )

    newRigEntry: BoolProperty(default=True, name='Create New Rig-Set')
    newRigName: StringProperty(default='Rigs', name='Rig-Set Name')
    newRigPath: StringProperty(default='', subtype='DIR_PATH', name='Rig-Set Path')

    @classmethod
    def poll(cls, context):
        props = context.scene.trifecta_updateprops
        return not props.running

    def execute(self, context):
        global Queue
        prefs = context.preferences.addons[__package__].preferences
        rigs_rev = {value[0]: key for key, value in rigs_ids.items()}
        if self.newRigEntry:
            newRigName = rigs_rev[self.rigs]
            #if self.newRigName == '':
            #    self.report({'ERROR'}, 'Rig-set must be named!')
            #    return {'CANCELLED'}
            
            if (new_path := bpy.path.abspath(self.newRigPath)) == '':
                self.report({'ERROR'}, 'Rig-set path is empty!')
                return {'CANCELLED'}
            new_path_parent = os.path.split(new_path)[0]
            if not os.path.exists(new_path_parent):
                self.report({'ERROR'}, 'Path for new rig-set is invalid!')
                return {'CANCELLED'}
            if prefs.rigs.get(newRigName) != None:
                self.report({'ERROR'}, 'Rig-set already exists! Replace the rig instead!')
                return {'CANCELLED'}
            
            new = prefs.rigs.add()
            new.name = rigs_rev[self.rigs]
            new.path = new_path
            context.scene.hisanimvars.rigs = newRigName
        queue = [(rigs_rev[self.rigs], self.rigs, 'ZIP')]
        Queue = (iter(enumerate(queue)), 1)
        bpy.ops.trifecta.download_queue('EXEC_DEFAULT')
        return {'FINISHED'}

    def invoke_extra(self, context, event):
        self.newRigEntry = True
        self.newRigName = ''
        self.newRigPath = ''

    def draw_extra(self, context):
        layout = self.layout
        props = bpy.context.scene.trifecta_updateprops
        prefs = context.preferences.addons[__package__].preferences
        col1 = layout.column()
        col2 = layout.column()
        col1.row().label(text='Choose a set of rigs to download.')
        col1.row().prop(self, 'rigs')
        #: return
        
        if not self.newRigEntry and len(prefs.rigs) > 0:
            col2.row().label(text='Choose a set of rigs to replace.')
            col2.prop(context.scene.hisanimvars, 'rigs')
        else:
            col1.prop(self, 'newRigPath')
        if len(prefs.rigs) < 1: return
        col1.row().prop(self, 'newRigEntry', text='Update Existing Rigs', invert_checkbox=True)

class TRIFECTA_OT_GET_BLEND(TRIFECTA_OT_genericText):
    bl_idname = 'trifecta.get_blend'
    bl_label = 'Download .blend'

    item_name: StringProperty()
    item_id: StringProperty()

    @classmethod
    def poll(cls, context):
        props = context.scene.trifecta_updateprops
        return not props.running

    def execute(self, context):
        global Queue
        queue = list()
        prefs = context.preferences.addons[__package__].preferences
        props = bpy.context.scene.hisanimvars
        items_path = prefs.items_path
        if not os.path.exists(items_path):
            self.report({'ERROR'}, 'The path you set for your TF2 Items does not exist!')
            return {'CANCELLED'}
        
        queue = list()

        queue.append((self.item_name, self.item_id, 'BLEND'))

        Queue = (iter(enumerate(queue)), len(queue))
        bpy.ops.trifecta.download_queue('EXEC_DEFAULT')
        return {'FINISHED'}

class TRIFECTA_OT_DOWNLOAD_ALL(TRIFECTA_OT_genericText):
    bl_idname = 'trifecta.download_all'
    bl_label = 'Download All'

    download_rigs: BoolProperty(default=False, name='Download Rigs', description='Downloads a standard set of rigs (hisanimations) next to the folder your downloads will be in')

    @classmethod
    def poll(cls, context):
        props = context.scene.trifecta_updateprops
        return not props.running

    def execute(self, context):
        global Queue
        queue = list()
        prefs = context.preferences.addons[__package__].preferences
        props = bpy.context.scene.hisanimvars
        items_path = prefs.items_path.rstrip('\\/')
        if not os.path.exists(items_path):
            self.report({'ERROR'}, 'The path you set for your TF2 Items does not exist!')
            return {'CANCELLED'}
        
        for key, value in ids.items():
            queue.append((key, value, 'BLEND'))

        if self.download_rigs:
            new_rig_set = prefs.rigs.add()
            new_rig_set.name = 'Standard Rigs'
            new_rig_set.path = os.path.join(
                    os.path.split(items_path)[0],
                    'rigs'
            )
            if not os.path.exists(new_rig_set.path):
                os.makedirs(new_rig_set.path)
            context.scene.hisanimvars.rigs = 'Standard Rigs'
            queue.append(('standard_rigs', rigs_ids['hisanimations'], 'ZIP', ''))

        Queue = (iter(enumerate(queue)), len(queue))
        bpy.ops.trifecta.download_queue('EXEC_DEFAULT')
        return {'FINISHED'}

    def draw_extra(self, context):
        layout = self.layout
        layout.prop(self, 'download_rigs')
        

#class TRIFECTA_OT_updateAll(Operator):
    #bl_idname

bpyClasses = [HISANIM_PT_UPDATER,
              HISANIM_OT_ADDONUPDATER, 
              updateProps,
              TRIFECTA_OT_DOWNLOAD_ALL,
              TRIFECTA_OT_GET_RIG,
              TRIFECTA_OT_GET_BLEND,
              TRIFECTA_OT_DOWNLOAD_QUEUE,
              #HISANIM_OT_PROMPT,
              #HISANIM_OT_STARTUP_UPDATE,
              #HISANIM_OT_check_update,
              #HISANIM_OT_notify_user
              ]

def register():
    for operator in bpyClasses:
        bpy.utils.register_class(operator)
    bpy.types.Scene.trifecta_updateprops = PointerProperty(type=updateProps)
    #bpy.app.timers.register(startup)
def unregister():
    for operator in bpyClasses:
        bpy.utils.unregister_class(operator)
    del bpy.types.Scene.trifecta_updateprops