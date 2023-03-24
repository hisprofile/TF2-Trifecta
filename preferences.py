import bpy, os, glob

from pathlib import Path

from bpy.props import (StringProperty, CollectionProperty,
                                        IntProperty, EnumProperty,
                                        BoolProperty)
from bpy.types import (UIList, PropertyGroup,
                                        AddonPreferences, Operator)
names = ['scout', 'soldier', 'pyro', 'demo', 'heavy', 'engineer', 'medic', 'sniper', 'spy', 'allclass2', 'allclass3', 'allclass', 'weapons', 'TF2-V3']

class AssetPaths(PropertyGroup):
    def get_path(self):
        return self.get("path", "")
    def set_path(self, value):
        #print('setting path')
        prefs = bpy.context.preferences.addons[__package__].preferences
        value = bpy.path.abspath(value)
        self["path"] = value
        name = os.path.basename(value)
        if value == '':
            self.this_is = 'EMPTY'
        elif name.endswith('.blend'):
            self.this_is = 'BLEND'
        elif os.path.exists(value[:value.rfind('.') if '.' in value else None]):
            self.this_is = 'FOLDER'
        else:
            self.this_is = 'UNKNOWN'
        name = name[:name.rfind('.') if "." in name else None]
        self['name'] = name

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
        default='Path:'
    )

    toggle: BoolProperty(
        default=False
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
            layout.label(icon=ICON)
            if item.toggle:
                layout.prop(item, "name", emboss=True, icon_value=icon, icon_only=True)
                layout.prop(item, 'toggle', icon='DOT', text='', emboss=True)
            else:
                layout.prop(item, "path", emboss=False, icon_value=icon, icon_only=True)
                if item == paths[pathsindex]:
                    layout.prop(item, 'toggle', icon='RADIOBUT_ON' if paths[pathsindex] == item else 'RADIOBUT_OFF', text='', emboss=True)
                else:
                    layout.label(icon='RADIOBUT_OFF')     

        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text='')

class hisanimFilePaths(AddonPreferences):
    bl_idname = __package__
    hisanim_paths: CollectionProperty(type=AssetPaths)
    hisanim_pathsindex: IntProperty(default=0)
    autonaming: BoolProperty(default=True)
    is_executed: BoolProperty(default=False)
    
    def draw(self, context):
        if not self.is_executed:
            runpullpath()
            self.is_executed = True
        prefs = bpy.context.preferences.addons[__package__].preferences
        paths = prefs.hisanim_paths
        layout = self.layout
        row = layout.row()
        row.template_list('HISANIM_UL_ASSETS', 'Asset Paths',
                self, 'hisanim_paths',
                self, 'hisanim_pathsindex')
        row = row.column(align=True)
        row.operator('hisanim.addpath', icon='ADD', text='')
        row.operator('hisanim.removepath', icon='REMOVE', text='')
        row.operator('hisanim.pullpath', icon='IMPORT', text='')
        row.separator()
        row = row.column()
        row.operator('hisanim.detectpath', icon='VIEWZOOM', text='')
        row.enabled = True if len(paths) > 0 else False    

class HISANIM_OT_DETECTPATH(Operator):
    bl_idname = 'hisanim.detectpath'
    bl_label = 'Detect Paths'
    bl_description = 'If the required assets for the TF2-Trifecta are relative to your selected entry, the addon will attempt to locate them'

    def execute(self, context):
        prefs = context.preferences.addons[__package__].preferences
        paths = prefs.hisanim_paths
        pathsindex = prefs.hisanim_pathsindex
        selectedpath = paths[pathsindex].path

        parent = Path(selectedpath).parents[0]
        parent2 = Path(selectedpath).parents[1]
        
        for i in glob.glob('*.blend', root_dir=parent):
            path = os.path.join(parent, i)
            name = os.path.basename(path)
            name = name[:name.rfind('.')]
            for file in names:
                if file in name and paths.get(file) == None:
                    newitem = paths.add()
                    newitem.path = path
                    newitem.name = file

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
        runpullpath()
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
    
class HISANIM_OT_REMOVEPATH(Operator):
    bl_idname = 'hisanim.removepath'
    bl_label = 'Remove Path'
    bl_description = 'Remove the selected path'

    def execute(self, context):
        prefs = context.preferences.addons[__package__].preferences
        prefs.hisanim_paths.remove(prefs.hisanim_pathsindex)
        prefs.hisanim_pathsindex = min(len(prefs.hisanim_paths) - 1, prefs.hisanim_pathsindex)
        return {'FINISHED'}


classes = [HISANIM_UL_ASSETS,
        AssetPaths,
        hisanimFilePaths,
        HISANIM_OT_ADDPATH,
        HISANIM_OT_REMOVEPATH,
        HISANIM_OT_DETECTPATH,
        HISANIM_OT_PULLPATH]

def runpullpath():
    prefs = bpy.context.preferences.addons[__package__].preferences
    paths = prefs.hisanim_paths
    libraries = bpy.context.preferences.filepaths.asset_libraries
    for i in names[:-1]:
        if (assetpath := libraries.get(i)) != None and paths.get(i) == None:
            path = glob.glob('*.blend', root_dir=assetpath.path)
            if len(path) == 0:
                continue
            path = path[0]
            newitem = paths.add()
            newitem.path = assetpath.path + '/' + path
            newitem.name = assetpath.name

    if libraries.get('TF2-V3') != None:
        assetpath = libraries.get('TF2-V3')

        newitem = paths.add()
        newitem.path = assetpath.path
        newitem.name = assetpath.name

def register():
    for i in classes:
        bpy.utils.register_class(i)
    
def unregister():
    for i in classes:
        bpy.utils.unregister_class(i)