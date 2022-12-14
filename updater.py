import bpy, os, shutil, shutil
from pathlib import Path
from . import dload, icons, mercdeployer, PATHS, addonUpdater
import zipfile
global blend_files
global files
files = ['scout', 'soldier', 'pyro', 'demo', 'heavy', 'engineer', 'medic', 'sniper', 'spy']
def RefreshPaths():
    blend_files = []
    prefs = bpy.context.preferences
    filepaths = prefs.filepaths
    asset_libraries = filepaths.asset_libraries
    for asset_library in asset_libraries:
        library_path = Path(asset_library.path)
        blend_files.append(str([fp for fp in library_path.glob("**/*.blend")]))
    # taken from https://blender.stackexchange.com/questions/244971/how-do-i-get-all-assets-in-a-given-userassetlibrary-with-the-python-api
    PATHS.FPATHS = {}
    #files = ['scout', 'soldier', 'pyro', 'demo', 'heavy', 'engineer', 'medic', 'sniper', 'spy']
    for i in files: # add paths to definitoin
        for ii in blend_files:
            try:
                ii = str(ii)[str(ii).index("(") + 2:str(ii).index(")")-1]
                if i in ii and not "V3" in ii: # skip TF2-V3 
                    PATHS.FPATHS[i] = ii
            except:
                continue
                
    for i in blend_files: # for allclass folders
        try:
            i = str(i)[str(i).index("(") + 2:str(i).index(")")-1]
            if 'allclass.b' in i:
                PATHS.FPATHS['allclass'] = i
        except:
            print(i, " is an invalid path!")
            continue
            
    for i in blend_files:
        try:
            i = str(i)[str(i).index("(") + 2:str(i).index(")")-1]
            if 'allclass2' in i:
                PATHS.FPATHS['allclass2'] = i
        except:
            print(i, " is an invalid path!")
            continue

    for i in blend_files:
        try:
            i = str(i)[str(i).index("(") + 2:str(i).index(")")-1]
            if 'allclass3' in i:
                PATHS.FPATHS['allclass3'] = i
        except:
            print(i, " is an invalid path!")
            continue
classes = mercdeployer.classes
allclasses = ['allclass', 'allclass2', 'allclass3']
class HISANIM_PT_UPDATER(bpy.types.Panel): # the panel for the TF2 Collection Updater
    bl_label = "TF2 Trifecta Updater"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'scene'
    def draw(self, context):
        layout = self.layout
        self.layout.icon
        layout.label(text='Update Class Cosmetics')
        row = layout.row()
        for i in classes:
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
        row = layout.row()
        row.operator('hisanim.hectorisupdate')
        layout.label(text='Face Panel + Phonemes Rigs by Hectoris919')
        layout.label(text='Open the console to view progress!')
        row = layout.row()
        row.operator('hisanim.addonupdate', icon_value=icons.id('tfupdater'))

class HISANIM_OT_CLSUPDATE(bpy.types.Operator):
    bl_idname = 'hisanim.clsupdate'
    bl_label = 'Update Class'
    bl_description = 'Press to update class'
    UPDATE: bpy.props.StringProperty(default='')
    def execute(self, context):
        RefreshPaths() # refresh paths, just cause
        switch = False
        try:
            GET = PATHS.FPATHS[self.UPDATE]
        except: # if the addon cannot find an existing .blend, it will go through your asset paths..
            # The rest can be understood by reading the print lines.
            print(f'No existing .blend file found for {self.UPDATE}!')
            try:
                print('Attempting to find existing directory...')
                assetpath = context.preferences.filepaths.asset_libraries
                for i in assetpath:
                    if self.UPDATE in i.path.casefold():
                        FINDPATH = i.name
                        print(f'Directory found at {i.path}!')
                        break
                PATHS.FPATHS[self.UPDATE] = context.preferences.filepaths.asset_libraries[FINDPATH].path.replace(r'\\'[0], '/') + "/"
                GET = PATHS.FPATHS[self.UPDATE]
                print(GET)
                del FINDPATH
                switch = True
            except:
                self.report({'INFO'}, f"Cannot find a directory for {self.UPDATE}!")
                return {'CANCELLED'}
        DLOADTO = GET[:GET.rfind('/')+1]
        if switch == False:
            print(f"Deleting old file from {GET}...")
            if os.path.exists(GET):
                os.remove(GET)
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
        zipfile.ZipFile(DLOADTO+f'{self.UPDATE}cosmetics.zip', 'r').extractall(DLOADTO)
        print('Extracted!')
        print('Removing .zip file...')
        os.remove(DLOADTO+f'{self.UPDATE}cosmetics.zip')
        print('Removed!')
        print(f'Updating {self.UPDATE} complete!')
        #bpy.ops.wm.console_toggle()
        return {'FINISHED'}

class HISANIM_OT_ALLCLSUPDATE(bpy.types.Operator):
    bl_idname = 'hisanim.allclsupdate'
    bl_label = 'Update Class'
    bl_description = 'Press to update class'
    UPDATE: bpy.props.StringProperty(default='')
    def execute(self, context):
        RefreshPaths()
        switch = False
        try:
            GET = PATHS.FPATHS[self.UPDATE]
        except: # if the addon cannot find an existing .blend, it will go through your asset paths..
            # The rest can be understood by reading the print lines.
            print(f'No existing .blend file found for {self.UPDATE}!')
            try:
                print('Attempting to find existing directory...')
                assetpath = context.preferences.filepaths.asset_libraries
                for i in assetpath:
                    if self.UPDATE in i.path.casefold():
                        FINDPATH = i.name
                        print(f'Directory found at {i.path}!')
                        break
                PATHS.FPATHS[self.UPDATE] = context.preferences.filepaths.asset_libraries[FINDPATH].path.replace(r'\\', '/') + "/"
                GET = PATHS.FPATHS[self.UPDATE]
                print(GET)
                del FINDPATH
                switch = True
            except:
                self.report({'INFO'}, f"Cannot find a directory for {self.UPDATE}!")
                return {'CANCELLED'}
        DLOADTO = GET[:GET.rfind('/')+1]
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
        zipfile.ZipFile(DLOADTO+f'{self.UPDATE}.zip', 'r').extractall(DLOADTO)
        print('Extracted!')
        print('Removing .zip file...')
        os.remove(DLOADTO+f'{self.UPDATE}.zip')
        print('Removed!')
        print(f'Updating {self.UPDATE} complete!')
        return {'FINISHED'}

class HISANIM_OT_MERCUPDATE(bpy.types.Operator):
    bl_idname = 'hisanim.mercupdate'
    bl_label = 'Standard Mercs'
    bl_description = "Download hisanimations' TF2 rigs, the default rigs to use"

    def execute(self, execute):
        DLOADTO = bpy.context.preferences.filepaths.asset_libraries['TF2-V3'].path + "/"
        print('Deleting old .blend files...')
        for i in files:
            try:
                os.remove(f'{DLOADTO + i}.blend')
                print(f'Deleted {i}.blend')
            except:
                print(f'Could not delete {i}.blend!')
        
        print(f"Downloading hisanimations' TF2-V3 port...")
        dload.save('https://gitlab.com/hisprofile/the-tf2-collection/raw/main/TF2-V3.zip')
        print('''hisanimations' port downloaded!''')
        print('Moving to asset library path...')
        shutil.move(str(Path(__file__).parent) + f"/TF2-V3.zip", DLOADTO)
        print('Moved!')
        print('Extracting .zip file...')
        zipfile.ZipFile(DLOADTO+'TF2-V3.zip', 'r').extractall(DLOADTO)
        print('Extracted!')
        print('Removing .zip flie...')
        os.remove(DLOADTO+'TF2-V3.zip')
        print('Removed!')
        print("Downloaded hisanimations' port!")
        return {'FINISHED'}

class HISANIM_OT_HECTORISUPDATE(bpy.types.Operator):
    bl_idname = 'hisanim.hectorisupdate'
    bl_label = 'Face Panel + Phonemes Rigs'
    bl_description = "Download Hectoris919's version of hisanimation's port, complete with a face rig and phonemes"

    def execute(self, execute):
        self.report({'INFO'}, 'Not ready yet!')
        return {'FINISHED'}
    
class HISANIM_OT_ADDONUPDATER(bpy.types.Operator):
    bl_idname = 'hisanim.addonupdate'
    bl_label = 'Update Addon'
    bl_description = "Get the latest version of the addon. Addon-Updater made by Herwork"

    def execute(self, execute):
        addonUpdater.main()
        self.report({'INFO'}, 'Please restart blender to apply the update')
        return {'FINISHED'}

bpyClasses = [HISANIM_PT_UPDATER, HISANIM_OT_CLSUPDATE, HISANIM_OT_ALLCLSUPDATE, HISANIM_OT_MERCUPDATE, HISANIM_OT_HECTORISUPDATE, HISANIM_OT_ADDONUPDATER]

def register():
    for operator in bpyClasses:
        bpy.utils.register_class(operator)
def unregister():
    for operator in bpyClasses:
        bpy.utils.unregister_class(operator)