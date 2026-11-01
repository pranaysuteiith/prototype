import bpy,json,glob,os
R='/Users/pranay/My project/Characters/Boy_GreenSweater';out=[]
for path in [R+'/Models/Boy_GreenSweater_Rigged.fbx']+sorted(glob.glob(R+'/Animations/*.fbx')):
 for ob in list(bpy.data.objects):bpy.data.objects.remove(ob,do_unlink=True)
 for act in list(bpy.data.actions):bpy.data.actions.remove(act)
 bpy.ops.import_scene.fbx(filepath=path,use_anim=True)
 arms=[o for o in bpy.context.scene.objects if o.type=='ARMATURE'];meshes=[o for o in bpy.context.scene.objects if o.type=='MESH']
 out.append({'file':os.path.basename(path),'bytes':os.path.getsize(path),'armatures':len(arms),'bones':len(arms[0].data.bones) if arms else 0,'meshObjects':len(meshes),'triangles':sum(sum(len(p.vertices)-2 for p in o.data.polygons) for o in meshes),'actions':[a.name for a in bpy.data.actions],'allMeshesHaveUV':all(bool(o.data.uv_layers) for o in meshes),'allSkinnedMeshesHaveWeights':all(len(o.vertex_groups)>0 for o in meshes if any(m.type=='ARMATURE' for m in o.modifiers))})
json.dump(out,open(R+'/fbx-validation.json','w'),indent=2);print('FBX_ROUNDTRIP',json.dumps(out))
