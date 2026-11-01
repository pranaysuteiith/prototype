import bpy,json
from mathutils import Vector
R='/Users/pranay/My project/Characters/Boy_GreenSweater';S=bpy.context.scene
for lib in bpy.data.libraries:
 if lib.filepath.endswith('/Boy_GreenSweater.blend'):lib.filepath='//Boy_GreenSweater.blend'
bpy.ops.wm.save_as_mainfile(filepath=R+'/Blender/Cafe_With_Boy_GreenSweater.blend')
# Preview camera exists only in this rendering process, after saving the reusable café copy.
cam=bpy.data.objects.new('Character placement preview',bpy.data.cameras.new('Character placement preview'));S.collection.objects.link(cam);S.camera=cam;cam.location=(-8,-11,6.3);cam.rotation_euler=(Vector((-3.2,-2.9,1.25))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=6.5
try:S.render.engine='BLENDER_EEVEE'
except TypeError:pass
S.render.resolution_x=1100;S.render.resolution_y=900;S.render.resolution_percentage=100;S.render.image_settings.file_format='PNG';S.render.filepath=R+'/Previews/Cafe_Instance.png';bpy.ops.render.render(write_still=True)
print('CAFE_PREVIEW_COMPLETE')
