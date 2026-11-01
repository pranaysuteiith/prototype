import bpy,os,json,math
from collections import defaultdict
from mathutils import Vector
ROOT='/Users/pranay/Documents/Codex/2026-10-22/new-chat-6/outputs';KIT=ROOT+'/doro-unity';S=bpy.context.scene
# Bring the parasol into the visible cafe terrace.
for o in S.objects:
    if any(s in o.name for s in ['Umbrella wooden pole','Ivory parasol fabric','Parasol seam','Parasol finial']):o.location+=Vector((.6,-2.7,0))
S.camera.data.dof.aperture_fstop=.045
S.camera['Preview aperture note']='Art-directed f/0.045 to simulate a small miniature at full-size game units. Unity Bokeh settings are independent.'
S.render.filepath=ROOT+'/doro-style-preview.png'
bpy.ops.wm.save_as_mainfile(filepath=ROOT+'/doro-style.blend')
bpy.ops.render.render(write_still=True)
# Keep a clear, unblurred view for modelling inspection.
S.camera.data.dof.use_dof=False;S.render.filepath=ROOT+'/doro-style-sharp.png'
bpy.ops.render.render(write_still=True)
S.camera.data.dof.use_dof=True;S.render.filepath=ROOT+'/doro-style-preview.png'

# Batch the export while keeping original objects editable in the .blend.
originals=[o for o in S.objects if o.type=='MESH']
old_selection=list(bpy.context.selected_objects);old_active=bpy.context.view_layer.objects.active
temp=bpy.data.collections.new('99_Temporary_Unity_Export');S.collection.children.link(temp)
dg=bpy.context.evaluated_depsgraph_get();groups=defaultdict(list)
tree_names=['Lime tree west','Lime tree terrace','Lime tree east','Background tree west','Background tree east','Foreground tree','Far tree']
neighbours=['Bakery west','Bookshop east','Townhouse back','Foreground atelier','South east shop']
def group_for(o):
    root=o
    while root.parent:root=root.parent
    if root!=o:return root.name
    cols=[c.name for c in o.users_collection]
    if '01_Cafe' in cols:return 'Cafe'
    if '02_Terrace' in cols:return 'Terrace'
    if '03_Trees' in cols:
        for name in tree_names:
            if o.name.startswith(name):return name
        return 'Ivy_and_Garden'
    if '04_Street' in cols:return 'Roads_and_Street'
    if '05_Neighbours' in cols:
        for name in neighbours:
            if o.name.startswith(name):return name
    return 'Miscellaneous'
created=[]
try:
    for o in originals:
        ev=o.evaluated_get(dg)
        m=bpy.data.meshes.new_from_object(ev,preserve_all_data_layers=True,depsgraph=dg)
        copy=bpy.data.objects.new('ExportCopy',m);temp.objects.link(copy);copy.matrix_world=o.matrix_world.copy()
        groups[group_for(o)].append(copy)
    bpy.ops.object.select_all(action='DESELECT')
    for name,objects in groups.items():
        for o in objects:o.select_set(True)
        bpy.context.view_layer.objects.active=objects[0]
        if len(objects)>1:bpy.ops.object.join()
        joined=bpy.context.view_layer.objects.active;joined.name='GEO_'+name.replace(' ','_')
        created.append(joined);joined.select_set(False)
    for o in created:o.select_set(True)
    bpy.context.view_layer.objects.active=created[0]
    path=KIT+'/Models/DoroCrossroads.fbx'
    result=bpy.ops.export_scene.fbx(filepath=path,use_selection=True,object_types={'MESH'},axis_forward='-Z',axis_up='Y',apply_unit_scale=True,apply_scale_options='FBX_SCALE_UNITS',bake_anim=False,path_mode='RELATIVE',use_mesh_modifiers=True)
    tris=0
    for o in created:o.data.calc_loop_triangles();tris+=len(o.data.loop_triangles)
    report={'name':'Doro Painted Coffee Crossroads','source_mesh_objects':len(originals),'export_mesh_objects':len(created),'export_triangles':tris,'export_bytes':os.path.getsize(path),'fbx_result':list(result),'road_intersections':1,'unit_scale_m':S.unit_settings.scale_length,'camera_blender':list(S.camera.location),'camera_target_blender':[-1.1,.2,2.2],'camera_lens_mm':S.camera.data.lens,'navigation':'WASD/arrows; middle/right drag; scroll; touch drag and pinch (Input System)','focus':'Center-screen raycast against simplified focus colliders; exponential smoothing; ground-plane fallback.','textures':'Painted atlas plus isolated foliage swatches; all packed into .blend and included as PNGs.'}
    with open(KIT+'/scene-manifest.json','w') as f:json.dump(report,f,indent=2)
    print(json.dumps(report))
finally:
    for o in list(temp.objects):
        mesh=o.data;bpy.data.objects.remove(o,do_unlink=True)
        if mesh.users==0:bpy.data.meshes.remove(mesh)
    bpy.data.collections.remove(temp)
    bpy.ops.object.select_all(action='DESELECT')
    for o in old_selection:
        if o.name in S.objects:o.select_set(True)
    if old_active and old_active.name in S.objects:bpy.context.view_layer.objects.active=old_active
bpy.ops.wm.save_as_mainfile(filepath=ROOT+'/doro-style.blend')
print('DORO_EXPORT_READY')
