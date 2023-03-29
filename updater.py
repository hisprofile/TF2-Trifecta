import bpy, os, shutil, shutil, glob
from pathlib import Path
from . import dload, icons, mercdeployer, addonUpdater
import zipfile
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
        row = layout.row()
        row.operator('hisanim.hectorisupdate')
        layout.label(text='Face Panel + Phonemes Rigs by Hectoris919')
        layout.label(text='Open the console to view progress!')
        row = layout.row()
        row.operator('hisanim.addonupdate', icon_value=icons.id('tfupdater'))
        row = layout.row()
        row.prop(context.scene.hisanimvars, 'savespace')
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
            DLOADTO = GET.path[:GET.path.rfind('/')+1]
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
        #RefreshPaths()
        '''try:
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
                return {'CANCELLED'}'''
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
        if switch == False:
            print(f"Deleting old file from {GET.path}...")
            if os.path.exists(GET.path):
                os.remove(GET.path)
                print('Deleted!')
            else:
                print("Nothing to delete!")
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
        '''for i in files:
            try:
                os.remove(f'{DLOADTO + i}.blend')
                print(f'Deleted {i}.blend')
            except:
                print(f'Could not delete {i}.blend!')'''
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