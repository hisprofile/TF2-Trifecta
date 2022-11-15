bl_info = {
    "name" : "The TF2 Trifecta",
    "description" : "A group of three addons: Wardrobe, Merc Deployer, and Bonemerge.",
    "author" : "hisanimations",
    "version" : (1, 0),
    "blender" : (3, 0, 0),
    "location" : "View3d > Wardrobe, View3d > Merc Deployer, View3d > Bonemerge",
    "support" : "COMMUNITY",
    "category" : "Object, Mesh, Rigging",
}

import bpy, json, os
from pathlib import Path
from bpy.props import *
from bpy.types import *
from mathutils import *
from bpy.app.handlers import persistent
import importlib, sys
for filename in [f for f in os.listdir(os.path.dirname(os.path.realpath(__file__))) if f.endswith(".py") ]:
    if filename == os.path.basename(__file__): continue
    module = sys.modules.get("{}.{}".format(__name__,filename[:-3]))
    if module: importlib.reload(module)
from bpy.app.handlers import persistent
# borrowed from BST
from . import bonemerge, mercdeployer, uilist, icons
global loc
global rot
loc = bonemerge.loc
rot = bonemerge.rot
global addn
addn = "Wardrobe" # addon name
classes = []
global select
def RemoveNodeGroups(a): # iterate through every node and node group by using the "tree" method and removing said nodes
    for i in a.nodes:
        if i.type == 'GROUP':
            RemoveNodeGroups(i.node_tree)
            i.node_tree.user_clear()
            a.nodes.remove(i)
        else:
            a.nodes.remove(i)

def returnsearch(a):
    path = str(Path(__file__).parent)
    path = path + "/master.json"
    #path = r'C:\Users\Javiers\Documents\master.json'
    files = ["scout", "soldier", "pyro", "demo", "heavy", "engineer", "sniper", "medic", "spy", "allclass", "allclass2", "allclass3"]
    cln = ["named", "unnamed"]
    f = open(path)
    cosmetics = json.loads(f.read())
    f.close()
    hits = []
    for key in a:
        for i in files:
            for ii in cln:
                for v in cosmetics[i][ii]:
                    if key.casefold() in v.casefold() and not f'{v}_-_{i}' in hits:
                        hits.append(f'{v}_-_{i}')
                    
    return hits


def Collapse(a, b): # merge TF2 BVLG groups
    if a.type == 'GROUP' and b in a.node_tree.name:
        c = b + "-WDRB"
        
        if a.node_tree.name == c:
            return "continue"
        try:
            bpy.data.node_groups[c]
            RemoveNodeGroups(a.node_tree)
            a.node_tree = bpy.data.node_groups[c]
        except:
            a.node_tree.name = c
            mercdeployer.NoUserNodeGroup(a.node_tree)

prefs = bpy.context.preferences
filepaths = prefs.filepaths
asset_libraries = filepaths.asset_libraries
blend_files = []
for asset_library in asset_libraries:
    library_name = asset_library.path
    library_path = Path(asset_library.path)
    blend_files.append(str([fp for fp in library_path.glob("**/*.blend")]))# if fp.is_file()]
# taken from https://blender.stackexchange.com/questions/244971/how-do-i-get-all-assets-in-a-given-userassetlibrary-with-the-python-api
global PATHS
PATHS = {}
files = ['scout', 'soldier', 'pyro', 'demo', 'heavy', 'engineer', 'medic', 'sniper', 'spy']
for i in files: # add paths to definitoin
    for ii in blend_files:
        try:
            ii = str(ii)[str(ii).index("('") + 2:str(ii).index("')")]
            if i in ii and not "V3" in ii: # skip TF2-V3 
                PATHS[i] = ii
        except:
            continue
            
for i in blend_files: # for allclass folders
    try:
        i = str(i)[str(i).index("('") + 2:str(i).index("')")]
        if 'allclass.b' in i:
            PATHS['allclass'] = i
    except:
        print(i, " is an invalid path!")
        continue
        
for i in blend_files:
    try:
        i = str(i)[str(i).index("('") + 2:str(i).index("')")]
        if 'allclass2' in i:
            PATHS['allclass2'] = i
    except:
        print(i, " is an invalid path!")
        continue

for i in blend_files:
    try:
        i = str(i)[str(i).index("('") + 2:str(i).index("')")]
        if 'allclass3' in i:
            PATHS['allclass3'] = i
    except:
        print(i, " is an invalid path!")
        continue

class HISANIM_OT_AddLightwarps(bpy.types.Operator): # switch to lightwarps with a button
    bl_idname = 'hisanim.lightwarps'
    bl_label = 'Use Lightwarps (TF2 Style)'
    bl_description = 'Make use of the lightwarps to achieve a better TF2 look'
    bl_options = {'UNDO'}
    
    def execute(self, context):
        try:
            NT = bpy.data.node_groups['VertexLitGeneric-WDRB']
        except:
            self.report({'INFO'}, 'Cosmetic and class needed to proceed!')
            return {'CANCELLED'}
        
        NT.nodes['Group'].node_tree.use_fake_user = True
        NT.nodes['Group'].node_tree = bpy.data.node_groups['tf2combined-eevee']
        try:
            NT.nodes['Lightwarp']
        except:
            NT.nodes.new(type="ShaderNodeTexImage").name = "Lightwarp"
        try:
            NT.nodes['Lightwarp'].image = bpy.data.images['pyro_lightwarp.png']
        except:
            self.report({'INFO'}, 'Add a class first!')
            return {'CANCELLED'}
        
        NT.nodes['Lightwarp'].location[0] = 960
        NT.nodes['Lightwarp'].location[1] = -440
        NT.links.new(NT.nodes['Group'].outputs['lightwarp vector'], NT.nodes['Lightwarp'].inputs['Vector'])
        NT.links.new(NT.nodes['Lightwarp'].outputs['Color'], NT.nodes['Group'].inputs['Lightwarp'])
        return {'FINISHED'}
classes.append(HISANIM_OT_AddLightwarps)

class HISANIM_OT_RemoveLightwarps(bpy.types.Operator): # be cycles compatible
    bl_idname = 'hisanim.removelightwarps'
    bl_label = 'Make Cycles compatible (Default)'
    bl_description = 'Make the cosmetics Cycles compatible'
    bl_options = {'UNDO'}
    
    def execute(self, execute):
        try:
            NT = bpy.data.node_groups['VertexLitGeneric-WDRB']
        except:
            self.report({'INFO'}, 'Cosmetic needed to proceed!')
            return {'CANCELLED'}
        NT.nodes['Group'].node_tree = bpy.data.node_groups['tf2combined-cycles']
        return {'FINISHED'}

classes.append(HISANIM_OT_RemoveLightwarps)
        

class hisanimsearchs(bpy.types.PropertyGroup): # keyword to look for

    query: bpy.props.StringProperty(default="")

class HISANIM_OT_MATFIX(bpy.types.Operator):
    bl_idname = 'hisanim.matfix'
    bl_label = 'Mat'
    bl_description = 'Attempt to fix a material with sections that are black'
    
    def execute(self, execute):
        if bpy.context.object.get('skin_groups') == None:
            return {'CANCELLED'}

class HISANIM_OT_LOAD(bpy.types.Operator):
    LOAD: bpy.props.StringProperty(default='')
    bl_idname = 'hisanim.loadcosmetic'
    bl_label = 'Cosmetic'
    bl_description = f'Load this cosmetic into your scene'
    bl_options = {'UNDO'}

    def execute(self, context):
        D = bpy.data
        CLASS = self.LOAD.split("_-_")[1]
        COSMETIC = self.LOAD.split("_-_")[0]
        p = PATHS[CLASS] # shortcut to paths. self.CLASS refers to the class folder.
        cos = COSMETIC
        
        # check if the cosmetic already exists. if it does, use the existing assets.
        # may be deprecated at some point in favor of Merc Deployer's method, which is
        # to use the same assets but not the same material.

        with bpy.data.libraries.load(p, assets_only=True) as (file_contents, data_to):
            data_to.objects = [cos]
        list = [i.name for i in D.objects if not "_ARM" in i.name and cos in i.name]
        justadded = sorted(list)[-1]
        print(justadded)
        skins = D.objects[justadded]['skin_groups']
        count = 0
        #updates the skin_groups dictionary on the object with its materials
        for num in skins:
            Range = count + len(skins[num])
            newmatlist = []
            for i in range(count, Range):
                newmatlist.append(D.objects[justadded].material_slots[i].material.name)
            skins[num] = newmatlist
            count = Range
        D.objects[justadded]['skin_groups'] = skins
        del newmatlist, Range, count, skins, list

        try:
            bpy.data.collections[addn]
            bpy.data.collections[addn].objects.link(bpy.data.objects[justadded])
            
            #these try and except blocks are used in case objects are linked to both the
            #scene collection and Wardrobe's collection. in my testing they seem to never
            #be linked to the scene collection. can't take any chances though
            
            try:
                bpy.context.scene.collection.objects.unlink(bpy.data.objects[justadded])
            except:
                pass
            bpy.data.objects[justadded].use_fake_user = False
            bpy.data.collections[addn].objects.link(bpy.data.objects[justadded].parent)
            try:
                bpy.context.scene.collection.objects.unlink(bpy.data.objects[justadded].parent)
            except:
                pass
            bpy.data.objects[justadded].parent.use_fake_user = False
        except:
            bpy.context.scene.collection.children.link(bpy.data.collections.new(addn))
            bpy.data.collections[addn].objects.link(bpy.data.objects[justadded])
            try:
                bpy.context.scene.collection.objects.unlink(bpy.data.objects[justadded])
            except:
                pass
            bpy.data.objects[justadded].use_fake_user = False
            bpy.data.collections[addn].objects.link(bpy.data.objects[justadded].parent)
            try:
                bpy.context.scene.collection.objects.unlink(bpy.data.objects[justadded].parent)
            except:
                pass
            bpy.data.objects[justadded].parent.use_fake_user = False
        bpy.data.objects[justadded].parent.location = bpy.context.scene.cursor.location
        mercdeployer.PurgeNodeGroups()
        

        for mat in D.objects[justadded].material_slots:
            for NODE in mat.material.node_tree.nodes:
                if Collapse(NODE, 'VertexLitGeneric') == 'continue': # use VertexLitGeneric-WDRB, recursively remove nodes and node groups from VertexLitGeneric
                    continue
                if NODE.type == 'TEX_IMAGE':
                    if mercdeployer.ReuseImage(NODE) == 'continue': # use existing images
                        continue
                if NODE.name == 'VertexLitGeneric':
                    NODE.inputs['rim * ambient'].default_value = 1 # for better colors

        if bpy.context.scene.wrdbbluteam: # this one speaks for itself
            print("BLU")
            try:
                SKIN = bpy.data.objects[justadded]['skin_groups']
                OBJMAT = bpy.data.objects[justadded].material_slots
                for i in SKIN: # return where blu materials are found as BLU
                    for ii in SKIN[i]:
                        if "blu" in ii:
                            BLU = i
                            print(BLU)
                counter = 0
                for i in SKIN[BLU]: # set the materials as BLU
                    OBJMAT[counter].material = bpy.data.materials[i]
                    counter += 1
                del counter, SKIN, OBJMAT
            except:
                pass
            
        select = bpy.context.object
        # if a Bonemerge compatible rig or mesh parented to one is selected, automatically bind the cosmetic
        # to the rig.
        try:
            if select.parent:
                select = select.parent
        except:
            pass
        try:
            select['BMBCOMPATIBLE']
            var = 1
        except:
            var = 0
        
        if var == 1:
    
            for ii in bpy.data.objects[justadded].parent.pose.bones:
                print(ii.name)
                try:
                    bpy.data.objects[select.name].pose.bones[ii.name]
                    print('found matching bone!')
                except:
                    continue
                
                try:
                    ii.constraints[loc]
                    pass
                except:
                    ii.constraints.new('COPY_LOCATION').name = loc
                    ii.constraints.new('COPY_ROTATION').name = rot
                
                
                ii.constraints[loc].target = select
                ii.constraints[loc].subtarget = ii.name
                ii.constraints[rot].target = select
                ii.constraints[rot].subtarget = ii.name
        mercdeployer.PurgeNodeGroups()
        mercdeployer.PurgeImages()
        return {'FINISHED'}
classes.append(HISANIM_OT_LOAD)
class HISANIM_OT_Search(bpy.types.Operator):
    bl_idname = 'hisanim.search'
    bl_label = 'Search for cosmetics'
    bl_description = "Go ahead, search"
    
    def execute(self, context):
        lookfor = bpy.context.scene.hisanimsearchs.query
        lookfor = lookfor.split("|")
        lookfor.sort()
        hits = returnsearch(lookfor)
        class WDRB_PT_PART2(bpy.types.Panel):
            bl_label = "Search Results"
            bl_space_type = 'VIEW_3D'
            bl_region_type = 'UI'
            bl_category = addn
            bl_icon = "MOD_CLOTH"
            global operators
            operators = hits
            def draw(self, context):
                layout = self.layout
                row = layout.row()
                if len(hits) == 1:
                    row.label(text=f'{len(hits)} Result')
                else:
                    row.label(text=f'{len(hits)} Results')
                
                for ops in hits:
                    # draw the search results as buttons
                    row=layout.row()
                    row.label(text=ops.split("_-_")[1])
                    BACKS = '\\'
                    OPER = row.operator('hisanim.loadcosmetic', text=ops.split('_-_')[0])
                    OPER.LOAD = ops
            if len(hits) == 0:
                def draw(self, context):
                    layout = self.layout
                    row = layout.row()
                    row.label(text='Nothing found!')
        bpy.utils.register_class(WDRB_PT_PART2)
        
        return {'FINISHED'}
classes.append(HISANIM_OT_Search)

class HISANIM_OT_ClearSearch(bpy.types.Operator): # clear the search
    bl_idname = 'hisanim.clearsearch'
    bl_label = 'Clear Search'
    bl_description = 'Clear your search history'
    
    def execute(self, context):
        
        try:
            bpy.utils.unregister_class(bpy.types.WDRB_PT_PART2)
            return {'FINISHED'}
        except:
            pass
            return {'CANCELLED'}
classes.append(HISANIM_OT_ClearSearch)
classes.append(hisanimsearchs)

class HISANIM_OT_MATFIX(bpy.types.Operator):
    bl_idname = 'hisanim.materialfix'
    bl_label = 'Fix Material'
    bl_description = 'Fix Material'
    bl_options = {'UNDO'}
    
    MAT: bpy.props.StringProperty(default='')
    
    def execute(self, context):
        try:
            bpy.data.materials[self.MAT].node_tree.nodes['WRDB-MIX']
            return {'CANCELLED'}
        except:
            MAT = bpy.data.materials[self.MAT]
            NODEMIX = MAT.node_tree.nodes.new('ShaderNodeMixRGB')
            NODEMIX.name = 'WRDB-MIX'
            NODEMIX.location = Vector((-400, 210))
            NODEGAMMA = MAT.node_tree.nodes.new('ShaderNodeGamma')
            NODEGAMMA.name = 'WRDB-GAMMA'
            NODEGAMMA.location = Vector((-780, 110))
            NODEGAMMA.inputs[0].default_value = list(MAT.node_tree.nodes['VertexLitGeneric'].inputs['$color2 [RGB field]'].default_value)
            MAT.node_tree.nodes['VertexLitGeneric'].inputs['$color2 [RGB field]'].default_value = [1, 1, 1, 1]
            NODEGAMMA.inputs[1].default_value = 2.2
            MATLINK = MAT.node_tree.links
            MATLINK.new(MAT.node_tree.nodes['$basetexture'].outputs['Alpha'], NODEMIX.inputs[0])
            MATLINK.new(MAT.node_tree.nodes['$basetexture'].outputs['Color'], NODEMIX.inputs[1])
            MATLINK.new(NODEGAMMA.outputs[0], NODEMIX.inputs[2])
            MATLINK.new(NODEMIX.outputs[0], MAT.node_tree.nodes['VertexLitGeneric'].inputs['$basetexture [texture]'])
            return {'FINISHED'}
classes.append(HISANIM_OT_MATFIX)
class HISANIM_OT_PAINTS(bpy.types.Operator):
    bl_idname = 'hisanim.paint'
    bl_label = 'Paint'
    bl_description = 'Use this paint on cosmetic'
    bl_options = {'UNDO'}

    PAINT: bpy.props.StringProperty(default='')

    def execute(self, context):
        paintvalue = self.PAINT.split(' ')
        paintlist = [int(i)/255 for i in paintvalue]
        paintlist.append(1.0)
        MAT = context.object.active_material
        if MAT.node_tree.nodes.get('DEFAULTPAINT') == None: # check if the default paint rgb node exists. if not, create the backup.
            RGBBAK = MAT.node_tree.nodes.new(type='ShaderNodeRGB')
            RGBBAK.name = 'DEFAULTPAINT'
            RGBBAK.location = Vector((-650, -550))
            RGBBAK.label = 'DEFAULTPAINT'
            if not MAT.node_tree.nodes.get('WRDB-GAMMA') == None: # set the backup color.
                RGBBAK.outputs[0].default_value = list(MAT.node_tree.nodes['WRDB-GAMMA'].inputs[0].default_value)
            else:
                RGBBAK.outputs[0].default_value = list(MAT.node_tree.nodes['VertexLitGeneric'].inputs['$color2 [RGB field]'].default_value)
        try: # set the selected paint.
            MAT.node_tree.nodes['WRDB-GAMMA'].inputs[0].default_value = paintlist
        except:
            MAT.node_tree.nodes['VertexLitGeneric'].inputs['$color2 [RGB field]'].default_value = paintlist
        return {'FINISHED'}
class HISANIM_OT_PAINTCLEAR(bpy.types.Operator):
    bl_idname = 'hisanim.paintclear'
    bl_label = 'Clear Paint'
    bl_description = 'Clear Paint'
    bl_options = {'UNDO'}

    def execute(self, context):
        MAT = context.object.active_material.node_tree
        if MAT.nodes.get('DEFAULTPAINT') == None: # check if the default paint color exists. if not, assume no paint is applied.
            return {'CANCELLED'}
        if not MAT.nodes.get('WRDB-GAMMA') == None: # set the default color.
            MAT.nodes['WRDB-GAMMA'].inputs[0].default_value = list(MAT.nodes['DEFAULTPAINT'].outputs[0].default_value)
        else:
            MAT.nodes['VertexLitGeneric'].inputs['$color2 [RGB field]'].default_value = list(MAT.nodes['DEFAULTPAINT'].outputs[0].default_value)
        MAT.nodes.remove(MAT.nodes['DEFAULTPAINT'])
        return {'FINISHED'}

classes.append(HISANIM_OT_PAINTS)
class WDRB_PT_PART1(bpy.types.Panel):
    """A Custom Panel in the Viewport Toolbar""" # for the searching segment.
    bl_label = addn
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = addn
    bl_icon = "MOD_CLOTH"
    
    def draw(self, context):
        
        props = bpy.context.scene.hisanimsearchs
        layout = self.layout
        row = layout.row()
        row.prop(props, "query", text="Search", icon="VIEWZOOM")
        layout.label(text="Warning! Don't leave the text field empty!")
        row=layout.row()
        row.operator('hisanim.search', icon='VIEWZOOM')
        row=layout.row()
        row.operator('hisanim.clearsearch', icon='X')
        layout.label(text='Material settings')
        row=layout.row()
        row.operator('hisanim.lightwarps')
        row=layout.row()
        row.operator('hisanim.removelightwarps')
        row = layout.row()
        row.prop(context.scene, 'wrdbbluteam')
        row = layout.row()

class WDRB_PT_PART3(bpy.types.Panel): # for the material fixer and selector segment.
    bl_label = 'Material Fixer/Selector'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = addn
    bl_icon = "MOD_CLOTH"
    @classmethod
    def poll(cls, context): # only show if an object is selected and has a dictionary property named 'skin_groups'.
        try:
            return True if not context.object.get('skin_groups') == None and len(context.selected_objects) > 0 else False
        except:
            return False
    def draw(self, context):
        if not context.object.get('skin_groups') == None:
            layout = self.layout
            ob = context.object
            layout.label(text='Attempt to fix material')
            row = layout.row()
            row.template_list("MATERIAL_UL_matslots", "", ob, "material_slots", ob, "active_material_index")
            row = layout.row()
            oper = row.operator('hisanim.materialfix')
            oper.MAT = context.object.active_material.name

#panelspace for paints
class WDRB_PT_PART4(bpy.types.Panel):
    bl_label = 'Paints'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = addn
    #check if the panel can be displayed
    @classmethod
    def poll(cls, context): # only show if an object is selected and has a dictionary property named 'skin_groups'.
        try:
            return True if not context.object.get('skin_groups') == None and len(context.selected_objects) > 0 else False
        except:
            return False
    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.template_list('HISANIM_UL_PAINTLIST', "Paints", context.scene, "paintlist", context.scene, "paintindex") # use the cool paint index and icons
        row=layout.row()
        oper = row.operator('hisanim.paint', text = 'Add Paint')
        oper.PAINT = uilist.paints[context.scene.paintlist[context.scene.paintindex].name]
        row = layout.row()
        row.operator('hisanim.paintclear')
@persistent
def load_handler(loadpaints): # fill the paintlist collectiongroup with "paints"'s keys.
    bpy.context.scene.paintlist.clear()
    for i in uilist.paints: 
        item = bpy.context.scene.paintlist.add()
        item.name = i

bpy.app.handlers.load_post.append(load_handler)

paintnames = uilist.paintnames
classes.append(WDRB_PT_PART1)
classes.append(WDRB_PT_PART3)
classes.append(WDRB_PT_PART4)
classes.append(uilist.PaintList)
classes.append(uilist.HISANIM_UL_PAINTLIST)
classes.append(uilist.MaterialList)
classes.append(uilist.HISANIM_UL_MATERIALLIST)
classes.append(mercdeployer.MD_PT_MERCDEPLOY)
classes.append(bonemerge.HISANIM_OT_ATTACH)
classes.append(bonemerge.HISANIM_OT_DETACH)
classes.append(bonemerge.BM_PT_BONEMERGE)
classes.append(bonemerge.HISANIM_OT_BINDFACE)
classes.append(bonemerge.HISANIM_OT_ATTEMPTFIX)
classes.append(HISANIM_OT_PAINTCLEAR)
def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.hisanimsearchs = bpy.props.PointerProperty(type=hisanimsearchs)
    bpy.types.Scene.bluteam = BoolProperty(
        name="Blu Team",
        description="Swap classes",
        default = False)
    bpy.types.Scene.cosmeticcompatibility = BoolProperty(
        name="Cosmetic Compatible",
        description="Use cosmetic compatible bodygroups that don't intersect with cosmetics. Disabling will use SFM bodygroups",
        default = True)
    bpy.types.Scene.wrdbbluteam = BoolProperty(
        name="Blu Team",
        description="Swap classes",
        default = False)
    bpy.types.Scene.paintlist = CollectionProperty(type = uilist.PaintList)
    bpy.types.Scene.hisamatlist = CollectionProperty(type = uilist.MaterialList)
    bpy.types.Scene.paintindex = IntProperty(name='Paint Index', default = 0)
    bpy.types.Scene.hisamatindex = IntProperty(name='Selected Material Index', default = 0)
    icons.register()
def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    icons.unregister()
    del bpy.types.Scene.bluteam
    del bpy.types.Scene.cosmeticcompatibility
    del bpy.types.Scene.paintlist
    del bpy.types.Scene.paintindex
    del bpy.types.Scene.hisamatlist
    del bpy.types.Scene.hisamatindex
    
if __name__ == "__main__":
    register()
