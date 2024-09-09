import bpy, json, os, time
from pathlib import Path
from bpy.props import *
from bpy.types import Context
from mathutils import *
from . import bonemerge, mercdeployer, faceposer
from .preferences import ids

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

def getRigs(self, context):
    prefs = context.preferences.addons[__package__].preferences
    rigs = prefs.rigs

    rig_list = [(rig.name, rig.name, '', '', n) for n, rig in enumerate(rigs)]
    return rig_list

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
    name: StringProperty()
    tag: StringProperty()
    asset_reference: IntProperty()
    blend_reference: IntProperty()
    #use: BoolProperty(name='Use', default=False, get=gett, set=sett)

def fart(a = None, b = None, c = None):
    return str(time.time())

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
    hisanimrimpower: FloatProperty(name='Rimlight Strength',
                                description='Multiply the overall rim boost by this number',
                                default=0.400, min=0.0, max=1.0, options=set())
    hisanimscale: BoolProperty(default=False, name='Scale With', description='Scales cosmetics with targets bones. Disabled by default', options=set())
    hisanimtarget: PointerProperty(type=bpy.types.Object, poll=bonemerge.IsArmature)
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
    randomadditive: BoolProperty(name = 'Additive', description='Add onto the current face values', options=set())
    randomstrength: FloatProperty(name='Random Strength', min=0.0, max=1.0, description='Any random value calculated will be multiplied with this number', default=1.0, options=set())
    keyframe: BoolProperty(default=False, name='Keyframe Sliders', description='Keyframe the randomized changes', options=set())
    lockfilter: StringProperty()
    activeslider: StringProperty()
    activeface: PointerProperty(type=bpy.types.Object)
    lastactiveface: PointerProperty(type=bpy.types.Object)
    hierarchal_influence: BoolProperty(default=False, name='Hierarchal Influence', description='Activate the influence going down from the bone tree')
    sliders: CollectionProperty(type=faceposer.faceslider)
    sliderindex: IntProperty(options=set())
    dragging: BoolProperty(default=False, options=set())
    updating: BoolProperty(default = False, options=set())
    callonce: BoolProperty(default = False, options=set())
    LR: FloatProperty(default=0.0, options=set(), min=-1.0, max=1.0, name='L <-> R', description='Which way flexing will lean more towards', step=50)
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
    rigs: EnumProperty(items=getRigs, name='Rigs')
    merc: StringProperty(default='')
    toggle_mat: BoolProperty(default=False)
    needs_override: BoolProperty()
    enable_faceposer: BoolProperty(default = False)
    noKeyStatus: BoolProperty(default=False, name='Hide Keyframe Status', description='May improve performance')

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
    bl_idname = 'hisanim.loadcosmetic'
    bl_label = 'Cosmetic'
    bl_description = f'Load this cosmetic into your scene'
    bl_options = {'UNDO'}

    asset_reference: IntProperty()
    blend_reference: IntProperty()

    autobind: BoolProperty()

    def invoke(self, context, event):
        self.autobind = event.shift
        return self.execute(context)

    def execute(self, context):
        D = bpy.data
        prefs = context.preferences.addons[__package__].preferences
        
        blend = prefs.blends[self.blend_reference]
        asset = blend.assets[self.asset_reference]
        obj_reference = asset.reference

        if not os.path.exists(blend.path):
            self.report({'ERROR'}, f'{blend.path} does not exist!')
            return {'CANCELLED'}
        
        try:
            with bpy.data.libraries.load(blend.path, assets_only=True, link=True) as (From, To):
                To.objects = [obj_reference]
        except:
            self.report({'ERROR'}, f'{blend.path} is corrupt! Try to redownload!')
            return {'CANCELLED'}
        
        justadded: bpy.types.Object = To.objects[0]

        if justadded == None:    
            self.report({'ERROR'}, f'"{obj_reference}" does not exist in {os.path.basename(blend.path)}')
            return {'CANCELLED'}
        
        justadded = justadded.make_local()
        justadded.data.make_local()
        for mat in justadded.data.materials:
            mat: bpy.types.Material
            mat.make_local()
        if justadded.parent:
            justadded.parent.make_local()
            justadded.parent.data.make_local()

        skins = justadded.get('skin_groups')

        # updates the skin_groups dictionary on the object with its materials
        # previously it would iterate through the skin_groups dictionary, but this would not work if there were more entries than
        # material slots. it will now only iterate through the minimum between how many material slots there are and how many entries there are.
        
        if (wardcol := context.scene.collection.children.get('Wardrobe')) == None:
            wardcol = bpy.data.collections.new('Wardrobe')
            context.scene.collection.children.link(wardcol)
        
        wardcol.objects.link(justadded)
        if justadded.parent:
            wardcol.objects.link(justadded.parent) # link everything and its children to the 'Wardrobe' collection for better management.
            justadded.parent.location = context.scene.cursor.location
        else:
            justadded.location = context.scene.cursor.location

        for mat in justadded.material_slots:
            for NODE in mat.material.node_tree.nodes:
                if NODE.name == 'VertexLitGeneric':
                    #NODE.inputs['rim * ambient'].default_value = 1 # for better colors
                    NODE.inputs['$rimlightboost [value]'].default_value = NODE.inputs['$rimlightboost [value]'].default_value * context.scene.hisanimvars.hisanimrimpower

        if bpy.context.scene.hisanimvars.wrdbbluteam: # this one speaks for itself
            found = False
            mat_str = False
            if skins:
                skins = dict(skins)
                for index, group in skins.items():
                    for material in group:
                        if not isinstance(material, bpy.types.Material):
                            mat_str = True
                            break
                        if 'blu' in material.name:
                            found = True
                            break
                    if mat_str: break
                    if found: break
            if found:
                for n, material in enumerate(group):
                    justadded.material_slots[n].material = material
        bpy.data.orphans_purge(do_linked_ids=True, do_recursive=True)
        if (bpy.context.object == None) or (justadded.parent == None): return {'FINISHED'}

        select = bpy.context.object
        # if a Bonemerge compatible rig or mesh parented to one is selected, automatically bind the cosmetic
        # to the rig.
        if not select.select_get() or self.autobind:
            return {'FINISHED'}

        if select.parent:
            #select.select_set(False)
            select = select.parent
        if select.get('BMBCOMPATIBLE') != None: # and (context.scene.hisanimvars.autobind if context.scene.hisanimvars.hisanimweapons else True): # if the selected armature is bonemerge compatible, bind to it.
            bpy.types.Scene.host = select
            bpy.types.Scene.parasite = justadded.parent
            bpy.ops.hisanim.attachto()
            delattr(bpy.types.Scene, 'host')
            delattr(bpy.types.Scene, 'parasite')
        
        #mercdeployer.PurgeNodeGroups()
        #mercdeployer.PurgeImages()
        return {'FINISHED'}

class HISANIM_OT_Search(bpy.types.Operator):
    bl_idname = 'hisanim.search'
    bl_label = 'Search for cosmetics'
    bl_description = "Go ahead, search"
    
    def execute(self, context):
        from .preferences import order
        prefs = context.preferences.addons[__package__].preferences
        context.scene.hisanimvars.results.clear()
        context.scene.hisanimvars.searched = True
        lookfor: str = bpy.context.scene.hisanimvars.query
        lookfor = lookfor.split("|")
        lookfor.sort()

        if len(prefs.blends) < 1:
            self.report({'ERROR'}, 'You have no .blend files to search through! Set your TF2 Items path and scan the folder!')
            return {'CANCELLED'}

        for request in lookfor:
            for nb, blend in sorted(filter(lambda a: a[1].no_search == False, enumerate(prefs.blends)), key=lambda a: order.get(a[1].tag, -1)):
                #print(blend)
                for na, asset in filter(lambda a: (request.lower() in a[1].name.lower()) or (request.lower() in blend.tag.lower()), enumerate(blend.assets)):
                    #print(asset)
                    new = context.scene.hisanimvars.results.add()
                    new.name = asset.name
                    new.asset_reference = na
                    new.blend_reference = nb
                    new.tag = blend.tag
        
        #hits = returnsearch(lookfor)
        #for hit in hits:
        #    new = context.scene.hisanimvars.results.add()
        #    new.name = hit
        return {'FINISHED'}

class HISANIM_OT_ClearSearch(bpy.types.Operator): # clear the search
    bl_idname = 'hisanim.clearsearch'
    bl_label = 'Clear Search'
    bl_description = 'Clear your search history'
    
    def execute(self, context):
        
        context.scene.hisanimvars.results.clear()
        context.scene.hisanimvars.searched = False
        return {'FINISHED'}

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
        if MAT.node_tree == None:
            return {'CANCELLED'}
        TF2D = MAT.node_tree.nodes.get('TF2 Diffuse')
        if TF2D == None:
            self.report({'ERROR'}, 'Could not find TF2 Diffuse in material!')
            return {'CANCELLED'}
        color2 = TF2D.inputs['$color2']
        if MAT.get('$colortint_base') == None: # check if the default paint rgb node exists. if not, create the backup.
            MAT['$colortint_base'] = color2.default_value

        color2.default_value = paintlist

        return {'FINISHED'}

class HISANIM_OT_PAINTCLEAR(bpy.types.Operator):
    bl_idname = 'hisanim.paintclear'
    bl_label = 'Clear Paint'
    bl_description = 'Clear Paint'
    bl_options = {'UNDO'}

    def execute(self, context):
        MAT = context.object.active_material
        if MAT.node_tree == None:
            return {'CANCELLED'}
        TF2D = MAT.node_tree.nodes.get('TF2 Diffuse')
        if TF2D == None:
            self.report({'ERROR'}, 'Could not find TF2 Diffuse in material!')
            return {'CANCELLED'}
        color2 = TF2D.inputs['$color2']
        color2.default_value = MAT.get('$colortint_base', [1, 1, 1, 1])
        return {'FINISHED'}
    
class HISANIM_OT_relocatePaths(bpy.types.Operator):
    bl_idname = 'hisanim.relocatepaths'
    bl_label = 'Relocate Paths'
    bl_description = 'Redefine libraries in file based on entries in the TF2-Trifecta'

    def execute(self, context):
        prefs = context.preferences.addons[__package__].preferences
        blends = prefs.blends
        items_path = prefs.items_path
        if not os.path.exists(items_path):
            self.report({'ERROR'}, 'Your TF2 Items path does not exist!')
        files = list(map(lambda a: a +'cosmetics.blend', ids.keys()))
        TF2_V3 = list(map(lambda a: a + '.blend', mercdeployer.mercs))
        #for lib in bpy.data.libraries:
        #    lib.name = os.path.basename(lib.filepath)
        for file in files:
            if (lib := bpy.data.libraries.get(file)) != None:
                lib.filepath = os.path.join(items_path, file)
                lib.reload()
        if (path := prefs.rigs.get(context.scene.hisanimvars.rigs)) == None: return {'FINISHED'}
        for merc in TF2_V3:
            if (lib := bpy.data.libraries.get(merc)) != None:
                lib.filepath = os.path.join(path.path, merc)
                lib.reload()
        return {'FINISHED'}
    
class TRIFECTA_OT_setWdrb(bpy.types.Operator):
    bl_idname = 'trifecta.setwdrb'
    bl_label = 'Wardrobe'
    bl_description = 'Set the current tool to Wardrobe'

    def execute(self, context):
        context.scene.hisanimvars.tools = 'WARDROBE'
        return {'FINISHED'}
    
class TRIFECTA_OT_setMD(bpy.types.Operator):
    bl_idname = 'trifecta.setmd'
    bl_label = 'Merc Deployer'
    bl_description = 'Set the current tool to Merc Deployer'

    def execute(self, context):
        context.scene.hisanimvars.tools = 'MERC DEPLOYER'
        return {'FINISHED'}
    
class TRIFECTA_OT_setBM(bpy.types.Operator):
    bl_idname = 'trifecta.setbm'
    bl_label = 'Bonemerge'
    bl_description = 'Set the current tool to Bonemerge'

    def execute(self, context):
        context.scene.hisanimvars.tools = 'BONEMERGE'
        return {'FINISHED'}
    
class TRIFECTA_OT_setFP(bpy.types.Operator):
    bl_idname = 'trifecta.setfp'
    bl_label = 'Face Poser'
    bl_description = 'Set the current tool to the Face Poser'

    def execute(self, context):
        context.scene.hisanimvars.tools = 'FACE POSER'
        return {'FINISHED'}

classes = [
            searchHits,
            hisanimvars,
            HISANIM_OT_PAINTCLEAR,
            HISANIM_OT_LOAD,
            HISANIM_OT_PAINTS,
            HISANIM_OT_RemoveLightwarps,
            HISANIM_OT_Search,
            HISANIM_OT_ClearSearch,
            HISANIM_OT_relocatePaths,
            WDRB_OT_Select,
            WDRB_OT_Cancel,
            WDRB_OT_Confirm,
            TRIFECTA_OT_setWdrb,
            TRIFECTA_OT_setMD,
            TRIFECTA_OT_setBM,
            TRIFECTA_OT_setFP
            ]
def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.hisanimvars = PointerProperty(type=hisanimvars)
    
def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.hisanimvars
    
