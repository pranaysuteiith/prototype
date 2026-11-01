import bpy,os,math,json
from mathutils import Vector
R='/Users/pranay/My project/Characters/Boy_GreenSweater';S=bpy.context.scene;arm=bpy.data.objects['ARM_Boy_GreenSweater'];cam=S.camera
# Use the asset's dedicated studio only. The live café is not loaded in this process.
def clear_pose():
 arm.animation_data.action=None
 for p in arm.pose.bones:p.rotation_quaternion=(1,0,0,0);p.location=(0,0,0);p.scale=(1,1,1)
 bpy.context.view_layer.update()
def aim(pos,target=(0,0,.60),scale=1.42):
 cam.location=pos;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=scale

def render(name,pos,target=(0,0,.60),scale=1.42,res=1024):
 aim(pos,target,scale);S.render.resolution_x=res;S.render.resolution_y=res;S.render.resolution_percentage=100;S.render.filepath=R+'/Previews/'+name+'.png';bpy.ops.render.render(write_still=True);print('RENDERED',name,flush=True)
clear_pose()
for name,pos in [('Front',(0,-3,.60)),('Back',(0,3,.60)),('Left',(3,0,.60)),('Right',(-3,0,.60))]:render(name,pos)
render('Isometric',(-2.4,-3.4,2.0),scale=1.52)
for action,frame,name in [('ANIM_Idle',20,'Idle'),('ANIM_Wave',42,'Wave'),('ANIM_Sit',73,'Sit')]:
 arm.animation_data.action=bpy.data.actions[action];S.frame_set(frame);render(name,(-2.4,-3.4,1.7),scale=1.43)
arm.animation_data.action=bpy.data.actions['ANIM_Walk'];os.makedirs(R+'/Previews/WalkFrames',exist_ok=True);aim((-2.4,-3.4,1.8),scale=1.44)
S.render.resolution_x=512;S.render.resolution_y=512
for f in range(1,25):S.frame_set(f);S.render.filepath=R+'/Previews/WalkFrames/frame_%03d.png'%f;bpy.ops.render.render(write_still=True);print('WALK_FRAME',f,flush=True)
clear_pose();print('ALL_PREVIEWS_COMPLETE',flush=True)
