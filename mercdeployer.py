import bpy
import os
import random
from pathlib import Path

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

def append(a, b):  # get a class from TF2-V3
    blendfile = f'{bpy.context.preferences.addons[__package__].preferences.hisanim_paths["TF2-V3"].path}/{a}.blend'
    section = "/Collection/"
    object = a + b

    directory = blendfile + section

    bpy.ops.wm.append(filename=object, directory=directory)


def appendtext(a):  # add the .py script to add further control to faces
    blendfile = f'{bpy.context.preferences.addons[__package__].preferences.hisanim_paths["TF2-V3"].path}/{a}.blend'
    section = "/Text/"
    object = f'{a}.py'

    directory = blendfile + section
    try:
        bpy.data.texts[f'{a}.py']
        bpy.data.texts[f'{a}.py'].use_fake_user = True
    except:
        try:
            bpy.ops.wm.append(filename=object, directory=directory)
        except:
            return "cancelled"
        try:
            bpy.data.texts[f'{a}.py'].as_module()
        except:
            return "cancelled"
        bpy.data.texts[f'{a}.py'].use_module = True
        bpy.data.texts[f'{a}.py'].use_fake_user = True
    return {'FINISHED'}


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


def PurgeNodeGroups():  # delete unused node groups from the .blend file
    for i in bpy.data.node_groups:
        if i.users == 0:
            bpy.data.node_groups.remove(i)
    return {'FINISHED'}


def PurgeImages():  # delete unused images
    for i in bpy.data.images:
        if i.users == 0:
            bpy.data.images.remove(i)
    return {'FINISHED'}


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
    bl_label = 'Load Mercenary'
    bl_options = {'UNDO'}

    def execute(self, context):
        prefs = bpy.context.preferences.addons[__package__].preferences
        if prefs.hisanim_paths.get('TF2-V3') == None:
            self.report(
                {'ERROR'}, 'No Mercs Found! Make sure you have TF2-V3 setup as an entry!')
            return {'CANCELLED'}
        if prefs.hisanim_paths['TF2-V3'].this_is != 'FOLDER':
            self.report({'ERROR'}, 'TF2 Rigs entry is invalid!')
        PATH = prefs.hisanim_paths['TF2-V3'].path
        bak = GetActiveCol()
        SetActiveCol()
        if appendtext(self.merc) == "cancelled":
            self.report(
                {'ERROR'}, "Entry for rigs exists, but .blend file could not be found!")
            return {'CANCELLED'}
        if context.scene.hisanimvars.savespace:  # if linking is enabled
            link(os.path.join(PATH, f'{self.merc}.blend'),
                 self.merc + self.type, 'Collection')
            name = self.merc + self.type
            bpy.data.objects.remove(bpy.data.objects[name])
            bpy.context.scene.collection.children.link(
                bpy.data.collections[name].make_local())

            '''
            This is to make everything but images and node groups localized. Everything must be localized in order,
            or duplicates will form. The order is
            Objects > Meshes > Materials > Armatures
            
            If you make one mesh local that a linked object is still using but another localized object is also using it, then the localized object will receive a localized version of the mesh
            where the linked object will keep using the linked mesh.

            If all users of a data block attempting to be localized are ALL localized, then the linked data block will be deleted upon all localized users receiving their localized version of the data block.
            '''

            for i in bpy.data.collections[name].objects:
                if i.type != 'MESH':
                    continue
                NEW = i.make_local()
                NEW.data.make_local()

            for i in bpy.data.collections[name].objects:
                if i.type != 'MESH':
                    continue
                for m in i.material_slots:
                    if m.material.library != None:
                        m.material.make_local()

            for i in bpy.data.collections[name].objects:
                if i.type != 'EMPTY':
                    continue
                i.make_local()

            armature = bpy.data.collections[name].objects[0]
            while armature.parent != None:  # get the absolute root of the objects
                armature = armature.parent
            for i in armature.children_recursive:
                if i.type != 'ARMATURE':
                    continue
                i.make_local().data.make_local()
            armature.make_local().data.make_local()
        else:
            append(self.merc, self.type)
        # make a variable targeting the added collection of the character
        justadded = str(self.merc + self.type)
        # this mostly pertains to blu switching. any material added has been switched to BLU and will therefore be skipped.
        matblacklist = []
        armature = bpy.data.collections[justadded].objects[0]
        while armature.parent != None:  # get the absolute root of the objects
            armature = armature.parent
        armature.location = bpy.context.scene.cursor.location
        if (text := armature.get('rig_ui')) != None:
            text.as_module()
        # iterate through collection of objects
        for obj in bpy.data.collections[justadded].objects:
            if (goto := bpy.data.collections.get('Deployed Mercs')) == None:
                # If the collection 'Deployed Mercs' does not exist yet, create it
                bpy.context.scene.collection.children.link(
                    bpy.data.collections.new('Deployed Mercs'))
                goto = bpy.data.collections['Deployed Mercs']
            # link the current object to 'Deployed Mercs'
            goto.objects.link(obj)
            if obj.get('FLEXES') and not context.scene.hisanimvars.wrinklemaps:
                bpy.data.objects.remove(obj)
                continue
            if obj.modifiers.get('FLEXES') != None and not context.scene.hisanimvars.wrinklemaps:
                obj.modifiers.remove(obj.modifiers.get('FLEXES'))
            if obj.get('COSMETIC') != None:
                # if Cosmetic Compatibility is enabled and a mesh is not compatible, delete it.
                if context.scene.hisanimvars.cosmeticcompatibility and not obj['COSMETIC']:
                    bpy.data.objects.remove(obj)
                    continue
                # vice versa
                if not context.scene.hisanimvars.cosmeticcompatibility and obj['COSMETIC']:
                    bpy.data.objects.remove(obj)
                    continue
            for mat in obj.material_slots:
                # if Save Space is enabled, this is useless as all material contents will be linked.
                if context.scene.hisanimvars.savespace:
                    break
                mat = mat.material
                for NODE in mat.node_tree.nodes:
                    # use existing nodegroups
                    if Collapse(NODE, 'TF2 BVLG') == "continue":
                        continue

                    if Collapse(NODE, 'TF2 Diffuse') == "continue":
                        continue

                    if Collapse(NODE, 'TF2 Eye') == "continue":
                        continue
                    # use existing images
                    if NODE.type == 'TEX_IMAGE':
                        ReuseImage(NODE, PATH + f'/{self.merc}.blend')

                if mat in matblacklist:
                    continue # relevant towards BLU. if the material has already been swapped to BLU, continue.
                
                if context.scene.hisanimvars.bluteam:
                    if (red := mat.node_tree.nodes.get('REDTEX')) != None and (blu := mat.node_tree.nodes.get('BLUTEX')) != None:
                        getconnect = red.outputs[0].links[0].to_node
                        mat.node_tree.links.new(
                            blu.outputs[0], getconnect.inputs[0])
                        matblacklist.append(mat)
                        break
        armature = bpy.data.collections[justadded].objects[0]
        while armature.parent != None:  # get the absolute root of the objects
            armature = armature.parent
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

            if ".0" in shape:
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
        PurgeNodeGroups()
        PurgeImages()
        PurgeNodeGroups()
        bpy.context.view_layer.active_layer_collection = bak
        return {'FINISHED'}

class HISANIM_OT_RANDOMIZEFACE(bpy.types.Operator):
    bl_idname = 'hisanim.randomizeface'
    bl_label = 'Randomize Face'
    bl_description = 'Randomize the values of the facial sliders'
    bl_options = {'UNDO'}
    reset: bpy.props.BoolProperty(default=False)

    def execute(self, context):
        props = context.scene.hisanimvars
        data = context.object.data
        for i in data.keys():
            if i == 'aaa_fs':
                continue
            if (locklist := data.get('locklist')) != None:
                if locklist.get(i) == True: continue
            try:
                prop = data.id_properties_ui(i).as_dict()
            except:
                continue
            min = prop.get('min')
            max = prop.get('max')
            randval = random.random() 
            randval = MAP(randval, 0, 1, min, max) * (1- self.reset) * props.randomstrength
            if props.randomadditive and not self.reset:
                data[i] = data[i] + randval
            else:
                data[i] = randval
            
            if props.keyframe:
                data.keyframe_insert(data_path=f'["{i}"]')
                context.scene.frame_current += 1
                context.scene.frame_current += -1
        
        data.keyframe_insert(data_path='["aaa_fs"]')
        data.keyframe_delete(data_path='["aaa_fs"]')

        return {'FINISHED'}

class HISANIM_OT_LOCK(bpy.types.Operator):
    bl_idname = 'hisanim.lock'
    bl_label = 'Lock Slider'
    bl_options = {'UNDO'}

    datapath: bpy.props.StringProperty()
    key: bpy.props.StringProperty()

    def execute(self, context):
        obj = bpy.data.objects[self.datapath]
        if (locklist := obj.data.get('locklist')) == None:
            obj.data['locklist'] = {}
            locklist = obj.data['locklist']
        if (lockstate := locklist.get(self.key)) == None:
            locklist[self.key] = True
            return {'FINISHED'}
        locklist[self.key] = 1 - lockstate
        return {'FINISHED'}

class MD_PT_MERCDEPLOY(bpy.types.Panel):
    '''Rolling in the nonsense, deploy the fantasy!'''
    bl_label = "Merc Deployer"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Merc Deployer"
    bl_icon = "FORCE_DRAG"

    def draw(self, context):
        layout = self.layout
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
        row = layout.row()
        row.prop(context.scene.hisanimvars, "cosmeticcompatibility")


classes =   [HISANIM_OT_LOADMERC,
            HISANIM_OT_RANDOMIZEFACE,
            HISANIM_OT_LOCK]
            #MD_PT_MERCDEPLOY]


def register():
    for i in classes:
        bpy.utils.register_class(i)


def unregister():
    for i in reversed(classes):
        bpy.utils.unregister_class(i)
