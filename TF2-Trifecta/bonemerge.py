import bpy

loc = "BONEMERGE-ATTACH-LOC"
rot = "BONEMERGE-ATTACH-ROT"

bpy.types.Scene.target = bpy.props.PointerProperty(type=bpy.types.Object)

class VIEW3D_PT_BONEMERGE(bpy.types.Panel):
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
        self.layout.prop_search(context.scene, "target", bpy.data, "objects", text="Link to", icon='ARMATURE_DATA')
        
        row = layout.row()
        row.operator('hisanim.attachto', icon="LINKED")
        row=layout.row()
        row.operator('hisanim.detachfrom', icon="UNLINKED")
        


class HISANIM_OT_ATTACH(bpy.types.Operator):
    bl_idname = "hisanim.attachto"
    bl_label = "Attach"
    bl_description = "Attach to a class"
    bl_options = {'UNDO'}
    
    def execute(self, context):
        if context.scene.target == None:
            raise TypeError("\n\nNo armature selected!")
        obj = context.scene.target.name
    
        
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
                    bpy.data.objects[obj].pose.bones[ii.name] # check if the target bone exists. if not, continue.
                except:
                    continue
                
                try:
                    ii.constraints[loc] # check if constraints already exist. if so, swap targets. if not, create constraints.
                    pass
                except:
                    ii.constraints.new('COPY_LOCATION').name = loc
                    ii.constraints.new('COPY_ROTATION').name = rot
                
                ii.constraints[loc].target = bpy.data.objects[obj]
                ii.constraints[loc].subtarget = ii.name
                ii.constraints[rot].target = bpy.data.objects[obj]
                ii.constraints[rot].subtarget = ii.name
        
        return {'FINISHED'}
    
class HISANIM_OT_DETACH(bpy.types.Operator):
    bl_idname = "hisanim.detachfrom"
    bl_label = "Detach"
    bl_description = "Detach from a class"
    bl_options = {'UNDO'}
    
    def execute(self, context):
        
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
                except:
                    continue
        
        return {'FINISHED'}