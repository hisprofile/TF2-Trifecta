import bpy
from . import bonemerge, mercdeployer, newuilist
from bpy.types import (UIList)

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
                    split = row.split(factor=0.7, align=True)
                    split.prop(item, 'value', slider=True, text=Name)
                    split.prop(props, 'LR', slider=True, text='L-R')
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
                    row.prop(item, 'value', slider=True, text=Name)
                else:
                    row.prop(props.activeface.data, f'["{item.name}"]', text=item.name[4:])
                op = row.operator('hisanim.keyslider', icon='DECORATE_KEYFRAME' if isKeyed else 'DECORATE_ANIMATE', text='', depress=isKeyed)
                op.delete = isKeyed
                op.slider = item.name
                row.prop(item, 'realvalue', icon='RESTRICT_VIEW_OFF' if item.realvalue else 'RESTRICT_VIEW_ON', text='')

        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text='')

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
        props = context.scene.hisanimvars
        isKeyed = hasKey(bpy.context.object, item)
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
    def draw_item(self, context,
            layout, data,
            item, icon,
            active_data, active_propname,
            index):
        props = context.scene.poselibVars
        row = layout.row()
        row.prop(item, 'use', text='')
        row.label(text="_".join(item.name.split("_")[1:]))

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
        row = layout.row()
        row.prop(props, 'tools')
        if props.tools == 'WARDROBE':
            row = layout.row()
            row.label(text='Spawn TF2 Cosmetics', icon='MOD_CLOTH')
            row = layout.row()
            row.prop(props, 'query', text="Search", icon="VIEWZOOM")
            row = layout.row()
            row.prop(context.scene.hisanimvars, 'hisanimweapons')
            if props.hisanimweapons:
                row = layout.row()
                row.prop(props, 'autobind')
            if props.query == '': layout.label(text="Warning! Don't leave the text field empty!")
            if prefs.missing == True:
                row = layout.row()
                row.label(text='Assets missing. Check preferences for info.')
            row=layout.row()
            row.operator('hisanim.search', icon='VIEWZOOM')
            row=layout.row()
            row.operator('hisanim.clearsearch', icon='X')
            if props.ddmatsettings or not prefs.compactable:
                if prefs.compactable: row = layout.row()
                if prefs.compactable: row.prop(props, 'ddmatsettings', icon='DISCLOSURE_TRI_DOWN', emboss=False)
                if prefs.compactable: row.label(text='Material settings')
                if not prefs.compactable: layout.label(text='Material settings')
                row=layout.row()
                row.operator('hisanim.lightwarps')
                row=layout.row()
                row.operator('hisanim.removelightwarps')
                row = layout.row()
                row.prop(context.scene.hisanimvars, 'hisanimrimpower', slider=True)
                row = layout.row()
                row.prop(context.scene.hisanimvars, 'wrdbbluteam')
            else:
                row = layout.row()
                row.prop(props, 'ddmatsettings', icon='DISCLOSURE_TRI_RIGHT', emboss=False)
                row.label(text='Material settings', icon='MATERIAL')

            if len(context.selected_objects) > 0:
                if context.object.get('skin_groups') != None:
                    row = layout.row()
                    if props.ddpaints or not prefs.compactable:
                        if prefs.compactable: row.prop(props, 'ddpaints', icon='DISCLOSURE_TRI_DOWN', emboss=False)
                        if prefs.compactable: row.label(text='Paints')
                        ob = context.object
                        row = layout.row()
                        row.label(text='Attempt to fix material')
                        row = layout.row()
                        row.template_list("MATERIAL_UL_matslots", "", ob, "material_slots", ob, "active_material_index")
                        row = layout.row(align=True)
                        row.operator('hisanim.materialfix')
                        row.operator('hisanim.revertfix')
                        row = layout.row()
                        row.template_icon_view(context.window_manager, 'hisanim_paints', show_labels=True, scale=4, scale_popup=4)
                        row=layout.row(align=True)
                        oper = row.operator('hisanim.paint', text = 'Add Paint')
                        oper.PAINT = newuilist.paints[context.window_manager.hisanim_paints]
                        row.operator('hisanim.paintclear')
                    else:
                        row.prop(props, 'ddpaints', icon='DISCLOSURE_TRI_RIGHT', emboss=False)
                        row.label(text='Paints', icon='BRUSH_DATA')

            if props.searched:
                if props.ddsearch or not prefs.compactable:
                    if prefs.compactable: row = layout.row()
                    if prefs.compactable: row.prop(props, 'ddsearch', icon='DISCLOSURE_TRI_DOWN', emboss=False)
                    if prefs.compactable: row.label(text='Search Results')
                    if not prefs.compactable: layout.label(text='Search Results')
                    hits = props.results
                    split = layout.split(factor=0.2)
                    row = layout.row()
                    if len(hits) > 0:
                        if len(hits) == 1:
                            row.label(text=f'{len(hits)} Result')
                        else:
                            row.label(text=f'{len(hits)} Results')
                        layout.row().template_list('HISANIM_UL_RESULTS', 'Results', props, 'results', props, 'resultindex')
                    else: 
                        layout = self.layout
                        layout.label(text='Nothing found!')
                else:
                    row = layout.row()
                    row.prop(props, 'ddsearch', icon='DISCLOSURE_TRI_RIGHT', emboss=False)
                    row.label(text='Search Results', icon='VIEWZOOM')
        
        if props.tools == 'MERCDEPLOYER':
            row = layout.row()
            row.label(text='Deploy Mercenaries', icon='FORCE_DRAG')
            cln = ["IK", "FK"]
            mercs = ['scout', 'soldier', 'pyro', 'demo',
                    'heavy', 'engineer', 'medic', 'sniper', 'spy']
            if prefs.hisanim_paths.get('TF2-V3') != None:
                if prefs.hisanim_paths.get('TF2-V3').this_is != 'FOLDER':
                    row = layout.row()
                    row.label(text='TF2-V3 contains an invalid path!')
                else:
                    row = layout.row()
                    row.label(text='Move face in custom properties under data tab.')
                    row = layout.row(align=True)
                    for i in mercs:
                        row.label(text=i)
                        col = layout.column()
                        for ii in cln:
                            MERC = row.operator('hisanim.loadmerc', text=ii)
                            MERC.merc = i
                            MERC.type = ii
                        row = layout.row(align=True)
                    row.prop(context.scene.hisanimvars, "bluteam")
                    layout.row().prop(context.scene.hisanimvars, "cosmeticcompatibility")
                    layout.row().prop(props, 'wrinklemaps', text='Wrinkle Maps')
                    layout.row().prop(props, 'hisanimrimpower', slider=True)

                    
            else:
                row = layout.row()
                row.label(text='TF2-V3 has not been added!')
                row = layout.row()
                row.label(text='If it is added, check name.')
            
        if props.tools == 'BONEMERGE':
            row = layout.row()
            row.label(text='Attach TF2 cosmetics.', icon='DECORATE_LINKED')
            ob = context.object
            row = layout.row()
            self.layout.prop_search(context.scene.hisanimvars, "hisanimtarget", bpy.data, "objects", text="Link to", icon='ARMATURE_DATA')
            
            row = layout.row()
            row.operator('hisanim.attachto', icon="LINKED")
            row=layout.row()
            row.operator('hisanim.detachfrom', icon="UNLINKED")
            row = layout.row()
            row.prop(context.scene.hisanimvars, 'hisanimscale')
            row = layout.row()
            row.label(text='Bind facial cosmetics')
            row = layout.row()
            row.operator('hisanim.bindface')
            row = layout.row()
            row.label(text='Attempt to fix cosmetic')
            row = layout.row()
            row.operator('hisanim.attemptfix')

        if props.tools == 'FACEPOSER':
            rNone = False
            if len(context.selected_objects) == 0: rNone = True
            if rNone: 
                layout.label(text='Select a face!')
                return None
            if context.object == None: return None
            if context.object.type == 'EMPTY': rNone = True
            if context.object.data.get('aaa_fs') == None: rNone = True
            if rNone:
                layout.label(text='Select a face!')
                return None
            
            if props.ddfacepanel or not prefs.compactable:
                if prefs.compactable:
                    row = layout.row()
                    row.prop(props, 'ddfacepanel', icon='DISCLOSURE_TRI_DOWN', emboss=False)
                    row.label(text='Face Poser')
                row = layout.row()
                row.template_list('HISANIM_UL_SLIDERS', 'Sliders', props, 'sliders', props, 'sliderindex')
                op = row.operator('hisanim.fixfaceposer', icon='PANEL_CLOSE' if props.dragging else 'CHECKMARK', text='')
                layout.row().prop(props, 'LR', slider=True)
                row = layout.row(align=True)
                row.prop(props, 'up', text='Upper', toggle=True)
                row.prop(props, 'mid', text='Mid', toggle=True)
                row.prop(props, 'low', text='Lower', toggle=True)
                layout.row().prop(props, 'sensitivity', slider=True, text='Sensitivity')
                layout.row().operator('hisanim.keyeverything')
            else:
                row = layout.row()
                row.prop(props, 'ddfacepanel', icon='DISCLOSURE_TRI_RIGHT', emboss=False)
                row.label(text='Face Poser')

            if props.ddposelib or not prefs.compactable:
                if prefs.compactable:
                    row = layout.row()
                    row.prop(props, 'ddposelib', icon='DISCLOSURE_TRI_DOWN', emboss=False)
                    row.label(text='Pose Library')

                row = layout.row()
                if poselib.stage == 'SELECT':
                    col = row.column()
                    col.template_list('POSELIB_UL_panel', 'Pose Library', poselib, 'visemesCol', poselib, 'activeViseme')
                    col = row.column()
                    col.operator('poselib.prepareadd', text='', icon='ADD')
                    col.operator('poselib.remove', text='', icon='REMOVE')
                    col.label(text='', icon='BLANK1')
                    op = col.operator('poselib.move', text='', icon='TRIA_UP')
                    op.pos = 1
                    op1 = col.operator('poselib.move', text='', icon='TRIA_DOWN')
                    op1.pos = -1
                    layout.row().operator('poselib.rename')
                if poselib.stage == 'ADD':
                    row.template_list('HISANIM_UL_USESLIDERS', 'Sliders', props, 'sliders', props, 'sliderindex')
                    row = layout.row(align=True)
                    row.prop(poselib, 'sort', toggle=True)
                    row.prop(props, 'up', text='Upper', toggle=True)
                    row.prop(props, 'mid', text='Mid', toggle=True)
                    row.prop(props, 'low', text='Lower', toggle=True)
                    layout.row().prop(poselib, 'name')
                    layout.row().operator('poselib.add')
                    layout.row().operator('poselib.cancel')
                if poselib.stage == 'APPLY':
                    row.label(text=poselib.visemeName)
                    layout.row().template_list('POSELIB_UL_visemes', 'Items', poselib, 'dictVisemes', poselib, 'activeItem')
                    layout.row().prop(poselib, 'value', slider=True)
                    layout.row().prop(poselib, 'keyframe')
                    layout.row().operator('poselib.apply')
                    layout.row().operator('poselib.cancelapply')
                layout.row().operator('poselib.refresh')
            else:
                row = layout.row()
                row.prop(props, 'ddposelib', icon='DISCLOSURE_TRI_RIGHT', emboss=False)
                row.label(text='Pose Library')
                

            if props.ddrandomize or not prefs.compactable:
                if prefs.compactable:
                    row = layout.row()
                    row.prop(props, 'ddrandomize', icon='DISCLOSURE_TRI_DOWN', emboss=False)
                    row.label(text='Face Randomizer')
                row = layout.row()
                row.prop(props, 'keyframe')
                row = layout.row()
                row.prop(props, 'randomadditive')
                row = layout.row()
                row.prop(props, 'randomstrength', slider=True)
                row =layout.row()
                op = row.operator('hisanim.randomizeface')
                op.reset = False
                row = layout.row()
                set0 = row.operator('hisanim.randomizeface', text='Reset Face')
                set0.reset = True
                row = layout.row()
                row.prop(context.object.data, '["aaa_fs"]')
            else:
                row = layout.row()
                row.prop(props, 'ddrandomize', icon='DISCLOSURE_TRI_RIGHT', emboss=False)
                row.label(text='Face Randomizer')

            if props.ddlocks or not prefs.compactable:
                if prefs.compactable:
                    row = layout.row()
                    row.prop(props, 'ddlocks', icon='DISCLOSURE_TRI_DOWN', emboss=False)
                    row.label(text='Lock Sliders')
                data = context.object.data
                if data.get('locklist') == None:
                    layout.row().label(text='Locking will prevent randomizing.')
                layout.row().template_list('HISANIM_UL_LOCKSLIDER', 'Lock Sliders', props, 'sliders', props, 'sliderindex')
            else:
                row = layout.row()
                row.prop(props, 'ddlocks', icon='DISCLOSURE_TRI_RIGHT', emboss=False)
                row.label(text='Lock Sliders')

classes = [
    TRIFECTA_PT_PANEL,
    HISANIM_UL_SLIDERS,
    HISANIM_UL_RESULTS,
    HISANIM_UL_LOCKSLIDER,
    POSELIB_UL_panel,
    HISANIM_UL_USESLIDERS,
    POSELIB_UL_visemes
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

import bpy
from bpy.props import StringProperty, IntProperty, CollectionProperty, BoolProperty
from bpy.types import PropertyGroup, UIList, Operator, Panel


    