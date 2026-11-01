import bpy,math,os,json
from mathutils import Vector
ROOT='/Users/pranay/Documents/Codex/2026-10-22/new-chat-6/outputs'
S=bpy.context.scene
c=bpy.data.collections['07_CameraRig']
def marker(name,loc):
    o=bpy.data.objects.new(name,None);c.objects.link(o);o.location=loc;o.empty_display_size=.4;return o
pivot=marker('Camera_Pan_Pivot',(-1.1,.0,1.8))
focus=marker('Focus_Target_Center',(-.8,-.2,2.5))
focus['Unity_behavior']='Center-screen raycast; smooth camera-forward depth; update after zoom/pan.'
data=bpy.data.cameras.new('Miniature Perspective 60mm');cam=bpy.data.objects.new('Doro_Game_Camera',data);c.objects.link(cam)
cam.location=(26,-34,29);cam.rotation_euler=(Vector((-1.1,.2,2.2))-cam.location).to_track_quat('-Z','Y').to_euler()
data.type=next(e.identifier for e in data.bl_rna.properties['type'].enum_items if e.identifier=='PERSP')
data.lens=57;data.clip_end=250;data.dof.use_dof=True;data.dof.focus_object=focus;data.dof.aperture_fstop=3.2
S.camera=cam
cam['Unity_start_position']='26,29,34 (Unity Y-up coordinates, negative Blender Y)'
cam['Zoom_limits_m']='18 to 65; dolly distance, keep lens fixed for a stable miniature look'
cam['Preview_note']='Blender focus-object preview. Unity runtime autofocus is supplied separately.'
# Bookmarks are compositional examples, not a locked camera track.
for name,loc in [('Focus_Cafe',(-.8,0,2.7)),('Focus_Terrace',(-5.6,1,1.25)),('Focus_Crossroad',(7.6,-7.1,.1)),('Focus_Tree',(-6,5.7,4.3))]:marker(name,loc)
light=bpy.data.lights.new('Large soft afternoon key','AREA');light.energy=2300;light.shape='DISK';light.size=12
o=bpy.data.objects.new('Large soft afternoon key',light);c.objects.link(o);o.location=(-8,-10,20);o.rotation_euler=(Vector((0,0,0))-o.location).to_track_quat('-Z','Y').to_euler()
light=bpy.data.lights.new('Soft sky fill','AREA');light.energy=1100;light.size=14
o=bpy.data.objects.new('Soft sky fill',light);c.objects.link(o);o.location=(10,8,17);o.rotation_euler=(Vector((0,0,0))-o.location).to_track_quat('-Z','Y').to_euler()
sun=bpy.data.lights.new('Warm afternoon sun','SUN');sun.energy=1.5;sun.angle=.18;sun.color=(1,.89,.71)
o=bpy.data.objects.new('Warm afternoon sun',sun);c.objects.link(o);o.rotation_euler=(.4,-.6,-.5)
S.world.use_nodes=True
world=next(n for n in S.world.node_tree.nodes if n.type=='BACKGROUND');world.inputs['Color'].default_value=(.67,.76,.85,1);world.inputs['Strength'].default_value=.65
S.render.resolution_x=1600;S.render.resolution_y=900;S.render.resolution_percentage=65
S.render.image_settings.file_format=next(e.identifier for e in S.render.image_settings.bl_rna.properties['file_format'].enum_items if e.identifier=='PNG')
S.render.filepath=ROOT+'/doro-style-preview.png'
try:S.view_settings.view_transform='AgX'
except:pass
try:S.view_settings.look='AgX - Medium High Contrast'
except:pass
S.view_settings.exposure=.25
S.render.film_transparent=False
if hasattr(S,'eevee'):
    if hasattr(S.eevee,'taa_render_samples'):S.eevee.taa_render_samples=32
for screen in bpy.data.screens:
    for a in screen.areas:
        if a.type=='VIEW_3D':
            a.spaces.active.region_3d.view_perspective='CAMERA'
            a.spaces.active.clip_end=300
            a.spaces.active.shading.type='MATERIAL'
S['Reference']='Tilt-Shift City Coffee Corner(1).png'
S['Style']='Cream stucco, green striped awning, amber windows, timber, layered gouache leaf geometry and a painted atlas.'
S['Layout']='Single crossroads: road X=7.6, road Y=-7.1. Cafe northwest of intersection.'
S['Unity_pipeline']='URP, perspective camera, depth texture, Volume Bokeh DOF. Import textures; Blender node graphs do not transfer.'
S['Units']='One Blender unit = one metre; Z-up source, Y-up Unity export.'
bpy.ops.wm.save_as_mainfile(filepath=ROOT+'/doro-style.blend')
bpy.ops.render.render(write_still=True)
print('DORO_PREVIEW_READY',S.render.filepath)
