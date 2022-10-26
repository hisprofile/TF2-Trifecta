import bpy
from pathlib import Path

from bpy.props import BoolProperty

prefs = bpy.context.preferences
filepaths = prefs.filepaths
asset_libraries = filepaths.asset_libraries
blend_files = []

global path
#global classes
global cln
cln = ["IK", "FK"]
path = [i.path for i in asset_libraries]

for i in path:
    if "TF2-V3" in i:
        path = i.replace("\\", "/")
        
classes = ['scout', 'soldier', 'pyro', 'demo', 'heavy', 'engineer', 'medic', 'sniper', 'spy']
def append(a, b): # get a class from TF2-V3
    blendfile = f'{path}/{a}.blend'
    section = "\\Collection\\"
    object = a + b
    
    directory = blendfile + section
    
    bpy.ops.wm.append(filename=object, directory=directory)

def appendtext(a): # add the .py script to add further control to faces
    blendfile = f'{path}/{a}.blend'
    section = "\\Text\\"
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
    ihate = bpy.context.view_layer
    if a == None:
        ihate.active_layer_collection = ihate.layer_collection
        return {'FINISHED'}
def GetActiveCol(): # get the active collection
    return bpy.context.view_layer.active_layer_collection

def Collapse(a, b): # merge TF2 BVLG groups
    if a.type == 'GROUP' and b in a.node_tree.name:
        c = b + "-MD"
        
        if a.node_tree.name == c:
            return "continue"
        try:
            bpy.data.node_groups[c]
            a.node_tree = bpy.data.node_groups[c]
            RemoveNodeGroups(bpy.data.node_groups[DELETE])
        except:
            a.node_tree.name = c
            NoUserNodeGroup(a.node_tree)
    
    return {'FINISHED'}
#append("scout", "FK")
class MERCDEPLOY(bpy.types.Panel):
    '''Rolling in the nonsense, deploy the fantasy!'''
    bl_label = "Merc Deployer"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Merc Deployer"
    bl_icon = "FORCE_DRAG"
    
    for i in classes:
        global opname
        opname = i
        for ii in cln:
            global opcln
            opcln = ii
            name = i+ii
            class name(bpy.types.Operator):
                merc = opname
                type = opcln
                bl_idname = f'''hisanim.{merc}{type.lower()}'''
                bl_label = type
                bl_options = {'UNDO'}
                
                def execute(self, context):
                    bak = GetActiveCol()
                    SetActiveCol()
                    if appendtext(self.merc) == "cancelled":
                        self.report({'INFO'}, "No Mercs Found!")
                        return {'CANCELLED'}
                    append(self.merc, self.type)
                    justadded = str(self.merc + self.type) # make a variable targeting the added collection of the character
                    matblacklist = []
                    for obj in bpy.data.collections[justadded].objects: # iterate through collection of objects
                        
                        try:
                            goto = bpy.data.collections['Deployed Mercs']
                            goto.objects.link(obj)
                            
                        except:
                            bpy.context.scene.collection.children.link(bpy.data.collections.new('Deployed Mercs'))
                            goto = bpy.data.collections['Deployed Mercs']
                            goto.objects.link(obj)
                        # create new collection to contain all the mercs
                        try:
                            obj['COSMETIC']
                            if context.scene.cosmeticcompatibility and obj['COSMETIC'] == False:
                                bpy.data.objects.remove(obj)
                                continue
                            
                            if not context.scene.cosmeticcompatibility and obj['COSMETIC']:
                                bpy.data.objects.remove(obj)
                                continue
                        except:
                            pass
                        # remove non cosmetic compatible meshes, and vice versa.
                        if obj.type == 'ARMATURE':
                            armature = obj.name
                            bpy.data.objects[armature].location = bpy.context.scene.cursor.location
                            #move character to cursor
                            continue
                        
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
                                
                                #use existing images
                                
                                if NODE.type == 'TEX_IMAGE':
                                    if ".0" in NODE.image.name:
                                        try:
                                            lookfor = NODE.image.name[:NODE.image.name.rindex(".")]
                                            print(f'looking for {lookfor}..')
                                            NODE.image = bpy.data.images[lookfor]
                                            print("found!")
                                            NODE.image.use_fake_user = False
                                        except:
                                            print(f"no original match found for {NODE.image.name}!")
                                            print("RENAMING")
                                            old = NODE.image.name
                                            new = NODE.image.name[:NODE.image.name.rindex(".")]
                                            print(f'{old} --> {new}')
                                            NODE.image.name = new
                                            NODE.image.use_fake_user = False
                                            continue
                                        
                            if mat in matblacklist:
                                continue
                            # relevant towards BLU. if the material has already been swapped to BLU, continue.
                            if context.scene.bluteam:
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
                    for i in bpy.data.objects[armature].pose.bones:
                        # use existing bone shapes
                        if i.custom_shape == None:
                            continue
                        shape = i.custom_shape.name
                        
                        if ".0" in shape:
                            try:
                                DELETE = shape
                                if DELETE not in pending:
                                    pending.append(DELETE)
                                lookfor = shape[:shape.index(".")]
                                i.custom_shape = bpy.data.objects[lookfor]
                            except:
                                bpy.data.objects[shape].name = shape[:shape.index(".")]
                    print(pending)
                    if len(pending) > 0:
                        for i in pending:
                            bpy.data.objects.remove(bpy.data.objects[i])
                                    
                                    
                    print("DELETING")
                    #delete  unused images and nodegroups.
                    PurgeNodeGroups()
                    PurgeImages()
                    PurgeNodeGroups()
                    bpy.context.view_layer.active_layer_collection = bak
                    return {'FINISHED'}
            bpy.utils.register_class(name)
    def draw(self, context):
        layout = self.layout
        row = layout.row(align=True)
        for i in classes:
            row.label(text=i)
            col = layout.column()
            for ii in cln:
                row.operator(f'hisanim.{i}{ii.lower()}')
            row = layout.row(align=True)
        row.prop(context.scene, "bluteam")
        row = layout.row()
        row.prop(context.scene, "cosmeticcompatibility")
