import bpy,math,json
from mathutils import Quaternion,Vector
from math import sin,cos,pi
BASE='/Users/pranay/Documents/Codex/2026-10-22/new-chat-6';OUT=BASE+'/outputs/Characters/CH_Female_v001'
rig=bpy.data.objects['CH_Rig'];studio=bpy.data.scenes['CH_Character_Preview_Studio']
def reset():
    for p in rig.pose.bones:p.rotation_quaternion=Quaternion((1,0,0,0));p.location=(0,0,0);p.scale=(1,1,1)
def rest_world_rotation(name,q):
    p=rig.pose.bones[name];r=p.bone.matrix_local.to_quaternion();p.rotation_quaternion=r.inverted()@q@r
def idle_pose(breath=0):
    reset()
    for side,s in [(1,'L'),(-1,'R')]:
        rest_world_rotation('UpperArm.'+s,Quaternion((0,1,0),side*math.radians(82)))
        rig.pose.bones['Forearm.'+s].rotation_quaternion=Quaternion((0,0,1),-side*math.radians(8))
        for name in ['Index','Middle','Ring','Little']:
            for n,amount in [('01',.12),('02',.16)]:
                p=rig.pose.bones[name+'.'+n+'.'+s];r=p.bone.matrix_local.to_quaternion()
                p.rotation_quaternion=r.inverted()@Quaternion((0,1,0),side*amount)@r
    rig.pose.bones['Chest'].rotation_quaternion=Quaternion((1,0,0),math.radians(.45)*breath)
    rig.pose.bones['Head'].rotation_quaternion=Quaternion((0,1,0),math.radians(1.2)*breath)
    rig.pose.bones['Pelvis'].location.y=.003*breath
def key(frame):
    for p in rig.pose.bones:
        p.keyframe_insert(data_path='rotation_quaternion',frame=frame,group=p.name)
        if p.name in ['Root','Pelvis']:p.keyframe_insert(data_path='location',frame=frame,group=p.name)
def action(name,start,end,cyclic=False):
    if bpy.data.actions.get(name):raise RuntimeError('Action already exists: '+name)
    a=bpy.data.actions.new(name);a.use_fake_user=True;a.use_frame_range=True;a.frame_start=start;a.frame_end=end;a.use_cyclic=cyclic
    rig.animation_data_create();rig.animation_data.action=a;return a
idle=action('CH_Idle',1,61,True)
for frame in [1,11,21,31,41,51,61]:idle_pose(sin((frame-1)/60*2*pi));key(frame)
walk=action('CH_Walk',1,25,True)
for frame in range(1,26,2):
    phase=(frame-1)/24*2*pi;wave=sin(phase);idle_pose(0)
    for side,s in [(1,'L'),(-1,'R')]:
        pitch=-side*.29*wave;knee=max(0,-side*wave)*.42
        rest_world_rotation('Thigh.'+s,Quaternion((1,0,0),pitch))
        rest_world_rotation('Shin.'+s,Quaternion((1,0,0),knee))
        rest_world_rotation('Foot.'+s,Quaternion((1,0,0),-pitch-knee))
        q=Quaternion((1,0,0),side*.22*wave)@Quaternion((0,1,0),side*math.radians(82))
        rest_world_rotation('UpperArm.'+s,q)
    rig.pose.bones['Pelvis'].location.y=-.018*wave*wave
    rig.pose.bones['Spine'].rotation_quaternion=Quaternion((0,1,0),.025*wave)
    key(frame)
waveAction=action('CH_Wave',1,73,False)
for frame in [1,9,17,25,31,37,43,49,57,65,73]:
    idle_pose(0)
    ramp=max(0,min(1,(frame-1)/20,(73-frame)/18));ramp=ramp*ramp*(3-2*ramp)
    # Right arm rises beside the head; forearm and wrist remain independently articulated.
    angle=math.radians(-82+147*ramp)
    rest_world_rotation('UpperArm.R',Quaternion((0,1,0),angle))
    rig.pose.bones['Forearm.R'].rotation_quaternion=Quaternion((0,0,1),math.radians(8)*(1-ramp)+.48*ramp)
    wrist=.30*sin((frame-25)/12*2*pi)*ramp
    rig.pose.bones['Hand.R'].rotation_quaternion=Quaternion((0,1,0),pi/2*ramp)@Quaternion((1,0,0),wrist)
    for name in ['Index','Middle','Ring','Little','Thumb']:
        for n in ['01','02']:rig.pose.bones[name+'.'+n+'.R'].rotation_quaternion=Quaternion((1,0,0,0))
    rig.pose.bones['Head'].rotation_quaternion=Quaternion((0,1,0),-.035*ramp)
    key(frame)
for a in [idle,walk,waveAction]:
    for layer in a.layers:
        for strip in layer.strips:
            for bag in strip.channelbags:
                for fc in bag.fcurves:
                    for k in fc.keyframe_points:k.interpolation='BEZIER' if a==idle else 'LINEAR'
rig.animation_data.action=idle
studio.frame_set(1);bpy.context.scene.frame_set(1)
rig['Actions']='CH_Idle (1-61), CH_Walk (1-25, in place), CH_Wave (1-73). Source rest pose remains T-pose.'
# Idle front and a clear right-handed wave for deformation inspection.
camera=studio.camera;target=rig.matrix_world@Vector((0,0,.98))
for name,act,frame,pos in [('CH_Idle_Front',idle,1,(0,-5,1.0)),('CH_Wave_Front',waveAction,31,(0,-5,1.0)),('CH_Walk_Isometric',walk,7,(3,-5,2.5))]:
    rig.animation_data.action=act;studio.frame_set(frame)
    camera.location=rig.matrix_world@Vector(pos);camera.rotation_euler=(target-camera.location).to_track_quat('-Z','Y').to_euler()
    studio.render.filepath=OUT+'/'+name+'.png';bpy.ops.render.render(write_still=True,scene=studio.name)
rig.animation_data.action=idle;studio.frame_set(1);bpy.context.scene.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
print(json.dumps({'actions':[{'name':a.name,'range':list(a.frame_range),'slots':len(a.slots)} for a in [idle,walk,waveAction]],'rest_pose':rig.data.pose_position,'current_action':rig.animation_data.action.name}))
