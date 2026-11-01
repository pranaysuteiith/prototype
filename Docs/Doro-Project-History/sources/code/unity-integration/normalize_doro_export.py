import bpy,os,json,math
from collections import defaultdict
from mathutils import Vector
S=bpy.context.scene
KIT='/Users/pranay/My project/Assets/DoroPainted'
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
        # Joining different UV names creates empty channels for portions of the mesh.
        # Consolidate each source object's render UV into a single consistently named layer.
        active = m.uv_layers.active
        if active:
            values = [tuple(d.uv) for d in active.data]
            for layer in list(m.uv_layers): m.uv_layers.remove(layer)
            layer = m.uv_layers.new(name='DoroPaintedUV')
            for d,uv in zip(layer.data,values): d.uv=uv
            layer.active_render=True
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
    print('DORO_NORMALIZED_EXPORT', len(created))
finally:
    pass
