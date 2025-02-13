import bpy, os, glob, time
from bpy_extras.io_utils import ImportHelper
from pathlib import Path

from . import updater, icons

from bpy.props import (StringProperty, CollectionProperty,
                        IntProperty, EnumProperty,
                        BoolProperty, PointerProperty)
from bpy.types import (UIList, PropertyGroup,
                        AddonPreferences, Operator)

from .panel import TRIFECTA_OT_genericText, textBox

ids = {
    'allclass1' :           '1JMHSJOHpCvZr_fYN9pZyXTCUZBTHq97m',
    'allclass2' :           '1JVKsEdeh-KH-bbnFstxz6QUCyuoSX7Ji',
    'allclass3' :           '1K3W7TyF1_BiAZmGBPe7QoNqDanAeTIJ1',
    'allclass4' :           '1Jm-SZ2ey6KU_oV0lgLYXG64Zw2092Mlc',
    'scout_cosmetics':      '1K5F6mD7Hz2RvKsBK5bm85H73Wd-zKrr7',
    'soldier_cosmetics':    '1KYZtQfyyFweYe22RMr2Y9ZYj01T6NfNr',
    'pyro_cosmetics':       '1JgsFhO-4ZOgFFvfYCIqTKDBo4CGd24v3',
    'demo_cosmetics' :      '1JWk1EK5PYZeAymmmiHloXzNPDZpSDiy-',
    'heavy_cosmetics':      '1JhfZOSS59D4s_Sd-cy-caIOkG1t8HUNx',
    'engineer_cosmetics':   '1JZ698JsOEZUJhYJCojOyafeHv-TQplEm',
    'medic_cosmetics':      '1JiPKKH2haiAdp2f3Rxngoqrsasu4Z9xK',
    'sniper_cosmetics':     '1KH97j5-VlxINLKPyx1bzjbdQo8IJh9fV',
    'spy_cosmetics':        '1KYibE4impR16PTnbiUF4VKbznw037wdq',
    'taunts_items':         '1K942RdNallqPmsHrSIlEBcwJN6ERuwMl',
    'weapons1':             '1Kw8SbHJCg7hBqVmBpphAQ32pex6NJrVb',
    'weapons2':             '1L-lq8q22hzakOKYR-BknZ75zJh29HJhk',
    'weapons3':             '1KbtVukiZ_xhFtbJf7P8ZW6VgfTEs5Fjx',
    '_resources':           '1-CWfEMCgrr-qQD8ifn9sA2qXk_YgdSzd',
}

rigs_ids = {
        'hisanimations': ('1lm48_APPInSeW8A1M8wOfCi14XgMlaBd', 'The standard set of rigs, and most supported by the TF2-Trifecta'),
        'Eccentric': ('1-MboVZ3PZ471AmXYHnYegoXozKd8OmVU', 'Includes control points overlayed on the face to pose'),
        'ThatLazyArtist': ('1-MVdFejB1wtO4v2zcurCMIK6MPxNvRTs', 'Includes a panel of sliders to pose the face'),
        'MvM Robots': ('11dZ5KiVHPB0QQSNES5GRFwVGJjB1O_iO', 'The robots from MvM with Rigify rigs'),
        'Ragdoll Rigs': ('1NDj-JbGnxQSCVuDyhklC7TPNGeovskR5', 'A set of ragdoll rigs for funny stuff'),
    }

order = {
    'Scout': 1,
    'Soldier': 2,
    'Pyro': 3,
    'Demo': 4,
    'Heavy': 5,
    'Engineer': 6,
    'Medic': 7,
    'Sniper': 8,
    'Spy': 9,
    'Allclass': 10,
    'Taunts': 11,
    'Weapons': 12,
}

VALIDATION = False

def set_abspath(self, value):
    self['items_path'] = bpy.path.abspath(value)

def get_selfpath(self):
    return self['items_path']

def on_start():
    bpy.app.timers.unregister(on_start)
    return None

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
        default='Rigs'
    )
    path: StringProperty(
        default = '',
        subtype = 'DIR_PATH'
    )

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

class HISANIM_UL_BLENDS(UIList):

    def draw_item(self, context,
            layout: bpy.types.UILayout, data,
            item, icon,
            active_data, active_propname,
            index):
        prefs = context.preferences.addons[__package__].preferences
        rigs = prefs.rigs
        rigsindex = prefs.rigsindex

        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            ICON = 'BLENDER' if not item.no_search else 'ASSET_MANAGER'
            split = layout.split(factor=0.8)
            split.label(text=item.name, icon=ICON)
            split.alignment = 'EXPAND'
            split = split.split()
            op = split.operator('trifecta.scan')
            op.blend = index
            op.revalidate = False
            op.scan_all = False
            op.prompt = False

        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text='')

class HISANIM_UL_ASSETS(UIList):

    def draw_item(self, context,
            layout, data,
            item, icon,
            active_data, active_propname,
            index):
        prefs = context.preferences.addons[__package__].preferences
        rigs = prefs.rigs
        rigsindex = prefs.rigsindex

        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            ICON = 'OBJECT_DATA'
            layout.label(text=item.name, icon=ICON)

        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text='')

class assets(PropertyGroup):
    name: StringProperty(default='')
    reference: StringProperty(default='')
    tag: StringProperty(default='')
    style: StringProperty(default='')
    mercenary: StringProperty(default='')
    blend: StringProperty(default='')

class blends(PropertyGroup):
    assets: CollectionProperty(type=assets)
    asset_index: IntProperty(min=0, options=set())
    drive_id: StringProperty(default='')
    path: StringProperty(subtype='FILE_PATH')
    tag: StringProperty(default='')
    no_search: BoolProperty(default=False, options=set())
    validated: BoolProperty(default=False, options=set())
    time_validated: IntProperty()

class hisanimFilePaths(AddonPreferences):
    bl_idname = __package__
    #prefs = bpy.context.preferences.addons[__package__].preferences

    def set_abspath(self, value):
        self['path_temp'] = bpy.path.abspath(value)

    def get_selfpath(self):
        #print(dir(self))
        #import time
        #time.sleep(0.5)
        return self.path_temp#self.items_path#self['items_path']

    path_temp: StringProperty() # have to offload the get/set to another property or else RECURSION ERROR!!! :DDDD
    blends: CollectionProperty(type=blends)
    blends_index: IntProperty(min=0, options=set())
    blends_more_info: BoolProperty(default=False, name='More Info', description='Show more information about .blend files and the content they hold')

    rigs: CollectionProperty(type=rigs)
    rigsindex: IntProperty(default=0, options=set())
    hide_auto_exc_warning: BoolProperty(name='Hide Warning Anyways', default=False)
    is_executed: BoolProperty(default=False, options=set())
    runonce_removepaths: IntProperty(default=0, options=set())
    items_path: StringProperty(default='', subtype='DIR_PATH', name='TF2 Items Folder', description='Folder containing all cosmetics and weapons .blend files.',
                               set=set_abspath,
                               get=get_selfpath)
    missing: bpy.props.BoolProperty(default=True, options=set())
    hide_update_msg: BoolProperty(default=False, name='Hide Future Prompts')
    update_notice: BoolProperty(default=True, name='Notify for Future Updates')
    
    def draw(self, context):
        prefs = context.preferences.addons[__package__].preferences
        rigs = prefs.rigs
        version = bpy.app.version
        props = context.scene.trifecta_updateprops
        layout = self.layout
        if (not context.preferences.filepaths.use_scripts_auto_execute) and (not self.hide_auto_exc_warning):
            box = layout.box()
            row = box.row()
            row.alert = True
            row.label(text='"Auto Run Python Scripts" is currently turned off.')
            box.row().label(text='Having this option enabled ensures full articulation of faces when opening the file.')
            box.row().label(text='It is possible to enable full facial expressions later with the REFRESH button in the face poser.')
            box.row().label(text='With this option enabled, ALWAYS be aware of what .blend files you open.')
            box.row().label(text='You can disable it later in "Save & Load"')
            box.row().prop(context.preferences.filepaths, 'use_scripts_auto_execute', text='Auto Run Python Scripts')
            box.row().prop(self, 'hide_auto_exc_warning')


        op = layout.row().operator('trifecta.textbox', text="What's different in 3.0?", icon='QUESTION')
        op.text = '''The TF2-Trifecta has a new way of adding assets. Simply place all supported .blend files into a folder, then validate and scan for assets.
If you are a past user of the TF2-Trifecta, please note that all of the old assets are INCOMPATIBLE with any version starting from 3.0. Users are required to download the new cosmetic ports for full functionality of the addon.'''
        op.icons='QUESTION,ERROR'
        op.size='56,56'
        op.width=350

        layout = layout.box()
        row = layout.row()
        row.alignment = 'EXPAND'
        row.alert = False
        

        row.prop(self, 'items_path')

        op = layout.operator('trifecta.scan')
        op.scan_all = True
        op.text = 'Open the console if you wish to view the progress!'
        op.icons = 'CONSOLE'
        op.size = '56'
        op.width = 330
        op.prompt = True
        if len(self.blends) < 1:
            layout.row().label(text='No detected .blend files')
        else:
            layout.template_list('HISANIM_UL_BLENDS', 'TF2 Items',
                                 self, 'blends',
                                 self, 'blends_index')
            blend = self.blends[self.blends_index]
            layout.prop(self, 'blends_more_info', toggle=True)
            if self.blends_more_info:
                layout.template_list('HISANIM_UL_ASSETS', 'TF2 Items',
                                 blend, 'assets',
                                 blend, 'asset_index')

                layout.row().label(text=f'Path: {blend.path}')
                layout.row().label(text=f'Assets: {len(blend.assets)}')
                layout.row().label(text=f'Google Drive ID: {blend.drive_id}')
                layout.row().label(text=f'Tag: {blend.tag}')
                layout.row().label(text=f'Resource Only: {blend.no_search}')

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
        if len(prefs.rigs) != 0:
            layout.prop(rigs[prefs.rigsindex], 'path', text='Path')
        
        layout.separator(factor=1)
        layout.row().label(text='Install all of the required assets through the Scene Properties!', icon='SCENE_DATA')
        op = layout.row().operator('wm.url_open', text='More from me!', icon='URL')
        op.url = 'https://github.com/hisprofile/blenderstuff/tree/main'
        layout.row().prop(self, 'hide_update_msg')
        layout.row().prop(self, 'update_notice')

class HISANIM_OT_SCAN(TRIFECTA_OT_genericText):
    bl_idname = 'trifecta.scan'
    bl_label = 'Scan'
    bl_description = 'Combs through .blend files to look for spawnable items'

    prompt: BoolProperty(default=True)
    blend: IntProperty(name='.blend file', default=-1)
    scan_all: BoolProperty()
    revalidate: BoolProperty(default=False, name='Revalidate Existing .blends', description='When enabled, this will go through all files regardless if they have been validated.')

    def execute(self, context: bpy.types.Context):
        prefs = context.preferences.addons[__package__].preferences
        blends = prefs.blends
        if not os.path.exists(prefs.items_path):
            self.report({'ERROR'}, f'Your items path is invalid!')
            return {'CANCELLED'}
        
        def remove_lib(path: str):
            for library in bpy.data.libraries:
                if bpy.path.abspath(library.filepath) == path:
                    bpy.data.libraries.remove(library, do_unlink=True)
                    return
                
        def scan(path, blend_obj = None):
            if blend_obj:
                blend_obj.validated = False
            try:
                with bpy.data.libraries.load(path, link=True) as (F, T):
                    T.scenes = ['tag_data']
            except:
                self.report({'ERROR'}, f'Failed to open {path}')
                fail_count +=1
                remove_lib(path)
                return
            if T.scenes[0] == None:
                self.report({'WARNING'}, f'{path} missing scene "tag_data"')
                remove_lib(path)
                return
            scn = T.scenes[0]
            if not (tag := scn.get('tag')):
                self.report({'WARNING'}, f'{path} is not compatible with the TF2-Trifecta. Missing "tag" property on scene.')
                remove_lib(path)
                return
            if blend_obj == None:
                new_blend = blends.add()
            else:
                new_blend = blend_obj
            new_blend.name = os.path.basename(path)
            new_blend.path = path
            new_blend.tag = tag
            print(f'.blend is supported. Tag is {tag}.')
            if not (drive_id := scn.get('drive_id')):
                self.report({'WARNING'}, f'{path} has no "drive_id" property on scene! It cannot be updated!')
            else:
                print(f'.blend has drive ID {drive_id}')
                new_blend.drive_id = drive_id

            if scn.get('resource_only'):
                print(f'.blend is resource only')
                new_blend.no_search= True
            bpy.data.batch_remove(T.scenes)
            remove_lib(path)
            if new_blend.no_search:
                print('Finished with .blend')
                new_blend.validated = True
                return
            print('Loading objects...')
            with bpy.data.libraries.load(path, link=True, assets_only=True) as (F, T):
                T.objects = F.objects
            obj_count = 0
            valid_objs = []
            new_blend.assets.clear()
            for obj in sorted(T.objects, key=lambda a: a.name.lower()):
               
                asset = new_blend.assets.add()
                if obj.get('name_search_props') != None:
                    name = obj['tf_name']
                    if obj.get('style_name'):
                        asset.style = obj['style_name']
                        name += f', {obj["style_name"]}'
                    if obj.get('style_index') and not obj.get('style_name'):
                        asset.style = obj['style_index']
                        name += f', {obj["style_index"]}'
                    if obj.get('class'):
                        asset.mercenary = obj['class']
                        name += f', {obj["class"].title()}'
                    asset.name = name
                else:
                    asset.name = obj.name
                asset.reference = obj.name
                obj_count += 1
                valid_objs.append(obj)
                print('\033[F\033[K', end='', flush=True)
                print(f'Found {obj_count} object{"" if obj_count == 1 else "s"}')
            new_blend.validated = True
            print(f'.blend has {obj_count} spawnables.')
            print('Finished with .blend')
            bpy.data.batch_remove(T.objects)
            remove_lib(path)
            return

        fail_count = 0

        if self.scan_all:
            blend_files = list(map(lambda a: os.path.join(prefs.items_path, a), glob.glob('*.blend', root_dir=prefs.items_path)))
            if self.revalidate:
                for n, b in enumerate(blends):
                    blends.remove(0)
            else:
                existing_paths = tuple(blend.path for blend in blends)
                blend_files = list(filter(lambda a: not a in existing_paths, blend_files))
                for blend in prefs.blends:
                    if blend.validated == False: blend_files.append(blend.path)
            if len(list(blend_files)) == 0:
                self.report({'INFO'}, 'No new .blend files were validated')
            context.window_manager.progress_begin(0, 9999)
            for n, blend in enumerate(blend_files):
                context.window_manager.progress_update((n+1)*100+len(blend_files))
                blend_obj = blends.get(os.path.basename(blend))
                print(f'Opening {blend}...')
                scan(blend, blend_obj)
            
        else:
            blend_obj = blends[self.blend]
            blend = blend_obj.path
            print(f'Opening {blend}...')
            scan(blend, blend_obj)

        if fail_count > 0:
            self.report({'WARNING'}, 'Is it possible the files were extracted wrong?')
            self.report({'WARNING'}, f'{fail_count} .blend file{"" if fail_count == 1 else "s"} failed to validate. Open INFO to read more.')
        else:
            self.report({'INFO'}, 'All files validated and scanned!')
        context.window_manager.progress_end()
        return {'FINISHED'}
    
    def draw_extra(self, context):
        self.layout.row().prop(self, 'revalidate')

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

    #dirname: StringProperty()
    directory: StringProperty()

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        filepath = self.directory
        if not os.path.isfile(os.path.join(filepath,'scout.blend')):
            self.report({'ERROR'}, 'The folder you have chosen does not contain the nine rigs inside!')
            #return {'CANCELLED'}
        prefs = context.preferences.addons[__package__].preferences
        new = prefs.rigs.add()
        new.name = 'Rigs'
        new.path = filepath
        prefs.rigsindex = len(prefs.rigs) - 1
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

classes = [
        assets,
        blends,
        HISANIM_UL_ASSETS,
        HISANIM_UL_RIGS,
        HISANIM_UL_BLENDS,
        AssetPaths,
        rigs,
        hisanimFilePaths,
        HISANIM_OT_ADDRIG_1,
        HISANIM_OT_ADDRIG_2,
        HISANIM_OT_REMOVERIG,
        HISANIM_OT_SCAN
        ]

def register():
    for i in classes:
        bpy.utils.register_class(i)
    bpy.app.timers.register(on_start)
    prefs = bpy.context.preferences.addons[__package__].preferences

def unregister():
    for i in classes:
        bpy.utils.unregister_class(i)