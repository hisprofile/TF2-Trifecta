import bpy
from .newuilist import paints
from bpy.types import (UIList)
from bpy.props import *
from . import faceposer, icons

def hasKey(obj, slider) -> bool:
        if bpy.context.scene.hisanimvars.noKeyStatus: return False
        data = obj.data
        if data.animation_data == None:
            return False
        
        scene = bpy.context.scene
        action = data.animation_data.action
        if action == None:
            return False
        
        curv = action.fcurves.find(f'["{slider.name}"]')
        if curv == None: return False
        for point in curv.keyframe_points:
            if faceposer.get_frame(bpy.context) == point.co.x:
                return True
        return False

class HISANIM_UL_SLIDERS(bpy.types.UIList):

    def filter_items(self, context, data, propname):
        props = context.scene.hisanimvars
        items = getattr(data, propname)
        filtered = [self.bitflag_filter_item] * len(items)
        for i, item in enumerate(items):
            if self.filter_name.lower() not in item.name.lower():
                filtered[i] &= ~self.bitflag_filter_item
                
            if props.up or props.mid or props.low:
                
                if item.Type == 'NONE':
                    filtered[i] &= ~self.bitflag_filter_item

                if item.Type == 'UPPER':
                    if not props.up:
                        filtered[i] &= ~self.bitflag_filter_item
                
                if item.Type == 'MID':
                    if not props.mid:
                        filtered[i] &= ~self.bitflag_filter_item

                if item.Type == 'LOWER':
                    if not props.low:
                        filtered[i] &= ~self.bitflag_filter_item

        return filtered, []

    def draw_item(self, context,
            layout, data,
            item, icon,
            active_data, active_propname,
            index):
        props = context.scene.hisanimvars
        isKeyed = hasKey(bpy.context.object, item)
        if context.scene.poselibVars.stage != 'SELECT':
            layout.row().label(text='Operation in progress.')
            return None
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            if item.split:
                row = layout.row(align=True)
                Name = item.name.split('_')[-1]

                if not item.realvalue:
                    row.alert = isKeyed
                    row.prop(item, 'value', slider=True, text=Name, expand=True)
                    row.alert = False
                else:
                    row.prop(props.activeface.data, f'["{item.R}"]', text='R')
                    row.prop(props.activeface.data, f'["{item.L}"]', text='L')
                
                op = row.operator('hisanim.keyslider', icon='DECORATE_KEYFRAME' if isKeyed else 'DECORATE_ANIMATE', text='', depress=isKeyed, emboss=False)
                #op.delete = isKeyed
                op.slider = item.name
                row.prop(item, 'realvalue', icon='RESTRICT_VIEW_OFF' if item.realvalue else 'RESTRICT_VIEW_ON', text='', emboss = False)

            else:
                row = layout.row(align=True)
                Name = item.name.split('_')[-1]
                if not item.realvalue:
                    row.alert = isKeyed
                    row.prop(item, 'value', slider=True, text=Name)
                    row.alert = False
                    
                else:
                    row.prop(props.activeface.data, f'["{item.name}"]', text='Flex Scale' if item.name[4:] == 'fs' else item.name[4:])
                op = row.operator('hisanim.keyslider', icon='DECORATE_KEYFRAME' if isKeyed else 'DECORATE_ANIMATE', text='', depress=isKeyed, emboss=False)
                op.delete = isKeyed
                op.slider = item.name
                row.prop(item, 'realvalue', icon='RESTRICT_VIEW_OFF' if item.realvalue else 'RESTRICT_VIEW_ON', text='', emboss=False)

        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text='')

class MESH_UL_skeys_nodriver(UIList):

    def filter_items(self, context, data, propname):
        props = context.scene.hisanimvars
        items = getattr(data, propname)
        filtered = [self.bitflag_filter_item] * len(items)
        for i, item in enumerate(items):
            if self.filter_name.lower() not in item.name.lower():
                filtered[i] &= ~self.bitflag_filter_item
            
            find = f'key_blocks["{item.name}"].value'
            if context.object.data.shape_keys.animation_data.drivers.find(find) != None:
                filtered[i] &= ~self.bitflag_filter_item

        return filtered, []
    
    def draw_item(self, _context, layout, _data, item, icon, active_data, _active_propname, index):
        obj = active_data
        key_block = item
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            row = layout.row()
            row.label(text='', icon='SHAPEKEY_DATA')
            if not item.id_data.use_relative:
                row.prop(key_block, "frame", text="")
            elif index > 0:
                row.prop(key_block, "value", text=item.name, emboss=True, slider=True)
                row.prop_decorator(item, "value")
            else:
                row.label(text="")
            row.prop(key_block, "mute", text="", emboss=False)
        elif self.layout_type == 'GRID':
            layout.alignment = 'CENTER'
            layout.label(text="", icon_value=icon)

class HISANIM_UL_LOCKSLIDER(bpy.types.UIList):
    def draw_item(self, context,
            layout, data,
            item, icon,
            active_data, active_propname,
            index):
        props = context.scene.hisanimvars
        DATA = props.activeface.data
        if context.scene.poselibVars.stage != 'SELECT':
            layout.row().label(text='Operation in progress.')
            return None
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            if item.split:
                split = layout.split(factor=0.2, align=True)
                split.prop(item, 'locked', icon='LOCKED' if item.locked else 'UNLOCKED')
                split.prop(DATA, f'["{item.R}"]', text=item.R[4:])
                split = layout.split(factor=0.2, align=True)
                split.prop(item, 'lockedL', icon='LOCKED' if item.lockedL else 'UNLOCKED')
                split.prop(DATA, f'["{item.L}"]', text=item.L[4:])
                pass
            else:
                split = layout.split(factor=0.2, align=True)
                split.prop(item, 'locked', icon='LOCKED' if item.locked else 'UNLOCKED')
                DATA = bpy.context.object.data
                split.prop(DATA, f'["{item.name}"]', text=item.name[4:])

        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text='')

class HISANIM_UL_RESULTS(bpy.types.UIList):

    def filter_items(self, context, data, propname):
        prefs = context.preferences.addons[__package__].preferences
        items = getattr(data, propname)
        filtered = [self.bitflag_filter_item] * len(items)
        for i, item in enumerate(items):
            blend = prefs.blends[item.blend_reference]
            #print(blend)
            if self.filter_name.lower() not in item.name.lower():
                filtered[i] &= ~self.bitflag_filter_item
            
            if self.filter_name.lower() in blend.name.lower():
                filtered[i] |= self.bitflag_filter_item

        return filtered, []

    def draw_item(self, context,
            layout, data,
            item, icon,
            active_data, active_propname,
            index):
        props = context.scene.hisanimvars
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            name = item.name
            split = layout.split(factor=0.2)
            split.label(text=item.tag)
            
            op = split.operator('hisanim.loadcosmetic', text=item.name)
            op.asset_reference = item.asset_reference
            op.blend_reference = item.blend_reference

        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text='')
        

class HISANIM_UL_USESLIDERS(bpy.types.UIList):

    def filter_items(self, context, data, propname):
        poselib = context.scene.poselibVars
        props = context.scene.hisanimvars
        items = getattr(data, propname)
        filtered = [self.bitflag_filter_item] * len(items)
        for i, item in enumerate(items):
            if self.filter_name.lower() not in item.name.lower():
                filtered[i] &= ~self.bitflag_filter_item
                
            if props.up or props.mid or props.low:
                
                if item.Type == 'NONE':
                    filtered[i] &= ~self.bitflag_filter_item

                if item.Type == 'UPPER':
                    if not props.up:
                        filtered[i] &= ~self.bitflag_filter_item
                
                if item.Type == 'MID':
                    if not props.mid:
                        filtered[i] &= ~self.bitflag_filter_item

                if item.Type == 'LOWER':
                    if not props.low:
                        filtered[i] &= ~self.bitflag_filter_item

        sortedItems = bpy.types.UI_UL_list.sort_items_helper([(num, item) for num, item in enumerate(items)], key=lambda a: a[1].use, reverse=True)
        return filtered, sortedItems if poselib.sort else []

    def draw_item(self, context,
            layout, data,
            item, icon,
            active_data, active_propname,
            index):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            row = layout.row(align=True)
            row.prop(item, 'use', text='')
            if item.split:
                row.label(text="_".join(item.name.split('_')[2:]))
            else:
                row.label(text="_".join(item.name.split('_')[1:]))

        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text='')

class POSELIB_UL_panel(UIList):
    def draw_item(self, context,
            layout, data,
            item, icon,
            active_data, active_propname,
            index):
        props = context.scene.poselibVars
        split = layout.split(factor=0.75)
        split.label(text=item.name)
        op = split.operator('poselib.prepareapply', text='', icon='FORWARD')
        op.viseme = item.name

class POSELIB_UL_visemes(UIList):

    def filter_items(self, context, data, propname):
        props = context.scene.hisanimvars
        items = getattr(data, propname)
        filtered = [self.bitflag_filter_item] * len(items)
        for i, item in enumerate(items):
            if self.filter_name.lower() not in item.name.lower():
                filtered[i] &= ~self.bitflag_filter_item
            if item.name.startswith('!'):
                filtered[i] &= ~self.bitflag_filter_item

        return filtered, []

    def draw_item(self, context,
            layout, data,
            item, icon,
            active_data, active_propname,
            index):
        props = context.scene.poselibVars
        row = layout.row()
        row.prop(item, 'use', text='')
        row.label(text="_".join(item.name.split("_")[1:]))

class LOADOUT_UL_loadouts(UIList):
    def draw_item(self, context,
            layout, data,
            item, icon,
            active_data, active_propname,
            index):
        props = context.scene.hisanimvars
        row = layout.row()
        row.label(text=': '.join(item.name.split('_-_')))
        if props.stage == 'NONE':
            op = row.operator('loadout.select', text='', icon='FORWARD')
            op.loadout = item.name

class TRIFECTA_PT_PANEL(bpy.types.Panel):
    """A Custom Panel in the Viewport Toolbar"""
    bl_label = 'TF2-Trifecta'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'TF2-Trifecta'
    bl_icon = "MOD_CLOTH"

    def draw_header(self, context):
        layout = self.layout
        #bpy.ops.wm.url_open()
        layout.operator('wm.url_open', text='', icon='URL').url = 'https://github.com/hisprofile/blenderstuff/tree/main/Guides/TF2%20Blender'

    def draw(self, context):
        prefs = context.preferences.addons[__package__].preferences
        props = context.scene.hisanimvars
        poselib = context.scene.poselibVars
        obj = context.object
        layout = self.layout
        
        row = layout.row()
        row.label(text=f'Tool: {props.tools.title()}')
        row.operator('trifecta.setwdrb', icon='MOD_CLOTH', text='', depress=props.tools == 'WARDROBE')
        row.operator('trifecta.setmd', icon='FORCE_DRAG', text='', depress=props.tools == 'MERC DEPLOYER')
        row.operator('trifecta.setbm', icon='GROUP_BONE', text='', depress=props.tools == 'BONEMERGE')
        row.operator('trifecta.setfp', icon='RESTRICT_SELECT_OFF', text='', depress=props.tools == 'FACE POSER')
        
        if not prefs.items_path:
            row = layout.row()
            row.alert = True
            row.label(text='Your TF2 Items path has not been set. Check preferences for info.', icon='ERROR')
            op = row.operator('trifecta.textbox', text='', icon='QUESTION')
            op.text = "You have not set your TF2 Items path in preferences. In 3.0+, all cosmetics and weapons will now be stored in a single folder. Please dedicate an empty folder to your TF2 Items Path."
            op.icons = 'ERROR'
            op.size = '60'
            op.width=350

        elif len(prefs.blends) < 1:
            row = layout.row()
            row.alert = True
            row.label(text='Scan the .blend files in your TF2 Items folder!', icon='ERROR')
            op = row.operator('trifecta.textbox', text='', icon='QUESTION')
            op.text = "You have set your TF2 Items path. All that is left is to download and scan .blend files for cosmetics & weapons. In the scene properties, either open the TF2 Items Folder link, or download all the assets through the \"Install TF2 Items\" box. Downloading through the scene properties will automatically scan your files."
            op.icons = 'ERROR'
            op.size = '60'
            op.width=350

        if not context.preferences.filepaths.use_scripts_auto_execute and prefs.hide_auto_exc_warning == False:
            row = layout.row()
            row.alert = True
            row.label(text='Auto-Execute Scripts is off.', icon='ERROR')
            op = row.operator('trifecta.textbox', text='', icon='QUESTION')
            op.text = 'To ensure full functionality of the face scripts, "Auto Execute Python Scripts" must be enabled. Be careful of what .blend files you open, and NEVER run Blender in administrator mode.'
            op.icons = 'ERROR'
            op.size = '60'
            op.width=350

        if props.tools == 'MERC DEPLOYER':
            cln = ["IK", "FK"]
            mercs = ['scout', 'soldier', 'pyro', 'demo',
                    'heavy', 'engineer', 'medic', 'sniper', 'spy']
            if len(prefs.rigs) > 0:
                row = layout.row()
                row.prop(context.scene.hisanimvars, 'rigs')
                if context.scene.hisanimvars.rigs == '': return
                for i in mercs:
                    row = layout.box().row(align=True)
                    row.label(text=i.title(), icon_value=icons.id(i))
                    for ii in cln:
                        if ii == 'FK':
                            row.alert=True
                        MERC = row.operator('hisanim.loadmerc', text='New' if ii == 'IK' else 'Legacy')
                        MERC.merc = i
                        MERC.type = ii

                row = layout.row()
                row.prop(context.scene.hisanimvars, "bluteam", text='BLU Team')
                op = row.operator('trifecta.textbox', text='', icon='QUESTION')
                op.text='''"New" rigs are made with Rigify, allowing for more extensive control over the armature with features like IK/FK swapping. "Legacy" rigs comprise of ONLY forward kinematics, and should only be used to apply taunts onto.
When "In-Game Models" is enabled, lower-poly bodygroups will be used to ensure the most compatibility with cosmetics. When disabled, the higher-poly (A.K.A. SFM) bodygroups will be used instead.
"Rimlight Strength" determines the intensity of rim-lights on characters. Because TF2-shading can't be translated 1:1, this is left at 0.4 by default.'''
                op.width=325
                op.size='56,50,56'
                op.icons='ARMATURE_DATA,OUTLINER_OB_ARMATURE,SHADING_RENDERED'
                op.url = 'https://github.com/hisprofile/TF2-Trifecta?tab=readme-ov-file#merc-deployer'

                layout.row().prop(context.scene.hisanimvars, "cosmeticcompatibility", text='Simple Models', invert_checkbox=False)
                layout.row().prop(props, 'hisanimrimpower', slider=True)
            
            else:
                layout.row().label(text='A set of rigs have not been added!')
            return

        if props.tools == 'BONEMERGE':
            ob = context.object
            row = layout.row()
            self.layout.prop_search(context.scene.hisanimvars, "hisanimtarget", bpy.data, "objects", text="Link to", icon='ARMATURE_DATA')
            
            box = layout.row().box()
            row = box.row()
            row.label(text='Binding cosmetics')
            op = row.operator('trifecta.textbox', text='', icon='QUESTION')
            op.text='Target an armature, then select a cosmetic to bind to the targeted armature.'
            op.size='56'
            op.icons='GROUP_BONE'
            op.width=325
            op.url=''

            op = box.row().operator('hisanim.attachto', icon="LINKED")
            box.row().prop(props, 'hierarchal_influence')
            box.row().prop(context.scene.hisanimvars, 'hisanimscale')
            bbox = box.box()
            bbox.label(text='Detachments', icon='UNLINKED')
            if not hasattr(context, 'selected_objects'):
                bbox.row().label(text='No selected objects!')
            elif len(context.selected_objects) < 1:
                bbox.row().label(text='No selected objects!')
            else:
                obj = context.object
                if obj.parent and obj.type == 'MESH':
                    obj = obj.parent

                targets = [(con, getattr(con, 'target', None)) for con in obj.constraints if con.name.startswith('bm_target') and hasattr(con, 'target')]

                if targets:
                    for con, target in targets:
                        row = bbox.row(align=True)
                        row.alignment = 'RIGHT'
                        row.label(text=target.name, icon='OBJECT_DATA')
                        row = row.row(align=True)
                        row.alignment = 'RIGHT'
                        row.prop(con, 'influence', text='')
                        op = row.operator('hisanim.detachfrom', text='', icon='UNLINKED')
                        op.target = target.name
                        row.prop_decorator(con, 'influence')
                    
                else:
                    bbox.row().label(text='Object is not bound to anything!')
            box = layout.row().box()
            row = box.row()
            row.label(text='Bind facial cosmetics')
            op = row.operator('trifecta.textbox', text='', icon='QUESTION')
            op.text = 'When binding a cosmetic to a face, it can only be posed through shape keys. Flex controllers are unsupported.'
            op.icons = 'MESH_MONKEY'
            op.size = '60'
            op.width = 350
            op.url = 'https://github.com/hisprofile/TF2-Trifecta?tab=readme-ov-file#bonemerge'
            box.row().operator('hisanim.bindface')
            box.row().operator('bm.unbindface'),
            layout.row().operator('hisanim.attemptfix')

        if props.tools == 'FACE POSER':
            if len(context.selected_objects) == 0:
                layout.label(text='Select a face!')
                return None
            if context.object == None:
                layout.label(text='Select a face!')
                return None
            if context.object.type != 'MESH':
                layout.label(text='Select a face!')
                return None
            if context.object.data.get('aaa_fs') == None:
                layout.label(text='Select a face!')
                return None
            if context.object.data.animation_data != None:
                if context.object.data.animation_data.drivers.find('["aaa_fs"]') != None:
                    row = layout.row()
                    row.alert = True
                    row.label(text="ThatLazyArtist's and Eccentric's rigs are not supported.")
                    op = row.operator('trifecta.textbox', text='', icon='QUESTION')
                    op.text = "The Faceposer tool was developed to mimic SFM's face posing UI, and only works on hisanimations' rigs. Eccentric's and ThatLazyArtist's rigs have a panel on the rigs themselves to pose the face. Enter \"Pose Mode\" and pose the face there!"
                    op.size = '60'
                    op.icons = 'NONE'
                    op.width=350
                    layout.row().label(text='There is a face panel on the rig. Pose the face there!')
                    box = layout.box()
                    row = box.row(align=True)
                    row.operator('hisanim.optimize', icon='MODIFIER_ON')
                    row.operator('hisanim.restore', icon='MODIFIER_OFF')
                    return

class WARDROBE_PT_SEARCH(bpy.types.Panel):
    bl_label = ''
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_parent_id = "TRIFECTA_PT_PANEL"
    bl_category = 'TF2-Trifecta'
    

    @classmethod
    def poll(cls, context):
        props = context.scene.hisanimvars
        return props.tools == 'WARDROBE'

    def draw_header(self, context):
        self.layout.separator()
        self.layout.label(icon='VIEWZOOM', text='Search')

    def draw(self, context):
        prefs = context.preferences.addons[__package__].preferences
        props = context.scene.hisanimvars
        poselib = context.scene.poselibVars
        layout = self.layout
        box = layout.box()
        box.row().prop(props, 'query', text="", icon="VIEWZOOM")
        box.row().operator('hisanim.search', icon='VIEWZOOM')
        box.row().operator('hisanim.clearsearch', icon='X')

class WARDROBE_PT_MATERIAL(bpy.types.Panel):
    bl_label = ''
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_parent_id = "TRIFECTA_PT_PANEL"
    bl_category = 'TF2-Trifecta'
    bl_options = {'HEADER_LAYOUT_EXPAND'}

    @classmethod
    def poll(cls, context):
        props = context.scene.hisanimvars
        return props.tools == 'WARDROBE'
    
    def draw_header(self, context):
        l = self.layout
        l.separator()
        l.label(icon='MATERIAL', text='Material Settings')
        #op = self.layout.operator('trifecta.textbox', icon='QUESTION', text='')
        #op.text = "When using EEVEE, Enabling TF2 style on all spawned items will make them appear closer in appearance to the mercenaries, fixing any contrast issues. When using Cycles, this should be set to default.\nRimlight Strength determines the intensity of rim-lights on characters. Because TF2-shading can't be translated 1:1, this is left at 0.4 by default."
        #op.icons = 'SHADING_RENDERED,SHADING_RENDERED'
        #op.size = '76,78'
        #op.width = 460
        #op.url = 'https://github.com/hisprofile/TF2-Trifecta?tab=readme-ov-file#material-settings'
        #l.separator()
    
    def draw(self, context):
        prefs = context.preferences.addons[__package__].preferences
        props = context.scene.hisanimvars
        poselib = context.scene.poselibVars
        obj = context.object
        layout = self.layout
        box = layout.box()
        
        #if props.toggle_mat: box.row().operator('hisanim.removelightwarps')
        #else: box.row().operator('hisanim.lightwarps')
        box.row().prop(context.scene.hisanimvars, 'hisanimrimpower', slider=True)
        row = box.row()
        row.prop(context.scene.hisanimvars, 'bluteam', text='BLU Team')
                  
class WARDROBE_PT_PAINTS(bpy.types.Panel):
    bl_label = ''
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_parent_id = "TRIFECTA_PT_PANEL"
    bl_category = 'TF2-Trifecta'
    bl_options = {'HEADER_LAYOUT_EXPAND', 'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        props = context.scene.hisanimvars
        if context.object == None: return False
        if context.object.type != 'MESH': return False
        if context.object.get('skin_groups') == None: return False
        return props.tools == 'WARDROBE'
    
    def draw_header(self, context):
        l = self.layout
        l.alignment = 'EXPAND'
        l.separator()
        l.label(icon='BRUSH_DATA', text='Paints')
        #op = l.operator('trifecta.textbox', icon='QUESTION', text='')
        #op.text = 'If a cosmetic seems to be painted incorrectly, selecting one of the materials and executing "Fix Material" may help.'
        #op.icons = 'SHADING_RENDERED'
        #op.size = '56'
        #op.width = 290
        #op.url = 'https://github.com/hisprofile/TF2-Trifecta?tab=readme-ov-file#paints'
        l.separator()

    def draw(self, context):
        prefs = context.preferences.addons[__package__].preferences
        props = context.scene.hisanimvars
        poselib = context.scene.poselibVars
        obj = context.object
        layout = self.layout
        box = layout.box()
        row = box.row()
        ob = context.object
        box.row().template_list("MATERIAL_UL_matslots", "", ob, "material_slots", ob, "active_material_index")
        MAT = ob.active_material
        
        if (MAT == None) or (MAT.node_tree == None):
            box.row().label(text='Unsupported material for paints!')
            return
        TF2D = MAT.node_tree.nodes.get('TF2 Diffuse')
        if TF2D == None:
            box.row().label(text='Unsupported material for paints!')
            return
        
        row = box.row(align=True)
        box.row().label(text='Add Paint')
        row = box.row(align=True)
        #col = box.column()
        row.template_icon_view(context.window_manager, 'hisanim_paints', show_labels=True, scale=4, scale_popup=4)
        row.scale_y = 1
        row = row.row(align=True)
        row.template_color_picker(TF2D.inputs['$color2'], 'default_value', value_slider=True, cubic=True)
        box.row().prop(TF2D.inputs['$color2'], 'default_value', text='Color (Gamma 2.2)')
        box.row().prop(TF2D.inputs['$blendtintbybasealpha'], 'default_value', text='Blend Color by Alpha', slider=True)
        box.row().prop(TF2D.inputs['$blendtintcoloroverbase'], 'default_value', text='Multiply or Mix Color', slider=True)
        row=box.row(align=True)
        oper = row.operator('hisanim.paint', text = 'Add Paint')
        oper.PAINT = paints[context.window_manager.hisanim_paints]
        row.operator('hisanim.paintclear')

class WARDROBE_PT_LOADOUT(bpy.types.Panel):
    bl_label = ''
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_parent_id = "TRIFECTA_PT_PANEL"
    bl_category = 'TF2-Trifecta'
    bl_options = {'HEADER_LAYOUT_EXPAND', 'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        props = context.scene.hisanimvars
        return props.tools == 'WARDROBE'
    
    def draw_header(self, context):
        l = self.layout
        l.alignment = 'EXPAND'
        l.separator()
        l.label(icon='ASSET_MANAGER', text='Loadout')
        op = l.operator('trifecta.textbox', icon='QUESTION', text='')
        op.text = 'The Loadout tool allows you to save combinations of equippable items to be spawned by batch at any time, saving you the time of having to search and spawn for each one.'
        op.icons = 'ASSET_MANAGER'
        op.size = '56'
        op.width = 325
        l.separator()

    def draw(self, context):
        prefs = context.preferences.addons[__package__].preferences
        props = context.scene.hisanimvars
        poselib = context.scene.poselibVars
        obj = context.object
        layout = self.layout
        box = layout.box()
        row = box.row()
        col = row.column()
        col.template_list('LOADOUT_UL_loadouts', 'Loadouts', props, 'loadout_data', props, 'loadout_index')
        col = row.column()
        col.operator('wdrb.select', text='', icon='ADD')
        col.operator('loadout.remove', text='', icon='REMOVE')
        col.operator('loadout.refresh', icon='FILE_REFRESH', text='', emboss=False)
        op = col.operator('loadout.move', text='', icon='TRIA_UP')
        op.pos = 1
        op1 = col.operator('loadout.move', text='', icon='TRIA_DOWN')
        op1.pos = -1
        if props.stage == 'SELECT':
            if (len(bpy.types.Scene.loadout_temp) == 0): box.row().label(text='No Cosmetics Selected!')
            box.row().prop(props, 'loadout_name', text='Name')
            row = box.row()
            row.operator('wdrb.cancel')
            row.operator('wdrb.confirm')

        if props.stage == 'DISPLAY':
            box.row().operator('wdrb.cancel')
            box.row().operator('loadout.load')

        if props.stage == 'NONE':
            row = box.row()
            row.operator('loadout.rename')

class WARDROBE_PT_RESULTS(bpy.types.Panel):
    bl_label = ''
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_parent_id = "WARDROBE_PT_SEARCH"
    bl_category = 'TF2-Trifecta'
    bl_options = {'HEADER_LAYOUT_EXPAND', 'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        props = context.scene.hisanimvars
        return props.tools == 'WARDROBE'
    
    def draw_header(self, context):
        prefs = context.preferences.addons[__package__].preferences
        props = context.scene.hisanimvars
        poselib = context.scene.poselibVars
        hits = props.results
        self.layout.alignment = 'EXPAND'
        self.layout.separator()
        self.layout.label(icon='VIEWZOOM', text=f'{"Search Result" if (len(hits) == 1) and props.searched else "Search Results"}{(" : " + str(len(hits))) if props.searched else ""}')

    def draw(self, context):
        prefs = context.preferences.addons[__package__].preferences
        props = context.scene.hisanimvars
        poselib = context.scene.poselibVars
        obj = context.object
        layout = self.layout
        box = layout.box()
        hits = props.results
        if len(hits) > 0 and props.searched:
            box.row().template_list('HISANIM_UL_RESULTS', 'Results', props, 'results', props, 'resultindex')
        else:
            if props.searched:
                box.label(text='Nothing found!')
            else:
                box.label(text='Search for something!')

class FACEPOSER_PT_FACEPOSER(bpy.types.Panel):
    bl_label = ''
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_parent_id = "TRIFECTA_PT_PANEL"
    bl_category = 'TF2-Trifecta'
    bl_options = {'HEADER_LAYOUT_EXPAND'}

    @classmethod
    def poll(cls, context):
        props = context.scene.hisanimvars
        if props.tools != 'FACE POSER': return False
        return props.enable_faceposer
    
    def draw_header(self, context):
        l = self.layout
        props = context.scene.hisanimvars
        l.alignment = 'EXPAND'
        l.separator()
        l.label(icon='RESTRICT_SELECT_OFF', text='Face Poser')
        l.prop(props, 'noKeyStatus', text='', icon='DECORATE_KEYFRAME' if not props.noKeyStatus else 'DECORATE_ANIMATE', invert_checkbox=True)
        op = l.operator('trifecta.textbox', icon='QUESTION', text='')
        op.text = "Don't be worried about the sliders automatically resetting. It was necessary to implement stereo flexes. The values mean nothing at all. Stereo sliders will appear as RED on a keyframe.\nWhen this button is HIGHLIGHTED, it indicates that Auto-Keyframing is enabled. Any changes you make will be saved.\nPressing this button will add a keyframe to all sliders. Useful for starting an animation sequence\nEnabling this button by stereo sliders will reveal the true value for sliders.\nFlex Controllers vs. Shapekeys: Flex Controllers simulate muscle strands being pulled, making it difficult to create a distorted face. Shapekeys can be easily stacked, so its easy to create a very deformed face.\nOptimizing mercenaries can give a significant performance boost by disabling the flex controllers, which will somewhat lock the face. Don't forget to restore the face on final render."
        op.icons = 'ERROR,REC,DECORATE_KEYFRAME,RESTRICT_VIEW_OFF,SHAPEKEY_DATA,MODIFIER_ON'
        op.size = '76,70,76,76,72,76'
        op.width = 420
        op.url = 'https://github.com/hisprofile/TF2-Trifecta?tab=readme-ov-file#face-poser-1'
        l.separator()

    def draw(self, context):
        prefs = context.preferences.addons[__package__].preferences
        props = context.scene.hisanimvars
        poselib = context.scene.poselibVars
        obj = context.object
        layout = self.layout
        box = layout.box()
        row = box.row(align=True)
        row.operator('hisanim.optimize', icon='MODIFIER_ON')
        row.operator('hisanim.restore', icon='MODIFIER_OFF')
        row = box.row(align=True)
        row.prop(props, 'use_flexes', toggle=True)
        row.prop(props, 'use_skeys', toggle=True)
        row = box.row(align=True)
        if props.mode == 'SKEYS':
            ob = context.object
            key = ob.data.shape_keys
            row.template_list("MESH_UL_skeys_nodriver", "", key, "key_blocks", ob, "active_shape_key_index", rows=5)
            return
        col = row.column()
        col.template_list('HISANIM_UL_SLIDERS', 'Sliders', props, 'sliders', props, 'sliderindex')
        col = row.column()
        col.operator('hisanim.fixfaceposer', icon='PANEL_CLOSE' if props.dragging else 'CHECKMARK', text='')
        col.row().prop(bpy.context.scene.tool_settings, 'use_keyframe_insert_auto', text='')
        col.row().operator('hisanim.keyeverything', icon='DECORATE_KEYFRAME', text='')
        col.row().operator('faceposer.refresh', text='', icon='FILE_REFRESH')
        col.row().operator('hisanim.resetface', icon='LOOP_BACK', text='')
        row = box.row(align=True)
        op = row.operator('hisanim.adjust', text='', icon='TRIA_LEFT')
        op.amount = -0.1
        row.prop(props, 'LR', slider=True)
        op = row.operator('hisanim.adjust', text='', icon='TRIA_RIGHT')
        op.amount = 0.1
        row = box.row(align=True)
        row.prop(props, 'up', text='Upper', toggle=True)
        row.prop(props, 'mid', text='Mid', toggle=True)
        row.prop(props, 'low', text='Lower', toggle=True)

class FACEPOSER_PT_POSELIBRARY(bpy.types.Panel):
    bl_label = ''
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_parent_id = "TRIFECTA_PT_PANEL"
    bl_category = 'TF2-Trifecta'
    bl_options = {'HEADER_LAYOUT_EXPAND'}

    @classmethod
    def poll(cls, context):
        props = context.scene.hisanimvars
        if props.tools != 'FACE POSER': return False
        return props.enable_faceposer
    
    def draw_header(self, context):
        l = self.layout
        l.alignment = 'EXPAND'
        l.separator()
        l.label(icon='OUTLINER_OB_GROUP_INSTANCE', text='Pose Library')
        op = l.operator('trifecta.textbox', text='', icon='QUESTION')
        op.text = 'The Pose Library is a place to store presets for face shapes. It will only save flex controller data.\nEnabling "Reset All" will reset the face before applying the preset.'
        op.icons = 'OUTLINER_OB_GROUP_INSTANCE,LOOP_BACK'
        op.size = '53,56'
        op.width = 300
        op.url = 'https://github.com/hisprofile/TF2-Trifecta?tab=readme-ov-file#pose-library'
        l.separator()

    def draw(self, context):
        props = context.scene.hisanimvars
        poselib = context.scene.poselibVars
        obj = context.object
        layout = self.layout
        box = layout.box()
        row = box.row()
        row.label(text=f'''{poselib.stage.title()}{(' "'  + poselib.visemeName + '"') if poselib.stage == 'APPLY' else ''}''')
        
        if obj.data.get('merc') and props.needs_override:
            box.row().label(text=f'Using: {obj.data.get("merc").title()}')
            box.operator('faceposer.override')

        row = box.row()

        if obj.data.get('merc') == None and props.needs_override:
            textBox(box, "The face you have selected doesn't natively support the pose library, but you can choose a mercenary preset and see if it works!")
            box.operator('faceposer.override')
        
            
        elif poselib.stage == 'SELECT':
            col = row.column()
            col.template_list('POSELIB_UL_panel', 'Pose Library', poselib, 'visemesCol', poselib, 'activeViseme')
            col = row.column()
            col.operator('poselib.prepareadd', text='', icon='ADD')
            col.operator('poselib.remove', text='', icon='REMOVE')
            col.operator('poselib.refresh', icon='FILE_REFRESH', text='', emboss=False)
            op = col.operator('poselib.move', text='', icon='TRIA_UP')
            op.pos = 1
            op1 = col.operator('poselib.move', text='', icon='TRIA_DOWN')
            op1.pos = -1
            row = box.row()
            row.operator('poselib.rename')

        elif poselib.stage == 'ADD':
            row.template_list('HISANIM_UL_USESLIDERS', 'Sliders', props, 'sliders', props, 'sliderindex')
            row = box.row(align=True)
            row.prop(poselib, 'sort', toggle=True)
            row.prop(props, 'up', text='Upper', toggle=True)
            row.prop(props, 'mid', text='Mid', toggle=True)
            row.prop(props, 'low', text='Lower', toggle=True)
            box.row().prop(poselib, 'name')
            box.row().operator('poselib.add')
            box.row().operator('poselib.cancel')

        elif poselib.stage == 'APPLY':
            row.template_list('POSELIB_UL_visemes', 'Items', poselib, 'dictVisemes', poselib, 'activeItem')
            box.row().prop(poselib, 'value', slider=True)
            row = box.row()
            row.prop(poselib, 'keyframe')
            p = row.row()
            p.prop(poselib, 'keyframe_unchanged')
            p.enabled = poselib.keyframe
            box.row().prop(poselib, 'reset')
            box.row().operator('poselib.apply')
            box.row().operator('poselib.cancelapply')
 
class FACEPOSER_PT_RANDOMIZER(bpy.types.Panel):
    bl_label = ''
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_parent_id = "TRIFECTA_PT_PANEL"
    bl_category = 'TF2-Trifecta'
    bl_options = {'HEADER_LAYOUT_EXPAND', 'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        props = context.scene.hisanimvars
        if props.tools != 'FACE POSER': return False
        return props.enable_faceposer
    
    def draw_header(self, context):
        l = self.layout
        l.alignment = 'EXPAND'
        l.separator()
        l.label(icon='RNDCURVE', text='Face Randomizer')
        op = l.operator('trifecta.textbox', icon='QUESTION', text='')
        op.text = 'Make funny faces!'
        op.icons = 'MONKEY'
        op.size = '56'
        op.width = 130
        op.url = 'https://github.com/hisprofile/TF2-Trifecta?tab=readme-ov-file#face-randomizer--lock-list'
        l.separator()

    def draw(self, context):
        prefs = context.preferences.addons[__package__].preferences
        props = context.scene.hisanimvars
        poselib = context.scene.poselibVars
        obj = context.object
        layout = self.layout
        box = layout.box()
        row = box.row()
        row.prop(props, 'keyframe')
        row.prop(props, 'randomadditive')
        
        box.row().prop(props, 'randomstrength', slider=True)
        box.row().operator('hisanim.randomizeface')
        box.row().operator('hisanim.resetface')
        box.row().prop(context.object.data, '["aaa_fs"]', text='Flex Scale')

class FACEPOSER_PT_LOCKLIST(bpy.types.Panel):
    bl_label = ''
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_parent_id = "TRIFECTA_PT_PANEL"
    bl_category = 'TF2-Trifecta'
    bl_options = {'HEADER_LAYOUT_EXPAND', 'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        props = context.scene.hisanimvars
        if props.tools != 'FACE POSER': return False
        return props.enable_faceposer
    
    def draw_header(self, context):
        l = self.layout
        l.alignment = 'EXPAND'
        l.separator()
        l.label(icon='LOCKED', text='Lock List')
        op = l.operator('trifecta.textbox', text='', icon='QUESTION')
        op.text = 'Locking a flex controller will keep it from getting randomized.'
        op.icons = 'LOCKED'
        op.size = '128'
        op.width = 375
        op.url = 'https://github.com/hisprofile/TF2-Trifecta?tab=readme-ov-file#face-randomizer--lock-list'
        l.separator()

    def draw(self, context):
        prefs = context.preferences.addons[__package__].preferences
        props = context.scene.hisanimvars
        poselib = context.scene.poselibVars
        obj = context.object
        layout = self.layout
        box = layout.box()
        data = context.object.data
        box.row().template_list('HISANIM_UL_LOCKSLIDER', 'Lock Sliders', props, 'sliders', props, 'sliderindex')

def textBox(self, sentence: str, icon='NONE', line=56):
    layout = self.box().column()
    if sentence.startswith('LINK:'):
        url, name = sentence.split('|')
        url = url.split('LINK:', maxsplit=1)[1]
        name = name.split('NAME:', maxsplit=1)[1]
        #print(url, name)
        layout.row().operator('wm.url_open', text=name, icon='URL').url = url
        return None
    sentence = sentence.split(' ')
    mix = sentence[0]
    sentence.pop(0)
    broken = False
    while True:
        add = ' ' + sentence[0]
        if len(mix + add) < line:
            mix += add
            sentence.pop(0)
            if sentence == []:
                layout.row().label(text=mix, icon='NONE' if broken else icon)
                return None

        else:
            layout.row().label(text=mix, icon='NONE' if broken else icon)
            broken = True
            mix = sentence[0]
            sentence.pop(0)
            if sentence == []:
                layout.row().label(text=mix)
                return None
            
class TRIFECTA_OT_genericText(bpy.types.Operator):
    bl_idname = 'trifecta.textbox'
    bl_label = 'Hints'
    bl_description = 'A window will display any possible questions you have'

    text: StringProperty(default='')
    icons: StringProperty()
    size: StringProperty()
    width: IntProperty(default=400)
    url: StringProperty(default='')

    def invoke(self, context, event):
        if not getattr(self, 'prompt', True):
            return self.execute(context)
        if event.shift and self.url != '':
            bpy.ops.wm.url_open(url=self.url)
            return self.execute(context)
        self.invoke_extra(context, event)
        return context.window_manager.invoke_props_dialog(self, width=self.width)
    
    def invoke_extra(self, context, event):
        pass
    
    def draw(self, context):
        sentences = self.text.split('\n')
        icons = self.icons.split(',')
        sizes = self.size.split(',')
        for sentence, icon, size in zip(sentences, icons, sizes):
            textBox(self.layout, sentence, icon, int(size))
        self.draw_extra(context)

    def draw_extra(self, context):
        pass

    def execute(self, context):
        return {'FINISHED'}

classes = [
    TRIFECTA_PT_PANEL,
    WARDROBE_PT_SEARCH,
    WARDROBE_PT_MATERIAL,
    WARDROBE_PT_PAINTS,
    #WARDROBE_PT_LOADOUT,
    WARDROBE_PT_RESULTS,
    FACEPOSER_PT_FACEPOSER,
    FACEPOSER_PT_POSELIBRARY,
    FACEPOSER_PT_RANDOMIZER,
    FACEPOSER_PT_LOCKLIST,
    HISANIM_UL_SLIDERS,
    HISANIM_UL_RESULTS,
    HISANIM_UL_LOCKSLIDER,
    POSELIB_UL_panel,
    HISANIM_UL_USESLIDERS,
    POSELIB_UL_visemes,
    LOADOUT_UL_loadouts,
    MESH_UL_skeys_nodriver,
    TRIFECTA_OT_genericText,
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)