import bpy, os, glob, time
from bpy_extras.io_utils import ImportHelper
from pathlib import Path

from . import updater, icons

from bpy.props import (StringProperty, CollectionProperty,
                        IntProperty, EnumProperty,
                        BoolProperty, PointerProperty)
from bpy.types import (UIList, PropertyGroup,
                        AddonPreferences, Operator)
names = ['scout', 'soldier', 'pyro', 'demo', 'heavy', 'engineer', 'medic', 'sniper', 'spy', 'allclass2', 'allclass3', 'allclass', 'weapons']

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

def format_size(size_in_bytes):
    """
    Convert size in bytes to a human-readable format.
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_in_bytes < 1024.0:
            return f"{size_in_bytes:.2f} {unit}"
        size_in_bytes /= 1024.0

def enumRigs(a = None, b = None):
    prefs = bpy.context.preferences.addons[__package__].preferences
    if prefs == None: return None
    rigs = prefs.rigs

    '''bpy.types.Scene.trifectarigs = EnumProperty(
        items=(
            (i.name, i.name, '', '', n) for n, i in enumerate(rigs)
        ),
        name = 'Rigs'
    )'''

class AssetPaths(PropertyGroup):
    def get_path(self):
        return self.get("path", "")
    def set_path(self, value):
        value = bpy.path.abspath(value)
        self["path"] = value
        name = os.path.basename(value)
        if value == '':
            self.this_is = 'EMPTY'
        elif os.path.isfile(value) and name.endswith('.blend'):
            self.this_is = 'BLEND'
            name = name[:name.rfind('.') if "." in name else None]
            if 'cosmetics' in name: name = name.replace('cosmetics', '')
        elif os.path.isdir(value):
            self.this_is = 'FOLDER'
            name = os.path.basename(Path(value))
        else:
            self.this_is = 'UNKNOWN'
        
        self.name = name

    path: StringProperty(
        default = '',
        subtype = 'FILE_PATH',
        get=get_path,
        set=set_path
    )
    
    this_is: EnumProperty(
        items=(
            ('EMPTY', 'Empty', '', 0),
            ('BLEND', '.blend file', 'This is a .blend file', 'BLENDER', 1),
            ('FOLDER', 'Folder', 'This is a folder', 'FILE_FOLDER', 2),
            ('UNKNOWN', 'Unknown', 'This entry is unknown', 'QUESTION', 3)
        ),
        name='Type'
    )

    name: StringProperty(
        default='New Entry'
    )

class rigs(PropertyGroup):
    name: StringProperty(
        default='Rigs', update=enumRigs
    )
    path: StringProperty(
        default = '',
        subtype = 'DIR_PATH'
    )

class HISANIM_UL_ASSETS(UIList):

    def draw_item(self, context,
            layout, data,
            item, icon,
            active_data, active_propname,
            index):
        prefs = context.preferences.addons[__package__].preferences
        paths = prefs.hisanim_paths
        pathsindex = prefs.hisanim_pathsindex

        if item.this_is == 'EMPTY':
            ICON = 'BLANK1'
        elif item.this_is == 'BLEND':
            ICON = 'BLENDER'
        elif item.this_is == 'FOLDER':
            ICON = 'FILE_FOLDER'
        else:
            ICON = 'QUESTION'

        if item != paths[pathsindex]:
            item.toggle = False

        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            row = layout.row()
            if ICON != 'BLANK1':
                row.label(icon=ICON)
            if ICON == 'FILE_FOLDER':
                row.alert = time.time() % 1 < 0.5
                op = row.operator('trifecta.textbox', text ='', icon='ERROR')
                op.text = 'If you were trying to add a set of rigs, do it in the window below. If you were trying to add a cosmetic file instead, select the .blend file.'
                op.icons = 'ERROR'
                op.size = '56'
                op.width = 310
            if item == paths[pathsindex]:
                row.prop(item, "name", text='')
            else:
                row.label(text=item.name)

        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text='')

class HISANIM_UL_RIGS(UIList):

    def draw_item(self, context,
            layout, data,
            item, icon,
            active_data, active_propname,
            index):
        prefs = context.preferences.addons[__package__].preferences
        rigs = prefs.rigs
        rigsindex = prefs.rigsindex

        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            row = layout.row()
            row.label(icon='ARMATURE_DATA', text='')
            if item == rigs[rigsindex]:
                row.prop(item, 'name', text='')
            else:
                row.label(text=item.name)

        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text='')

class ridOf(PropertyGroup):
    name: StringProperty(default='')
    index: IntProperty(default=0)

class hisanimFilePaths(AddonPreferences):
    bl_idname = __package__
    prefs = bpy.context.preferences.addons[__package__].preferences
    hisanim_paths: CollectionProperty(type=AssetPaths)
    rigs: CollectionProperty(type=rigs)
    hisanim_pathsindex: IntProperty(default=0, options=set())
    rigsindex: IntProperty(default=0, options=set())
    is_executed: BoolProperty(default=False, options=set())
    remove: CollectionProperty(type=ridOf)
    runonce_removepaths: IntProperty(default=0, options=set()) 
    missing: bpy.props.BoolProperty(default=True, options=set())
    quickswitch: bpy.props.BoolProperty(default=True, options=set(), name='Quick Switch', description='Replace the tool dropdown with a set of buttons')
    
    def draw(self, context):
        prefs = context.preferences.addons[__package__].preferences
        paths = prefs.hisanim_paths
        rigs = prefs.rigs
        version = bpy.app.version
        props = context.scene.trifecta_updateprops
        remaining = [i for i in names if paths.get(i) == None]
        layout = self.layout
        layout = layout.box()
        layout.label(text='Cosmetics & Weapons', icon='MOD_CLOTH')
        if len(remaining) > 0:
            row = layout.row()
            row.alert = True
            row.label(text='Missing entries:', icon = 'ERROR') if len(remaining) != 1 else row.label(text='Missing entry:', icon='ERROR')
            row = layout.row()
            row.label(text=f'{", ".join(remaining)}')
            row=layout.row()
            self.missing = True
        else:
            self.missing = False
        row = layout.row()
        row.template_list('HISANIM_UL_ASSETS', 'Asset Paths',
                self, 'hisanim_paths',
                self, 'hisanim_pathsindex')
        row = row.column(align=True)
        row.operator('hisanim.addpath', icon='ADD', text='')
        row.operator('hisanim.removepath', icon='REMOVE', text='')
        row.separator()
        row.operator('hisanim.detectpath', text='', icon='VIEWZOOM')
        row = layout.row()
        if len(prefs.hisanim_paths) != 0:
            row.prop(paths[prefs.hisanim_pathsindex], 'path', text='Path')
        row = layout.row()
        row.operator('trifecta.pathhelp')
        row.operator('hisanim.detectpath', text='Add Paths from Asset', icon='VIEWZOOM')
        row.operator('trifecta.batchadd', text='Add Paths from Folder', icon='VIEWZOOM')
        layout = self.layout
        norigs = len(prefs.rigs) < 1
        layout = layout.box()
        layout.label(text='Rigs', icon='ARMATURE_DATA')
        if norigs:
            layout.alert = True
            layout.label(text='No rigs have been added! Add a folder of rigs!', icon='ERROR')
            layout.alert = False
        row = layout.row()
        row.template_list('HISANIM_UL_RIGS', 'Rigs',
                self, 'rigs',
                self, 'rigsindex')
        col = row.column(align=True)
        col.operator('hisanim.addrig', text='', icon='ADD')
        col.operator('hisanim.removerig', text='', icon='REMOVE')
        if len(prefs.hisanim_paths) != 0:
            layout.prop(rigs[prefs.rigsindex], 'path', text='Path')

        if props.active:
            row = layout.row()
            row.label(text=props.stage)
            row.label(text=str(format_size(props.size)))
            if props.updateAll:
                row.label(text=f'{list(ids.keys())[props.iter].title()}, {props.iter + 1}/14')
            if version[0] > 3:
                row.progress(text='', type='RING', factor=props.var)
            else:
                row.label(text='.'*int(((time.time()*3)%3) + 1))
            layout.row().label(text='Do not close this window!')
        else:
            pass

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

        box = layout.box()
        box.label(text='Download Rigs')
        op = box.row().operator('trifecta.update', text='Download Rigs', icon_value=icons.id('tfupdater'))
        op.operation = 'ZIP'
        box.row().prop(props, 'newRigEntry')
        if props.newRigEntry:
            box.row().prop(props, 'newRigName')
            box.row().prop(props, 'newRigPath')

        

class HISANIM_OT_BATCHADD(Operator):
    bl_idname = 'trifecta.batchadd'
    bl_label = 'Batch Add'
    bl_description = ''

    filepath: StringProperty(name='filepath', subtype='DIR_PATH')

    def execute(self, context):
        prefs = bpy.context.preferences.addons[__package__].preferences
        paths = prefs.hisanim_paths

        mercs = ['scout', 'soldier', 'pyro', 'demo', 'heavy', 'engineer', 'medic', 'sniper', 'spy']
        misc = ['allclass', 'allclass2', 'allclass3', 'weapons']

        path = self.filepath
        for merc in mercs:
            if paths.get(merc) != None: continue
            f_path = os.path.join(path, f'{merc}/{merc}cosmetics.blend')
            if os.path.exists(f_path):
                new = paths.add()
                new.path = f_path
                new.name = merc
        
        for m in misc:
            if paths.get(m) != None: continue
            f_path = os.path.normpath(os.path.join(path, f'{m}/{m}.blend'))
            if os.path.exists(f_path):
                new = paths.add()
                new.path = f_path
                new.name = m
        
        return {'FINISHED'}
    
    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

class HISANIM_OT_DETECTPATH(Operator):
    bl_idname = 'hisanim.detectpath'
    bl_label = 'Detect Paths'
    bl_description = 'If the required assets for the TF2-Trifecta are relative to your selected entry, the addon will attempt to locate them'

    def execute(self, context):
        prefs = context.preferences.addons[__package__].preferences
        paths = prefs.hisanim_paths

        if len(paths) == 0:
            self.report({'ERROR'}, "Add at least one asset! This asset's path will be used to search for other assets!")
            return {'CANCELLED'}

        pathsindex = prefs.hisanim_pathsindex
        selectedpath = paths[pathsindex].path

        parent = Path(selectedpath).parents[0]
        parent2 = Path(selectedpath).parents[1]

        for i in glob.glob('**/*.blend', root_dir=parent2):
            path = os.path.join(parent2, i)
            name = os.path.basename(path)
            name = name[:name.rfind('.')]
            for file in names:
                if file in name and paths.get(file) == None:
                    newitem = paths.add()
                    newitem.path = path
                    newitem.name = file

        for i in [parent, parent2]:
            for folder in glob.glob('./**/', root_dir=i):
                folder = folder[2:-1]
                path = os.path.join(i, folder)
                name = os.path.basename(path)
                for file in names:
                    if file in name and paths.get(file) == None:
                        newitem = paths.add()
                        newitem.path = path
                        newitem.name = file

        prefs.autonaming = False
        return {'FINISHED'}

class HISANIM_OT_PULLPATH(Operator):
    bl_idname = 'hisanim.pullpath'
    bl_label = 'Pull Paths'
    bl_description = 'Pull existing paths from asset browser.'

    def execute(self, context):
        #runpullpath()
        return {'FINISHED'}

class HISANIM_OT_ADDPATH(Operator, ImportHelper):
    bl_idname = 'hisanim.addpath'
    bl_label = 'Add Path'
    bl_description = 'Add a path for the TF2-Trifecta to search through'

    filter_glob: StringProperty(
        default="*.blend",
        options={'HIDDEN'},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        if not os.path.basename(self.filepath).endswith('.blend'):
            self.report({'ERROR'}, 'Add a .blend file!')
            return {'CANCELLED'}
        prefs = context.preferences.addons[__package__].preferences
        new = prefs.hisanim_paths.add()
        new.path = self.filepath
        prefs.hisanim_pathsindex = len(prefs.hisanim_paths) - 1
        bpy.ops.hisanim.detectpath()
        return {'FINISHED'}

class HISANIM_OT_ADDRIG_1(Operator, ImportHelper):
    bl_idname = 'hisanim.addrig'
    bl_label = 'Add Rig'
    bl_description = 'Add a path for the TF2-Trifecta to search through'

    def invoke(self, context, event):
        result = context.window_manager.invoke_props_dialog(self, width=450)
        return result
    
    def draw(self, context):
        layout = self.layout
        layout.row().label(text='Ensure that the folder you add has the nine .blend files DIRECTLY in that folder!')

    def execute(self, context):
        bpy.ops.hisanim.addrig_final('INVOKE_DEFAULT')
        return {'FINISHED'}
    
class HISANIM_OT_ADDRIG_2(Operator, ImportHelper):
    bl_idname = 'hisanim.addrig_final'
    bl_label = 'Add Rig'
    bl_description = 'Add a path for the TF2-Trifecta to search through'

    filter_glob: StringProperty(
        default="*.Blol",
        options={'HIDDEN'},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )

    filename: StringProperty()
    directory: StringProperty()

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        filepath = self.directory
        if not os.path.isfile(os.path.join(filepath,'scout.blend')):
            self.report({'ERROR'}, 'The folder you have chosen does not contain the nine rigs inside!')
            return {'CANCELLED'}
        prefs = context.preferences.addons[__package__].preferences
        new = prefs.rigs.add()
        new.name = 'Rigs'
        new.path = self.filepath
        prefs.rigsindex = len(prefs.rigs) - 1
        enumRigs()
        return {'FINISHED'}

class HISANIM_OT_REMOVEPATH(Operator):
    bl_idname = 'hisanim.removepath'
    bl_label = 'Remove Path'
    bl_description = 'Remove the selected path'

    def execute(self, context):
        prefs = context.preferences.addons[__package__].preferences
        prefs.hisanim_paths.remove(prefs.hisanim_pathsindex)
        prefs.hisanim_pathsindex = min(len(prefs.hisanim_paths) - 1, prefs.hisanim_pathsindex)
        return {'FINISHED'}

class HISANIM_OT_REMOVERIG(Operator):
    bl_idname = 'hisanim.removerig'
    bl_label = 'Remove Rig'
    bl_description = 'Remove the selected path'

    def execute(self, context):
        prefs = context.preferences.addons[__package__].preferences
        prefs.rigs.remove(prefs.rigsindex)
        prefs.rigsindex = min(len(prefs.rigs) - 1, prefs.rigsindex)
        enumRigs()

        return {'FINISHED'}

class PREF_OT_pathhelp(Operator):
    bl_idname = 'trifecta.pathhelp'
    bl_label = 'Help Setup Paths'
    bl_description = "If you're having issues setting up your entries, this operator should help you"

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=800)
    
    def draw(self, context):
        mercs = ['scout', 'soldier', 'pyro', 'demo', 'heavy', 'engineer', 'medic', 'sniper', 'spy']
        misc = ['allclass', 'allclass2', 'allclass3', 'weapons']

        layout = self.layout
        prefs = context.preferences.addons[__package__].preferences
        if len(prefs.hisanim_paths) == 0:
            layout.label(text='Add an asset to get started!')
            return
        asset = prefs.hisanim_paths[prefs.hisanim_pathsindex]
        if asset.this_is == 'BLEND':
            path = Path(asset.path).parents[1]
        elif asset.this_is == 'FOLDER':
            path = Path(asset.path).parent
        else:
            layout.label(text='The path to active asset does not exist!')
            return
        
        path = os.path.normpath(path)
        layout.label(text='Based on the active asset, your paths should be set up like this:')
        for merc in mercs:
            t_path = os.path.normpath(os.path.join(path, f'{merc}/{merc}cosmetics.blend'))
            layout.row().label(text=f'"{merc}" : {t_path}')
        
        for m in misc:
            t_path = os.path.normpath(os.path.join(path, f'{m}/{m}.blend'))
            layout.row().label(text=f'"{m}" : {t_path}')

    def execute(self, context):
        return {'FINISHED'}


classes = [HISANIM_UL_ASSETS,
        HISANIM_UL_RIGS,
        AssetPaths,
        rigs,
        ridOf,
        hisanimFilePaths,
        HISANIM_OT_ADDPATH,
        HISANIM_OT_REMOVEPATH,
        HISANIM_OT_ADDRIG_1,
        HISANIM_OT_ADDRIG_2,
        HISANIM_OT_REMOVERIG,
        HISANIM_OT_DETECTPATH,
        HISANIM_OT_PULLPATH,
        PREF_OT_pathhelp,
        HISANIM_OT_BATCHADD,
        ]



def register():
    for i in classes:
        bpy.utils.register_class(i)
    prefs = bpy.context.preferences.addons[__package__].preferences
    if (p := prefs.hisanim_paths.get('TF2-V3')) != None:
        p.name = 'rigs'
    if (p := prefs.hisanim_paths.get('rigs')) != None:
        new = prefs.rigs.add()
        new.name = p.name
        new.path = p.path
        prefs.hisanim_paths.remove(prefs.hisanim_paths.find('rigs'))
        prefs.hisanim_pathsindex = min(len(prefs.hisanim_paths) - 1, prefs.hisanim_pathsindex)
    enumRigs()
    
def unregister():
    for i in classes:
        bpy.utils.unregister_class(i)