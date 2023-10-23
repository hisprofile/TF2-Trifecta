import bpy
from . import newuilist
from bpy.types import (UIList)
from bpy.props import *

def hasKey(obj, slider) -> bool:
        data = obj.data
        if data.animation_data == None:
            return False
        scene = bpy.context.scene
        action = data.animation_data.action
        if action == None:
            return False


        for curv in action.fcurves:
            if (curv.data_path == f'["{slider.name}"]') or (curv.data_path == f'["{slider.L}"]'):
                for point in curv.keyframe_points:
                    if scene.frame_current == point.co.x:
                        return True
        else:
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
            layout.row() # used as a little space to set the active item
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
                
                op = row.operator('hisanim.keyslider', icon='DECORATE_KEYFRAME' if isKeyed else 'DECORATE_ANIMATE', text='', depress=isKeyed)
                op.delete = isKeyed
                op.slider = item.name
                row.prop(item, 'realvalue', icon='RESTRICT_VIEW_OFF' if item.realvalue else 'RESTRICT_VIEW_ON', text='')

            else:
                row = layout.row(align=True)
                Name = item.name.split('_')[-1]
                if not item.realvalue:
                    row.alert = isKeyed
                    row.prop(item, 'value', slider=True, text=Name)
                    row.alert = False
                else:
                    row.prop(props.activeface.data, f'["{item.name}"]', text=item.name[4:])
                op = row.operator('hisanim.keyslider', icon='DECORATE_KEYFRAME' if isKeyed else 'DECORATE_ANIMATE', text='', depress=isKeyed)
                op.delete = isKeyed
                op.slider = item.name
                row.prop(item, 'realvalue', icon='RESTRICT_VIEW_OFF' if item.realvalue else 'RESTRICT_VIEW_ON', text='')

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
            split = layout.split(factor=0.6, align=False)
            split.prop(key_block, "name", text="", emboss=False, icon_value=icon)
            row = split.row(align=True)
            if key_block.mute or (obj.mode == 'EDIT' and not (obj.use_shape_key_edit_mode and obj.type == 'MESH')):
                split.active = False
            if not item.id_data.use_relative:
                row.prop(key_block, "frame", text="")
            elif index > 0:
                row.prop(key_block, "value", text="", emboss=True, slider=True)
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
    def draw_item(self, context,
            layout, data,
            item, icon,
            active_data, active_propname,
            index):
        props = context.scene.hisanimvars
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            name = item.name
            split = layout.split(factor=0.2)
            if props.stage == 'SELECT':
                split.prop(item, 'use', text='')
            else:
                split.label(text=item.name.split('_-_')[1].title())
            
            op = split.operator('hisanim.loadcosmetic', text=item.name.split('_-_')[0])
            op.LOAD = item.name

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
            layout.row() # used as a little space to set the active item
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
        row = layout.row()
        row.label(text=item.name)
        op = row.operator('poselib.prepareapply', text='', icon='FORWARD')
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

    def draw(self, context):
        prefs = context.preferences.addons[__package__].preferences
        props = bpy.context.scene.hisanimvars
        poselib = bpy.context.scene.poselibVars
        layout = self.layout
        
        if prefs.quickswitch:
            row = layout.row()
            row.label(text=f'Tool: {props.tools.title()}')
            row.prop(props, 'wr', icon='MOD_CLOTH', text='', toggle=True)
            row.prop(props, 'md', icon='FORCE_DRAG', text='', toggle=True)
            row.prop(props, 'bm', icon='GROUP_BONE', text='', toggle=True)
            row.prop(props, 'fp', icon='RESTRICT_SELECT_OFF', text='', toggle=True)
        else:
            layout.row().prop(props, 'tools')
        
        if prefs.missing == True:
            row = layout.row()
            row.alert = True
            row.label(text='Assets missing. Check preferences for info.', icon='ERROR')

        if props.tools == 'WARDROBE':
            layout.row().label(text='Spawn TF2 Cosmetics', icon='MOD_CLOTH')
            
            
            box = layout.box()
            box.label(text='Search', icon='VIEWZOOM')
            box.row().prop(props, 'query', text="", icon="VIEWZOOM")
            box.row().prop(context.scene.hisanimvars, 'hisanimweapons')
            if props.hisanimweapons:
                box.row().prop(props, 'autobind')
            box.row().operator('hisanim.search', icon='VIEWZOOM')
            box.row().operator('hisanim.clearsearch', icon='X')
            box = layout.box()
            row = box.row()
            if props.ddmatsettings or not prefs.compactable:
                if prefs.compactable: row.prop(props, 'ddmatsettings', icon='DISCLOSURE_TRI_DOWN', emboss=False)
                if prefs.compactable: row.label(text='Material settings')
                if not prefs.compactable: row.label(text='Material settings')
                op = row.operator('trifecta.textbox', icon='QUESTION', text='')
                op.text = "When using EEVEE, Enabling TF2 style on all spawned items will make them appear closer in appearance to the mercenaries, fixing any contrast issues. When using Cycles, this should be set to default.\nRimlight Strength determines the intensity of rim-lights on characters. Because TF2-shading can't be translated 1:1, this is left at 0.4 by default."
                op.icons = 'SHADING_RENDERED,SHADING_RENDERED'
                op.size = '76,76'
                op.width = 425
                if props.toggle_mat: box.row().operator('hisanim.removelightwarps')
                else: box.row().operator('hisanim.lightwarps')
                box.row().prop(context.scene.hisanimvars, 'hisanimrimpower', slider=True)
                row = box.row()
                row.prop(context.scene.hisanimvars, 'wrdbbluteam')
                
            else:
                row.prop(props, 'ddmatsettings', icon='DISCLOSURE_TRI_RIGHT', emboss=False)
                row.label(text='Material settings', icon='MATERIAL')

            if len(context.selected_objects) > 0:
                if context.object.get('skin_groups') != None:
                    box = layout.box()
                    row = box.row()
                    if props.ddpaints or not prefs.compactable:
                        if prefs.compactable: row.prop(props, 'ddpaints', icon='DISCLOSURE_TRI_DOWN', emboss=False)
                        row.label(text='Paints')
                        op = row.operator('trifecta.textbox', icon='QUESTION', text='')
                        op.text = 'If a cosmetic seems to be painted incorrectly, selecting one of the materials and executing "Fix Material" may help.'
                        op.icons = 'SHADING_RENDERED'
                        op.size = '56'
                        op.width = 260
                        ob = context.object
                        row = box.row()
                        row.label(text='Attempt to fix material')
                        box.row().template_list("MATERIAL_UL_matslots", "", ob, "material_slots", ob, "active_material_index")
                        row = box.row(align=True)
                        row.operator('hisanim.materialfix')
                        row.operator('hisanim.revertfix')
                        box.row().label(text='Add Paint')
                        box.row().template_icon_view(context.window_manager, 'hisanim_paints', show_labels=True, scale=4, scale_popup=4)
                        row=box.row(align=True)
                        oper = row.operator('hisanim.paint', text = 'Add Paint')
                        oper.PAINT = newuilist.paints[context.window_manager.hisanim_paints]
                        row.operator('hisanim.paintclear')
                    else:
                        row.prop(props, 'ddpaints', icon='DISCLOSURE_TRI_RIGHT', emboss=False)
                        row.label(text='Paints', icon='BRUSH_DATA')
            box = layout.box()
            row = box.row()
            if props.ddloadouts or not prefs.compactable:
                if prefs.compactable: row.prop(props, 'ddloadouts', icon='DISCLOSURE_TRI_DOWN', emboss=False)
                row.label(text='Loadouts')
                op = row.operator('trifecta.textbox', icon='QUESTION', text='')
                op.text = 'The Loadout tool allows you to save combinations of equippable items to be spawned by batch at any time, saving you the time of having to search and spawn for each one.'
                op.icons = 'ASSET_MANAGER'
                op.size = '56'
                op.width = 290
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
                    
            else:
                row.prop(props, 'ddloadouts', icon='DISCLOSURE_TRI_RIGHT', emboss=False)
                row.label(text='Loadouts', icon='ASSET_MANAGER')

            box = layout.box()
            row = box.row()
            hits = props.results
            if props.ddsearch or not prefs.compactable:
                if prefs.compactable: row.prop(props, 'ddsearch', icon='DISCLOSURE_TRI_DOWN', emboss=False)
                row.label(text=f'{"Search Result" if (len(hits) == 1) and props.searched else "Search Results"}{(" : " + str(len(hits))) if props.searched else ""}')
                if len(hits) > 0 and props.searched:
                    box.row().template_list('HISANIM_UL_RESULTS', 'Results', props, 'results', props, 'resultindex')
                else:
                    if props.searched:
                        box.label(text='Nothing found!')
                    else:
                        box.label(text='Search for something!')
            else:
                row.prop(props, 'ddsearch', icon='DISCLOSURE_TRI_RIGHT', emboss=False)
                row.label(text=f'{"Search Result" if (len(hits) == 1) and props.searched else "Search Results"}{(" : " + str(len(hits))) if props.searched else ""}', icon='VIEWZOOM')
            return
        
        if props.tools == 'MERC DEPLOYER':
            row = layout.row()
            row.label(text='Deploy Mercenaries', icon='FORCE_DRAG')
            cln = ["IK", "FK"]
            mercs = ['scout', 'soldier', 'pyro', 'demo',
                    'heavy', 'engineer', 'medic', 'sniper', 'spy']
            if prefs.hisanim_paths.get('rigs') != None:
                if prefs.hisanim_paths.get('rigs').this_is != 'FOLDER':
                    row = layout.row()
                    row.label(text='"rigs" have an invalid path!')
                else:
                    for i in mercs:
                        row = layout.box().row(align=True)
                        row.label(text=i.title())
                        for ii in cln:
                            if ii == 'FK':
                                row.alert=True

                            MERC = row.operator('hisanim.loadmerc', text='New' if ii == 'IK' else 'Legacy')
                            MERC.merc = i
                            MERC.type = ii
                    row = layout.row()
                    row.prop(context.scene.hisanimvars, "bluteam")
                    op = row.operator('trifecta.textbox', text='', icon='QUESTION')
                    op.text = '''"New" rigs are made with Rigify, allowing for more extensive control over the armature with features like IK/FK swapping. "Legacy" rigs comprise of ONLY forward kinematics, and should only be used to apply taunts onto.\nWhen "In-Game Models" is enabled, lower-poly bodygroups will be used to ensure the most compatibility with cosmetics. When disabled, the higher-poly (A.K.A. SFM) bodygroups will be used instead.\nRimlight Strength determines the intensity of rim-lights on characters. Because TF2-shading can't be translated 1:1, this is left at 0.4 by default.'''
                    op.icons='ARMATURE_DATA,OUTLINER_OB_ARMATURE,SHADING_RENDERED'
                    op.size = '76,76,76'
                    layout.row().prop(context.scene.hisanimvars, "cosmeticcompatibility")
                    layout.row().prop(props, 'hisanimrimpower', slider=True)
            
                    
            else:
                layout.row().label(text='"rigs" has not been added!')
                layout.row().label(text='If it is added, check name.')
            return

        if props.tools == 'BONEMERGE':
            row = layout.row()
            row.label(text='Attach TF2 cosmetics.', icon='DECORATE_LINKED')
            ob = context.object
            row = layout.row()
            self.layout.prop_search(context.scene.hisanimvars, "hisanimtarget", bpy.data, "objects", text="Link to", icon='ARMATURE_DATA')
            
            box = layout.row().box()
            box.row().label(text='Binding cosmetics') 
            box.row().operator('hisanim.attachto', icon="LINKED")
            box.row().operator('hisanim.detachfrom', icon="UNLINKED")
            box.row().prop(context.scene.hisanimvars, 'hisanimscale')
            box = layout.row().box()
            row = box.row()
            row.label(text='Bind facial cosmetics')
            op = row.operator('trifecta.textbox', text='', icon='QUESTION')
            op.text = 'When binding a cosmetic to a face, it can only be posed through shape keys. Flex controllers are unsupported.'
            op.icons = 'MESH_MONKEY'
            op.size = '56'
            op.width = 310
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
                    layout.row().label(text='There is a face panel on the rig. Pose the face there!')
                    return
                
            box = layout.box()
            row = box.row()
            if props.ddfacepanel or not prefs.compactable:
                if prefs.compactable:
                    row.prop(props, 'ddfacepanel', icon='DISCLOSURE_TRI_DOWN', emboss=False)
                row.label(text='Face Poser')
                op = row.operator('trifecta.textbox', icon='QUESTION', text='')
                op.text = "Don't be worried about the sliders automatically resetting. It was necessary to implement stereo flexes. The values mean nothing at all. Stereo sliders will appear as RED on a keyframe.\nWhen this button is BLUE, it indicates that Auto-Keyframing is enabled. Any changes you make will be saved.\nPressing this button will add a keyframe to all sliders. Useful for starting an animation sequence\nEnabling this button by stereo sliders will reveal the true value for sliders.\nFlex Controllers vs. Shapekeys: Flex Controllers simulate muscle strands being pulled, making it difficult to create a distorted face. Shapekeys can be easily stacked, so its easy to create a very deformed face.\nOptimizing mercenaries can give a significant performance boost by disabling the flex controllers, which will somewhat lock the face. Don't forget to restore the face on final render."
                op.icons = 'ERROR,REC,DECORATE_KEYFRAME,RESTRICT_VIEW_OFF,SHAPEKEY_DATA,MODIFIER_ON'
                op.size = '76,76,76,76,76,76'
                op.width = 400
                row = box.row(align=True)
                row.operator('hisanim.optimize', icon='MODIFIER_ON')
                row.operator('hisanim.restore', icon='MODIFIER_OFF')
                row = box.row(align=True)
                row.prop(props, 'use_flexes', toggle=True)
                row.prop(props, 'use_skeys', toggle=True)
                row = box.row(align=True)
                col = row.column()
                if props.mode == 'FLEXES':
                    col.template_list('HISANIM_UL_SLIDERS', 'Sliders', props, 'sliders', props, 'sliderindex')
                else:
                    ob = context.object
                    key = ob.data.shape_keys
                    col.template_list("MESH_UL_skeys_nodriver", "", key, "key_blocks", ob, "active_shape_key_index", rows=5)
                col = row.column()
                col.operator('hisanim.fixfaceposer', icon='PANEL_CLOSE' if props.dragging else 'CHECKMARK', text='')
                col.row().prop(bpy.context.scene.tool_settings, 'use_keyframe_insert_auto', text='')
                col.row().operator('hisanim.keyeverything', icon='DECORATE_KEYFRAME', text='')
                
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
            else:
                row.prop(props, 'ddfacepanel', icon='DISCLOSURE_TRI_RIGHT', emboss=False)
                row.label(text='Face Poser', icon='RESTRICT_SELECT_OFF')
            
            box = layout.box()
            row = box.row()

            if props.ddposelib or not prefs.compactable:
                if prefs.compactable:
                    row.prop(props, 'ddposelib', icon='DISCLOSURE_TRI_DOWN', emboss=False)
                row.label(text=f'''Pose Library: {poselib.stage.title()}{(' "'  + poselib.visemeName + '"') if poselib.stage == 'APPLY' else ''}''')
                op = row.operator('trifecta.textbox', text='', icon='QUESTION')
                op.text = 'The Pose Library is a place to store presets for face shapes. It will only save flex controller data.\nEnabling "Reset All" will reset the face before applying the preset.'
                op.icons = 'OUTLINER_OB_GROUP_INSTANCE,LOOP_BACK'
                op.size = '56,56'
                op.width = 290
                row = box.row()
                if poselib.stage == 'SELECT':
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
                    

                if poselib.stage == 'ADD':
                    row.template_list('HISANIM_UL_USESLIDERS', 'Sliders', props, 'sliders', props, 'sliderindex')
                    row = box.row(align=True)
                    row.prop(poselib, 'sort', toggle=True)
                    row.prop(props, 'up', text='Upper', toggle=True)
                    row.prop(props, 'mid', text='Mid', toggle=True)
                    row.prop(props, 'low', text='Lower', toggle=True)
                    box.row().prop(poselib, 'name')
                    box.row().operator('poselib.add')
                    box.row().operator('poselib.cancel')
                if poselib.stage == 'APPLY':
                    row.template_list('POSELIB_UL_visemes', 'Items', poselib, 'dictVisemes', poselib, 'activeItem')
                    box.row().prop(poselib, 'value', slider=True)
                    box.row().prop(poselib, 'keyframe')
                    box.row().prop(poselib, 'reset')
                    box.row().operator('poselib.apply')
                    box.row().operator('poselib.cancelapply')
            else:
                row.prop(props, 'ddposelib', icon='DISCLOSURE_TRI_RIGHT', emboss=False)
                row.label(text='Pose Library', icon='OUTLINER_OB_GROUP_INSTANCE')
                
            box = layout.box()
            row = box.row()

            if props.ddrandomize or not prefs.compactable:
                if prefs.compactable:
                    row.prop(props, 'ddrandomize', icon='DISCLOSURE_TRI_DOWN', emboss=False)
                row.label(text='Face Randomizer')
                op = row.operator('trifecta.textbox', icon='QUESTION', text='')
                op.text = 'Make funny faces!'
                op.icons = 'MONKEY'
                op.size = '56'
                op.width = 125
                row = box.row()
                row.prop(props, 'keyframe')
                row.prop(props, 'randomadditive')
                
                box.row().prop(props, 'randomstrength', slider=True)
                box.row().operator('hisanim.randomizeface')
                box.row().operator('hisanim.resetface')
                box.row().prop(context.object.data, '["aaa_fs"]', text='Flex Scale')
            else:
                row.prop(props, 'ddrandomize', icon='DISCLOSURE_TRI_RIGHT', emboss=False)
                row.label(text='Face Randomizer', icon='RNDCURVE')

            box = layout.box()
            row = box.row()

            if props.ddlocks or not prefs.compactable:
                if prefs.compactable:
                    row.prop(props, 'ddlocks', icon='DISCLOSURE_TRI_DOWN', emboss=False)
                row.label(text='Lock Sliders')
                op = row.operator('trifecta.textbox', text='', icon='QUESTION')
                op.text = 'Locking a flex controller will keep it from getting randomized.'
                op.icons = 'LOCKED'
                op.size = '128'
                op.width = 340
                
                data = context.object.data
                box.row().template_list('HISANIM_UL_LOCKSLIDER', 'Lock Sliders', props, 'sliders', props, 'sliderindex')
            else:
                row.prop(props, 'ddlocks', icon='DISCLOSURE_TRI_RIGHT', emboss=False)
                row.label(text='Lock Sliders', icon='LOCKED')

def textBox(self, sentence, icon='NONE', line=56):
    layout = self.layout
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

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=self.width)
    
    def draw(self, context):
        sentences = self.text.split('\n')
        icons = self.icons.split(',')
        sizes = self.size.split(',')
        for sentence, icon, size in zip(sentences, icons, sizes):
            textBox(self, sentence, icon, int(size))

    def execute(self, context):
        return {'FINISHED'}

classes = [
    TRIFECTA_PT_PANEL,
    HISANIM_UL_SLIDERS,
    HISANIM_UL_RESULTS,
    HISANIM_UL_LOCKSLIDER,
    POSELIB_UL_panel,
    HISANIM_UL_USESLIDERS,
    POSELIB_UL_visemes,
    LOADOUT_UL_loadouts,
    MESH_UL_skeys_nodriver,
    TRIFECTA_OT_genericText
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)