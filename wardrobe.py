import bpy, json, os
from pathlib import Path
from bpy.props import *
#from bpy.types import *
from bpy.types import Context
from mathutils import *
from . import bonemerge, mercdeployer, faceposer, loadout

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
    if not bpy.context.scene.hisanimvars.hisanimweapons:
        files = ["scout", "soldier", "pyro", "demo", "heavy", "engineer", "sniper", "medic", "spy", "allclass", "allclass2", "allclass3"]
    else:
        files = ['weapons']
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

def ReuseImage(a, path):
    if bpy.context.scene.hisanimvars.savespace:
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
    print(f'No match for {a.image.name}! How odd...')
    return

def Collapse(a, b): # merge TF2 BVLG groups
    if a.type == 'GROUP' and b in a.node_tree.name:
        c = b + "-WDRB"
        if a.node_tree.name == c:
            return "continue"
        if bpy.data.node_groups.get(c) != None:
            RemoveNodeGroups(a.node_tree)
            a.node_tree = bpy.data.node_groups[c]
        else:
            a.node_tree.name = c
            mercdeployer.NoUserNodeGroup(a.node_tree)

def link(a, b, c): # get a class from TF2-V3
    blendfile = a
    section = f"/{c}/"
    object = b
    
    directory = blendfile + section
    
    bpy.ops.wm.link(filename=object, directory=directory)

class HISANIM_OT_AddLightwarps(bpy.types.Operator): # switch to lightwarps with a button
    bl_idname = 'hisanim.lightwarps'
    bl_label = 'Use Lightwarps (TF2 Style)'
    bl_description = 'Make use of the lightwarps to achieve a better TF2 look'
    bl_options = {'UNDO'}
    
    def execute(self, context):
        props = bpy.context.scene.hisanimvars
        if (NT := bpy.data.node_groups.get('VertexLitGeneric-WDRB')) == None: 
            self.report({'INFO'}, 'Cosmetic and class needed to proceed!')
            return {'CANCELLED'}
        
        NT.nodes['Group'].node_tree.use_fake_user = True
        NT.nodes['Group'].node_tree = bpy.data.node_groups['tf2combined-eevee']
        if NT.nodes.get('Lightwarp') == None:
            NT.nodes.new(type="ShaderNodeTexImage").name = "Lightwarp"
        if (IMG := bpy.data.images.get('pyro_lightwarp.png')) == None:
            for i in range(100):
                num = f'{"0"*(3-len(str(i)))}{str(i)}'
                if (IMG := bpy.data.images.get(f'pyro_lightwarp.png.{num}')) != None:
                    NT.nodes['Lightwarp'].image = IMG
                    break
            else:
                self.report({'INFO'}, 'Add a class first!')
                return {'CANCELLED'}
        else:
            NT.nodes['Lightwarp'].image = IMG
        
        NT.nodes['Lightwarp'].location[0] = 960
        NT.nodes['Lightwarp'].location[1] = -440
        NT.links.new(NT.nodes['Group'].outputs['lightwarp vector'], NT.nodes['Lightwarp'].inputs['Vector'])
        NT.links.new(NT.nodes['Lightwarp'].outputs['Color'], NT.nodes['Group'].inputs['Lightwarp'])
        props.toggle_mat = True
        return {'FINISHED'}

class HISANIM_OT_RemoveLightwarps(bpy.types.Operator): # be cycles compatible
    bl_idname = 'hisanim.removelightwarps'
    bl_label = 'Make Cycles compatible (Default)'
    bl_description = 'Make the cosmetics Cycles compatible'
    bl_options = {'UNDO'}
    
    def execute(self, execute):
        props = bpy.context.scene.hisanimvars
        if (NT := bpy.data.node_groups.get('VertexLitGeneric-WDRB')) == None:
            self.report({'INFO'}, 'Cosmetic needed to proceed!')
            return {'CANCELLED'}
        NT.nodes['Group'].node_tree = bpy.data.node_groups['tf2combined-cycles']
        props.toggle_mat = False
        return {'FINISHED'}
        
class searchHits(bpy.types.PropertyGroup):
    scn = bpy.types.Scene
    def gett(self):
        scn = bpy.types.Scene
        try:
            return self.name in scn.loadout_temp
        except:
            return False
        
    def sett(self, value):
        scn = bpy.types.Scene
        if value == True:
            if self.name not in scn.loadout_temp: scn.loadout_temp.append(self.name)
        if value == False:
            if self.name in scn.loadout_temp: scn.loadout_temp.remove(self.name)

    name: StringProperty()
    use: BoolProperty(name='Use', default=False, get=gett, set=sett)

class hisanimvars(bpy.types.PropertyGroup): # list of properties the addon needs. Less to write for registering and unregistering
    def sW(self, val):
        bpy.context.scene.hisanimvars.tools = 'WARDROBE'
    def gW(self):
        return bpy.context.scene.hisanimvars.tools == 'WARDROBE'
    def sM(self, val):
        bpy.context.scene.hisanimvars.tools = 'MERC DEPLOYER'
    def gM(self):
        return bpy.context.scene.hisanimvars.tools == 'MERC DEPLOYER'
    def sB(self, val):
        bpy.context.scene.hisanimvars.tools = 'BONEMERGE'
    def gB(self):
        return bpy.context.scene.hisanimvars.tools == 'BONEMERGE'
    def sF(self, val):
        bpy.context.scene.hisanimvars.tools = 'FACE POSER'
    def gF(self):
        return bpy.context.scene.hisanimvars.tools == 'FACE POSER'
    def sFx(self, val):
        bpy.context.scene.hisanimvars.mode = 'FLEXES'
    def gFx(self):
        return bpy.context.scene.hisanimvars.mode == 'FLEXES'
    def sSk(self, val):
        bpy.context.scene.hisanimvars.mode = 'SKEYS'
    def gSk(self):
        return bpy.context.scene.hisanimvars.mode == 'SKEYS'
    
    bluteam: BoolProperty(
        name="Blu Team",
        description="Swap classes",
        default = False, options=set())
    query: StringProperty(default="")
    loadout_name: StringProperty(default='Loadout Name')
    cosmeticcompatibility: BoolProperty(
        name="In-Game Models",
        description="Use cosmetic compatible bodygroups that don't intersect with cosmetics. Disabling will use SFM bodygroups",
        default = True, options=set())
    wrdbbluteam: BoolProperty(
        name="Blu Team",
        description="Swap classes",
        default = False, options=set())
    hisanimweapons: BoolProperty(name='Search For Weapons', options=set())
    hisanimrimpower: FloatProperty(name='Rimlight Strength',
                                description='Multiply the overall rim boost by this number',
                                default=0.400, min=0.0, max=1.0, options=set())
    hisanimscale: BoolProperty(default=False, name='Scale With', description='Scales cosmetics with targets bones. Disabled by default', options=set())
    hisanimtarget: PointerProperty(type=bpy.types.Object, poll=bonemerge.IsArmature)
    savespace: BoolProperty(default=True, name='Save Space', description='When enabled, The TF2-Trifecta will link textures from source files', options=set())
    autobind: BoolProperty(default=False, name='Auto BoneMerge', description='When enabled, weapons will automatically bind to mercs', options=set())
    results: CollectionProperty(type=searchHits)
    resultindex: IntProperty(options=set())
    searched: BoolProperty(options=set())
    tools: EnumProperty(
        items=(
        ('WARDROBE', 'Wardrobe', "Show Wardrobe's tools", 'MOD_CLOTH', 0),
        ('MERC DEPLOYER', 'Merc Deployer', "Show Merc Deployer's tools", 'FORCE_DRAG', 1),
        ('BONEMERGE', 'Bonemerge', "Show Bonemerge's tools", 'GROUP_BONE', 2),
        ('FACE POSER', 'Face Poser', 'Show the Face Poser tools', 'RESTRICT_SELECT_OFF', 3)
        ),
        name='Tool', options=set()
    )
    wr: BoolProperty(default=True, name='', options=set(), set=sW, get=gW)
    md: BoolProperty(default=True, name='', options=set(), set=sM, get=gM)
    bm: BoolProperty(default=True, name='', options=set(), set=sB, get=gB)
    fp: BoolProperty(default=True, name='', options=set(), set=sF, get=gF)
    wardrobe: BoolProperty(default=True, name='', options=set(), set=sW, get=gW)
    wardrobe: BoolProperty(default=True, name='', options=set(), set=sW, get=gW)
    ddsearch: BoolProperty(default=True, name='', options=set())
    ddpaints: BoolProperty(default=True, name='', options=set())
    ddmatsettings: BoolProperty(default=True, name='', options=set())
    ddloadouts: BoolProperty(default=False, name='', options=set())
    ddfacepanel: BoolProperty(default=True, name='', options=set())
    ddrandomize: BoolProperty(default=True, name='', options=set())
    ddlocks: BoolProperty(default=True, name = '', options=set())
    ddposelib: BoolProperty(default=True, name='', options=set())
    randomadditive: BoolProperty(name = 'Additive', description='Add onto the current face values', options=set())
    randomstrength: FloatProperty(name='Random Strength', min=0.0, max=1.0, description='Any random value calculated will be multiplied with this number', default=1.0, options=set())
    keyframe: BoolProperty(default=False, name='Keyframe Sliders', description='Keyframe the randomized changes', options=set())
    lockfilter: StringProperty()
    activeslider: StringProperty()
    activeface: PointerProperty(type=bpy.types.Object)
    lastactiveface: PointerProperty(type=bpy.types.Object)
    loadout_data: CollectionProperty(type=loadout.funny_funnygroup)
    loadout_index:IntProperty(default=0)
    sliders: CollectionProperty(type=faceposer.faceslider)
    sliderindex: IntProperty(options=set())
    dragging: BoolProperty(default=False, options=set())
    updating: BoolProperty(default = False, options=set())
    callonce: BoolProperty(default = False, options=set())
    LR: FloatProperty(default=0.5, options=set(), min=0.0, max=1.0, name='L <-> R', description='Which way flexing will lean more towards', step=50)
    up: BoolProperty(default=False, options=set(), name='Upper', description='Show the Upper section of the face')
    mid: BoolProperty(default=False, options=set(), name='Mid', description='Show the Mid section of the face')
    low: BoolProperty(default=False, options=set(), name='Lower', description='Show the Lower section of the face')
    use_flexes: BoolProperty(default = True, options=set(), name='Flex Controllers', set=sFx, get=gFx)
    use_skeys: BoolProperty(default = False, options=set(), name='Shapekeys', set=sSk, get=gSk)
    mode: EnumProperty(
        items=(
            ('FLEXES', 'Flex Controllers', '', '', 0),
            ('SKEYS', 'Shape Keys', '', '', 1),
        ),
        name = 'Mode',
        default = 'FLEXES'
    )
    stage: EnumProperty(
        items=(
        ('NONE', 'None', '', '', 0),
        ('SELECT', 'Selection', '', '', 1),
        ('CONFIRM', 'Confirmation', '', '', 2),
        ('DISPLAY', 'Display', '', '', 3)
        ),
        name = 'Stages',
        default='NONE'
    )
    merc: StringProperty(default='')
    toggle_mat: BoolProperty(default=False)
    needs_override: BoolProperty()

class WDRB_OT_Select(bpy.types.Operator):
    bl_idname = 'wdrb.select'
    bl_label = 'Select'
    bl_description = 'Select'

    @classmethod
    def poll(cls, context):
        return bpy.context.scene.hisanimvars.stage == 'NONE'

    def execute(self, context):
        props = bpy.context.scene.hisanimvars
        props.loadout_name = 'Loadout Name'
        bpy.types.Scene.loadout_temp = []
        props.stage = 'SELECT'
        return {'FINISHED'}
    
class WDRB_OT_Cancel(bpy.types.Operator):
    bl_idname = 'wdrb.cancel'
    bl_label = 'Cancel'
    bl_description = 'Cancel'

    def execute(self, context):
        props = bpy.context.scene.hisanimvars
        props.stage = 'NONE'
        del bpy.types.Scene.loadout_temp
        loadout.update()
        return {'FINISHED'}
    
class WDRB_OT_Confirm(bpy.types.Operator):
    bl_idname = 'wdrb.confirm'
    bl_label = 'Confirm'
    bl_description = 'Confirm'

    @classmethod
    def poll(cls, context):
        return (bpy.context.scene.hisanimvars.loadout_name != '') * (len(bpy.types.Scene.loadout_temp) > 0) 
    
    def invoke(self, context, event):
        C = bpy.context
        scn = C.scene
        props = scn.hisanimvars

        jsonData = loadout.getJson()

        if jsonData.get(props.loadout_name) != None:
            return context.window_manager.invoke_props_dialog(self)
        else:
            return self.execute(context)

    def execute(self, context):
        props = bpy.context.scene.hisanimvars
        if not loadout.jsonExists():
            loadout.initJson()
        dictData = loadout.getJson()
        dictData[props.loadout_name] = bpy.types.Scene.loadout_temp
        del bpy.types.Scene.loadout_temp
        props.stage = 'NONE'
        loadout.writeJson(dictData)
        loadout.update()
        return {'FINISHED'}
    
    def draw(self, context):
        self.layout.row().label(text='Entry exists. Overwrite?')


class HISANIM_OT_LOAD(bpy.types.Operator):
    LOAD: StringProperty(default='')
    bl_idname = 'hisanim.loadcosmetic'
    bl_label = 'Cosmetic'
    bl_description = f'Load this cosmetic into your scene'
    bl_options = {'UNDO'}

    def execute(self, context):
        D = bpy.data
        CLASS = self.LOAD.split("_-_")[1]
        COSMETIC = self.LOAD.split("_-_")[0]

        nothing = True if len(bpy.context.selected_objects) == 0 else False

        prefs = context.preferences.addons[__package__].preferences
        paths = prefs.hisanim_paths
        if (p := paths.get(CLASS)) == None: # no entry
            self.report({'ERROR'}, f'Directory for "{CLASS}" not found! Make sure an entry for it exists in the addon preferences!')
            return {'CANCELLED'}
        
        if p.this_is != 'BLEND': # bad file extension type
            self.report({'ERROR'}, f'Path for "{CLASS}" entry does not end in a .blend file!')
            return {'CANCELLED'}
        p = p.path
        if not os.path.exists(p): # doesn't exist
            self.report({'ERROR'}, f'Entry for "{CLASS}" exists, but the path is invalid!')
            return {'CANCELLED'}
        cos = COSMETIC
        try:
            with bpy.data.libraries.load(p, assets_only=True) as (file_contents, data_to):
                data_to.objects = [cos]
        except:
            self.report({'ERROR'}, f'.blend file for "{CLASS}" entry is corrupt/unable to be opened! Redownload!')
            return {'CANCELLED'}
        list = [i.name for i in D.objects if not "_ARM" in i.name and cos in i.name]

        try:
            justadded = D.objects[sorted(list)[-1]]
        except:
            self.report({'ERROR'}, f'.blend file for "{CLASS}" entry is corrupt/unable to be opened! Redownload!')
            return {'CANCELLED'}
        skins = justadded.get('skin_groups')
        count = 0
        # updates the skin_groups dictionary on the object with its materials
        # previously it would iterate through the skin_groups dictionary, but this would not work if there were more entries than
        # material slots. it will now only iterate through the minimum between how many material slots there are and how many entries there are.
        for num in range(min(len(justadded.material_slots)//max(len(skins['0']), 1), len(skins))):
            Range = count + len(skins[str(num)]) # make a range between the last range (0 if first iteration) and the last range + how many entries are in this skin group
            newmatlist = []
            for i in range(count, Range):
                newmatlist.append(justadded.material_slots[i].material.name)
            skins[str(num)] = newmatlist
            count = Range
        justadded['skin_groups'] = skins
        del newmatlist, Range, count, skins, list

        if (wardcol := context.scene.collection.children.get('Wardrobe')) == None:
            wardcol = bpy.data.collections.new('Wardrobe')
            context.scene.collection.children.link(wardcol)
        
        if justadded.parent != None:

            justaddedParent = justadded.parent
            wardcol.objects.link(justaddedParent) # link everything and its children to the 'Wardrobe' collection for better management.
            justaddedParent.use_fake_user = False

            for child in justaddedParent.children:
                wardcol.objects.link(child)
                child.use_fake_user = False

            justaddedParent.location = context.scene.cursor.location
        
        else:
            wardcol.objects.link(justadded)
            justadded.location = context.scene.cursor.location

        for mat in justadded.material_slots:
            for NODE in mat.material.node_tree.nodes:
                if NODE.name == 'VertexLitGeneric':
                    NODE.inputs['rim * ambient'].default_value = 1 # for better colors
                    NODE.inputs['$rimlightboost [value]'].default_value = NODE.inputs['$rimlightboost [value]'].default_value* context.scene.hisanimvars.hisanimrimpower
                if Collapse(NODE, 'VertexLitGeneric') == 'continue': # use VertexLitGeneric-WDRB, recursively remove nodes and node groups from VertexLitGeneric
                    continue
                if NODE.type == 'TEX_IMAGE':
                    if ReuseImage(NODE, p) == 'continue': # use existing images
                        continue
        if bpy.context.scene.hisanimvars.wrdbbluteam: # this one speaks for itself
            var = False
            print("BLU")
            try:
                SKIN = justadded['skin_groups']
                OBJMAT = justadded.material_slots
                for i in SKIN: # return where blu materials are found as BLU
                    for ii in SKIN[i]:
                        if "blu" in ii:
                            BLU = i
                            print(BLU)
                            var = True
                            break
                    if var: break
                else: raise
                print(SKIN[BLU])
                for i in enumerate(SKIN[BLU]): # set the materials as BLU
                    print(i)
                    OBJMAT[i[0]].material = bpy.data.materials[i[1]]
                del SKIN, OBJMAT
            except:
                pass
        if (bpy.context.object == None) or nothing or (justadded.parent == None): return {'FINISHED'}

        select = bpy.context.object
        # if a Bonemerge compatible rig or mesh parented to one is selected, automatically bind the cosmetic
        # to the rig.

        if select.parent != None:
            select.select_set(False)
            select = select.parent
        
        if select.get('BMBCOMPATIBLE') != None and (context.scene.hisanimvars.autobind if context.scene.hisanimvars.hisanimweapons else True): # if the selected armature is bonemerge compatible, bind to it.
            bak = context.scene.hisanimvars.hisanimtarget
            context.scene.hisanimvars.hisanimtarget = select
            justadded.parent.select_set(True)
            bpy.ops.hisanim.attachto()
            context.scene.hisanimvars.hisanimtarget = bak
            del bak
        
        mercdeployer.PurgeNodeGroups()
        mercdeployer.PurgeImages()
        return {'FINISHED'}

class HISANIM_OT_Search(bpy.types.Operator):
    bl_idname = 'hisanim.search'
    bl_label = 'Search for cosmetics'
    bl_description = "Go ahead, search"
    
    def execute(self, context):
        context.scene.hisanimvars.results.clear()
        context.scene.hisanimvars.searched = True
        lookfor = bpy.context.scene.hisanimvars.query
        lookfor = lookfor.split("|")
        lookfor.sort()
        hits = returnsearch(lookfor)
        for hit in hits:
            new = context.scene.hisanimvars.results.add()
            new.name = hit
        return {'FINISHED'}

class HISANIM_OT_ClearSearch(bpy.types.Operator): # clear the search
    bl_idname = 'hisanim.clearsearch'
    bl_label = 'Clear Search'
    bl_description = 'Clear your search history'
    
    def execute(self, context):
        
        context.scene.hisanimvars.results.clear()
        context.scene.hisanimvars.searched = False
        return {'FINISHED'}

class HISANIM_OT_MATFIX(bpy.types.Operator):
    bl_idname = 'hisanim.materialfix'
    bl_label = 'Fix Material'
    bl_description = 'Fix Material'
    
    def execute(self, context):
        MAT = context.object.active_material

        if MAT.node_tree.nodes.get('WRDB-MIX') != None:
            return {'CANCELLED'}

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

class HISANIM_OT_REVERTFIX(bpy.types.Operator):
    bl_idname = 'hisanim.revertfix'
    bl_label = 'Revert Fix'
    bl_description = 'Revert a material fix done on a material'

    def execute(self, context):
        MAT = context.object.active_material
        MATLINK = MAT.node_tree.links
        if MAT.node_tree.nodes.get('WRDB-MIX') != None:
            MAT.node_tree.nodes['VertexLitGeneric'].inputs['$color2 [RGB field]'].default_value = list(MAT.node_tree.nodes['WRDB-GAMMA'].inputs[0].default_value)

            MAT.node_tree.nodes.remove(MAT.node_tree.nodes['WRDB-MIX'])
            MAT.node_tree.nodes.remove(MAT.node_tree.nodes['WRDB-GAMMA'])
            MATLINK.new(MAT.node_tree.nodes['$basetexture'].outputs[0], MAT.node_tree.nodes['VertexLitGeneric'].inputs[0])
            return {'FINISHED'}
        else:
            return {'CANCELLED'}

class HISANIM_OT_PAINTS(bpy.types.Operator):
    bl_idname = 'hisanim.paint'
    bl_label = 'Paint'
    bl_description = 'Use this paint on cosmetic'
    bl_options = {'UNDO'}

    PAINT: StringProperty(default='')

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
    
class HISANIM_OT_relocatePaths(bpy.types.Operator):
    bl_idname = 'hisanim.relocatepaths'
    bl_label = 'Relocate Paths'
    bl_description = 'Redefine libraries in file based on entries in the TF2-Trifecta'

    def execute(self, context):
        prefs = context.preferences.addons[__package__].preferences
        paths = prefs.assets
        files = list(map(lambda a: a +'cosmetics.blend', mercdeployer.mercs)) + ['allclass.blend', 'allclass2.blend', 'allclass3.blend']
        filesDict = {key: key.replace('cosmetics', '').replace('.blend', '') for key in files}
        TF2_V3 = list(map(lambda a: a + '.blend', mercdeployer.mercs))
        for lib in bpy.data.libraries:
            lib.name = os.path.basename(lib.filepath)
        for file in files:
            if (lib := bpy.data.libraries.get(file)) != None:
                if paths.get(filesDict[file]) == None: continue
                lib.filepath = paths[filesDict[file]].path
                lib.reload()
        if (path := paths.get('rigs')) == None: return {'FINISHED'}
        for merc in TF2_V3:
            if (lib := bpy.data.libraries.get(merc)) != None:
                lib.filepath = os.path.join(path.path, merc)
                lib.reload()
        return {'FINISHED'}

classes = [
            searchHits,
            hisanimvars,
            HISANIM_OT_PAINTCLEAR,
            HISANIM_OT_LOAD,
            HISANIM_OT_PAINTS,
            HISANIM_OT_AddLightwarps,
            HISANIM_OT_RemoveLightwarps,
            HISANIM_OT_Search,
            HISANIM_OT_ClearSearch,
            HISANIM_OT_REVERTFIX,
            HISANIM_OT_MATFIX,
            HISANIM_OT_relocatePaths,
            WDRB_OT_Select,
            WDRB_OT_Cancel,
            WDRB_OT_Confirm
            ]
def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.hisanimvars = PointerProperty(type=hisanimvars)
    
def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.hisanimvars
    