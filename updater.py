import bpy, os, shutil, shutil
from pathlib import Path
from . import dload, icons, mercdeployer, PATHS
import zipfile
global blend_files
def RefreshPaths():
    blend_files = []
    prefs = bpy.context.preferences
    filepaths = prefs.filepaths
    asset_libraries = filepaths.asset_libraries
    for asset_library in asset_libraries:
        library_name = asset_library.path
        library_path = Path(asset_library.path)
        blend_files.append(str([fp for fp in library_path.glob("**/*.blend")]))
    # taken from https://blender.stackexchange.com/questions/244971/how-do-i-get-all-assets-in-a-given-userassetlibrary-with-the-python-api
    PATHS.FPATHS = {}
    files = ['scout', 'soldier', 'pyro', 'demo', 'heavy', 'engineer', 'medic', 'sniper', 'spy']
    for i in files: # add paths to definitoin
        for ii in blend_files:
            try:
                ii = str(ii)[str(ii).index("('") + 2:str(ii).index("')")]
                if i in ii and not "V3" in ii: # skip TF2-V3 
                    PATHS.FPATHS[i] = ii
            except:
                continue
                
    for i in blend_files: # for allclass folders
        try:
            i = str(i)[str(i).index("('") + 2:str(i).index("')")]
            if 'allclass.b' in i:
                PATHS.FPATHS['allclass'] = i
        except:
            print(i, " is an invalid path!")
            continue
            
    for i in blend_files:
        try:
            i = str(i)[str(i).index("('") + 2:str(i).index("')")]
            if 'allclass2' in i:
                PATHS.FPATHS['allclass2'] = i
        except:
            print(i, " is an invalid path!")
            continue

    for i in blend_files:
        try:
            i = str(i)[str(i).index("('") + 2:str(i).index("')")]
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
            OPER = row.operator('hisanim.clsupdate', text='Update ' + i, icon_value=icons.id('tfupdater'))
            OPER.UPDATE = i
            row = layout.row()
        layout.label(text='Update Allclass Cosmetics')
        row = layout.row()
        for i in allclasses:
            OPER = row.operator('hisanim.allclsupdate', text='Update '+i, icon_value=icons.id('tfupdater'))
            OPER.UPDATE = i
            row = layout.row()
        layout.label(text='Note! Allclass will take much longer!')

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
        except:
            print(f'No existing .blend file found for {self.UPDATE}!')
            try:
                x = [i.name for i in context.preferences.filepaths.asset_libraries]
                print(x)
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
        LINK = f'https://bitbucket.org/hisanimations/tf2collection/raw/main/{self.UPDATE}cosmetics.zip'
        print(f'Downloading {self.UPDATE} from BitBucket...')
        dload.save(LINK)
        print(f'{self.UPDATE}.zip downloaded!')
        print('Updating master.json...')
        dload.save('https://bitbucket.org/hisanimations/tf2collection/raw/main/master.json', overwrite=True)#, DLOADTO)
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
        except:
            try:
                PATHS.FPATHS[self.UPDATE] = bpy.context.preferences.filepaths.asset_libraries['scout'].path.replace(r'\\', '/') + "/"
                GET = PATHS.FPATHS[self.UPDATE]
                print(GET)
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
        LINK = f'https://bitbucket.org/hisanimations/tf2collection/raw/main/{self.UPDATE}.zip'
        print(f'Downloading {self.UPDATE} from BitBucket...')
        dload.save(LINK)
        print(f'{self.UPDATE}.zip downloaded!')
        print('Updating master.json...')
        dload.save('https://bitbucket.org/hisanimations/tf2collection/raw/main/master.json', overwrite=True)#, DLOADTO)
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


def register():
    bpy.utils.register_class(HISANIM_PT_UPDATER)
    bpy.utils.register_class(HISANIM_OT_CLSUPDATE)
    bpy.utils.register_class(HISANIM_OT_ALLCLSUPDATE)
def unregister():
    bpy.utils.unregister_class(HISANIM_PT_UPDATER)
    bpy.utils.unregister_class(HISANIM_OT_CLSUPDATE)
    bpy.utils.unregister_class(HISANIM_OT_ALLCLSUPDATE)