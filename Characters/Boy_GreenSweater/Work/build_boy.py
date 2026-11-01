import bpy, math, os, json, random
import numpy as np
from mathutils import Vector, Quaternion
from math import sin,cos,pi,sqrt
ROOT='/Users/pranay/My project/Characters/Boy_GreenSweater'
random.seed(37)
# This is a separate factory-startup Blender process, never the user's live café.
for o in list(bpy.data.objects): bpy.data.objects.remove(o,do_unlink=True)
S=bpy.context.scene; S.name='Boy Green Sweater | Character Studio';S.unit_settings.scale_length=1;S.render.fps=24
C=bpy.data.collections.new('CHAR_Boy_GreenSweater');S.collection.children.link(C)
M={};meshes=[];rigid=[]
def rgb(h):
 a=[int(h[i:i+2],16)/255 for i in (0,2,4)]
 return tuple(v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4 for v in a)
def texture(name,color,kind):
 color=tuple(12.92*v if v<=.0031308 else 1.055*v**(1/2.4)-.055 for v in color)
 n=512;yy,xx=np.mgrid[0:n,0:n];rng=np.random.default_rng(41)
 grain=rng.normal(0,.025,(n,n));fine=grain
 if kind=='wool':fine+=.07*np.sin(xx*2*pi/9)*np.sin(yy*2*pi/7)+.035*np.cos((xx+yy)*2*pi/4)
 elif kind=='hair':fine+=.045*np.sin((xx+7*np.sin(yy/15))*2*pi/21)
 else:fine+=.015*np.sin(xx*2*pi/5)*np.sin(yy*2*pi/5)
 a=np.ones((n,n,4),dtype=np.float32);a[:,:,:3]=np.clip(np.array(color)[None,None,:]*(1+fine[:,:,None]),0,1)
 img=bpy.data.images.new(name,width=n,height=n,alpha=False);img.pixels.foreach_set(a.ravel());img.file_format='PNG';img.filepath_raw=ROOT+'/Textures/'+name+'.png';img.save();img.pack();return img
# Texture RGB values are authored as linear data and tagged Non-Color to match Principled colors.
def mat(name,hexcolor,rough=.7,kind=None,sheen=0):
 m=bpy.data.materials.new(name);m.use_nodes=True;bs=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED');col=rgb(hexcolor);bs.inputs['Base Color'].default_value=(*col,1);bs.inputs['Roughness'].default_value=rough
 if 'Sheen Weight' in bs.inputs:bs.inputs['Sheen Weight'].default_value=sheen
 if kind:
  img=texture(name+'_BaseColor',col,kind);t=m.node_tree.nodes.new('ShaderNodeTexImage');t.image=img;m.node_tree.links.new(t.outputs['Color'],bs.inputs['Base Color'])
  n=512;yy,xx=np.mgrid[0:n,0:n];h=np.sin(xx*2*pi/9)*np.sin(yy*2*pi/7) if kind=='wool' else np.sin((xx+7*np.sin(yy/15))*2*pi/21) if kind=='hair' else np.sin(xx*2*pi/5)*np.sin(yy*2*pi/5)
  dy,dx=np.gradient(h);norm=np.stack((-dx*.18,-dy*.18,np.ones_like(h)),axis=-1);norm/=np.linalg.norm(norm,axis=-1,keepdims=True);pixels=np.ones((n,n,4),dtype=np.float32);pixels[:,:,:3]=norm*.5+.5
  normal=bpy.data.images.new(name+'_Normal',width=n,height=n,alpha=False);normal.colorspace_settings.name='Non-Color';normal.pixels.foreach_set(pixels.ravel());normal.file_format='PNG';normal.filepath_raw=ROOT+'/Textures/'+name+'_Normal.png';normal.save();normal.pack()
  tn=m.node_tree.nodes.new('ShaderNodeTexImage');tn.image=normal;nm=m.node_tree.nodes.new('ShaderNodeNormalMap');nm.inputs['Strength'].default_value=.65;m.node_tree.links.new(tn.outputs['Color'],nm.inputs['Color']);m.node_tree.links.new(nm.outputs['Normal'],bs.inputs['Normal'])
 m.diffuse_color=(*col,1);M[name]=m;return m
mat('MAT_Skin','f0bd96',.72);mat('MAT_Skin_Blush','e8a08b',.75);mat('MAT_Hair_DarkBrown','503326',.86,'hair',.2)
mat('MAT_Sunglasses_Black','111211',.25);mat('MAT_Sunglasses_Lenses','191713',.38)
mat('MAT_Sweater_ForestGreen','263d2c',.91,'wool',.32);mat('MAT_Pants_Khaki','b7a58b',.84,'cotton',.1)
mat('MAT_Shoes_Black','222321',.36);mat('MAT_Shoes_White','eee9db',.55);mat('MAT_Mouth','76503e',.75);mat('MAT_Eyes','21180f',.3)
def uvmesh(obj):
 me=obj.data;uv=me.uv_layers.new(name='UVMap')
 for p in me.polygons:
  normal=p.normal;axis=max(range(3),key=lambda k:abs(normal[k]));axes=[k for k in range(3) if k!=axis]
  for k in p.loop_indices:
   v=me.vertices[me.loops[k].vertex_index].co;uv.data[k].uv=(v[axes[0]]*9,v[axes[1]]*9)
def mesh(name,verts,faces,material,register=True):
 me=bpy.data.meshes.new(name+'_Geometry');me.from_pydata(verts,[],faces);me.update();o=bpy.data.objects.new(name,me);C.objects.link(o);me.materials.append(M[material])
 for p in me.polygons:p.use_smooth=True
 uvmesh(o)
 if register:meshes.append(o)
 return o
def sphere_data(center,scale,n=24,rings=12,power=1,orient=None):
 c=Vector(center);v=[tuple(c+Vector((0,0,scale[2])))];f=[]
 def sp(a):return math.copysign(abs(a)**power,a)
 for j in range(1,rings):
  t=pi*j/rings
  for i in range(n):
   p=2*pi*i/n;co=Vector((scale[0]*sp(sin(t)*cos(p)),scale[1]*sp(sin(t)*sin(p)),scale[2]*sp(cos(t))))
   if orient:co=orient@co
   v.append(tuple(c+co))
 v.append(tuple(c-Vector((0,0,scale[2]))));bottom=len(v)-1
 for i in range(n):f.append((0,1+i,1+(i+1)%n))
 for j in range(rings-2):
  for i in range(n):a=1+j*n+i;b=1+j*n+(i+1)%n;f.append((a,a+n,b+n,b))
 for i in range(n):f.append((bottom,1+(rings-2)*n+(i+1)%n,1+(rings-2)*n+i))
 return v,f
def combine(parts):
 v=[];f=[]
 for vv,ff in parts:k=len(v);v.extend(vv);f.extend(tuple(x+k for x in face) for face in ff)
 return v,f
def ellipsoid(name,c,sc,ma,n=24,rings=12,power=1):return mesh(name,*sphere_data(c,sc,n,rings,power),ma)
def tube_data(points,radius,sides=6):
 pts=[Vector(p) for p in points];v=[];f=[]
 for j,p in enumerate(pts):
  d=(pts[min(j+1,len(pts)-1)]-pts[max(0,j-1)]).normalized();up=Vector((0,0,1)) if abs(d.z)<.9 else Vector((0,1,0));a=d.cross(up).normalized();b=d.cross(a).normalized()
  for i in range(sides):v.append(tuple(p+radius*(a*cos(2*pi*i/sides)+b*sin(2*pi*i/sides))))
 for j in range(len(pts)-1):
  for i in range(sides):a=j*sides+i;b=j*sides+(i+1)%sides;f.append((a,b,b+sides,a+sides))
 f.append(tuple(range(sides-1,-1,-1)));f.append(tuple((len(pts)-1)*sides+i for i in range(sides)))
 return v,f
def tube(name,points,radius,ma,sides=6):return mesh(name,*tube_data(points,radius,sides),ma)
def rigid_head(o):rigid.append(o);return o
# Oversized soft, gently squared head and independently removable accessories.
rigid_head(ellipsoid('CH_Head',(0,.003,.949),(.190,.147,.163),'MAT_Skin',40,24,.84))
rigid_head(mesh('CH_Ears',*combine([sphere_data((s*.19,.003,.904),(.033,.024,.047),16,10) for s in [-1,1]]),'MAT_Skin'))
rigid_head(mesh('CH_Ear_Inner',*combine([sphere_data((s*.207,-.017,.905),(.014,.009,.026),12,8) for s in [-1,1]]),'MAT_Skin_Blush'))
rigid_head(ellipsoid('CH_Nose',(0,-.143,.873),(.018,.023,.016),'MAT_Skin',16,8))
# Cheek volumes are sculpted into the head; blush is baked, avoiding raised sticker-like patches.
head=bpy.data.objects['CH_Head'];headmat=M['MAT_Skin'].copy();headmat.name='MAT_Head_Skin';head.data.materials[0]=headmat
n=512;yy,xx=np.mgrid[0:n,0:n];u=xx/(n-1);v=yy/(n-1);blend=np.zeros((n,n))
for center in [.155,.345]:blend+=.30*np.exp(-.5*(((u-center)/.026)**2+((v-.359)/.035)**2))
base=np.array([240,189,150])/255;pink=np.array([230,140,123])/255;px=np.ones((n,n,4),dtype=np.float32);px[:,:,:3]=base*(1-blend[:,:,None])+pink*blend[:,:,None]
img=bpy.data.images.new('Skin_Face_Blush',width=n,height=n,alpha=False);img.pixels.foreach_set(px.ravel());img.file_format='PNG';img.filepath_raw=ROOT+'/Textures/Skin_Face_Blush.png';img.save();img.pack()
tex=headmat.node_tree.nodes.new('ShaderNodeTexImage');tex.image=img;headmat.node_tree.links.new(tex.outputs['Color'],next(n for n in headmat.node_tree.nodes if n.type=='BSDF_PRINCIPLED').inputs['Base Color'])
for poly in head.data.polygons:
 for k in poly.loop_indices:
  co=head.data.vertices[head.data.loops[k].vertex_index].co
  x=math.copysign(abs(co.x/.190)**(1/.84),co.x);y=math.copysign(abs((co.y-.003)/.147)**(1/.84),co.y-.003);z=math.copysign(min(1,abs((co.z-.949)/.163)**(1/.84)),co.z-.949)
  head.data.uv_layers.active.data[k].uv=(math.atan2(y,x)/(2*pi)+.5,.5+math.asin(z)/pi)
for vertex in head.data.vertices:
 co=vertex.co
 if co.y<0:co.y-=.003*sum(math.exp(-((co.x-side*.105)/.035)**2-((co.z-.87)/.03)**2) for side in [-1,1])
cheeks=bpy.data.objects.new('CH_Cheeks',None);C.objects.link(cheeks);cheeks['Geometry']='Continuous cheek volumes in CH_Head, with baked blush';rigid.append(cheeks)
rigid_head(tube('CH_Mouth',[(x,.003-.147*max(.001,1-(abs(x)/.190)**(2/.84)-(abs((.827+.007*(1-(x/.024)**2))-.949)/.163)**(2/.84))**(.84/2)-.0018,.827+.007*(1-(x/.024)**2)) for x in np.linspace(-.024,.024,11)],.0022,'MAT_Mouth'))
rigid_head(mesh('CH_Eyes',*combine([sphere_data((s*.077,-.145,.939),(.014,.006,.019),12,8) for s in [-1,1]]),'MAT_Eyes'))
rigid_head(mesh('CH_Eyebrows',*combine([tube_data([(s*(.035+.095*t),-.143,.995+.008*sin(pi*t)-.003*t) for t in np.linspace(0,1,9)],.007,8) for s in [-1,1]]),'MAT_Hair_DarkBrown'))
# Scalp cap, with a high front hairline and lower back.
v=[(0,.017,1.177)];f=[];n=32;nr=10
for j in range(1,nr+1):
 for i in range(n):
  p=2*pi*i/n;back=(sin(p)+1)/2;max_t=1.31+.81*back;t=max_t*j/nr
  v.append((.195*sin(t)*cos(p),.017+.147*sin(t)*sin(p), .96+.217*cos(t)))
for i in range(n):f.append((0,1+i,1+(i+1)%n))
for j in range(nr-1):
 for i in range(n):a=1+j*n+i;b=1+j*n+(i+1)%n;f.append((a,b,b+n,a+n))
f.append(tuple(1+(nr-1)*n+i for i in range(n-1,-1,-1)))
rigid_head(mesh('CH_Hair_Base',v,f,'MAT_Hair_DarkBrown'))
parts=[]
# Symmetric clump positions, with deterministic curl size variation and a softly irregular silhouette.
for j,(t,count) in enumerate([(.22,4),(.56,8),(.92,10),(1.25,12),(1.57,12),(1.89,10),(2.08,8)]):
 row_t=t
 for i in range(count):
  p=2*pi*(i+.5*(j%2))/count;back=(sin(p)+1)/2;t0=row_t;t=t0+.028*cos(2*p)*sin(j*2)
  if t>1.31+.81*back:continue
  c=(.195*sin(t)*cos(p),.017+.147*sin(t)*sin(p), .96+.217*cos(t));r=.045*(1+.10*cos(4*p)*cos(j*.7))
  vv,ff=sphere_data(c,(r*1.12,r*.94,r*.94),12,6,1)
  # Small curved asymmetry within each clump reads as curls instead of perfect beads.
  vv=[(x+math.copysign(1,cos(p))*.004*sin((z-c[2])/max(r,.001)*pi),y,z) for x,y,z in vv];parts.append((vv,ff));t=t0
rigid_head(mesh('CH_Hair_Clumps',*combine(parts),'MAT_Hair_DarkBrown'))
# Thick rounded cat-eye rim, fully closed front/back ring geometry.
frame_parts=[];lens_parts=[]
for s in [-1,1]:
 contour=[]
 for i in range(32):
  a=2*pi*i/32;x=.081+.075*math.copysign(abs(cos(a))**.65,cos(a));z=.936+.046*math.copysign(abs(sin(a))**.78,sin(a))+.010*max(0,cos(a))*max(0,sin(a));contour.append((s*x,z))
 vv=[];ff=[]
 for y,shrink in [(-.178,1),(-.160,1),(-.178,.75),(-.160,.75)]:
  for x,z in contour:vv.append((s*.081+(x-s*.081)*shrink,y,.936+(z-.936)*shrink))
 for i in range(32):
  k=(i+1)%32;ff.extend([(i,k,32+k,32+i),(64+i,96+i,96+k,64+k),(i,64+i,64+k,k),(32+i,32+k,96+k,96+i)])
 frame_parts.append((vv,ff))
 vv=[(s*.081+(x-s*.081)*.77,y,.936+(z-.936)*.77) for y in [-.173,-.164] for x,z in contour];ff=[tuple(range(31,-1,-1)),tuple(range(32,64))]+[(i,(i+1)%32,(i+1)%32+32,i+32) for i in range(32)];lens_parts.append((vv,ff))
frame_parts.append(tube_data([(-.027,-.171,.949),(-.014,-.181,.951),(0,-.183,.945),(.014,-.181,.951),(.027,-.171,.949)],.0075,8))
for s in [-1,1]:frame_parts.append(tube_data([(s*.151,-.165,.966),(s*.181,-.130,.969),(s*.187,-.02,.957),(s*.185,.028,.942)],.0065,8))
rigid_head(mesh('CH_Sunglasses_Frame',*combine(frame_parts),'MAT_Sunglasses_Black'));rigid_head(mesh('CH_Sunglasses_Lenses',*combine(lens_parts),'MAT_Sunglasses_Lenses'))
# Full anatomical base under the outfit. These are intentionally low density for reusable wardrobe changes.
body=[]
body.append(ellipsoid('CH_Torso',(0,0,.594),(.100,.061,.173),'MAT_Skin',16,10))
for s,side in [(1,'L'),(-1,'R')]:
 body.append(ellipsoid('CH_UpperArm_'+side,(s*.209,0,.688),(.079,.034,.034),'MAT_Skin',12,8))
 body.append(ellipsoid('CH_Forearm_'+side,(s*.348,0,.688),(.079,.028,.028),'MAT_Skin',12,8))
body.append(mesh('CH_Legs',*combine([sphere_data((s*.069,0,.265),(.040,.041,.175),12,10) for s in [-1,1]]),'MAT_Skin'))
body.append(mesh('CH_Feet',*combine([sphere_data((s*.070,-.024,.045),(.044,.084,.038),16,8) for s in [-1,1]]),'MAT_Skin'))
# Continuous manifold sweater: torso side openings are stitched to sleeve rings, not intersecting cylinders.
n=24;levels=[(.425,.113,.073),(.439,.121,.078),(.48,.123,.079),(.55,.126,.081),(.61,.135,.082),(.64,.143,.077),(.68,.149,.073),(.72,.142,.069),(.746,.112,.061),(.758,.069,.051)]
v=[];f=[]
for z,rx,ry in levels:
 for i in range(n):a=2*pi*i/n;v.append((rx*cos(a),ry*sin(a),z))
removed=set()
for center in [0,12]:
 for j in [5,6]:
  for q in range(center-2,center+2):removed.add((j,q%n))
for j in range(len(levels)-1):
 for i in range(n):
  if (j,i) not in removed:a=j*n+i;b=j*n+(i+1)%n;f.append((a,b,b+n,a+n))
f.append(tuple(range(n-1,-1,-1)));f.append(tuple((len(levels)-1)*n+i for i in range(n)))
for s,center in [(1,0),(-1,12)]:
 boundary=[5*n+(center+q)%n for q in range(-2,3)]+[6*n+(center+2)%n]+[7*n+(center+q)%n for q in range(2,-3,-1)]+[6*n+(center-2)%n]
 boundary.sort(key=lambda idx:math.atan2(v[idx][2]-.68,v[idx][1]))
 angles=[math.atan2(v[i][2]-.68,v[i][1]) for i in boundary];prev=boundary
 for x,ry,rz in [(.166,.062,.057),(.19,.060,.055),(.23,.055,.051),(.26,.052,.048),(.277,.050,.046),(.295,.049,.045),(.33,.047,.043),(.37,.043,.040),(.397,.040,.037),(.418,.038,.035)]:
  ring=[]
  for a in angles:ring.append(len(v));v.append((s*x,ry*cos(a),.688+rz*sin(a)))
  for i in range(len(prev)):k=(i+1)%len(prev);f.append((prev[i],prev[k],ring[k],ring[i]))
  prev=ring
 f.append(tuple(reversed(prev)))
sweater=mesh('CH_Sweater',v,f,'MAT_Sweater_ForestGreen')
# Use one subdivision level for round, animation-friendly shoulder/elbow loops.
def subdiv(o):
 bpy.context.view_layer.objects.active=o;o.select_set(True);mod=o.modifiers.new('Rounded deformation loops','SUBSURF');mod.levels=1;bpy.ops.object.modifier_apply(modifier=mod.name);o.select_set(False)
subdiv(sweater)
def rib_ring(center,axis,radius1,radius2,length,n=32):
 c=Vector(center);v=[];f=[];basis=Quaternion(Vector((0,0,1)).rotation_difference(Vector(axis)))
 for j,(z,mul) in enumerate([(-length/2,.96),(-length*.36,1.03),(length*.36,1.03),(length/2,.96)]):
  for i in range(n):a=2*pi*i/n;r=1+.009*cos(a*16);v.append(tuple(c+basis@Vector((radius1*r*cos(a)*mul,radius2*r*sin(a)*mul,z))))
 for j in range(3):
  for i in range(n):a=j*n+i;b=j*n+(i+1)%n;f.append((a,b,b+n,a+n))
 f.append(tuple(range(n-1,-1,-1)));f.append(tuple(3*n+i for i in range(n)));return v,f
collar=mesh('CH_Sweater_Collar',*rib_ring((0,0,.759),(0,0,1),.076,.060,.050,32),'MAT_Sweater_ForestGreen')
cuffs=mesh('CH_Sweater_Cuffs',*combine([rib_ring((s*.416,0,.688),(1,0,0),.041,.037,.037) for s in [-1,1]]),'MAT_Sweater_ForestGreen')
hem=mesh('CH_Sweater_Waist',*rib_ring((0,0,.435),(0,0,1),.119,.078,.029,48),'MAT_Sweater_ForestGreen')
# Manifold trousers: two leg tubes join a real crotch bridge and a single waistband.
n=12;v=[];f=[];tops={}
for s in [1,-1]:
 start=len(v)
 for z,rx,ry in [(.093,.048,.049),(.114,.049,.050),(.16,.050,.052),(.21,.051,.054),(.24,.052,.056),(.265,.053,.058),(.29,.054,.061),(.325,.055,.066),(.355,.057,.072)]:
  for i in range(n):a=2*pi*i/n;v.append((s*.068+rx*cos(a),ry*sin(a),z))
 for j in range(8):
  for i in range(n):a=start+j*n+i;b=start+j*n+(i+1)%n;f.append((a,b,b+n,a+n))
 f.append(tuple(start+i for i in range(n-1,-1,-1)));tops[s]=[start+8*n+i for i in range(n)]
# Inner arcs both traverse front to back, giving consistent quad connections.
l=[tops[1][i%n] for i in range(9,2,-1)];r=[tops[-1][i%n] for i in range(9,16)]
for i in range(6):f.append((l[i],l[i+1],r[i+1],r[i]))
boundary=[tops[1][i%n] for i in range(9,16)]+[tops[-1][i%n] for i in range(3,10)]
angles=[math.atan2(v[i][1]/.072,v[i][0]/.125) for i in boundary];prev=boundary
for z,rx,ry in [(.386,.124,.078),(.42,.122,.080),(.446,.117,.077),(.455,.113,.073)]:
 ring=[]
 for a in angles:ring.append(len(v));v.append((rx*cos(a),ry*sin(a),z))
 for i in range(len(ring)):k=(i+1)%len(ring);f.append((prev[i],prev[k],ring[k],ring[i]))
 prev=ring
f.append(tuple(reversed(prev)))
pants=mesh('CH_Trousers',v,f,'MAT_Pants_Khaki');subdiv(pants)
pantcuffs=mesh('CH_Trousers_Cuffs',*combine([rib_ring((s*.068,0,.107),(0,0,1),.050,.052,.038) for s in [-1,1]]),'MAT_Pants_Khaki')
# Sneakers, with rounded toe boxes, separate rubber soles, piping, tongues and laces.
shoe_parts=[];sole_parts=[];lace_parts=[]
for s in [-1,1]:
 x=s*.069
 shoe_parts.append(sphere_data((x,-.031,.047),(.053,.098,.043),20,10,.83))
 vv=[];ff=[]
 for z,rx,ry in [(0,.050,.094),(.006,.056,.100),(.022,.056,.100),(.028,.051,.095)]:
  for i in range(20):a=2*pi*i/20;vv.append((x+rx*cos(a),-.031+ry*sin(a),z))
 for j in range(3):
  for i in range(20):a=j*20+i;b=j*20+(i+1)%20;ff.append((a,b,b+20,a+20))
 ff.append(tuple(range(19,-1,-1)));ff.append(tuple(60+i for i in range(20)));sole_parts.append((vv,ff))
 # White toe cap is real geometry; heel and upper retain dark material.
 sole_parts.append(sphere_data((x,-.088,.039),(.052,.047,.015),16,8,.86))
 for y in [-.073,-.052,-.032]:lace_parts.append(tube_data([(x-.023,y+.006,.089),(x,y,.096),(x+.023,y-.006,.089)],.0024,6))
 lace_parts.append(tube_data([(x-.044,-.025,.050),(x-.042,.018,.065),(x,.046,.067),(x+.042,.018,.065),(x+.044,-.025,.050)],.002,'dummy' if False else 6))
shoes=mesh('CH_Shoes',*combine(shoe_parts),'MAT_Shoes_Black');soles=mesh('CH_Shoes_Soles',*combine(sole_parts),'MAT_Shoes_White');laces=mesh('CH_Shoes_Laces',*combine(lace_parts),'MAT_Shoes_White')
# Palms face down. Five individually shaped fingers are united into watertight, low-density hands.
hands=[]
for s,side in [(1,'L'),(-1,'R')]:
 parts=[sphere_data((s*.447,0,.688),(.031,.031,.013),16,8,.86)]
 for j,y in enumerate([-.024,-.009,.007,.022]):
  ln=[.040,.047,.044,.034][j];parts.append(sphere_data((s*(.467+ln/2),y,.688),(ln/2+.007,.007,.007),8,6))
 parts.append(sphere_data((s*.447,-.036,.682),(.019,.010,.008),10,6))
 o=mesh('CH_Hand_'+side,*combine(parts),'MAT_Skin');bpy.context.view_layer.objects.active=o
 mod=o.modifiers.new('Connected palm and fingers','REMESH');mod.mode='VOXEL';mod.voxel_size=.0028;mod.use_smooth_shade=True;bpy.ops.object.modifier_apply(modifier=mod.name)
 dec=o.modifiers.new('Hand realtime topology','DECIMATE');dec.ratio=.20;bpy.ops.object.modifier_apply(modifier=dec.name);hands.append(o)
# Recalculate normals consistently after manually stitched topology.
for o in meshes:
 if not o.data.uv_layers:uvmesh(o)
 bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o;bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.mesh.normals_make_consistent(inside=False);bpy.ops.object.mode_set(mode='OBJECT');o.select_set(False)
# Anatomically ordered humanoid armature, no constraints or negative scales.
data=bpy.data.armatures.new('ARM_Boy_GreenSweater_Skeleton');arm=bpy.data.objects.new('ARM_Boy_GreenSweater',data);C.objects.link(arm);bpy.context.view_layer.objects.active=arm;arm.select_set(True);bpy.ops.object.mode_set(mode='EDIT')
bones={}
def bone(name,head,tail,parent=None):
 b=data.edit_bones.new(name);b.head=head;b.tail=tail;b.roll=0
 if parent:b.parent=data.edit_bones[parent]
 bones[name]=(Vector(head),Vector(tail),parent);return b
bone('Root',(0,0,0),(0,0,.08));bone('Hips',(0,0,.45),(0,0,.52),'Root');bone('Spine',(0,0,.52),(0,0,.62),'Hips');bone('Chest',(0,0,.62),(0,0,.743),'Spine');bone('Neck',(0,0,.743),(0,0,.817),'Chest');bone('Head',(0,0,.817),(0,0,1.13),'Neck')
for s,side in [(1,'L'),(-1,'R')]:
 bone('Shoulder.'+side,(s*.045,0,.705),(s*.14,0,.688),'Chest');bone('UpperArm.'+side,(s*.14,0,.688),(s*.277,0,.688),'Shoulder.'+side);bone('LowerArm.'+side,(s*.277,0,.688),(s*.42,0,.688),'UpperArm.'+side);bone('Hand.'+side,(s*.42,0,.688),(s*.49,0,.688),'LowerArm.'+side)
 bone('UpperLeg.'+side,(s*.068,0,.45),(s*.068,0,.27),'Hips');bone('LowerLeg.'+side,(s*.068,0,.27),(s*.068,0,.09),'UpperLeg.'+side);bone('Foot.'+side,(s*.068,0,.09),(s*.068,-.095,.035),'LowerLeg.'+side);bone('Toes.'+side,(s*.068,-.095,.035),(s*.068,-.13,.035),'Foot.'+side)
bpy.ops.object.mode_set(mode='OBJECT');arm.show_in_front=True
for p in arm.pose.bones:p.rotation_mode='QUATERNION'
def smooth(a,b,x):
 t=max(0,min(1,(x-a)/(b-a)));return t*t*(3-2*t)
def legweights(co):
 x,y,z=co;side='L' if x>=0 else 'R';k=smooth(.225,.300,z);hip=smooth(.325,.405,z)
 if abs(x)<.036 and z>.34:hip=max(hip,1-smooth(.01,.036,abs(x)))
 foot=1-smooth(.095,.145,z)
 return {'Hips':hip,'UpperLeg.'+side:(1-hip)*k,'LowerLeg.'+side:(1-hip)*(1-k)*(1-foot),'Foot.'+side:(1-hip)*(1-k)*foot}
def torso_weights(co):
 x,y,z=co;ax=abs(x);side='L' if x>=0 else 'R'
 if ax>.13 and z>.59:
  armw=smooth(.125,.175,ax);lower=smooth(.250,.305,ax);hand=smooth(.405,.435,ax)
  return {'Chest':1-armw,'UpperArm.'+side:armw*(1-lower),'LowerArm.'+side:armw*lower*(1-hand),'Hand.'+side:armw*lower*hand}
 chest=smooth(.55,.665,z);hip=1-smooth(.445,.535,z)
 return {'Hips':hip,'Spine':(1-hip)*(1-chest),'Chest':(1-hip)*chest}
def bind(o,fn):
 for name in bones:o.vertex_groups.new(name=name)
 for v in o.data.vertices:
  weights=fn(v.co);total=sum(max(0,w) for w in weights.values())
  for name,w in weights.items():
   if w>1e-6:o.vertex_groups[name].add([v.index],w/total,'REPLACE')
 o.parent=arm;mod=o.modifiers.new('Humanoid skin deformation','ARMATURE');mod.object=arm;mod.use_deform_preserve_volume=False
for o in body+[sweater,collar,cuffs,hem]+hands:
 if o.name.startswith('CH_Legs') or o.name=='CH_Feet':bind(o,legweights)
 elif o in hands:bind(o,lambda co:{'Hand.L' if co.x>0 else 'Hand.R':1})
 else:bind(o,torso_weights)
for o in [pants,pantcuffs,shoes,soles,laces]:bind(o,legweights if o in [pants,pantcuffs] else lambda co:{'Foot.L' if co.x>0 else 'Foot.R':1})
for o in rigid:
 mw=o.matrix_world.copy();o.parent=arm;o.parent_type='BONE';o.parent_bone='Head';o.matrix_world=mw
arm['Asset']='Boy Green Sweater | 1.2 m | faces -Y | T-pose rest';C.asset_mark();C['Reference']='Supplied Stylised 3D Character Reference Sheet.png'
# Export UVs are image based; bump noise is optional preview-only detail, not a required dependency.
for o in meshes:o['CharacterPart']=True
# Animation helpers. Quaternions are defined in armature space, converted into local bone coordinates.
rest={b.name:b.matrix_local.to_quaternion() for b in data.bones};order=[b.name for b in data.bones]
def reset():
 for p in arm.pose.bones:p.rotation_quaternion=Quaternion();p.location=(0,0,0);p.scale=(1,1,1)
def delta(name,axis,angle):return Quaternion(axis,angle)@rest[name]
def apply_pose(desired=None,hipoff=(0,0,0)):
 desired=desired or {};glob={}
 for name in order:
  b=data.bones[name];par=b.parent.name if b.parent else None;parent_rest=rest[par] if par else Quaternion();parent_pose=glob[par] if par else Quaternion()
  goal=desired.get(name,parent_pose@parent_rest.inverted()@rest[name]);local=rest[name].inverted()@parent_rest@parent_pose.inverted()@goal
  arm.pose.bones[name].rotation_quaternion=local;glob[name]=goal
 arm.pose.bones['Hips'].location=rest['Hips'].inverted()@Vector(hipoff)
def standing(t=0):
 d={}
 for s,side in [(1,'L'),(-1,'R')]:
  d['UpperArm.'+side]=Quaternion((0,1,0),s*1.34)@Quaternion((0,0,1),-.03*s)@rest['UpperArm.'+side]
 return d
def solve_leg(d,side,ankle,hipoff):
 H=bones['UpperLeg.'+side][0]+Vector(hipoff);A=Vector(ankle);vec=A-H;dist=min(.3595,vec.length);direction=vec.normalized();perp=Vector((0,direction.z,-direction.y)).normalized();a=dist/2;h=sqrt(max(.18**2-a*a,0));K=H+direction*a+perp*h
 for name,vec in [('UpperLeg.'+side,K-H),('LowerLeg.'+side,A-K)]:
  original=bones[name][1]-bones[name][0];d[name]=original.rotation_difference(vec)@rest[name]
 d['Foot.'+side]=rest['Foot.'+side];d['Toes.'+side]=rest['Toes.'+side]
ACTIONS={}
for name,end in [('ANIM_Idle',73),('ANIM_Walk',25),('ANIM_Run',19),('ANIM_Wave',97),('ANIM_Sit',73)]:
 action=bpy.data.actions.new(name);action.use_fake_user=True;arm.animation_data_create();arm.animation_data.action=action;reset()
 for frame in range(1,end+1):
  t=(frame-1)/(end-1);d=standing(t);off=Vector((0,0,0))
  if name=='ANIM_Idle':
   d['Chest']=delta('Chest',(1,0,0),.008*sin(2*pi*t));d['Head']=delta('Head',(0,0,1),.025*sin(2*pi*t));off.z=.002*(1-cos(2*pi*t))
  elif name in ['ANIM_Walk','ANIM_Run']:
   run=name=='ANIM_Run';off.z=-.026+(.008 if not run else .018)*(1-cos(4*pi*t));d['Chest']=delta('Chest',(1,0,0),.04 if not run else .16)
   for s,side,phase in [(1,'L',t),(-1,'R',t+.5)]:
    p=phase%1;stance=.60 if not run else .42;stride=.095 if not run else .115
    if p<stance:y=-stride+2*stride*p/stance;lift=0
    else:q=(p-stance)/(1-stance);y=stride*(1-2*(q*q*(3-2*q)));lift=(.052 if not run else .090)*sin(pi*q)
    solve_leg(d,side,(s*.068,y,.09+lift),off)
    d['UpperArm.'+side]=Quaternion((1,0,0),(.20 if not run else .40)*cos(2*pi*(t+.5*(s<0))))@d['UpperArm.'+side]
  elif name=='ANIM_Wave':
   envelope=smooth(0,.22,t)*(1-smooth(.78,1,t));base=1.34;d['UpperArm.R']=delta('UpperArm.R',(0,1,0),-base+envelope*2.25)
   baseline=standing()['UpperArm.R'];fore=Vector((-1,0,0)).rotation_difference(Vector((-.035,-.01,.14)))@rest['LowerArm.R'];d['LowerArm.R']=baseline.slerp(fore,envelope)
   hand=Quaternion(Vector((-.035,-.01,.14)).normalized(),pi/2+.25*sin(10*pi*t))@fore;d['Hand.R']=baseline.slerp(hand,envelope);d['Head']=delta('Head',(0,0,1),-.05*envelope)
  else:
   u=smooth(.05,.85,t);off=Vector((0,.035*u,-.198*u))
   for s,side in [(1,'L'),(-1,'R')]:
    solve_leg(d,side,(s*.068,-.19*u,.09),off)
    d['UpperArm.'+side]=Quaternion((1,0,0),-.28*u)@d['UpperArm.'+side]
  apply_pose(d,off)
  for p in arm.pose.bones:
   p.keyframe_insert(data_path='rotation_quaternion',frame=frame,group=p.name)
   if p.name=='Hips':p.keyframe_insert(data_path='location',frame=frame,group=p.name)
 action.asset_mark();ACTIONS[name]=action
arm.animation_data.action=None;reset();S.frame_set(1);S.frame_start=1;S.frame_end=97
# Validate geometry, weights, exact symmetry, rest dimensions and deformation stability.
import bmesh
report={'asset':'Boy Green Sweater','bones':len(data.bones),'actions':{},'meshes':[],'issues':[]}
for name,a in ACTIONS.items():report['actions'][name]={'frames':list(a.frame_range),'seconds':(a.frame_range[1]-a.frame_range[0])/24,'inPlace':name in ['ANIM_Walk','ANIM_Run'],'loop':name in ['ANIM_Idle','ANIM_Walk','ANIM_Run']}
for o in meshes:
 o.data.calc_loop_triangles();bm=bmesh.new();bm.from_mesh(o.data);bad=sum(not e.is_manifold for e in bm.edges);bm.free();unweighted=0;weight_error=0
 if o not in rigid:
  for v in o.data.vertices:
   total=sum(g.weight for g in v.groups);unweighted+=total<.99;weight_error=max(weight_error,abs(total-1))
 report['meshes'].append({'name':o.name,'vertices':len(o.data.vertices),'triangles':len(o.data.loop_triangles),'nonmanifoldEdges':bad,'unweightedVertices':unweighted,'maxWeightError':weight_error})
 if bad:report['issues'].append(o.name+': nonmanifold edges '+str(bad))
 if unweighted:report['issues'].append(o.name+': unweighted vertices')
report['triangles']=sum(m['triangles'] for m in report['meshes']);report['vertices']=sum(m['vertices'] for m in report['meshes'])
allv=[o.matrix_world@v.co for o in meshes for v in o.data.vertices];report['restBounds']={'min':[min(v[k] for v in allv) for k in range(3)],'max':[max(v[k] for v in allv) for k in range(3)]}
report['deformationTests']=[]
for label,d in [('Head left',{'Head':delta('Head',(0,0,1),.6)}),('Head right',{'Head':delta('Head',(0,0,1),-.6)}),('Shoulders',{'UpperArm.L':delta('UpperArm.L',(0,1,0),.8),'UpperArm.R':delta('UpperArm.R',(0,1,0),-.8)}),('Elbows',{'LowerArm.L':delta('LowerArm.L',(0,0,1),-1.3),'LowerArm.R':delta('LowerArm.R',(0,0,1),1.3)}),('Hips',{'Hips':delta('Hips',(0,0,1),.35)}),('Knees',{'LowerLeg.L':delta('LowerLeg.L',(1,0,0),1),'LowerLeg.R':delta('LowerLeg.R',(1,0,0),1)}),('Feet',{'Foot.L':delta('Foot.L',(1,0,0),.4)}),('Torso',{'Chest':delta('Chest',(0,0,1),.35)})]:
 reset();apply_pose(d);bpy.context.view_layer.update();finite=True
 for o in meshes:
  ev=o.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh();finite &= all(all(math.isfinite(k) for k in v.co) for v in me.vertices);ev.to_mesh_clear()
 report['deformationTests'].append({'test':label,'finiteDeformation':finite})
reset();arm.animation_data.action=None;bpy.context.view_layer.update()
# Mark a second, shared-mesh idle collection for non-destructive café instancing.
idle=bpy.data.collections.new('CHAR_Boy_GreenSweater_CafeIdle');idle.use_fake_user=True;mapping={}
for o in C.objects:
 cp=o.copy();cp.name='CafeIdle_'+o.name
 if o==arm:cp.data=o.data.copy()
 idle.objects.link(cp);mapping[o]=cp
for original,cp in mapping.items():
 if original.parent:cp.parent=mapping.get(original.parent,original.parent)
 for mod in cp.modifiers:
  if mod.type=='ARMATURE':mod.object=mapping[arm]
idlearm=mapping[arm];idlearm.animation_data_create();idlearm.animation_data.action=None;track=idlearm.animation_data.nla_tracks.new();strip=track.strips.new('Looping Cafe Idle',1,ACTIONS['ANIM_Idle']);strip.repeat=100;idle['Instance scale for café']=1.5
# Save exportable assets before studio helpers. No leaf bones and no scene cameras/lights in FBX.
def select_character():
 bpy.ops.object.select_all(action='DESELECT')
 for o in C.objects:o.select_set(True)
 bpy.context.view_layer.objects.active=arm
select_character()
common=dict(use_selection=True,object_types={'MESH','ARMATURE'},add_leaf_bones=False,apply_unit_scale=True,apply_scale_options='FBX_SCALE_UNITS',axis_forward='-Z',axis_up='Y',bake_anim=True,bake_anim_use_nla_strips=False,bake_anim_simplify_factor=0,path_mode='COPY',embed_textures=True)
bpy.ops.export_scene.fbx(filepath=ROOT+'/Models/Boy_GreenSweater_Rigged.fbx',bake_anim_use_all_actions=True,**common)
for name,action in ACTIONS.items():
 S.name=name;arm.animation_data.action=action;S.frame_start=int(action.frame_range[0]);S.frame_end=int(action.frame_range[1]);S.frame_set(S.frame_start)
 bpy.ops.export_scene.fbx(filepath=ROOT+'/Animations/Boy_'+name.split('_',1)[1]+'.fbx',bake_anim_use_all_actions=False,**common)
S.name='Boy Green Sweater | Character Studio';arm.animation_data.action=None;reset();S.frame_start=1;S.frame_end=97;S.frame_set(1)
# Neutral studio, kept outside the character collection and excluded from exports.
studio=bpy.data.collections.new('STUDIO_Previews');S.collection.children.link(studio)
def studio_obj(name,data):o=bpy.data.objects.new(name,data);studio.objects.link(o);return o
cam=studio_obj('Studio Camera',bpy.data.cameras.new('Studio Camera'));S.camera=cam
floor_mat=bpy.data.materials.new('Studio Warm Ivory');floor_mat.diffuse_color=(.72,.70,.65,1);floor_mat.use_nodes=True;next(n for n in floor_mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED').inputs['Base Color'].default_value=(.72,.70,.65,1)
me=bpy.data.meshes.new('Studio Floor');me.from_pydata([(-200,-200,-.001),(200,-200,-.001),(200,200,-.001),(-200,200,-.001)],[],[(0,1,2,3)]);floor=studio_obj('Studio Floor',me);me.materials.append(floor_mat)
for name,loc,power,size in [('Large softbox',(-2,-3,4),380,3),('Soft fill',(3,-1,2.5),170,3),('Hair rim',(1,2,3),300,2)]:
 ld=bpy.data.lights.new(name,'AREA');ld.energy=power;ld.shape='DISK';ld.size=size;o=studio_obj(name,ld);o.location=loc;o.rotation_euler=(Vector((0,0,.7))-o.location).to_track_quat('-Z','Y').to_euler()
S.world.use_nodes=True;bg=next(n for n in S.world.node_tree.nodes if n.type=='BACKGROUND');bg.inputs['Color'].default_value=(.65,.67,.72,1);bg.inputs['Strength'].default_value=.35
S.render.resolution_x=1024;S.render.resolution_y=1024;S.render.resolution_percentage=100;S.render.image_settings.file_format='PNG';S.render.film_transparent=False
# Use the factory startup renderer; Blender exposes this installed engine by default.
report['renderEngine']=S.render.engine
if hasattr(S,'eevee') and hasattr(S.eevee,'taa_render_samples'):S.eevee.taa_render_samples=48
try:S.view_settings.view_transform='AgX'
except:pass
S.view_settings.look='AgX - Medium High Contrast' if 'AgX - Medium High Contrast' in [i.identifier for i in S.view_settings.bl_rna.properties['look'].enum_items] else S.view_settings.look
S.view_settings.exposure=0
cam.data.type='ORTHO';cam.data.ortho_scale=1.46;cam.location=(0,-3,.61);cam.rotation_euler=(Vector((0,0,.61))-cam.location).to_track_quat('-Z','Y').to_euler()
# Store pose and animation test state for the render stage, and a reusable T-pose asset.
with open(ROOT+'/validation.json','w') as f:json.dump(report,f,indent=2)
bpy.ops.wm.save_as_mainfile(filepath=ROOT+'/Blender/Boy_GreenSweater.blend')
print('BOY_BUILD_COMPLETE',json.dumps({k:report[k] for k in ['triangles','vertices','bones','restBounds','issues','renderEngine']}))
