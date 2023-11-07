import bpy
#from . import poselib
from .poselib import textBox

loc = "BONEMERGE-ATTACH-LOC"
rot = "BONEMERGE-ATTACH-ROT"
scale = "BONEMERGE-ATTACH-SCALE"
def IsArmature(scene, obj):
    if obj.type=='ARMATURE':
        return True
    else:
        return False

def GetRoot(a):
    for i in a:
        if i.parent == None:
            return i
        
class HISANIM_OT_ATTACH(bpy.types.Operator):
    bl_idname = "hisanim.attachto"
    bl_label = "Attach"
    bl_description = "Attach to a class"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        if len(context.selected_objects) == 0: return False
        return True
    
    def execute(self, context):
        if context.scene.hisanimvars.hisanimtarget == None:
            if (obj := bpy.context.object) == None:
                self.report({'INFO'}, 'No armature selected!')
                return {'CANCELLED'}
            if obj.type != 'ARMATURE':
                self.report({'INFO'}, 'No armature selected!')
                return {'CANCELLED'}
        else:
            obj = context.scene.hisanimvars.hisanimtarget
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
                if obj.pose.bones.get(ii.name) != None: # check if the target bone exists. if not, continue.
                    if doOnce: # this will parent the cosmetic to the target if at least
                        doOnce = False
                        # one bone from the cosmetic exists in the target
                        if context.scene.hisanimvars.hisanimscale:
                            i.parent = obj # make the cosmetic's armature's parent the merc
                            if i.get('BAKLOC') == None:
                                i['BAKLOC'] = i.location # save previous location
                            i.location = [0, 0, 0]
                        else:
                            if i.constraints.get('COPLOC') == None: # always copy merc's location
                                LOC = i.constraints.new('COPY_LOCATION')
                                LOC.name = 'COPLOC'
                                LOC.target = obj
                    if ii.constraints.get(loc) == None: # check if constraints already exist. if so, swap targets. if not, create constraints.
                        if context.scene.hisanimvars.hisanimscale:
                            ii.constraints.new('COPY_SCALE').name = scale
                        ii.constraints.new('COPY_LOCATION').name = loc
                        ii.constraints.new('COPY_ROTATION').name = rot
                else:
                    continue
                LOC = ii.constraints[loc]
                ROT = ii.constraints[rot]

                LOC.target = obj
                LOC.subtarget = ii.name
                ROT.target = obj
                ROT.subtarget = ii.name
                if context.scene.hisanimvars.hisanimscale:
                    if ii.constraints.get(scale) == None:
                        ii.constraints.new('COPY_SCALE').name = scale
                    SCALE = ii.constraints[scale]
                    SCALE.target = obj
                    SCALE.subtarget = ii.name
        
        return {'FINISHED'}
    
class HISANIM_OT_DETACH(bpy.types.Operator):
    bl_idname = "hisanim.detachfrom"
    bl_label = "Detach"
    bl_description = "Detach from a class"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        if len(context.selected_objects) == 0: return False
        return True
    
    def execute(self, context):
        doOnce = True
        for i in bpy.context.selected_objects:
            if i == None:
                continue
            if not (i.type == 'ARMATURE' or i.type == 'MESH'):
                continue
            if i.type == 'MESH':
                i = i.parent
            if doOnce == True:
                i.parent = None
                if i.get('BAKLOC') != None:
                    i.location = [*i.get('BAKLOC')]
                    del i['BAKLOC']
                doOnce = False
                if i.constraints.get('COPLOC') != None:
                    i.constraints.remove(i.constraints.get('COPLOC'))
            for ii in i.pose.bones:
                try:
                    ii.constraints.remove(ii.constraints[loc])
                    ii.constraints.remove(ii.constraints[rot])
                    ii.constraints.remove(ii.constraints[scale])
                except:
                    continue
        
        return {'FINISHED'}
    
class HISANIM_OT_BINDFACE(bpy.types.Operator):
    bl_idname = 'hisanim.bindface'
    bl_label = 'Bind Face Cosmetic'
    bl_description = 'Bind facial cosmetics to a face'
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        if len(context.selected_objects) == 2:
            for obj in context.selected_objects:
                if obj.type != 'MESH':
                    return False
            return True
    
    def execute(self, context):
        objs = list(context.selected_objects)
        objs.remove(context.object)
        cos = objs[0]
        face = context.object

        if face.data.get('aaa_fs') == None:
            self.report({'ERROR'}, 'The object you have as active is invalid! Make sure a mercenary is selected last!')
            return {'CANCELLED'}
        
        if cos.get('skeys') == None:
            cos['skeys'] = []
        
        skeys = list(cos['skeys'])

        skey_s = cos.data.shape_keys

        if skey_s == None:
            self.report({'ERROR'}, 'Source object has no shape keys!')
            return {'CANCELLED'}

        kb_s = skey_s.key_blocks
        skey_t = face.data.shape_keys

        if skey_t == None:
            self.report({'ERROR'}, 'Target object has no shape keys!')
            return {'CANCELLED'}

        kb_t = skey_t.key_blocks
        for skey in kb_s:
            if kb_t.get(skey.name) != None:
                if skey.name not in skeys:
                    skeys.append(skey.name)
                driv = kb_s[skey.name].driver_add('value').driver
                driv.variables.new()
                driv.expression = 'var'
                driv.variables[0].targets[0].id_type = 'KEY'
                driv.variables[0].targets[0].id = skey_t
                driv.variables[0].targets[0].data_path = f'key_blocks["{skey.name}"].value'
        
        if skeys == []:
            self.report({'ERROR'}, 'Neither objects have matching shape keys!')
            return {'CANCELLED'}

        cos['skeys'] = skeys

        return {'FINISHED'}
    
class BM_OT_UNBINDFACE(bpy.types.Operator):
    bl_idname = 'bm.unbindface'
    bl_label = 'Unbind Face Cosmetic'
    bl_description = 'Unbinds the cosmetic from the mercenary'
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        if len(context.selected_objects) == 0: return False
        return context.object.type == 'MESH'

    def execute(self, context):
        ob = context.object
        data = ob.data
        skeys = data.shape_keys

        if ob.get('skeys') == None:
            return {'CANCELLED'}
        if data.shape_keys == None:
            return {'CANCELLED'}

        for item in ob['skeys']:
            if (driv := skeys.animation_data.drivers.find(f'key_blocks["{item}"].value')) != None:
                skeys.animation_data.drivers.remove(driv)

        del ob['skeys']
        
        return {'FINISHED'}

class HISANIM_OT_ATTEMPTFIX(bpy.types.Operator):
    bl_idname = 'hisanim.attemptfix'
    bl_label = 'Attempt to Fix Cosmetic'
    bl_description = 'If a cosmetic appears to be worn incorrectly, this button may fix it'
    bl_options = {'UNDO'}
    
    def execute(self, context):
        SELECT = context.object
        if SELECT.type == 'MESH':
            if SELECT.parent == None: return {'CANCELLED'}
        
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
    
classes = [
    HISANIM_OT_ATTACH,
    HISANIM_OT_ATTEMPTFIX,
    HISANIM_OT_BINDFACE,
    HISANIM_OT_DETACH,
    BM_OT_UNBINDFACE,
]

def register():
    for i in classes:
        bpy.utils.register_class(i)

def unregister():
    for i in reversed(classes):
        bpy.utils.unregister_class(i)