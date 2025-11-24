import bpy

from bpy.props import *
from typing import List, Set

#loc = "BONEMERGE-ATTACH-LOC"
#rot = "BONEMERGE-ATTACH-ROT"
#scale = "BONEMERGE-ATTACH-SCALE"

loc = "BONEMERGE-LOC"
rot = "BONEMERGE-ROT"
scale = "BONEMERGE-SCALE"

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

        def recursive(bone: bpy.types.PoseBone, depth: int):
            if target_bones.get(bone.name) == None: # check if the target bone exists. if not, continue.
                for child in bone.children:
                    recursive(child, depth)
                return
            expr = 'var'

            constraints_loc = [con for con in bone.constraints if con.name.startswith(loc) and (getattr(con, 'target', None) == target)]
            constraints_rot = [con for con in bone.constraints if con.name.startswith(rot) and (getattr(con, 'target', None) == target)]
            constraints_sca = [con for con in bone.constraints if con.name.startswith(scale) and (getattr(con, 'target', None) == target)]
            drivers = []

            if not constraints_loc:
                CON = bone.constraints.new('COPY_LOCATION')
                CON.name = loc
                CON.target = target
                CON.subtarget = bone.name
            else:
                if len(constraints_loc) > 1:
                    self.report({'INFO'}, f'Removed extra loc constraints on {bone.name}')
                    [bone.constraints.remove(con) for con in constraints_loc[1:]]
                CON = constraints_loc[0]
            driv = CON.driver_add('influence')
            drivers.append(driv)
            driv.driver.expression = expr
            var = driv.driver.variables.new()
            var.targets[0].id = obj
            var.targets[0].data_path = data_path

            if not constraints_rot:
                CON = bone.constraints.new('COPY_ROTATION')
                CON.name = rot
                CON.target = target
                CON.subtarget = bone.name
            else:
                if len(constraints_rot) > 1:
                    self.report({'INFO'}, f'Removed extra rot constraints on {bone.name}')
                    [bone.constraints.remove(con) for con in constraints_rot[1:]]
                CON = constraints_rot[0]
            driv = CON.driver_add('influence')
            drivers.append(driv)
            driv.driver.expression = expr
            var = driv.driver.variables.new()
            var.targets[0].id = obj
            var.targets[0].data_path = data_path

            if context.scene.hisanimvars.hisanimscale:
                if not constraints_sca:
                    CON = bone.constraints.new('COPY_SCALE')
                    CON.name = scale
                    CON.target = target
                    CON.subtarget = bone.name
                else:
                    if len(constraints_sca) > 1:
                        self.report({'INFO'}, f'Removed extra scale constraints on {bone.name}')
                        [bone.constraints.remove(con) for con in constraints_sca[1:]]
                    CON = constraints_sca[0]
                driv = CON.driver_add('influence')
                drivers.append(driv)
                driv.driver.expression = expr
                var = driv.driver.variables.new()
                var.targets[0].id = obj
                var.targets[0].data_path = data_path

            bone['depth'] = depth

            bone_drivers.append((bone, drivers))

            max_depth[0] = max(depth, max_depth[0])

            for bone in bone.children:
                recursive(bone, depth+1)

        if (target := getattr(bpy.types.Scene, 'host', None)):
            #self.report({'INFO'}, 'No armature selected!')
            pass

        elif context.scene.hisanimvars.hisanimtarget == None:
            if not hasattr(context, 'object'):
                self.report({'INFO'}, 'No armature selected!')
                return {'CANCELLED'}
            if (target := getattr(bpy.types.Scene, 'host', None)) == None:
                self.report({'INFO'}, 'No armature selected!')
            if (target := context.object) == None:
                self.report({'INFO'}, 'No armature selected!')
                return {'CANCELLED'}
            if target.type != 'ARMATURE':
                self.report({'INFO'}, 'No armature selected!')
                return {'CANCELLED'}
        else:
            target = context.scene.hisanimvars.hisanimtarget

        if target == 'None':
            self.report({'INFO'}, 'No armature selected!')
            return {'CANCELLED'}

        if (host := getattr(bpy.types.Scene, 'host', None)) and (parasite := getattr(bpy.types.Scene, 'parasite', None)):
            target = host
            objs = [parasite]
        else:
            objs = context.selected_objects
        objs: Set[bpy.types.Object] = set(obj if obj.type == 'ARMATURE' else obj.parent for obj in objs)

        for obj in objs:
            if obj == None:
                continue
            if not (obj.type == 'ARMATURE' or obj.type == 'MESH'):
                continue # if the iteration is neither armature nor mesh, continue.
            if obj == target:
                continue # if the target is selected while cycling through selected objects, it will be skipped.
            if obj.type == 'MESH':
                obj = obj.parent # if the mesh is selected instead of the parent armature, swap the iteration with its parent

            targets = [con for con in obj.constraints if con.name.startswith('bm_target') and (getattr(con, 'target', None) == target)]

            if not targets:
                new_target: bpy.types.CopyLocationConstraint = obj.constraints.new('COPY_LOCATION')
                new_target.target = target
                new_target.name = 'bm_target'
                new_target.enabled = False
                new_target.influence = 1.0
            else:
                if len(targets) > 1:
                    [obj.constraints.remove(con) for con in targets[1:]]
                new_target = targets[0]

            data_path = new_target.path_from_id('influence')

            target_bones = target.pose.bones
            bone_drivers = []
            max_depth = [0]
            
            
            
            for bone in obj.pose.bones:
                if bone.parent != None: continue
                recursive(bone, 1)

            if context.scene.hisanimvars.hierarchal_influence:
                max_depth = max_depth[0]
                for bone, drivers in bone_drivers:
                    depth = bone.get('depth')
                    
                    for driver in drivers:
                        driver: bpy.types.FCurve
                        driver.driver.expression = f'var*{max_depth}-{depth-1}'

        return {'FINISHED'}
    
class HISANIM_OT_DETACH(bpy.types.Operator):
    bl_idname = "hisanim.detachfrom"
    bl_label = "Detach"
    bl_description = "Detach from a class"
    bl_options = {'UNDO'}

    detach_similar: BoolProperty(default=False)
    target: StringProperty(default='')

    @classmethod
    def poll(cls, context):
        if len(context.selected_objects) == 0: return False
        return True
    
    def invoke(self, context, event):
        print(event.shift)
        if event.shift:
            self.detach_similar = True
        else:
            self.detach_similar = False
        return self.execute(context)
    
    def execute(self, context):

        obj = context.object

        if self.detach_similar:
            objs = context.selected_objects
        else:
            objs = [obj]

        objs: Set[bpy.types.Object] = set(object if object.type == 'ARMATURE' else object.parent for object in objs)

        target = bpy.data.objects.get(self.target)
        

        for obj in objs:
            
            if obj == None:
                continue
            if not obj.type == 'ARMATURE':
                continue
            con_targets = [con for con in obj.constraints if getattr(con, 'target', None) == target]     
            for bone in obj.pose.bones:
                
                constraints_loc = [con for con in bone.constraints if (con.name.startswith(loc)) and (getattr(con, 'target', None) == target)]
                constraints_rot = [con for con in bone.constraints if (con.name.startswith(rot)) and (getattr(con, 'target', None) == target)]
                constraints_sca = [con for con in bone.constraints if (con.name.startswith(scale)) and (getattr(con, 'target', None) == target)]

                if obj.animation_data:
                    for con in constraints_loc:
                        data_path = con.path_from_id('influence')
                        driver = obj.animation_data.drivers.find(data_path)
                        if driver:
                            obj.animation_data.drivers.remove(driver)
                    for con in constraints_rot:
                        data_path = con.path_from_id('influence')
                        driver = obj.animation_data.drivers.find(data_path)
                        if driver:
                            obj.animation_data.drivers.remove(driver)
                    for con in constraints_sca:
                        data_path = con.path_from_id('influence')
                        driver = obj.animation_data.drivers.find(data_path)
                        if driver:
                            obj.animation_data.drivers.remove(driver)

                for con in constraints_loc:
                    bone.constraints.remove(con)
                for con in constraints_rot:
                    bone.constraints.remove(con)
                for con in constraints_sca:
                    bone.constraints.remove(con)

            for con in con_targets:
                obj.constraints.remove(con)

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
        for bone in SELECT.pose.bones:
            if not bone.parent: continue

            constraints_loc = [con for con in bone.constraints if con.name.startswith(loc)]
            constraints_rot = [con for con in bone.constraints if con.name.startswith(rot)]
            constraints_sca = [con for con in bone.constraints if con.name.startswith(scale)]

            for constraint in constraints_loc:
                constraint.enabled = False
            for constraint in constraints_rot:
                constraint.enabled = False
            for constraint in constraints_sca:
                constraint.enabled = False

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