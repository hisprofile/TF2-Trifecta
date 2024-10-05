import bpy
import os

from typing import Dict, Set
from bpy.types import ID

from . import icons, panel

global path
global cln
cln = ["IK", "FK"]

mercs = ['scout', 'soldier', 'pyro', 'demo',
            'heavy', 'engineer', 'medic', 'sniper', 'spy']

map_to_do = dict()

def MAP(x,a,b,c,d, clamp=None):
    y=(x-a)/(b-a)*(d-c)+c
    
    if clamp:
        return min(max(y, c), d)
    else:
        return y

def SetActiveCol(a=None):  # set the active collection
    VL = bpy.context.view_layer
    if a == None:
        VL.active_layer_collection = VL.layer_collection
        return {'FINISHED'}


def GetActiveCol():  # get the active collection
    return bpy.context.view_layer.active_layer_collection

def link(path, name, type):
    with bpy.data.libraries.load(path, link=True, relative=True) as (From, To):
        setattr(To, type, [name])

def recursive(d_block):
        if map_to_do.get(d_block): return
        user_map = bpy.data.user_map(subset=[d_block])
        IDs = user_map[d_block]
        map_to_do[d_block] = d_block.make_local()
        for ID in IDs:
            if map_to_do.get(ID): continue
            recursive(ID)
        return d_block

def get_id_reference_map() -> Dict[ID, Set[ID]]:
    """Return a dictionary of direct datablock references for every datablock in the blend file."""
    inv_map = {}
    for key, values in bpy.data.user_map().items():
        for value in values:
            if value == key:
                # So an object is not considered to be referencing itself.
                continue
            inv_map.setdefault(value, set()).add(key)
    return inv_map


def recursive_get_referenced_ids(
    ref_map: Dict[ID, Set[ID]], id: ID, referenced_ids: Set, visited: Set
):
    """Recursively populate referenced_ids with IDs referenced by id."""
    if id in visited:
        # Avoid infinite recursion from circular references.
        return
    visited.add(id)
    for ref in ref_map.get(id, []):
        referenced_ids.add(ref)
        recursive_get_referenced_ids(
            ref_map=ref_map, id=ref, referenced_ids=referenced_ids, visited=visited
        )


def get_all_referenced_ids(id: ID, ref_map: Dict[ID, Set[ID]]) -> Set[ID]:
    """Return a set of IDs directly or indirectly referenced by id."""
    referenced_ids = set()
    recursive_get_referenced_ids(
        ref_map=ref_map, id=id, referenced_ids=referenced_ids, visited=set()
    )
    return referenced_ids

class HISANIM_OT_LOADMERC(bpy.types.Operator):
    merc: bpy.props.StringProperty(default='')
    type: bpy.props.StringProperty(default='')
    bl_idname = 'hisanim.loadmerc'
    bl_label = 'Deploy Mercenary'
    bl_description = 'Deploy a mercenary with a specified rig into your scene'
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        prefs = context.preferences.addons[__package__].preferences
        return prefs.rigs.get(context.scene.hisanimvars.rigs) != None

    def execute(self, context):
        prefs = bpy.context.preferences.addons[__package__].preferences
        props = bpy.context.scene.hisanimvars
        PATH = prefs.rigs[context.scene.hisanimvars.rigs].path

        if not os.path.exists(PATH):
            self.report({'ERROR'}, f'Entry for rigs exists, but the path does not exist!')
            return {'CANCELLED'}

        bak = GetActiveCol()

        SetActiveCol()

        merc_blend = os.path.join(PATH, f'{self.merc}.blend')

        if not os.path.exists(merc_blend):
            #self.report({'ERROR'}, f'Your selected rig-set, {context.scene.hisanimvars.rigs}, does not contain ')
            self.report({'ERROR'}, f'{merc_blend} does not exist!')
            return {'CANCELLED'}
        
        try:
            with bpy.data.libraries.load(merc_blend, link=True) as (data_from, data_to):
                data_to.collections = [self.merc+self.type]
        except:
            self.report({'ERROR'}, f'An error occured when trying to open {merc_blend}. The file is corrupted.')
            self.report({'ERROR'}, f'.blend file for "{self.merc}" is corrupt! Check INFO for more information.')

        if data_to.collections[0] == None:
            self.report({'WARNING'}, f'{merc_blend} is missing a collection named {self.merc+self.type}. Were the rigs setup correctly?')
            self.report({'ERROR'}, f'.blend file is missing collection "{self.merc+self.type}". Check INFO for more information.')
            return {'CANCELLED'}
        
        col: bpy.types.Collection = data_to.collections[0]
        col = col.make_local()

        context.scene.collection.children.link(col)

        for colChild in col.children_recursive:
            recursive(colChild)

        for obj in col.objects:
            recursive(obj)

        for colChild in col.children_recursive:
            for obj in colChild.objects:
                recursive(obj)

        for obj in col.all_objects:
            if obj.data == None:
                continue
            #recursive(obj.data)
            map_to_do[obj.data] = obj.data.make_local()

        for obj in col.all_objects:
            if not isinstance(obj.data, bpy.types.Mesh):
                continue
            mesh = obj.data
            for material in mesh.materials:
                map_to_do[material] = material.make_local()

            for modifier in obj.modifiers:
                if modifier.type != 'NODES': continue
                modifier.node_group.make_local()


        for linked, local in list(map_to_do.items()):
            #print(linked, linked.library)
            linked.user_remap(local)
            #print(linked, linked.library)
        #for ID in map_to_do.keys():
        #    print(ID)
            #bpy.data.batch_remove({ID})


        # make a variable targeting the added collection of the character
        # this mostly pertains to blu switching. any material added has been switched to BLU and will therefore be skipped.
        matblacklist = []
        # iterate through collection of objects

        if ((goto := context.scene.get('MERC_COL')) == None) or (context.scene.get('MERC_COL') not in context.scene.collection.children_recursive):
            context.scene['MERC_COL'] = bpy.data.collections.new('Deployed Mercs')
            context.scene.collection.children.link(context.scene['MERC_COL'])
            goto = context.scene.get('MERC_COL')

        for obj in col.objects:
            # link the current object to 'Deployed Mercs'
            goto.objects.link(obj)

            if obj.get('COSMETIC') != None:
                # if Cosmetic Compatibility is enabled and a mesh is not compatible, delete it.
                if context.scene.hisanimvars.cosmeticcompatibility and not obj['COSMETIC']:
                    bpy.data.objects.remove(obj)
                    continue
                # vice versa
                if not context.scene.hisanimvars.cosmeticcompatibility and obj['COSMETIC']:
                    bpy.data.objects.remove(obj)
                    continue

        for obj in data_to.collections[0].objects: # go through the collection 
            for mat in obj.material_slots:
                # if Save Space is enabled, this is useless as all material contents will be linked.
                mat = mat.material
                if mat == None:
                    continue
                if mat.node_tree == None:
                    continue
                if mat.node_tree.nodes == None:
                    continue
                if mat in matblacklist:
                    continue
                if context.scene.hisanimvars.bluteam:
                    if (red := mat.node_tree.nodes.get('REDTEX')) != None and (blu := mat.node_tree.nodes.get('BLUTEX')) != None:
                        for link in red.outputs[0].links:
                            mat.node_tree.links.new(
                                blu.outputs[0], link.to_socket)
                        matblacklist.append(mat)
                
                for NODE in mat.node_tree.nodes:

                    if NODE.type == 'GROUP':
                        if NODE.node_tree.name == 'TF2 BVLG':
                            NODE.inputs['Rim boost'].default_value = NODE.inputs['Rim boost'].default_value * props.hisanimrimpower     

                matblacklist.append(mat)

        for obj in col.all_objects:
            if obj.parent: continue
            obj.location = context.scene.cursor.location

        context.scene['new_spawn'] = col

        refmap = get_id_reference_map()
        refmap = get_all_referenced_ids(col, refmap)

        for ID in refmap:
            if not isinstance(ID, bpy.types.Text): continue
            ID.as_module()

        del context.scene['new_spawn']

        bpy.data.collections.remove(col)
        map_to_do.clear()
        bpy.context.view_layer.active_layer_collection = bak
        bpy.data.orphans_purge(do_linked_ids=True, do_recursive=True)
        return {'FINISHED'}
    
class MD_OT_hint(bpy.types.Operator):
    bl_idname = 'md.hint'
    bl_label = 'Hints'
    bl_description = 'A window will display any possible questions you have'

    def invoke(self, context, event):
        import random
        if random.random() >= 0.5:
            from urllib import request
            from pathlib import Path
            img = request.urlretrieve('https://i.imgur.com/WHs40vm.png', 'mercdeployer.png')
            path = os.path.join(Path(__file__).parent, 'mercdeployer.png')
            bpy.ops.object.load_reference_image(filepath=path)
            bpy.data.images['mercdeployer.png'].pack()
            os.remove(path)
        del random
        return context.window_manager.invoke_props_dialog(self, width=325)
    
    def draw(self, context):
        textBox = panel.textBox
        textBox(self.layout, '"New" rigs are made with Rigify, allowing for more extensive control over the armature with features like IK/FK swapping. "Legacy" rigs comprise of ONLY forward kinematics, and should only be used to apply taunts onto.', 'ARMATURE_DATA', 56)
        textBox(self.layout, 'When "In-Game Models" is enabled, lower-poly bodygroups will be used to ensure the most compatibility with cosmetics. When disabled, the higher-poly (A.K.A. SFM) bodygroups will be used instead.', 'OUTLINER_OB_ARMATURE', 50)
        textBox(self.layout, '''"Rimlight Strength" determines the intensity of rim-lights on characters. Because TF2-shading can't be translated 1:1, this is left at 0.4 by default.''', 'SHADING_RENDERED')

    def execute(self, context):
        return {'FINISHED'}

class MD_PT_spawnmenu(bpy.types.Panel):
    bl_label = ''
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'WINDOW'

    def draw(self, context):
        layout = self.layout
        props = context.scene.hisanimvars
        prefs = context.preferences.addons[__package__].preferences

        if len(prefs.rigs) < 1:
            layout.row().label(text='No rigs added!')
            return None
        
        row = layout.row()
        row.prop(context.scene.hisanimvars, 'rigs')

        row = layout.row()
        row.prop(props, "bluteam", text='BLU Team')

        layout.row().prop(props, "cosmeticcompatibility")
        layout.row().prop(props, 'hisanimrimpower', slider=True)
        
        grid = layout.box().column_flow(columns=2, align=False)
        for c in cln:
            grid.label(text='New' if c == 'IK' else 'Legacy')
            grid.alert = False if c == 'IK' else True
            for merc in mercs:
                op = grid.operator('hisanim.loadmerc', text=merc.title(), icon_value=icons.id(merc) if c == 'IK' else 0)
                op.merc = merc
                op.type = c

class MD_MT_Menu(bpy.types.Menu):
    bl_label = 'Merc Deployer'
    bl_idname = 'VIEW3D_MT_merc_deployer'

    def draw(self, context):
        prefs = context.preferences.addons[__package__].preferences
        layout = self.layout
        layout.alignment = 'LEFT'
        layout.popover(panel='MD_PT_props', text='Properties')
        if len(prefs.rigs) < 1:
            layout.row().label(text='No rigs added!')
            return None
        grid = layout.column_flow(columns=2, align=False)
        for c in cln:
            grid.label(text='New' if c == 'IK' else 'Legacy')
            for merc in mercs:
                op = grid.operator('hisanim.loadmerc', text=merc.title(), icon_value=icons.id(merc) if c == 'IK' else 0)
                grid.alert = True
                op.merc = merc
                op.type = c

def menu_func(self, context):
    #self.layout.menu(MD_MT_Menu.bl_idname, icon='FORCE_DRAG')
    self.layout.popover(panel='MD_PT_spawnmenu', text='Merc Deployer', icon='FORCE_DRAG')

classes = [HISANIM_OT_LOADMERC,
           MD_OT_hint,
           MD_MT_Menu,
           MD_PT_spawnmenu
           ]

def register():
    for i in classes:
        bpy.utils.register_class(i)
    bpy.types.VIEW3D_MT_add.append(menu_func)

def unregister():
    bpy.types.VIEW3D_MT_add.remove(menu_func)
    for i in reversed(classes):
        bpy.utils.unregister_class(i)