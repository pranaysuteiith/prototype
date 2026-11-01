import bpy,json,math,os
R='/Users/pranay/My project/Characters/Boy_GreenSweater';S=bpy.context.scene;arm=bpy.data.objects['ARM_Boy_GreenSweater'];report={}
def reset():
 arm.animation_data.action=None
 for p in arm.pose.bones:p.rotation_quaternion=(1,0,0,0);p.location=(0,0,0);p.scale=(1,1,1)
for name in ['ANIM_Idle','ANIM_Walk','ANIM_Run','ANIM_Wave','ANIM_Sit']:
 reset();a=bpy.data.actions[name];arm.animation_data.action=a;start,end=map(int,a.frame_range)
 S.frame_set(start);first={p.name:p.matrix.copy() for p in arm.pose.bones};S.frame_set(end)
 err=max(abs(p.matrix[i][j]-first[p.name][i][j]) for p in arm.pose.bones for i in range(4) for j in range(4))
 minz=100;maxz=-100
 for frame in range(start,end+1):
  S.frame_set(frame);dg=bpy.context.evaluated_depsgraph_get()
  for name0 in ['CH_Shoes','CH_Shoes_Soles']:
   ob=bpy.data.objects[name0].evaluated_get(dg);me=ob.to_mesh();z=min((ob.matrix_world@v.co).z for v in me.vertices);minz=min(z,minz);maxz=max(z,maxz);ob.to_mesh_clear()
 report[name]={'endpointBoneMatrixDelta':err,'loopEndpointsMatch':err<1e-5 if name in ['ANIM_Idle','ANIM_Walk','ANIM_Run'] else None,'minimumSoleZAcrossFrames':minz,'highestLowestSoleZ':maxz}
reset();S.frame_set(1)
report['restPose']={'negativeObjectScales':[o.name for o in bpy.data.collections['CHAR_Boy_GreenSweater'].objects if min(o.scale)<0],'armatureScale':list(arm.scale),'tPoseUpperArmHorizontal':all(abs(arm.data.bones['UpperArm.'+s].head_local.z-arm.data.bones['UpperArm.'+s].tail_local.z)<1e-6 for s in ['L','R']),'allActionsPresent':len([a for a in bpy.data.actions if a.name.startswith('ANIM_')])==5}
json.dump(report,open(R+'/animation-audit.json','w'),indent=2);print('ANIMATION_AUDIT',json.dumps(report))
