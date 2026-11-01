import bpy,math,os,bmesh
from mathutils import Vector
BASE='/Users/pranay/Documents/Codex/2026-10-22/new-chat-6';OUT=BASE+'/outputs/Characters/CH_Female_v001'
rig=bpy.data.objects['CH_Rig'];original_scene=bpy.context.scene
# Correct the open scalp shell's outward winding; longitudinal hair locks are already outward.
hair=bpy.data.objects['CH_Hair_Back'];bm=bmesh.new();bm.from_mesh(hair.data);bm.faces.ensure_lookup_table()
bmesh.ops.reverse_faces(bm,faces=[bm.faces[i] for i in range(72*24)])
bm.to_mesh(hair.data);bm.free();hair.data.update()
studio=bpy.data.scenes.new('CH_Character_Preview_Studio')
studio.collection.children.link(bpy.data.collections['Characters'])
world=bpy.data.worlds.new('CH_Studio_World');world.use_nodes=True;studio.world=world
bg=next(n for n in world.node_tree.nodes if n.type=='BACKGROUND');bg.inputs['Color'].default_value=(.55,.52,.47,1);bg.inputs['Strength'].default_value=.4
studio.render.engine='CYCLES';studio.cycles.samples=32;studio.cycles.use_denoising=True
studio.render.resolution_x=768;studio.render.resolution_y=768;studio.render.resolution_percentage=100
studio.render.image_settings.file_format='PNG';studio.render.film_transparent=False
try:studio.view_settings.view_transform='AgX';studio.view_settings.look='AgX - Medium High Contrast'
except:pass
mat=bpy.data.materials.new('CH_Studio_Backdrop');mat.use_nodes=True
bs=next(n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED');bs.inputs['Base Color'].default_value=(.34,.31,.27,1);bs.inputs['Roughness'].default_value=1
mesh=bpy.data.meshes.new('CH_Studio_Floor_Mesh');mesh.from_pydata([(-10,-10,-.008),(10,-10,-.008),(10,10,-.008),(-10,10,-.008)],[],[(0,1,2,3)]);mesh.materials.append(mat)
floor=bpy.data.objects.new('CH_Studio_Floor',mesh);studio.collection.objects.link(floor);floor.location=rig.location
for name,position,power,size in [('Key',(-3,-4,5),420,4),('Fill',(3,-1,3),190,3),('Rim',(1,3,4),350,3)]:
    data=bpy.data.lights.new('CH_Studio_'+name,'AREA');data.energy=power;data.size=size
    ob=bpy.data.objects.new('CH_Studio_'+name,data);studio.collection.objects.link(ob)
    ob.location=rig.matrix_world@Vector(position);target=rig.matrix_world@Vector((0,0,1));ob.rotation_euler=(target-ob.location).to_track_quat('-Z','Y').to_euler()
data=bpy.data.cameras.new('CH_Preview_Lens');data.type='ORTHO';data.ortho_scale=2.32
camera=bpy.data.objects.new('CH_Preview_Camera',data);studio.collection.objects.link(camera);studio.camera=camera
target=rig.matrix_world@Vector((0,0,.98));camera.location=rig.matrix_world@Vector((0,-5,1.0));camera.rotation_euler=(target-camera.location).to_track_quat('-Z','Y').to_euler()
studio.render.filepath=OUT+'/CH_Front_TPose.png'
bpy.ops.render.render(write_still=True,scene=studio.name)
print('CHARACTER_FRONT_PREVIEW_READY',studio.render.filepath)
