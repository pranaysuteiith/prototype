import bpy,json
R='/Users/pranay/My project/Characters/Boy_GreenSweater';S=bpy.context.scene;C=bpy.data.collections['CHAR_Boy_GreenSweater'];arm=bpy.data.objects['ARM_Boy_GreenSweater'];original=S.name
for ob in C.objects:
 if ob.type!='MESH' or ob.data.uv_layers:continue
 me=ob.data;uv=me.uv_layers.new(name='UVMap')
 for p in me.polygons:
  axis=max(range(3),key=lambda k:abs(p.normal[k]));axes=[k for k in range(3) if k!=axis]
  for k in p.loop_indices:
   v=me.vertices[me.loops[k].vertex_index].co;uv.data[k].uv=(v[axes[0]]*9,v[axes[1]]*9)
bpy.ops.object.select_all(action='DESELECT')
for ob in C.objects:ob.select_set(True)
bpy.context.view_layer.objects.active=arm
common=dict(use_selection=True,object_types={'MESH','ARMATURE'},add_leaf_bones=False,apply_unit_scale=True,apply_scale_options='FBX_SCALE_UNITS',axis_forward='-Z',axis_up='Y',bake_anim=True,bake_anim_use_nla_strips=False,bake_anim_simplify_factor=0,path_mode='COPY',embed_textures=True)
bpy.ops.export_scene.fbx(filepath=R+'/Models/Boy_GreenSweater_Rigged.fbx',bake_anim_use_all_actions=True,**common)
for name in ['Idle','Walk','Run','Wave','Sit']:
 action=bpy.data.actions['ANIM_'+name];S.name=action.name;arm.animation_data.action=action;S.frame_start=int(action.frame_range[0]);S.frame_end=int(action.frame_range[1]);S.frame_set(S.frame_start)
 bpy.ops.export_scene.fbx(filepath=R+'/Animations/Boy_'+name+'.fbx',bake_anim_use_all_actions=False,**common)
arm.animation_data.action=None
for p in arm.pose.bones:p.rotation_quaternion=(1,0,0,0);p.location=(0,0,0);p.scale=(1,1,1)
S.name=original;S.frame_start=1;S.frame_end=97;S.frame_set(1)
r=json.load(open(R+'/validation.json'))
for m in r['meshes']:m['uvLayers']=len(bpy.data.objects[m['name']].data.uv_layers)
json.dump(r,open(R+'/validation.json','w'),indent=2)
bpy.ops.wm.save_as_mainfile(filepath=R+'/Blender/Boy_GreenSweater.blend')
print('UV_FINALIZED',all(m['uvLayers']>0 for m in r['meshes']))
