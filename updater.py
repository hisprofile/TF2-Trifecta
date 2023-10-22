import bpy, os, shutil, shutil, glob, json, zipfile
from pathlib import Path
from . import dload, icons, mercdeployer
from urllib import request
global blend_files
global files

files = ['scout', 'soldier', 'pyro', 'demo', 'heavy', 'engineer', 'medic', 'sniper', 'spy']
classes = mercdeployer.classes
allclasses = ['allclass', 'allclass2', 'allclass3']
class HISANIM_PT_UPDATER(bpy.types.Panel): # the panel for the TF2 Collection Updater
    bl_label = "TF2 Trifecta"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'scene'
    def draw(self, context):
        layout = self.layout
        self.layout.icon
        layout.label(text='Update Class Cosmetics')
        row = layout.row()
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
        layout.label(text='Update/Replace TF2-V3 Rigs')  
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
        row = layout.row()
        row.operator('hisanim.addonupdate', icon_value=icons.id('tfupdater'))
        layout.row().operator('hisanim.relocatepaths', text='Redefine Library Paths', icon='FILE_REFRESH')
        row = layout.row()
        row.prop(context.scene.hisanimvars, 'savespace')
        row = layout.row()
        row.prop(context.preferences.addons[__package__].preferences, 'compactable', text='Compactable View')
        layout.row().prop(context.preferences.addons[__package__].preferences, 'quickswitch')
        row = layout.row()
        row.alignment = 'RIGHT'
        op = row.operator('trifecta.textbox', text='', icon='QUESTION')
        op.text = '''fasdf asdf\nf ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣿⣿⣿⣿⣿⣿⣿⣮⣝⡯⠀⠀⢀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⢼⣧⣿⣿⣿⡿⠻⠿⢿⣯⣿⣮⣀⡁⢑⡀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⣾⣿⡟⠁⠀⠙⠧⠞⠈⢓⣿⣿⣿⣿⢿⣾⣷⡀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢻⣫⠟⠀⠀⠀⠀⠀⠀⠀⠀⡙⣿⣿⣿⣿⣿⣿⡇⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣾⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠢⢈⢻⣿⣿⣿⣿⡇⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠠⣿⠁⠚⣛⣒⠀⠀⠀⡀⠐⢒⡒⠳⠤⢺⣟⣿⣿⡇⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⠋⠀⠋⠚⠛⠃⢈⣩⣓⢮⠿⠯⠷⠀⠀⢽⣿⠏⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⡜⠄⠀⠀⠀⠀⠀⠀⢸⠩⠀⠀⠀⠀⠀⠀⠀⢻⡤⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠔⡸⡎⠀⠀⠀⠀⠀⠀⠀⠀⠠⠁⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠂⠀⠀⠀⠀⠈⠀⡳⣿⠆⠄⠀⠀⠁⠀⠠⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡇⠀⠀⠘⠤⡔⢎⣵⣸⢯⠜⠀⠀⠀⠀⡀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣇⠀⣠⣆⣿⣿⣾⣹⣏⢳⣄⡀⠀⠀⠀⠃⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠠⣸⠤⠋⠙⠓⠶⠖⣾⠾⠟⠋⢣⣲⣦⡾⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⢀⣤⣶⣶⣾⣽⣿⢷⠀⢈⠃⢙⠃⠀⠀⠀⢐⡾⣾⡿⠃⠀⠀⠠⣄⠀⠀⠀⠀
⠀⢀⣤⣾⣿⣿⣿⣿⣿⣿⣯⣆⢣⣑⣄⠴⡇⣽⣦⣢⣾⣾⠋⡀⠐⠀⠁⢀⣿⣷⣄⠀⠀
⣰⣿⣿⣿⣿⣿⣿⣿⣿⣿⣻⣗⣉⣛⣿⣶⣟⣿⣿⣛⣁⣐⣀⣀⣀⣠⣶⣿⣡⣨⣟⣑⣢'''
        op.icons='NONE,NONE'
        op.size='56,56'

class HISANIM_OT_CLSUPDATE(bpy.types.Operator):
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

class HISANIM_OT_ALLCLSUPDATE(bpy.types.Operator):
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

class HISANIM_OT_MERCUPDATE(bpy.types.Operator):
    bl_idname = 'hisanim.mercupdate'
    bl_label = 'Standard Mercs'
    bl_description = "Download hisanimations' TF2 rigs, the default rigs to use"

    def execute(self, execute):
        prefs = bpy.context.preferences.addons[__package__].preferences
        #DLOADTO = bpy.context.preferences.filepaths.asset_libraries['TF2-V3'].path + "/"
        if (GET := prefs.hisanim_paths.get('TF2-V3')) == None:
            self.report({'INFO'}, 'No entry for TF2-V3!')
            return {'CANCELLED'}
        GET = GET.path
        print('Deleting old .blend files...')
        for i in glob.glob("*.blend", root_dir=GET):
            os.remove(os.path.join(GET, i))
            print(f'Deleted {i}..')
        DLOADTO = GET
        print(f"Downloading hisanimations' TF2-V3 port...")
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

class HISANIM_OT_HECTORISUPDATE(bpy.types.Operator):
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
        #DLOADTO = bpy.context.preferences.filepaths.asset_libraries['TF2-V3'].path + "/"
        if (GET := prefs.hisanim_paths.get('TF2-V3')) == None:
            self.report({'INFO'}, 'No entry for TF2-V3!')
            return {'CANCELLED'}
        GET = GET.path
        print('Deleting old .blend files...')
        for i in glob.glob("*.blend", root_dir=GET):
            os.remove(os.path.join(GET, i))
            print(f'Deleted {i}..')
        DLOADTO = GET
        print(f"Downloading Hectoris919's TF2-V3 port...")
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
    
class HISANIM_OT_ECCENTRICUPDATE(bpy.types.Operator):
    bl_idname = 'hisanim.eccentricupdate'
    bl_label = 'Face Panel'
    bl_description = "Download Eccentric's TF2 rigs, used with a face panel"

    def execute(self, execute):
        prefs = bpy.context.preferences.addons[__package__].preferences
        #DLOADTO = bpy.context.preferences.filepaths.asset_libraries['TF2-V3'].path + "/"
        if (GET := prefs.hisanim_paths.get('TF2-V3')) == None:
            self.report({'INFO'}, 'No entry for TF2-V3!')
            return {'CANCELLED'}
        GET = GET.path
        print('Deleting old .blend files...')
        for i in glob.glob("*.blend", root_dir=GET):
            os.remove(os.path.join(GET, i))
            print(f'Deleted {i}..')
        DLOADTO = GET
        print(f"Downloading Eccentric's TF2-V3 version...")
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
    
class HISANIM_OT_ADDONUPDATER(bpy.types.Operator):
    bl_idname = 'hisanim.addonupdate'
    bl_label = 'Update Addon'
    bl_description = "Get the latest version of the addon. Updater made by Herwork and hisanimations"

    def execute(self, context):
        PATH = Path(__file__).parent.parent
        print("Fetching new download URL from GitHub")
        # Getting the new release URL from GitHub REST API
        try:
            githubResponse = request.urlopen("https://api.github.com/repos/hisprofile/TF2-Trifecta/releases")
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
        class HISANIM_OT_reloadAddon(bpy.types.Operator):
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
                row.label(icon='ERROR')
                row.label(text='Blender may crash!')
        
        bpy.utils.register_class(HISANIM_OT_reloadAddon)
        bpy.utils.register_class(HISANIM_PT_tempPanel)
        self.report({'INFO'}, 'Addon downloaded! Press "Reload Addon" to apply changes.')
        return {'FINISHED'}

bpyClasses = [HISANIM_PT_UPDATER, HISANIM_OT_CLSUPDATE, HISANIM_OT_ALLCLSUPDATE, HISANIM_OT_MERCUPDATE, HISANIM_OT_HECTORISUPDATE, HISANIM_OT_ADDONUPDATER, HISANIM_OT_ECCENTRICUPDATE]

def register():
    for operator in bpyClasses:
        bpy.utils.register_class(operator)
def unregister():
    for operator in bpyClasses:
        bpy.utils.unregister_class(operator)