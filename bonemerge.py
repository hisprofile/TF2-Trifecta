import bpy

loc = "BONEMERGE-ATTACH-LOC"
rot = "BONEMERGE-ATTACH-ROT"
scale = "BONEMERGE-ATTACH-SCALE"

bpy.types.Scene.hisanimtarget = bpy.props.PointerProperty(type=bpy.types.Object)
def GetRoot(a):
    for i in a:
        if i.parent == None:
            return i
        
class BM_PT_BONEMERGE(bpy.types.Panel):
    """A Custom Panel in the Viewport Toolbar"""
    bl_label = "Bonemerge"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Bonemerge"
    bl_icon = "BONE_DATA"
    
    def draw(self, context):
        layout = self.layout
        row = layout.row()
        
        
        row.label(text='Attach TF2 cosmetics.', icon='MOD_CLOTH')
        ob = context.object
        row = layout.row()
        self.layout.prop_search(context.scene, "hisanimtarget", bpy.data, "objects", text="Link to", icon='ARMATURE_DATA')
        
        row = layout.row()
        row.operator('hisanim.attachto', icon="LINKED")
        row=layout.row()
        row.operator('hisanim.detachfrom', icon="UNLINKED")
        row = layout.row()
        row.label(text='Bind facial cosmetics')
        row = layout.row()
        row.operator('hisanim.bindface')
        row = layout.row()
        row.label(text='Attempt to fix cosmetic')
        row = layout.row()
        row.operator('hisanim.attemptfix')
        


class HISANIM_OT_ATTACH(bpy.types.Operator):
    bl_idname = "hisanim.attachto"
    bl_label = "Attach"
    bl_description = "Attach to a class"
    bl_options = {'UNDO'}
    
    def execute(self, context):
        if context.scene.hisanimtarget == None:
            self.report({'INFO'}, 'No armature selected!')
            return {'CANCELLED'}
        obj = context.scene.hisanimtarget
        doOnce = True
        
        for i in bpy.context.selected_objects:
            if i == None:
                continue
            if not (i.type == 'ARMATURE' or i.type == 'MESH'):
                continue # if the iteration is neither armature nor mesh, continue.
            if i.name == obj:
                continue # if the target is selected while cycling through selected objects, it will be skipped.
            if i.type == 'MESH':
                i = i.parent # if the mesh is selected instead of the parent armature, swap the iteration with its parent
            for ii in i.pose.bones:
                try:
                    obj.pose.bones[ii.name] # check if the target bone exists. if not, continue.
                    if doOnce:
                        print
                        i.parent = obj
                        if i.get('BAKLOC') == None:
                            i['BAKLOC'] = i.location
                        i.location = [0, 0, 0]
                        doOnce = False
                except:
                    continue
                
                try:
                    ii.constraints[loc] # check if constraints already exist. if so, swap targets. if not, create constraints.
                    pass
                except:
                    ii.constraints.new('COPY_SCALE').name = scale
                    ii.constraints.new('COPY_LOCATION').name = loc
                    ii.constraints.new('COPY_ROTATION').name = rot

                SCALE = ii.constraints[scale]
                LOC = ii.constraints[loc]
                ROT = ii.constraints[rot]

                SCALE.target = obj
                SCALE.subtarget = ii.name
                LOC.target = obj
                LOC.subtarget = ii.name
                ROT.target = obj
                ROT.subtarget = ii.name
        
        return {'FINISHED'}
    
class HISANIM_OT_DETACH(bpy.types.Operator):
    bl_idname = "hisanim.detachfrom"
    bl_label = "Detach"
    bl_description = "Detach from a class"
    bl_options = {'UNDO'}
    
    def execute(self, context):
        doOnce = True
        for i in bpy.context.selected_objects:
            if i == None:
                continue
            if not (i.type == 'ARMATURE' or i.type == 'MESH'):
                continue
            if i.type == 'MESH':
                i = i.parent
            for ii in i.pose.bones:
                try:
                    ii.constraints.remove(ii.constraints[loc])
                    ii.constraints.remove(ii.constraints[rot])
                    ii.constraints.remove(ii.constraints[scale])
                    if doOnce == True:
                        print('Doing once')
                        i.parent = None
                        if i.get('BAKLOC') != None:
                            i.location = [*i.get('BAKLOC')]
                            del i['BAKLOC']
                        doOnce = False
                except:
                    continue
        
        return {'FINISHED'}
class HISANIM_OT_BINDFACE(bpy.types.Operator):
    bl_idname = 'hisanim.bindface'
    bl_label = 'Bind Face Cosmetics'
    bl_description = 'Bind facial cosmetics to a face'
    bl_options = {'UNDO'}
    
    def execute(self, context):
        #print('rad')
        CON = context.selected_objects
        
        for i in CON[1].data.shape_keys.key_blocks:
            find = i.name.casefold()
            i.slider_min = -10
            i.slider_max = 10
            print(i)
            for ii in CON[0].data.shape_keys.key_blocks:
                if ii.name.casefold() == find:
                    val = i.driver_add("value").driver
                    val.variables.new()
                    i.driver_add("value").driver.expression = 'var'
                    val.variables[0].targets[0].id_type = 'KEY'
                    val.variables[0].targets[0].id = CON[0].data.shape_keys
                    val.variables[0].targets[0].data_path = f'key_blocks["{ii.name}"].value'
            
        
        return {'FINISHED'}
class HISANIM_OT_ATTEMPTFIX(bpy.types.Operator):
    bl_idname = 'hisanim.attemptfix'
    bl_label = 'Attempt to Fix Cosmetic'
    bl_description = 'If a cosmetic appears to be worn incorrectly, this button may fix it'
    bl_options = {'UNDO'}
    
    def execute(self, context):
        SELECT = context.object
        if not SELECT.type == 'ARMATURE':
            SELECT = SELECT.parent
        skipbone = SELECT.data.bones[0]
        for i in SELECT.pose.bones:
            if i.name == skipbone.name:
                continue
            try:
                i.constraints[loc].enabled = False
                i.constraints[rot].enabled = False
            except:
                pass
        return {'FINISHED'}