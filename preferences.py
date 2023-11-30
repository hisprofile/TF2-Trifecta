import bpy, os, glob
from bpy_extras.io_utils import ImportHelper
from pathlib import Path

from bpy.props import (StringProperty, CollectionProperty,
                        IntProperty, EnumProperty,
                        BoolProperty)
from bpy.types import (UIList, PropertyGroup,
                        AddonPreferences, Operator)
names = ['scout', 'soldier', 'pyro', 'demo', 'heavy', 'engineer', 'medic', 'sniper', 'spy', 'allclass2', 'allclass3', 'allclass', 'weapons', 'rigs']

class AssetPaths(PropertyGroup):
    def get_path(self):
        return self.get("path", "")
    def set_path(self, value):
        bak = self.name
        value = bpy.path.abspath(value)
        self["path"] = value
        name = os.path.basename(value)
        if value == '':
            self.this_is = 'EMPTY'
        elif name.endswith('.blend') and os.path.exists(value):
            self.this_is = 'BLEND'
            name = name[:name.rfind('.') if "." in name else None]
            if 'cosmetics' in name: name = name.replace('cosmetics', '')
        elif os.path.exists(value[:value.rfind('.') if '.' in value else None]):
            self.this_is = 'FOLDER'
            if name == 'New Entry':
                name = os.path.basename(Path(value))
            else:
                name = bak
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
    prefs = bpy.context.preferences.addons[__package__].preferences
    name: StringProperty(
        default='Rigs'
    )
    path: StringProperty(
        default = '',
        subtype = 'FILE_PATH'
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
            row.label(text=item.name)

        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text='')

class ridOf(PropertyGroup):
    name: StringProperty(default='')
    index: IntProperty(default=0)

class hisanimFilePaths(AddonPreferences):
    bl_idname = __package__
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
        prefs = bpy.context.preferences.addons[__package__].preferences
        paths = prefs.hisanim_paths
        remaining = [i for i in names if paths.get(i) == None]
        layout = self.layout
        layout.row().label(text='Every entry needs to end in .blend, except for "rigs". "rigs" needs to be a folder.')
        layout.row().label(text='''Don't use the name "TF2-V3" anymore, use "rigs" instead.''')
        layout.row().label(text='Names are held in the window below.')
        if len(remaining) > 0:
            row = layout.row()
            row.label(text='Missing entries:') if len(remaining) != 1 else row.label(text='Missing entry:')
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
        row = layout.row()
        row.template_list('HISANIM_UL_RIGS', 'Asset Paths',
                self, 'rigs',
                self, 'rigsindex')
        col = row.column(align=True)
        col.operator('hisanim.addrig', text='', icon='ADD')
        col.operator('hisanim.removerig', text='', icon='REMOVE')

class HISANIM_OT_BATCHADD(Operator):
    bl_idname = 'trifecta.batchadd'
    bl_label = 'Batch Add'
    bl_description = ''

    filepath: StringProperty(name='filepath', subtype='FILE_PATH')

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
        
        if paths.get('rigs') != None: return {'FINISHED'}

        if os.path.exists(os.path.join(path, 'TF2-V3')):
            new = paths.add()
            new.path = os.path.join(path, 'TF2-V3')
            new.name = 'rigs'
        
        if os.path.exists(os.path.join(path, 'rigs')):
            new = paths.add()
            new.path = os.path.join(path, 'rigs')
            new.name = 'rigs'
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

class HISANIM_OT_ADDPATH(Operator):
    bl_idname = 'hisanim.addpath'
    bl_label = 'Add Path'
    bl_description = 'Add a path for the TF2-Trifecta to search through'

    def execute(self, context):
        prefs = context.preferences.addons[__package__].preferences
        prefs.hisanim_paths.add()
        prefs.hisanim_pathsindex = len(prefs.hisanim_paths) - 1
        return {'FINISHED'}
    
class HISANIM_OT_ADDRIG(Operator, ImportHelper):
    bl_idname = 'hisanim.addrig'
    bl_label = 'Add Rig'
    bl_description = 'Add a path for the TF2-Trifecta to search through'

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=450)
    
    def draw(self, context):
        layout = self.layout
        layout.row().label(text='Ensure that the folder you add has the nine .blend files DIRECTLY in that folder')

    def execute(self, context):
        prefs = context.preferences.addons[__package__].preferences
        prefs.rigs.add()
        prefs.rigsindex = len(prefs.rigs) - 1
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
        rigs = ['rigs']

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
        layout.row().label(text=f'"rigs" : {os.path.normpath(os.path.join(path, "rigs"))}')

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
        HISANIM_OT_ADDRIG,
        HISANIM_OT_REMOVERIG,
        HISANIM_OT_DETECTPATH,
        HISANIM_OT_PULLPATH,
        PREF_OT_pathhelp,
        HISANIM_OT_BATCHADD]


def register():
    for i in classes:
        bpy.utils.register_class(i)
    prefs = bpy.context.preferences.addons[__package__].preferences
    if (p := prefs.hisanim_paths.get('TF2-V3')) != None:
        p.name = 'rigs'
        print(p.name, 'success')
    if (p := prefs.hisanim_paths.get('rigs')) != None:
        new = prefs.rigs.add()
        new.name = p.name
        new.path = p.path
        prefs.hisanim_paths.remove(prefs.hisanim_paths.find('rigs'))
        prefs.hisanim_pathsindex = min(len(prefs.hisanim_paths) - 1, prefs.hisanim_pathsindex)
    
def unregister():
    for i in classes:
        bpy.utils.unregister_class(i)