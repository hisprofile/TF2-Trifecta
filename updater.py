import bpy, os, shutil, shutil, glob, json, zipfile, threading, time, requests
from pathlib import Path
from . import icons, mercdeployer, preferences
from urllib import request
from math import sin
from bpy.types import Operator, PropertyGroup
from bpy.props import *
from datetime import datetime
import uuid
global blend_files
global files
#bpy

area = None

mercs = ['scout', 'soldier', 'pyro', 'demo', 'heavy', 'engineer', 'medic', 'sniper', 'spy']
classes = mercdeployer.classes
misc = ['allclass', 'allclass2', 'allclass3', 'weapons', 'rigs']

ids = {
    'allclass': '1XxOCordVSxw2kal5ujeOd_wp5dcQ7RKo',
    'allclass2' : '1RnemK8RV-J3Onzc1fMBEVf0uon0NSXtm',
    'allclass3': '1rT_Z5o9g8IF-eALfDIIdjWB_n_03RJYm',
    'scout': '1TS6KGbE8jKtIremS_4Go3T1eXyajifKu',
    'soldier': '1c4D0_RueeuRkAj34JPmHl7T8F6GG91Yc',
    'pyro': '1cAP7NY1x_IHVQQtnWwjFNstQKjXp-Qlu',
    'demo': '1p2Cu9wfxbentYMVKGdgnJuaMpT7db68j',
    'heavy': '1JjqQXDKuDXGDkLvMvshojppd1IbNMij-',
    'engineer': '1c8jyJlD4VknD2RfexXa6owV_kaKOExQO',
    'medic': '1VQvixt9pW85zMafkuhsVZaZtocivy_zH',
    'sniper': '1VMCOr8aeaJhTk2xivlsnC55DaUpLoqJV',
    'spy': '1dhANUyTvy8ylOFUBEKCxZo11BE-IO8L3',
    'weapons': '12WyUdeVFIvS_IM-RkKHUP-Fc4kzoGZwa',
    'standard-rigs': '1-Npd2KupzpzmoMvXfl1-KWwPnoADODVj'
}

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

class HISANIM_PT_UPDATER(bpy.types.Panel): # the panel for the TF2 Collection Updater
    bl_label = "TF2 Trifecta"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'scene'
    def draw(self, context):
        version = bpy.app.version
        addon_fp = os.path.abspath(Path(__file__).parent)
        props = bpy.context.scene.trifecta_updateprops
        layout = self.layout
        if props.active:
            row = layout.row()
            row.label(text=props.stage)
            row.label(text=f'{format_size(props.size)}/{format_size(props.download_size)}')
            if props.updateAll:
                row.label(text=f'{list(ids.keys())[props.iter].title()}, {props.iter + 1}/14')
            if version >= (4, 0, 0):
                row.progress(text='', type='RING', factor=props.progress)
            else:
                row.label(text='.'*int(((time.time()*3)%3) + 1))
        else:
            layout.row().operator('wm.url_open', text='Installation Documentation', icon='URL').url = 'https://github.com/hisprofile/blenderstuff/blob/main/Guides/TF2%20Blender/!TF2-Trifecta%20Installation.md'
        box = layout.box()
        box.label(text='Update Class Cosmetics')
        id_items = ids.items()
        for asset, id in list(id_items)[3:-2]:
            op = box.row().operator('trifecta.update', text=f'Download {asset.title()}', icon_value=icons.id('tfupdater'))
            op.id = id
            op.asset = asset
            op.operation = 'BLEND'

        box = layout.box()
        box.label(text='Update Misc.')
        for asset, id in [*list(id_items)[:3], list(id_items)[-2]]:
            op = box.row().operator('trifecta.update', text=f'Download {asset.title()}', icon_value=icons.id('tfupdater'))
            op.id = id
            op.asset = asset
            op.operation = 'BLEND'

        box = layout.box()
        box.label(text='Download Rigs')
        op = box.row().operator('trifecta.update', text='Download Rigs', icon_value=icons.id('tfupdater'))
        op.operation = 'ZIP'
        box.row().prop(props, 'newRigEntry')
        if props.newRigEntry:
            box.row().prop(props, 'newRigName')
            box.row().prop(props, 'newRigPath')

        box = layout.box()
        box.label(text='Install TF2 Collection')
        op = box.row().operator('trifecta.update', text='Install TF2 Collection', icon_value=icons.id('tfupdater'))
        op.updateAll = True
        box.row().label(text='Place path in an empty folder.')
        row = box.row()
        row.alignment = 'EXPAND'
        row.label(text='TF2 Collection Path:')
        row.prop(props, 'tf2ColPath', text='')
        box.row().prop(props, 'tf2ColRig')
        row = layout.row()
        row.operator('hisanim.addonupdate', icon_value=icons.id('tfupdater'))
        layout.row().operator('hisanim.relocatepaths', text='Redefine Library Paths', icon='FILE_REFRESH')
        row = layout.row()
        row.prop(context.scene.hisanimvars, 'savespace')
        layout.row().prop(context.preferences.addons[__package__].preferences, 'quickswitch')

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
    
def update_masterjson():
    #url = "https://docs.google.com/uc?export=download"
    #id = '1sdpUfuXf9NyEAuu0_TVdaAmSoFlKvUOm'
    #session = requests.Session()
    #params = {'id': id, 'confirm': 1}
    #response = session.get(url, params=params, stream=True)
    file = request.urlopen('https://raw.githubusercontent.com/hisprofile/TF2-Trifecta/main/master.json')
    file = file.read()
    destination = Path(os.path.join(os.path.dirname(__file__), 'master.json'))
    with open(destination, "w+") as f:
        #for i, chunk in enumerate(response.iter_content(32768)):
            #if chunk:  # filter out keep-alive new chunks
                #f.write(chunk)
        f.write(file.decode())
    f.close()

    return None

def download_file_from_google_drive_blank(context):
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

        ### Download Properties ###
        #url = "https://docs.google.com/uc?export=download"
        url = 'https://drive.usercontent.google.com/download?'
        #https://drive.usercontent.google.com/download?id=1cAP7NY1x_IHVQQtnWwjFNstQKjXp-Qlu?confirm=t&uuid=a908a383-e795-4d21-974d-73c8e49a2d6f
        file_id = props.id
        chunk_size=32768
        session = requests.Session()
        #params = {'id': file_id, 'confirm': 't', 'authuser': 0}
        params = {'id': file_id, 'confirm': 't', 'uuid': str(uuid.uuid4())}
        response = session.get(url, params=params, stream=True)
        #print(response.headers.get('Content-Length', 1))
        props.download_size = int(response.headers.get('Content-Length', 1))
        #raise SmallDownload

        d = response

        wm = bpy.context.window_manager

        ### Start Download ###
        if response.status_code != 200:
            props.stop = True
            props.fail = response.status_code
            raise InvalidResponse
        
        if props.operation == 'ZIP':
            rigs = prefs.rigs[scn.hisanimvars.rigs]
            destination = os.path.join(rigs.path, 'rigs.zip')
            folder = rigs.path
            
            rigs_backup = os.path.join(folder, 'bak')
            os.makedirs(rigs_backup)
            for file in glob.glob('*.blend', root_dir=folder):#os.listdir(folder):
                shutil.move(os.path.join(folder, file), os.path.join(folder, 'bak', file))

        if props.operation == 'BLEND':
            destination = prefs.hisanim_paths[props.asset].path
            folder = os.path.dirname(destination)
            if Path(destination).exists():
                bak = shutil.move(destination, os.path.join(folder, 'bak.blend'))

        with open(destination, "wb") as file:
            for i, chunk in enumerate(response.iter_content(chunk_size)):
                    if props.fstop:
                        raise
                    if chunk:  # filter out keep-alive new chunks
                        try:
                            props.size = i*chunk_size
                            props.progress = props.size/props.download_size
                        except Exception as e:
                            print(e)
                            pass
                        file.write(chunk)
        file.close()

        filesize = os.stat(destination)[6]

        if filesize < 2_000_000:
            raise SmallDownload

        '''
        If the file size is less than 2mb, then it's probably gone to waste. Obviously the best thing to do would be to verify via
        checksum, but I don't really have a way to implement that in way that's constantly up to date with the files.
        '''

        props.size = os.stat(destination)[6]
        if props.operation == 'ZIP': # ZIP is alias for downloading rig sets
            props.stage = 'Extracting...'

            with zipfile.ZipFile(destination, 'r') as zip:
                info = zip.infolist()
                obj_count = len(info)
                print(obj_count)
                for n, file_info in enumerate(info):
                    props.progress = obj_count / (n + 1)
                    if bpy.context.screen != None:
                        for area in bpy.context.screen.areas:
                            if area.type == 'PROPERTIES':
                                area.tag_redraw()
                    file_path = os.path.join(folder, file_info.filename)
                    zip.extract(file_info, folder)

            props.stage = 'Removing...'
            #props.var = 1.0
            os.remove(destination)
            shutil.rmtree(rigs_backup)
        
        if props.operation == 'BLEND' and bak != '':
            os.remove(bak)
        props.finished = True

    #except SmallDownload:
        #props.stop = True
        #props.error = "Download too small, assuming download failed!"
        #print(props.error)
        #return None

    except Exception as E:
        props.stop = True
        props.error = str(E)
        print(E)
        return None

        if props.operation == 'ZIP':# and Path(destination).exists():
            os.remove(destination)
            for file in os.listdir(rigs_backup):
                shutil.move(os.path.join(rigs_backup, file), os.path.join(folder, file))
            shutil.rmtree(rigs_backup)
            pass

        if props.operation == 'BLEND':
            os.remove(destination)
            if bak != '': shutil.move(bak, destination)
    return None

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


class TRIFECTA_OT_downloader(Operator):
    bl_idname = 'trifecta.update'
    bl_label = 'Grab File'
    bl_description = "Get file from hisanimation's Google Drive"
    _timer = None
    start = 0
    progress: FloatProperty(default=0.0)

    ### Initializers for download operation ###

    updateAll: BoolProperty(default=False)
    id: StringProperty(name='ID')
    file: StringProperty(name='File')
    filepath:StringProperty(name='Filepath', subtype='DIR_PATH')
    newpath: StringProperty(name='New path', subtype='DIR_PATH')
    asset: StringProperty(default='')
    operation: EnumProperty(items=(
        ('BLEND', '', '', 0),
        ('ZIP', '', '', 1)
    ), name='Operation')

    ### Rig download properties ###

    rigs: EnumProperty(items=(
        ('1-Npd2KupzpzmoMvXfl1-KWwPnoADODVj', 'hisanimations', '', '', 0),
        ('1-MboVZ3PZ471AmXYHnYegoXozKd8OmVU', 'Eccentric', '', '', 1),
        ('1-MVdFejB1wtO4v2zcurCMIK6MPxNvRTs', 'ThatLazyArtist', '', '', 2)
    ), name='Rig Set')

    ### TF2 Collection update properties ###

    scout: BoolProperty(default=True)
    soldier: BoolProperty(default=True)
    pyro: BoolProperty(default=True)
    demo: BoolProperty(default=True)
    heavy: BoolProperty(default=True)
    engineer: BoolProperty(default=True)
    medic: BoolProperty(default=True)
    sniper: BoolProperty(default=True)
    spy: BoolProperty(default=True)

    allclass: BoolProperty(default=False)
    allclass2: BoolProperty(default=False)
    allclass3: BoolProperty(default=True)
    weapons: BoolProperty(default=False)
    
    @classmethod
    def poll(cls, context):
        props = context.scene.trifecta_updateprops
        return not props.active

    def modal(self, context, event):
        global area

        props = context.scene.trifecta_updateprops
        prefs = context.preferences.addons[__package__].preferences
        wm = context.window_manager
        props.running = True

        if event.type in {'ESC'}:
            props.fstop = True

        if props.stop:
            props.fstop = False
            props.stop = False
            props.active = False
            props.running = False
            props.finished = False
            props.updateAll = False
            wm.event_timer_remove(self._timer)
            area.tag_redraw()
            self.report({'WARNING'}, f"Cancelling! Code: {props.fail}, Error: {props.error}")
            return {'CANCELLED'}

        if not props.active:
            props.active = True
            thread = threading.Thread(target=download_file_from_google_drive_blank, args=(context,), daemon=True)
            thread.start()

        if props.finished:
            props.active = False
            props.finished=False
            if props.updateAll and props.iter != 13:
                self.report({'INFO'}, f'{list(ids.keys())[props.iter].title()} done!')
                props.iter += 1
                props.size = 0.0
                props.stage = 'Downloading...'
                props.id = list(ids.items())[props.iter][1]
                props.asset = list(ids.items())[props.iter][0]
                props.operation = 'BLEND'
                #if props.iter == 13: props.updateAll = False
                if props.iter == 13 and props.tf2ColRig:
                    props.operation = 'ZIP'
                    return {'PASS_THROUGH'}
                elif props.iter == 13 and not props.tf2ColRig:
                    props.finished = True
                    self.report({'INFO'}, 'Finished downloading!')
                    wm.event_timer_remove(self._timer)
                    area.tag_redraw()
                else:
                    return {'PASS_THROUGH'}
            props.updateAll = False
            self.report({'INFO'}, 'Finished downloading!')
            wm.event_timer_remove(self._timer)
            area.tag_redraw()
            return {'FINISHED'}

        if event.type == 'TIMER' and props.stage == 'Downloading...':
            #tim = time.time()
            #tim = sin(tim*5)
            #tim = MAP(tim, -1, 1, 0.01, 0.08)
            #props.var = (props.var + tim) % 1
            area.tag_redraw()

        if props.stage == 'Moving...':
            print(os.stat(props.newpath)[6], props.newpath)
            if os.stat(props.newpath)[6] == 0:
                props.var = 0.0
            else:
                print(os.stat(props.newpath)[6])
                props.var = props.size/os.stat(props.newpath)[6]

        return {'PASS_THROUGH'}

    def execute(self, context):
        global area

        area = context.area

        props = bpy.context.scene.trifecta_updateprops
        prefs = context.preferences.addons[__package__].preferences
        assets = prefs.hisanim_paths
        thread = threading.Thread(target=update_masterjson, daemon=True)
        thread.start()
        if props.newRigEntry and self.operation == 'ZIP':
            if props.newRigName == '':
                self.report({'ERROR'}, 'Rig-set must be named!')
                return {'CANCELLED'}
            
            if props.newRigPath == '':
                self.report({'ERROR'}, 'Rig-set path is empty!')
                return {'CANCELLED'}
            
            if os.path.isfile(props.newRigPath):
                props.newRigPath = Path(props.newRigPath).parent
            
            if not Path(props.newRigPath).exists():
                self.report({'ERROR'}, 'Path for new rig-set is invalid!')
                return {'CANCELLED'}
            
            if prefs.rigs.get(props.newRigName) != None:
                self.report({'ERROR'}, 'Rig-set already exists!')
                return {'CANCELLED'}

            new = prefs.rigs.add()
            new.name = props.newRigName
            new.path = props.newRigPath
            context.scene.hisanimvars.rigs = props.newRigName
            props.newRigEntry = False   
            props.newRigName = 'Rigs'
            props.newRigPath = ''

        elif self.operation == 'ZIP':
            pass
        
        elif self.updateAll:
            if props.tf2ColPath == '':
                self.report({'ERROR'}, 'Add a path to install to!')
                return {'CANCELLED'}
            props.updateAll = True
            root = Path(props.tf2ColPath)
            rigs = prefs.rigs
            for merc in mercs:
                #if not eval(f'self.{merc}'):
                #    continue
                if (asset := assets.get(merc)) == None: 
                    asset = prefs.hisanim_paths.add()
                    asset.path = os.path.join(root, merc, f'{merc}cosmetics.blend')
                    asset.name = merc
                    asset.this_is = 'BLEND'
                    if not Path(os.path.join(root, merc)).exists():
                        os.makedirs(os.path.join(root, merc))

            for m in misc[:-1]:
                #if not eval(f'self.{m}'):
                #    continue
                if (asset := assets.get(m)) == None: 
                    asset = prefs.hisanim_paths.add()
                    asset.path = os.path.join(root, m, f'{m}.blend')
                    asset.name = m
                    asset.this_is = 'BLEND'
                    if not Path(os.path.join(root, m)).exists():
                        os.makedirs(os.path.join(root, m))

            if props.tf2ColRig and rigs.get('rigs') == None:
                prefs.missing = False
                new = rigs.add()
                new.name = 'rigs'
                new.path = os.path.join(root, 'rigs')
                preferences.enumRigs()
                context.scene.hisanimvars.rigs = 'rigs'
                if not Path(os.path.join(root, 'rigs')).exists():
                    os.makedirs(os.path.join(root, 'rigs'))

            props.size = 0.0
            props.stage = 'Downloading...'
            props.iter = 0
            props.id = list(ids.items())[0][1]
            props.operation = 'BLEND'
            props.asset = list(ids.items())[0][0]

            wm = context.window_manager
            self._timer = wm.event_timer_add(0.1, window=context.window)
            self.time = time.time()
            self.report({'INFO'}, 'Press ESC to cancel!')
            wm.modal_handler_add(self)
            return {'RUNNING_MODAL'}

        props.size = 0.0
        props.stage = 'Downloading...'
        props.iter = 0
        props.id = self.id if self.operation == 'BLEND' else self.rigs
        if self.operation == 'BLEND' and assets.get(self.asset) == None:
            self.report({'ERROR'}, f'No asset added for {self.asset}!')
            return {'CANCELLED'}
        props.filepath = self.filepath
        props.operation = self.operation
        props.asset = self.asset

        wm = context.window_manager
        self._timer = wm.event_timer_add(0.1, window=context.window)
        self.time = time.time()
        wm.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        prefs = context.preferences.addons[__package__].preferences
        rigs = prefs.rigs
        props = bpy.context.scene.trifecta_updateprops
        if self.operation == 'ZIP':# or self.updateAll:
            if not props.newRigEntry and len(rigs) == 0:
                self.report({'ERROR'}, "Make a new set of rigs!")
                return {'CANCELLED'}
            return context.window_manager.invoke_props_dialog(self)
        if self.updateAll:
            return context.window_manager.invoke_confirm(self, event)
        return self.execute(context)
    
    def draw(self, context):
        props = bpy.context.scene.trifecta_updateprops
        layout = self.layout

        if self.operation == 'ZIP':
            layout.row().label(text='Choose a set of rigs to download.')
            layout.row().prop(self, 'rigs')
            if not props.newRigEntry:
                layout.row().label(text='Choose a set of rigs to replace.')
                layout.prop(context.scene.hisanimvars, 'rigs')

#class TRIFECTA_OT_updateAll(Operator):
    #bl_idname

bpyClasses = [HISANIM_PT_UPDATER,
              HISANIM_OT_ADDONUPDATER, 
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