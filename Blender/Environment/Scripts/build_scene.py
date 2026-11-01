import bpy, math, random, os, json
import numpy as np
from mathutils import Vector
from math import sin, cos, pi

ROOT='/Users/pranay/Documents/Codex/2026-10-22/new-chat-6/outputs'
KIT=ROOT+'/doro-unity'
random.seed(27)
S=bpy.context.scene
bpy.ops.wm.save_as_mainfile(filepath=ROOT+'/doro-style-before-environment.blend',copy=True)
for o in list(bpy.data.objects): bpy.data.objects.remove(o,do_unlink=True)
for c in list(bpy.data.collections):
    if c.name!='Collection' and c.users==0: bpy.data.collections.remove(c)
S.name='Doro | Painted Coffee Crossroads'
COL={}
for name in ['01_Cafe','02_Terrace','03_Trees','04_Street','05_Neighbours','06_Characters','07_CameraRig','08_FocusProxies']:
    c=bpy.data.collections.get(name) or bpy.data.collections.new(name)
    if c.name not in S.collection.children: S.collection.children.link(c)
    COL[name]=c
CURRENT='01_Cafe'

def move(o):
    for c in list(o.users_collection): c.objects.unlink(o)
    COL[CURRENT].objects.link(o)
    return o

PALETTE=['e6d7b6','faf0d6','baaa90','656a6b','eee9d6','9b693e','c28e51','48352a',
 '318157','fbf2d9','e4b55f','3c5756','2e3b39','386334','759e3c','a5c554',
 'c6d773','315a34','8db443','795538','e5af7f','263136','496b82','ecc546',
 '619bb7','d2735d','b84e42','5289b4','d5b347','397555','88877d','6a4733',
 'dc945c','768776','567847','d7c9ae','8a9b7b','b69c6d','c9c1ad','c9b195',
 'ebe0c4','424b4a','e3a94f','6b8f9e','b5876c','b8c79a','da9074','f6df9f',
 '7d5439','ba7657','939774','b9b46b','dbe0bd','4b8458','adbfa2','eaebe0',
 'c98c43','9bb77d','729663','d7b691','546e60','7c8d93','f3d57f','36524a']

# Every mesh uses this painted atlas. UV islands remain portable to Unity.
N=2048; T=N//8
rng=np.random.default_rng(27)
pix=np.ones((N,N,4),dtype=np.float32)
for tile,h in enumerate(PALETTE):
    base=np.array([int(h[i:i+2],16)/255 for i in (0,2,4)],dtype=np.float32)
    a=np.empty((T,T,3),dtype=np.float32); a[:]=base
    for j in range(95):
        cx,cy=rng.integers(0,T,2); rx=int(rng.integers(5,45)); ry=int(rng.integers(1,8))
        x0=max(0,cx-rx);x1=min(T,cx+rx+1);y0=max(0,cy-ry);y1=min(T,cy+ry+1)
        yy,xx=np.mgrid[y0:y1,x0:x1]
        mask=np.clip(1-((xx-cx)/rx)**2-((yy-cy)/ry)**2,0,1)*rng.uniform(.12,.5)
        dry=(rng.random(mask.shape)>.18).astype(np.float32)
        color=np.clip(base+rng.uniform(-.09,.09),.015,1)
        a[y0:y1,x0:x1]=a[y0:y1,x0:x1]*(1-mask[...,None]*dry[...,None])+color*mask[...,None]*dry[...,None]
    a+=rng.normal(0,.008,(T,T,1))
    row,col=divmod(tile,8);pix[row*T:(row+1)*T,col*T:(col+1)*T,:3]=np.clip(a,0,1)
image=bpy.data.images.new('Doro_Painted_Atlas_2K',width=N,height=N,alpha=True)
image.pixels.foreach_set(pix.ravel());image.filepath_raw=KIT+'/Textures/Doro_Painted_Atlas.png'
image.file_format='PNG';image.save();image.pack()
MAT=bpy.data.materials.new('Doro_Painted_Atlas');MAT.use_nodes=True
nodes=MAT.node_tree.nodes;bs=next(n for n in nodes if n.type=='BSDF_PRINCIPLED')
bs.inputs['Roughness'].default_value=.88
tex=nodes.new('ShaderNodeTexImage');tex.image=image
MAT.node_tree.links.new(tex.outputs['Color'],bs.inputs['Base Color'])
if 'Specular IOR Level' in bs.inputs:bs.inputs['Specular IOR Level'].default_value=.2
WARM=bpy.data.materials.new('Doro_Warm_Window');WARM.use_nodes=True
wb=next(n for n in WARM.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
wb.inputs['Base Color'].default_value=(.85,.48,.11,1);wb.inputs['Roughness'].default_value=.65
if 'Emission Color' in wb.inputs:
    wb.inputs['Emission Color'].default_value=(1,.57,.19,1);wb.inputs['Emission Strength'].default_value=.28

def uv(o,tile):
    if o.type!='MESH': return
    o.data.materials.clear();o.data.materials.append(MAT)
    layer=o.data.uv_layers.active or o.data.uv_layers.new(name='PaintedUV')
    col=tile%8;row=tile//8
    if len(o.data.uv_layers)==0:return
    # Surface-local mapping on meshes without useful primitive UVs.
    for p in o.data.polygons:
        n=p.normal;axis=max(range(3),key=lambda i:abs(n[i]));axes=[i for i in range(3) if i!=axis]
        coords=[o.data.vertices[o.data.loops[k].vertex_index].co for k in p.loop_indices]
        for k,co in zip(p.loop_indices,coords):
            u=float(co[axes[0]]*.53)%1;v=float(co[axes[1]]*.53)%1
            # Planar mesh coordinates can collapse on tiny faces; retain generated UV when available.
            old=layer.data[k].uv
            if abs(old.x)+abs(old.y)>1e-5:u,v=old.x%1,old.y%1
            layer.data[k].uv=((col+.025+u*.95)/8,(row+.025+v*.95)/8)

def box(name,loc,size,tile,bevel=.025,rotation=0):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc)
    o=move(bpy.context.object);o.name=name;o.dimensions=size
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    uv(o,tile);o.rotation_euler.z=rotation
    if bevel:
        b=o.modifiers.new('Soft crafted edges','BEVEL');b.width=bevel;b.segments=2
    return o

def sphere(name,loc,scale,tile,segments=12,rings=8):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=segments,ring_count=rings,radius=1,location=loc)
    o=move(bpy.context.object);o.name=name;o.scale=scale;uv(o,tile)
    for p in o.data.polygons:p.use_smooth=True
    return o

def cyl(name,loc,radius,depth,tile,verts=12):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts,radius=radius,depth=depth,location=loc)
    o=move(bpy.context.object);o.name=name;uv(o,tile);return o

def rod(name,a,b,r,tile,verts=8):
    a,b=Vector(a),Vector(b);o=cyl(name,(a+b)/2,r,(b-a).length,tile,verts)
    o.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler();return o

def mesh(name,verts,faces,tile):
    m=bpy.data.meshes.new(name);m.from_pydata(verts,[],faces);m.update()
    o=bpy.data.objects.new(name,m);COL[CURRENT].objects.link(o);uv(o,tile);return o

def text(name,body,loc,size,tile,rotation=(pi/2,0,0)):
    c=bpy.data.curves.new(name,'FONT');c.body=body;c.size=size;c.align_x='CENTER';c.extrude=.004;c.bevel_depth=.001
    o=bpy.data.objects.new(name,c);COL[CURRENT].objects.link(o);o.location=loc;o.rotation_euler=rotation
    bpy.context.view_layer.objects.active=o;o.select_set(True)
    bpy.ops.object.convert(target='MESH');o=bpy.context.object;uv(o,tile);o.select_set(False);return o

def empty(name,loc):
    o=bpy.data.objects.new(name,None);COL[CURRENT].objects.link(o);o.location=loc;o.empty_display_size=.4
    return o

# A single plus-shaped road: exactly one intersection, with the cafe at its northwest corner.
CURRENT='04_Street'
box('Diorama foundation',(0,0,-.5),(37,33,.75),35,.3)
box('North south road',(7.6,0,-.035),(5.8,33,.16),3,.04)
box('East west road',(0,-7.1,-.027),(37,5.8,.16),3,.04)
for x in [-12,-6,0,13,17]: box('Lane dash EW',(x,-7.1,.064),(1.3,.10,.012),4,.015)
for y in [-13,0,6,11,15]: box('Lane dash NS',(7.6,y,.064),(.10,1.3,.012),4,.015)
for y in [-3.4,-10.8]:
    for x in np.arange(5.25,10.1,.65):box('Pedestrian crossing NS',(float(x),y,.067),(.37,1.7,.015),4,.01)
for x in [3.8,11.4]:
    for y in np.arange(-9.45,-4.7,.65):box('Pedestrian crossing EW',(x,float(y),.069),(1.7,.37,.015),4,.01)
box('Cafe raised sidewalk',(-2.6,3.9,.08),(14.1,16.7,.28),2,.14)
box('Other sidewalk east',(14.7,3.9,.08),(6.5,16.7,.28),2,.14)
box('South sidewalk',(-2.6,-13,.08),(14.1,5.9,.28),2,.14)
box('Southeast sidewalk',(14.7,-13,.08),(6.5,5.9,.28),2,.14)
# Tile grid, subtle rather than heavy black outlines.
for i in range(-9,5):
    for j in range(-4,12):
        box('Sandstone paving',(i+.5,j+.5,.238),(.977,.977,.034),random.choice([0,35,38,40]),.007)
for x,y,w,d in [(-2.5,-4.37,14,.12),(4.38,3.5,.12,16),(-9.62,3.5,.12,16)]:
    box('Ivory kerbstone',(x,y,.25),(w,d,.22),1,.025)

# Two-storey cafe. Front faces negative Y; all four sides are modelled.
CURRENT='01_Cafe'
box('Cafe cream stucco shell',(-.8,2.0,3.25),(6.3,5.8,6.0),0,.045)
box('Foundation plinth',(-.8,2.0,.45),(6.55,6.05,.38),2,.04)
box('Upper floor stringcourse',(-.8,2.0,3.5),(6.5,6.0,.16),1,.022)
box('Roof slab',(-.8,2.0,6.30),(6.65,6.15,.20),1,.04)
box('Flat roof charcoal',(-.8,2.0,6.43),(6.2,5.75,.07),30,.025)
for x in [-4.02,2.42]:box('Roof parapet side',(x,2.,6.62),(.18,6.15,.5),1,.025)
for y in [-1.0,5.0]:box('Roof parapet edge',(-.8,y,6.62),(6.6,.18,.5),1,.025)
for x,y,sz in [(-2.8,3.7,1.1),(-.4,3.4,.92),(-2.5,1.8,.6)]:
    box('Rooftop air conditioning',(x,y,6.95),(sz,sz,.8),38,.045)
    for z in [6.72,6.86,7.0,7.14]:box('AC louvre',(x,y-sz/2-.012,z),(sz*.8,.025,.026),41,.003)
for x in [-3.9,-1.75,.4,2.3]:
    box('Timber front upright',(x,-.971,1.75),(.13,.15,2.9),7,.012)
for x,w in [(-2.8,1.9),(-.65,1.95),(1.4,1.7)]:
    panel=box('Warm cafe glazing',(x,-.94,1.9),(w,.075,2.4),10,.015)
    panel.data.materials.clear();panel.data.materials.append(WARM)
    box('Window sill',(x,-1.05,.72),(w+.12,.24,.15),5,.018)
    box('Window glazing bar',(x,-1.05,1.9),(.045,.045,2.35),7,.004)
    box('Window transom',(x,-1.05,2.43),(w,.055,.055),7,.004)
    # Interior silhouettes visible through illustrated amber glazing.
    box('Interior shelf',(x,-1.012,1.23),(w*.85,.06,.06),5,.006)
    for k in range(4):
        cyl('Coffee cup silhouette',(x-w*.32+k*w*.2,-1.07,1.36),.07,.15,1,10).rotation_euler.x=pi/2
    rod('Hanging lamp stem',(x,-1.08,3.05),(x,-1.08,2.7),.015,12)
    bpy.ops.mesh.primitive_cone_add(vertices=16,radius1=.22,radius2=.08,depth=.17,location=(x,-1.1,2.61))
    o=move(bpy.context.object);o.name='Interior pendant shade';uv(o,42)
for x in [-2.7,.1]:
    box('Upper front window dark surround',(x,-.985,4.85),(1.9,.10,1.48),7,.015)
    box('Upper front window ochre',(x,-1.045,4.85),(1.74,.035,1.32),10,.01)
    box('Upper front window mullion',(x,-1.075,4.85),(.055,.035,1.35),5,.004)
    box('Upper front window transom',(x,-1.075,4.80),(1.75,.035,.055),5,.004)
for y in [.3,2.2,4.1]:
    for z in [1.9,4.8]:
        box('Side window timber',(2.39,y,z),(.10,1.45,1.4),7,.015)
        box('Side window amber',(2.45,y,z),(.035,1.29,1.24),10,.01)
        box('Side mullion',(2.48,y,z),(.035,.05,1.25),5,.004)
for y in [.5,3.5]:
    box('Rear upper window',(-.9,4.93,4.9),(1.65,.07,1.3),7,.01)
box('Rear service door',(-2.7,4.96,1.55),(1.0,.08,2.4),5,.01)
box('COFFEE sign timber frame',(-.8,-1.14,4.0),(5.45,.22,1.13),7,.035)
box('COFFEE sign painted wood',(-.8,-1.27,4.0),(5.25,.055,.97),5,.015)
text('COFFEE lettering','COFFEE',(-.40,-1.32,3.77),.65,1)
# Ceramic cup logo, with a real curved handle.
cyl('Cafe cup logo',(-2.65,-1.37,3.99),.21,.40,1,24).rotation_euler.x=pi/2
rod('Logo cup base',(-2.9,-1.40,3.75),(-2.4,-1.40,3.75),.025,1)
bpy.ops.mesh.primitive_torus_add(major_radius=.17,minor_radius=.035,major_segments=16,minor_segments=6,location=(-2.38,-1.37,4.02),rotation=(pi/2,0,0))
o=move(bpy.context.object);o.name='Cup handle logo';uv(o,1)
# Curved awning strips, scalloped front valance.
for i in range(14):
    x0=-4.0+i*6.4/14;x1=x0+6.4/14
    verts=[]
    for x in [x0,x1]:
        for j in range(7):
            t=j/6;verts.append((x,-1.02-1.65*t,3.34-.70*t+.15*sin(t*pi)))
    faces=[(j,j+1,7+j+1,7+j) for j in range(6)]
    mesh('Awning woven stripe',verts,faces,8 if i%2==0 else 9)
    verts=[(x0,-2.68,2.67),(x1,-2.68,2.67)]
    for j in range(8):
        t=j/7;verts.append((x1-(x1-x0)*t,-2.68,2.48-.16*sin(t*pi)))
    mesh('Scalloped canvas valance',verts,[tuple(range(len(verts)))],8 if i%2==0 else 9)
rod('Awning timber rail',(-4.05,-2.7,2.67),(2.45,-2.7,2.67),.035,5)
for x in [-3.85,2.25]:rod('Awning support',(x,-1.06,3.25),(x,-2.64,2.65),.025,12)
print('DORO_STAGE_1_OK',len(S.objects))
bpy.ops.wm.save_as_mainfile(filepath=ROOT+'/doro-style.blend')
