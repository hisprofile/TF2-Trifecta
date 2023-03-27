import bpy

from pathlib import Path

from bpy.props import BoolProperty
prefs = bpy.context.preferences
filepaths = prefs.filepaths
asset_libraries = filepaths.asset_libraries
blend_files = []

global path
global cln
cln = ["IK", "FK"]
path = [i.path for i in asset_libraries]

for i in path:
    if "TF2-V3" in i:
        path = i.replace("\\", "/")
        
classes = ['scout', 'soldier', 'pyro', 'demo', 'heavy', 'engineer', 'medic', 'sniper', 'spy']
def append(a, b): # get a class from TF2-V3
    blendfile = f'{bpy.context.preferences.addons[__package__].preferences.hisanim_paths["TF2-V3"].path}/{a}.blend'
    section = "/Collection/"
    object = a + b
    
    directory = blendfile + section
    
    bpy.ops.wm.append(filename=object, directory=directory)

def appendtext(a): # add the .py script to add further control to faces
    blendfile = f'{path}/{a}.blend'
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


def RemoveNodeGroups(a): # iterate through every node and node group by using the "tree" method and removing said nodes
    for i in a.nodes:
        if i.type == 'GROUP':
            RemoveNodeGroups(i.node_tree)
            i.node_tree.user_clear()
            a.nodes.remove(i)
        else:
            a.nodes.remove(i)

def NoUserNodeGroup(a): # remove fake users from node groups
    for i in a.nodes:
        if i.type == 'GROUP':
            NoUserNodeGroup(i.node_tree)
            i.node_tree.use_fake_user = False
        else:
            try:
                i.use_fake_user = False
            except:
                pass
def PurgeNodeGroups(): # delete unused node groups from the .blend file
    for i in bpy.data.node_groups:
            if i.users == 0:
                bpy.data.node_groups.remove(i)
    return {'FINISHED'}

def PurgeImages(): # delete unused images
    for i in bpy.data.images:
            if i.users == 0:
                bpy.data.images.remove(i)
    return {'FINISHED'}

def SetActiveCol(a = None): # set the active collection
    VL = bpy.context.view_layer
    if a == None:
        VL.active_layer_collection = VL.layer_collection
        return {'FINISHED'}
def GetActiveCol(): # get the active collection
    return bpy.context.view_layer.active_layer_collection

def Collapse(a, b): # merge TF2 BVLG groups
    if a.type == 'GROUP' and b in a.node_tree.name:
        c = b + "-MD"
        
        if a.node_tree.name == c:
            return "continue"
        if bpy.data.node_groups.get(c) != None:
            bpy.data.node_groups[c]
            RemoveNodeGroups(a.node_tree)
            a.node_tree = bpy.data.node_groups[c]
            #RemoveNodeGroups(bpy.data.node_groups[DELETE]) # i don't remember what this was for, but an error will always be raised, and it doesn't matter cause of the PurgeNodeGroups function
        else:
            a.node_tree.name = c
            NoUserNodeGroup(a.node_tree)
    return {'FINISHED'}

'''def ReuseImage(a):
    if ".0" in a.image.name:
        try:
            lookfor = a.image.name[:a.image.name.rindex(".")]
            print(f'looking for {lookfor}..')
            a.image = bpy.data.images[lookfor]
            print("found!")
            a.image.use_fake_user = False
        except:
            print(f"no original match found for {a.image.name}!")
            print("RENAMING")
            old = a.image.name
            new = a.image.name[:a.image.name.rindex(".")]
            print(f'{old} --> {new}')
            a.image.name = new
            a.image.use_fake_user = False
            return "continue"'''

def link(a, b, c): # get a class from TF2-V3
    blendfile = a
    section = f"/{c}/"
    object = b
    
    directory = blendfile + section
    
    bpy.ops.wm.link(filename=object, directory=directory)

def ReuseImage(a, path):
    bak = a.image.name
    a.image.name = a.image.name.upper()
    link(path, bak, 'Image') # link an image

    if (newimg := bpy.data.images.get(bak)) != None: # if the linked image was truly linked, replace the old image with the linked image and stop the function.
        a.image = newimg
        return None
    # if the function was not stopped, then revert the image name
    del newimg
    a.image.name = bak
    if ".0" in a.image.name: # if .0 is in the name, then it is most likely a duplicate. it will try to search for the original. and use that instead.
        lookfor = a.image.name[:a.image.name.rindex(".")]
        print(f'looking for {lookfor}...')
        if (lookfor := bpy.data.images.get(lookfor)) != None:
            a.image = lookfor
            print("found!")
            a.image.use_fake_user = False
            return None
        else: # the image is the first despite it having .0 in its name, then rename it.
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
        prefs  = bpy.context.preferences.addons[__package__].preferences
        if prefs.hisanim_paths.get('TF2-V3') == None:
            self.report({'INFO'}, 'No Mercs Found! Make sure you have TF2-V3 setup as an entry!')
        PATH = prefs.hisanim_paths['TF2-V3'].path
        bak = GetActiveCol()
        SetActiveCol()
        if appendtext(self.merc) == "cancelled":
            self.report({'INFO'}, "No Mercs Found!")
            return {'CANCELLED'}
        append(self.merc, self.type)
        justadded = str(self.merc + self.type) # make a variable targeting the added collection of the character
        matblacklist = []
        armature = bpy.data.collections[justadded].objects[0]
        armature.location = bpy.context.scene.cursor.location
        for obj in bpy.data.collections[justadded].objects: # iterate through collection of objects
            if (goto :=bpy.data.collections.get('Deployed Mercs')) == None:
                bpy.context.scene.collection.children.link(bpy.data.collections.new('Deployed Mercs')) # If the collection 'Deployed Mercs' does not exist yet, create it
                goto = bpy.data.collections['Deployed Mercs']
            goto.objects.link(obj) # link the current object to 'Deployed Mercs'

            if obj.get('COSMETIC') != None: # See if the
                if context.scene.hisanimvars.cosmeticcompatibility and not obj['COSMETIC']:
                    bpy.data.objects.remove(obj)
                    continue
                if not context.scene.hisanimvars.cosmeticcompatibility and obj['COSMETIC']:
                    bpy.data.objects.remove(obj)
                    continue
            # remove non cosmetic compatible meshes, and vice versa.
            '''if obj.type == 'ARMATURE':
                armature = obj.name
                bpy.data.objects[armature].location = bpy.context.scene.cursor.location
                #move character to cursor
                continue'''
            
            for mat in obj.material_slots:
                mat = mat.material
                for NODE in mat.node_tree.nodes:
                    #use existing nodegroups
                    if Collapse(NODE, 'TF2 BVLG') == "continue":
                        continue
                    
                    if Collapse(NODE, 'TF2 Diffuse') == "continue":
                        continue
                    
                    if Collapse(NODE, 'TF2 Eye') == "continue":
                        continue
                    #use existing imagesx
                    if NODE.type == 'TEX_IMAGE':
                        ReuseImage(NODE, PATH + f'/{self.merc}.blend')
                            
                if mat in matblacklist:
                    continue
                # relevant towards BLU. if the material has already been swapped to BLU, continue.
                if context.scene.hisanimvars.bluteam:
                    foundred = False
                    foundblu = False
                    # all this to compensate for spy's head material.
                    # multiple ifs are required, because if they were to be on the same line,
                    # they would return an error.
                    for NODE in mat.node_tree.nodes:
                        if NODE.type == 'TEX_IMAGE':
                            if 'blu' in NODE.image.name and foundblu == False:
                                foundblu = True
                                blutex = NODE
                                
                        if NODE.type == 'GROUP':
                            if 'blu' in NODE.name:
                                foundblu = True
                                blutex = NODE
                                
                        if NODE.type == 'TEX_IMAGE':
                            if 'red' in NODE.image.name and NODE.outputs[0].is_linked:
                                if NODE.outputs[0].links[0].to_node.type == 'GROUP':
                                    getconnect = NODE.outputs[0].links[0].to_node
                                    foundred = True
                                    
                        if NODE.type == 'GROUP':
                            if 'red' in NODE.name and NODE.outputs[0].links[0].to_node.type == 'GROUP':
                                getconnect = NODE.outputs[0].links[0].to_node
                                foundred = True
                                
                        if foundred and foundblu: # if red and blu textures have been found, connect the blu node to TF2 Diffuse and append the current material to matblacklist.
                            mat.node_tree.links.new(blutex.outputs[0], getconnect.inputs[0])
                            matblacklist.append(mat)
                            break
        
        bpy.data.collections.remove(bpy.data.collections[justadded]) # remove the newly added collection.
        pending = []
        #print(armature)
        for i in armature.pose.bones:
            # use existing bone shapes
            if i.custom_shape == None:
                continue
            shape = i.custom_shape.name
            
            if ".0" in shape:
                #print(shape)
                try:
                    DELETE = shape
                    if DELETE not in pending:
                        pending.append(DELETE)
                    lookfor = shape[:shape.index(".0")]
                    i.custom_shape = bpy.data.objects[lookfor]
                except:
                    bpy.data.objects[shape].name = shape[:shape.index(".")]
        #print(pending)
        if len(pending) > 0:
            for i in pending:
                try:
                    bpy.data.objects.remove(bpy.data.objects[i])
                except:
                    continue
                        
                        
        print("DELETING")
        #delete  unused images and nodegroups.
        PurgeNodeGroups()
        PurgeImages()
        PurgeNodeGroups()
        bpy.context.view_layer.active_layer_collection = bak
        return {'FINISHED'}
#bpy.utils.register_class(name)

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
        for i in classes:
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