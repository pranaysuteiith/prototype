import bpy,numpy as np,math,random,ast
from mathutils import Vector
from math import pi,sin,cos
ROOT='/Users/pranay/Documents/Codex/2026-10-22/new-chat-6/outputs';KIT=ROOT+'/doro-unity';S=bpy.context.scene
atlas=bpy.data.images['Doro_Painted_Atlas_2K'];px=np.array(atlas.pixels[:],dtype=np.float32).reshape(2048,2048,4)
leafmats={}
for tile in [13,14,15,16,17,18]:
    row,col=divmod(tile,8);crop=px[row*256:(row+1)*256,col*256:(col+1)*256].copy()
    # Isolated swatches prevent tiny leaves from sampling pale adjacent atlas tiles in mipmaps.
    im=bpy.data.images.new('Doro_Gouache_Leaf_'+str(tile),width=256,height=256,alpha=True)
    im.pixels.foreach_set(crop.ravel());im.filepath_raw=KIT+'/Textures/'+im.name+'.png';im.file_format='PNG';im.save();im.pack()
    mat=bpy.data.materials.new('Doro_Leaf_'+str(tile));mat.use_nodes=True
    bs=next(n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED');bs.inputs['Roughness'].default_value=1
    if 'Specular IOR Level' in bs.inputs:bs.inputs['Specular IOR Level'].default_value=0
    tex=mat.node_tree.nodes.new('ShaderNodeTexImage');tex.image=im;mat.node_tree.links.new(tex.outputs['Color'],bs.inputs['Base Color'])
    leafmats[tile]=mat
count=0
for o in list(S.objects):
    if o.type!='MESH' or not o.data.uv_layers:continue
    if any(s in o.name for s in ['gouache leaf dabs','brush foliage','ivy brush dabs','Trailing ivy','Side roof ivy']):
        old=o.data;layer=old.uv_layers.active;verts=[];faces=[];indices=[]
        for k in range(0,len(old.vertices),5):
            if k+4>=len(old.vertices):break
            a,b,c,d,p=[old.vertices[k+j].co.copy() for j in range(5)]
            center=(a+b+c+d)/4;u=(c-a)*.31;v=(b-d)*.31
            tileUV=layer.data[(k//5)*12].uv
            tile=int(tileUV.x*8)+8*int(tileUV.y*8)
            tile=tile if tile in leafmats else 14
            if 'ivy' in o.name.lower():tile=random.choice([13,14,14,15,17])
            ix=len(verts)
            for j in range(8):
                theta=j*math.tau/8;verts.append(center+u*math.cos(theta)+v*math.sin(theta))
            verts.append(p)
            for j in range(8):faces.append((ix+j,ix+(j+1)%8,ix+8));indices.append(list(leafmats).index(tile))
        m=bpy.data.meshes.new(o.name+'_rounded_leaf_mesh');m.from_pydata(verts,[],faces);m.update()
        for mat in leafmats.values():m.materials.append(mat)
        ul=m.uv_layers.new(name='PaintedUV')
        for p,mi in zip(m.polygons,indices):
            p.material_index=mi
            for idx,xy in zip(p.loop_indices,[(.1,.1),(.9,.1),(.5,.9)]):ul.data[idx].uv=xy
        o.data=m;count+=1
    elif 'foliage underpainting' in o.name or 'painted mass' in o.name:
        o.data.materials.clear();o.data.materials.append(leafmats[14 if 'underpainting' in o.name else 17])
        for p in o.data.polygons:
            for k in p.loop_indices:
                xy=o.data.uv_layers.active.data[k].uv
                xy.x=(xy.x*8)%1;xy.y=(xy.y*8)%1
# Reuse modelling helpers to add a little timber and painted detail to glazing.
COL={c.name:c for c in bpy.data.collections};CURRENT='01_Cafe';MAT=bpy.data.materials['Doro_Painted_Atlas']
source=ast.parse(open(ROOT+'/../work/doro-build/build_scene.py').read())
exec(compile(ast.Module(body=[n for n in source.body if isinstance(n,ast.FunctionDef)],type_ignores=[]),'helpers','exec'))
for x in [-2.7,.1]:
    for z in [4.3,5.3]:box('Upper window internal sill',(x,-1.09,z),(1.69,.04,.045),6,.005)
    for xx in [x-.65,x+.62]:box('Upper window curtain edge',(xx,-1.095,4.86),(.16,.03,1.24),40,.005)
    rod('Illustrated window glint',(x-.48,-1.115,5.22),(x-.2,-1.115,4.9),.018,47)
for x in [-3.2,-2.4,-1.0,.2,1.4]:
    box('Cafe counter display',(x,-1.10,.98),(.57,.045,.34),5,.01)
    sphere('Pastry in window',(x,-1.14,1.23),(.16,.06,.09),56)
# Focus preview. A deliberately wide virtual aperture gives the tiny diorama effect at metre scale.
S.camera.data.dof.aperture_fstop=.72
S.camera.data.lens=60
S.render.resolution_percentage=75
S.view_settings.exposure=.05
bpy.ops.wm.save_as_mainfile(filepath=ROOT+'/doro-style.blend')
bpy.ops.render.render(write_still=True)
print('DORO_REFINED',count,'foliage meshes')
