import bpy
import os
from . import icons, panel

global path
global cln
cln = ["IK", "FK"]

mercs = ['scout', 'soldier', 'pyro', 'demo',
            'heavy', 'engineer', 'medic', 'sniper', 'spy']

def MAP(x,a,b,c,d, clamp=None):
    y=(x-a)/(b-a)*(d-c)+c
    
    if clamp:
        return min(max(y, c), d)
    else:
        return y

# iterate through every node and node group by using the "tree" method and removing said nodes
def RemoveNodeGroups(a):
    for i in a.nodes:
        if i.type == 'GROUP':
            RemoveNodeGroups(i.node_tree)
            i.node_tree.user_clear()
            a.nodes.remove(i)
        else:
            a.nodes.remove(i)


def NoUserNodeGroup(a):  # remove fake users from node groups
    for i in a.nodes:
        if i.type == 'GROUP':
            NoUserNodeGroup(i.node_tree)
            i.node_tree.use_fake_user = False
        else:
            try:
                i.use_fake_user = False
            except:
                pass


def SetActiveCol(a=None):  # set the active collection
    VL = bpy.context.view_layer
    if a == None:
        VL.active_layer_collection = VL.layer_collection
        return {'FINISHED'}


def GetActiveCol():  # get the active collection
    return bpy.context.view_layer.active_layer_collection


def Collapse(a, b):  # merge TF2 BVLG groups
    if a.type == 'GROUP' and b in a.node_tree.name:
        c = b + "-MD"

        if a.node_tree.name == c:
            return "continue"
        if bpy.data.node_groups.get(c) != None:
            bpy.data.node_groups[c]
            # recursively remove the old nodegroup
            RemoveNodeGroups(a.node_tree)
            a.node_tree = bpy.data.node_groups[c]
        else:
            a.node_tree.name = c
            NoUserNodeGroup(a.node_tree)
    return {'FINISHED'}


def link(a, b, c):  # get a class from TF2-V3
    blendfile = a
    section = f"/{c}/"
    object = b

    directory = blendfile + section

    bpy.ops.wm.link(filename=object, directory=directory)


def ReuseImage(a, path):
    if bpy.context.scene.hisanimvars.savespace:
        bak = a.image.name
        a.image.name = a.image.name.upper()
        # if the image already exists, use it.
        if (newimg := bpy.data.images.get(bak)) != None:
            # bpy.data.images.remove(a.image)
            a.image = newimg
            return None
        link(path, bak, 'Image')  # link an image

        # if the linked image was truly linked, replace the old image with the linked image and stop the function.
        if (newimg := bpy.data.images.get(bak)) != None:
            # bpy.data.images.remove(a.image)
            a.image = newimg
            return None
        # if the function was not stopped, then revert the image name
        del newimg
        a.image.name = bak.lower()
    # if .0 is in the name, then it is most likely a duplicate. it will try to search for the original and use that instead.
    if ".0" in a.image.name:
        lookfor = a.image.name[:a.image.name.rindex(".")]
        print(f'looking for {lookfor}...')
        if (lookfor := bpy.data.images.get(lookfor)) != None:
            a.image = lookfor
            print("found!")
            a.image.use_fake_user = False
            return None
        else:  # the image is the first despite it having .0 in its name, then rename it.
            del lookfor
            print(f"no original match found for {a.image.name}! Renaming...")
            old = a.image.name
            new = a.image.name[:a.image.name.rindex(".")]
            print(f'{old} --> {new}')
            a.image.name = new
            a.image.use_fake_user = False
            return None


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

        if not os.path.exists(os.path.join(PATH, f'{self.merc}.blend')):
            self.report({'ERROR'}, f'Entry for rigs exists, but "{self.merc}.blend" could not be found inside!')
            return {'CANCELLED'}
        
        '''if appendtext(self.merc) == "cancelled":
            self.report(
                {'ERROR'}, "Entry for rigs exists, but .blend file could not be found!")
            return {'CANCELLED'}'''
        
        merc_blend = os.path.join(PATH, f'{self.merc}.blend')
        print(merc_blend)

        if context.scene.hisanimvars.savespace:  # if linking is enabled
            '''try:
                link(os.path.join(PATH, f'{self.merc}.blend'),
                    self.merc + self.type, 'Collection')
            except:
                self.report({'ERROR'}, f'.blend file for "{self.merc}" in rigs is corrupt! Redownload!')'''
            
            with bpy.data.libraries.load(merc_blend, link=True) as (data_from, data_to):
                data_to.collections = [self.merc+self.type]
            
            if data_to.collections[0] == None:
                self.report({'CANCELLED'}, f'.blend file for "{self.merc}" in rigs is corrupt! Redownload!')
                return {'CANCELLED'}

            if (script := bpy.data.texts.get(f'{self.merc}.py')) != None:
                script.as_module()
            else:
                if self.merc != 'pyro':
                    self.report({'WARNING'}, "Unless you spawned Pyro, something went wrong. The face script failed to import, which is weird...")

            name = self.merc + self.type

            context.scene.collection.children.link(data_to.collections[0].make_local())
            
            '''
            This is to make everything but images and node groups localized. Everything must be localized in order,
            or duplicates will form. The order is
            Objects > Meshes > Materials > Armatures
            
            If you make one mesh local that a linked object is still using but another localized object is also using it, then the localized object will receive a localized version of the mesh
            where the linked object will keep using the linked mesh.

            If all users of a data block attempting to be localized are ALL localized, then the linked data block will be deleted upon all localized users receiving their localized version of the data block.
            '''

            for i in data_to.collections[0].objects:
                if i.type != 'MESH':
                    continue
                NEW = i.make_local()

                for mod in NEW.modifiers:
                    if mod.type == 'NODES':
                        mod.node_group.make_local()
                NEW.data.make_local()

            for i in data_to.collections[0].objects:
                if i.type != 'MESH':
                    continue
                for m in i.material_slots:
                    if m.material.library != None:
                        m.material.make_local()

            for i in data_to.collections[0].objects:
                if i.type != 'EMPTY':
                    continue
                i.make_local()

            armature = data_to.collections[0].objects[0]
            while armature.parent != None:  # get the absolute root of the objects
                armature = armature.parent
            for i in armature.children_recursive:
                if i.type != 'ARMATURE':
                    continue
                i.make_local().data.make_local()
            armature.make_local().data.make_local()
        else:
            with bpy.data.libraries.load(merc_blend) as (data_from, data_to):
                data_to.collections = [self.merc+self.type]
            
            if data_to.collections[0] == None:
                self.report({'CANCELLED'}, f'.blend file for "{self.merc}" in rigs is corrupt! Redownload!')
                return {'CANCELLED'}

            if (script := bpy.data.texts.get(f'{self.merc}.py')) != None:
                script.as_module()
            else:
                if self.merc != 'pyro':
                    self.report({'WARNING'}, "Unless you spawned Pyro, something went wrong. The face script failed to import, which is weird...")

        # make a variable targeting the added collection of the character
        justadded = str(self.merc + self.type)
        # this mostly pertains to blu switching. any material added has been switched to BLU and will therefore be skipped.
        matblacklist = []
        # iterate through collection of objects

        if ((goto := context.scene.get('MERC_COL')) == None) or (context.scene.get('MERC_COL') not in context.scene.collection.children_recursive):
            context.scene['MERC_COL'] = bpy.data.collections.new('Deployed Mercs')
            context.scene.collection.children.link(context.scene['MERC_COL'])
            goto = context.scene.get('MERC_COL')

        for obj in data_to.collections[0].objects:
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
        armature = data_to.collections[0].objects[0]
        
        while armature.parent != None:  # get the absolute root of the objects
            armature = armature.parent

        for i in armature.children_recursive:
            if i.type != 'ARMATURE':
                continue
            i.make_local().data.make_local()
        armature.make_local().data.make_local()

        if (text := armature.get('rig_ui')) != None:
            text.as_module()

        armature.location = bpy.context.scene.cursor.location # set the character to 3d cursor location
        for obj in data_to.collections[0].objects: # go through the collection 
            for mat in obj.material_slots:
                # if Save Space is enabled, this is useless as all material contents will be linked.
                mat = mat.material
                if mat in matblacklist:
                    continue
                if context.scene.hisanimvars.bluteam:
                    if (red := mat.node_tree.nodes.get('REDTEX')) != None and (blu := mat.node_tree.nodes.get('BLUTEX')) != None:
                        getconnect = red.outputs[0].links[0].to_node
                        mat.node_tree.links.new(
                            blu.outputs[0], getconnect.inputs[0])
                        matblacklist.append(mat)
                        #break
                
                for NODE in mat.node_tree.nodes:
                    # use existing nodegroups

                    if NODE.type == 'GROUP':
                        if NODE.node_tree.name == 'TF2 BVLG':
                            print(NODE.name, mat.name)
                            NODE.inputs['Rim boost'].default_value = NODE.inputs['Rim boost'].default_value * props.hisanimrimpower     

                    if context.scene.hisanimvars.savespace: continue

                    if Collapse(NODE, 'TF2 BVLG') == "continue": continue

                    if Collapse(NODE, 'TF2 Diffuse') == "continue": continue

                    if Collapse(NODE, 'TF2 Eye') == "continue": continue
                    # use existing images
                    if NODE.type == 'TEX_IMAGE':
                        ReuseImage(NODE, PATH + f'/{self.merc}.blend')
                matblacklist.append(mat)

                 # relevant towards BLU. if the material has already been swapped to BLU, continue.
        armature = data_to.collections[0].objects[0]
        while armature.parent != None:  # get the absolute root of the objects
            armature = armature.parent
        try:
            for driver in armature.data.animation_data.drivers:
                driver = driver.driver
                for var in driver.variables:
                    var.targets[0].id = armature
        except:
            pass
        
        armature.location = bpy.context.scene.cursor.location
        # remove the newly added collection.
        bpy.data.collections.remove(bpy.data.collections[justadded])
        pending = []

        # use an invisible collection reserved for bone shapes.
        if bpy.data.collections.get('MDSHAPES') == None:
            bpy.data.collections.new('MDSHAPES').use_fake_user = True

        for i in armature.pose.bones:
            # use existing bone shapes
            if i.custom_shape == None:
                continue
            for col in i.custom_shape.users_collection:
                col.objects.unlink(i.custom_shape)
            bpy.data.collections['MDSHAPES'].objects.link(i.custom_shape)
            shape = i.custom_shape.name

            if ".0" in shape: # if .0 is in the name, it's most likely a duplicate. search for the original.
                try:
                    DELETE = shape
                    if DELETE not in pending:
                        pending.append(DELETE)
                    lookfor = shape[:shape.index(".0")]
                    i.custom_shape = bpy.data.objects[lookfor]
                except:
                    bpy.data.objects[shape].name = shape[:shape.index(".0")]
        if len(pending) > 0:
            for i in pending:
                try:
                    DATA = bpy.data.objects[i].data
                    bpy.data.objects.remove(bpy.data.objects[i])
                    bpy.data.meshes.remove(DATA)
                except:
                    continue

        print("DELETING")
        # delete  unused images and nodegroups.
        bpy.context.view_layer.active_layer_collection = bak
        bpy.ops.outliner.orphans_purge(do_recursive=True)
        return {'FINISHED'}
    
class MD_OT_hint(bpy.types.Operator):
    bl_idname = 'md.hint'
    bl_label = 'Hints'
    bl_description = 'A window will display any possible questions you have'

    def invoke(self, context, event):
        import random
        if random.random() >= 0.99:
            from urllib import request
            from pathlib import Path
            img = request.urlretrieve('https://i.imgur.com/WHs40vm.png', 'mercdeployer.png')
            path = os.path.join(Path(__file__).parent, 'mercdeployer.png')
            bpy.ops.object.load_reference_image(filepath=path)
            bpy.data.images['mercdeployer.png'].pack()
            os.remove(path)
        return context.window_manager.invoke_props_dialog(self, width=325)
    
    def draw(self, context):
        textBox = panel.textBox
        textBox(self.layout, '"New" rigs are made with Rigify, allowing for more extensive control over the armature with features like IK/FK swapping. "Legacy" rigs comprise of ONLY forward kinematics, and should only be used to apply taunts onto.', 'ARMATURE_DATA', 56)
        textBox(self.layout, 'When "In-Game Models" is enabled, lower-poly bodygroups will be used to ensure the most compatibility with cosmetics. When disabled, the higher-poly (A.K.A. SFM) bodygroups will be used instead.', 'OUTLINER_OB_ARMATURE', 50)
        textBox(self.layout, '''"Rimlight Strength" determines the intensity of rim-lights on characters. Because TF2-shading can't be translated 1:1, this is left at 0.4 by default.''', 'SHADING_RENDERED')

    def execute(self, context):
        return {'FINISHED'}


class MD_MT_Menu(bpy.types.Menu):
    bl_label = 'Merc Deployer'
    bl_idname = 'VIEW3D_MT_merc_deployer'

    def draw(self, context):
        prefs = context.preferences.addons[__package__].preferences
        layout = self.layout
        layout.alignment = 'LEFT'
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
    self.layout.menu(MD_MT_Menu.bl_idname, icon='FORCE_DRAG')

classes = [HISANIM_OT_LOADMERC,
           MD_OT_hint,
           MD_MT_Menu,
           ]

def register():
    for i in classes:
        bpy.utils.register_class(i)
    bpy.types.VIEW3D_MT_add.append(menu_func)

def unregister():
    bpy.types.VIEW3D_MT_add.remove(menu_func)
    for i in reversed(classes):
        bpy.utils.unregister_class(i)