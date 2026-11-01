import bpy,math,os,json,random
import numpy as np
from mathutils import Vector,Quaternion
from math import sin,cos,pi

BASE='/Users/pranay/Documents/Codex/2026-10-22/new-chat-6'
OUT=BASE+'/outputs/Characters/CH_Female_v001'
os.makedirs(OUT,exist_ok=True)
if bpy.data.objects.get('CH_Rig'):raise RuntimeError('CH_Rig already exists; refusing to duplicate or overwrite it.')
SCENE=bpy.context.scene
CH=bpy.data.collections.get('Characters') or bpy.data.collections.new('Characters')
if CH.name not in SCENE.collection.children:SCENE.collection.children.link(CH)
GEO=bpy.data.collections.new('CH_Female_Geometry');CH.children.link(GEO)
RIGCOL=bpy.data.collections.new('CH_Female_Rig');CH.children.link(RIGCOL)

def material(name,color,roughness=.5,metal=0):
    if bpy.data.materials.get(name):raise RuntimeError('Material name collision: '+name)
    m=bpy.data.materials.new(name);m.use_nodes=True
    bs=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
    bs.inputs['Base Color'].default_value=(*color,1)
    bs.inputs['Roughness'].default_value=roughness
    bs.inputs['Metallic'].default_value=metal
    return m

SKIN=material('CH_Skin_Peach',(.76,.46,.33),.65)
HAIR=material('CH_Hair_SatinBlack',(.012,.013,.017),.33)
EYE=material('CH_Eye_GlossBlack',(.006,.007,.009),.19)
WHITE=material('CH_Dress_SoftWhite',(.88,.86,.82),.5)
COLLAR=material('CH_Collar_PorcelainWhite',(.95,.93,.88),.43)
SOCK=material('CH_Socks_WhiteKnit',(.87,.85,.80),.8)
SHOE=material('CH_Shoes_PolishedBlack',(.009,.01,.013),.22)
SOLE=material('CH_Soles_RubberBlack',(.013,.014,.017),.65)
GOLD=material('CH_Buttons_ButterYellow',(.95,.62,.20),.4)
MOUTH=material('CH_Mouth_Rose',(.42,.075,.05),.62)
GLINT=material('CH_Eye_Catchlight',(.98,.98,.98),.2)
HAIRLINE=material('CH_Hair_SoftHighlight',(.021,.022,.027),.4)

# A small dedicated albedo map carries blush in object UVs; no translucent cheek decals.
W,H=1024,512
yy,xx=np.mgrid[0:H,0:W];u=(xx+.5)/W;v=(yy+.5)/H
theta=u*2*pi;phi=(v-.5)*pi
sx=np.sign(np.sin(theta))*np.abs(np.sin(theta))**.86
cz=np.sign(np.sin(phi))*np.abs(np.sin(phi))**.86
x=.355*np.cos(phi)**.86*sx;z=.305*cz
front=(np.cos(theta)<-.5).astype(float)
cheek=(np.exp(-((x-.19)/.07)**2-((z+.065)/.045)**2)+np.exp(-((x+.19)/.07)**2-((z+.065)/.045)**2))*front
rgba=np.ones((H,W,4),dtype=np.float32);rgba[:,:,:3]=(.76,.46,.33)
rose=np.array([.82,.32,.28]);rgba[:,:,:3]=rgba[:,:,:3]*(1-cheek[:,:,None]*.23)+rose*cheek[:,:,None]*.23
im=bpy.data.images.new('CH_Face_Albedo',width=W,height=H,alpha=True)
im.pixels.foreach_set(rgba.ravel());im.filepath_raw=OUT+'/CH_Face_Albedo.png';im.file_format='PNG';im.save();im.pack()
FACE_SKIN=SKIN.copy();FACE_SKIN.name='CH_Face_PeachBlush'
tex=FACE_SKIN.node_tree.nodes.new('ShaderNodeTexImage');tex.image=im
bs=next(n for n in FACE_SKIN.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
FACE_SKIN.node_tree.links.new(tex.outputs['Color'],bs.inputs['Base Color'])

def smooth(t):t=max(0,min(1,t));return t*t*(3-2*t)
def mix_weights(a,b,t):return {a:1-t,b:t} if .00001<t<.99999 else ({b:1} if t>=.99999 else {a:1})

class Builder:
    def __init__(self,name):self.name=name;self.v=[];self.f=[];self.weights=[];self.mats=[];self.mi=[];self.uv=[]
    def add(self,vertices,faces,mat,weights,uvs=None):
        offset=len(self.v);self.v.extend([tuple(v) for v in vertices])
        if mat not in self.mats:self.mats.append(mat)
        mi=self.mats.index(mat)
        self.f.extend([tuple(offset+i for i in face) for face in faces]);self.mi.extend([mi]*len(faces))
        self.weights.extend([weights(Vector(v)) if callable(weights) else dict(weights) for v in vertices])
        self.uv.extend(uvs if uvs is not None else [(0,0)]*len(vertices))
    def build(self,subdivision=0):
        mesh=bpy.data.meshes.new(self.name+'_Mesh');mesh.from_pydata(self.v,[],self.f);mesh.update()
        for m in self.mats:mesh.materials.append(m)
        layer=mesh.uv_layers.new(name='UVMap')
        for p,mi in zip(mesh.polygons,self.mi):
            p.material_index=mi;p.use_smooth=True
            for k in p.loop_indices:layer.data[k].uv=self.uv[mesh.loops[k].vertex_index]
        o=bpy.data.objects.new(self.name,mesh);GEO.objects.link(o)
        for i,w in enumerate(self.weights):
            total=sum(w.values())
            for bone,value in w.items():
                if value>1e-8:
                    vg=o.vertex_groups.get(bone) or o.vertex_groups.new(name=bone);vg.add([i],value/total,'REPLACE')
        if subdivision:
            m=o.modifiers.new('CH_Surface_Smoothing','SUBSURF');m.levels=subdivision;m.render_levels=subdivision
        return o

def ellipsoid(B,center,scale,mat,weights,segments=32,rings=20,exponent=1,rotation=None):
    vv=[];uv=[]
    for j in range(rings+1):
        phi=-pi/2+pi*j/rings
        for i in range(segments+1):
            t=2*pi*i/segments
            p=Vector((math.copysign(abs(cos(phi)*sin(t))**exponent,cos(phi)*sin(t))*scale[0],math.copysign(abs(cos(phi)*cos(t))**exponent,cos(phi)*cos(t))*scale[1],math.copysign(abs(sin(phi))**exponent,sin(phi))*scale[2]))
            if rotation:p=rotation@p
            vv.append(p+Vector(center));uv.append((i/segments,j/rings))
    faces=[]
    for j in range(rings):
        for i in range(segments):
            a=j*(segments+1)+i;faces.append((a,a+1,a+segments+2,a+segments+1))
    # The theta convention above reverses the ordinary UV sphere winding.
    B.add(vv,[tuple(reversed(f)) for f in faces],mat,weights,uv)

def tube(B,points,radii,mat,weights,sides=16,depths=None,cap=True):
    vv=[];uv=[]
    for j,p0 in enumerate(points):
        p=Vector(p0)
        tangent=(Vector(points[min(j+1,len(points)-1)])-Vector(points[max(0,j-1)])).normalized()
        ref=Vector((1,0,0)) if abs(tangent.x)<.9 else Vector((0,1,0))
        u=(ref-tangent*ref.dot(tangent)).normalized();v=tangent.cross(u).normalized()
        for k in range(sides):
            t=2*pi*k/sides;r=radii[j];depth=depths[j] if depths is not None else r
            vv.append(p+u*cos(t)*r+v*sin(t)*depth);uv.append((k/sides,j/max(1,len(points)-1)))
    faces=[]
    for j in range(len(points)-1):
        for k in range(sides):
            a=j*sides+k;b=j*sides+(k+1)%sides;faces.append((a,b,b+sides,a+sides))
    if cap:faces.extend([tuple(reversed(range(sides))),tuple((len(points)-1)*sides+k for k in range(sides))])
    B.add(vv,faces,mat,weights,uv)

def lathe(B,profile,mat,weights,segments=64,cap=True):
    vv=[];uv=[]
    for j,(z,rx,ry) in enumerate(profile):
        for i in range(segments):
            a=2*pi*i/segments;vv.append((rx*sin(a),ry*cos(a),z));uv.append((i/segments,j/max(1,len(profile)-1)))
    faces=[]
    for j in range(len(profile)-1):
        for i in range(segments):
            a=j*segments+i;b=j*segments+(i+1)%segments;faces.append((a,a+segments,b+segments,b))
    if cap:faces.extend([tuple(range(segments)),tuple(reversed([(len(profile)-1)*segments+i for i in range(segments)]))])
    B.add(vv,faces,mat,weights,uv)

def curve(B,points,r,mat,weights):tube(B,points,[r]*len(points),mat,weights,8)

# Rounded, gently squared head and deliberately small facial features.
B=Builder('CH_Head');ellipsoid(B,(0,0,1.585),(.355,.265,.305),FACE_SKIN,{'Head':1},64,40,.86);head=B.build()
B=Builder('CH_Face')
ellipsoid(B,(0,-.268,1.515),(.023,.023,.027),SKIN,{'Head':1},20,12)
for side in [-1,1]:
    ellipsoid(B,(side*.352,-.005,1.555),(.066,.047,.081),SKIN,{'Head':1},24,16)
    for lash in range(2):
        x=side*(.18+lash*.022);z=1.625+lash*.002
        curve(B,[(x,-.271,z),(x+side*.014,-.278,z+.021)],.0036,HAIR,{'Head':1})
    points=[]
    for i in range(15):
        t=i/14;points.append((side*(.092+t*.105),-.254,1.69+.009*sin(t*pi)))
    curve(B,points,.004,HAIR,{'Head':1})
curve(B,[(-.022,-.264,1.465),(-.012,-.269,1.462),(0,-.271,1.464),(.012,-.269,1.462),(.022,-.264,1.465)],.0026,MOUTH,{'Head':1})
face=B.build()
B=Builder('CH_Eyes')
for side in [-1,1]:
    ellipsoid(B,(side*.143,-.250,1.584),(.059,.032,.068),EYE,{'Head':1},32,24)
    ellipsoid(B,(side*.143-.016,-.280,1.608),(.009,.003,.010),GLINT,{'Head':1},12,8)
eyes=B.build()

# Back cap and overlapping broad long locks; all real geometry.
B=Builder('CH_Hair_Back');vv=[];ff=[]
seg,rows=72,24
for j in range(rows+1):
    t=j/rows
    for i in range(seg):
        a=2*pi*i/seg;front=max(0,-cos(a));end=2.0-.92*front**2
        polar=.008+(end-.008)*t
        vv.append((.380*sin(polar)*sin(a),.292*sin(polar)*cos(a)+.012,1.602+.335*cos(polar)))
for j in range(rows):
    for i in range(seg):
        a=j*seg+i;b=j*seg+(i+1)%seg;ff.append((a,b,b+seg,a+seg))
B.add(vv,[tuple(reversed(f)) for f in ff],HAIR,{'Head':1})
for idx,x0 in enumerate([-.29,-.145,0,.145,.29]):
    points=[];rr=[];dd=[]
    for j in range(25):
        t=j/24
        x=x0*(1+.10*sin(t*pi))
        y=.19+.045*sin(t*pi)+.015*(1-abs(x0)/.3)
        z=1.67-t*(.78-(.05 if abs(x0)>.2 else 0))
        width=.10+.026*sin(t*pi)
        width*=max(.07,min(1,(1-t)*9))**.5
        points.append((x,y,z));rr.append(width);dd.append(width*.70)
    tube(B,points,rr,HAIR,{'Head':1},20,dd)
hairback=B.build(1)
B=Builder('CH_Hair_Front')
for side in [-1,1]:
    points=[(side*(.28+.05*sin(t*pi*.75)),-.155-.065*sin(t*pi/2),1.78-.44*t) for t in np.linspace(0,1,24)]
    radii=[.043*(1-.55*t) for t in np.linspace(0,1,24)]
    tube(B,points,radii,HAIR,{'Head':1},16,[r*.65 for r in radii])
for start,end,width in [(-.13,-.285,.105),(-.055,-.07,.087),(.065,.105,.112),(.17,.285,.095)]:
    points=[];r=[];d=[]
    for j in range(22):
        t=j/21;x=start+(end-start)*t;z=1.90-.175*t+.015*sin(t*pi)
        y=-.15-.13*sin(t*pi/2)
        taper=sin(pi*(.12+.86*t))**.60
        points.append((x,y,z));r.append(width*taper);d.append(.040*taper)
    tube(B,points,r,HAIR,{'Head':1},20,d)
hairfront=B.build(1)

B=Builder('CH_Body')
ellipsoid(B,(0,.005,1.05),(.18,.12,.22),SKIN,lambda p:mix_weights('Spine','Chest',smooth((p.z-.98)/.18)),32,20)
tube(B,[(0,0,1.20),(0,0,1.28),(0,0,1.34)],[.075,.070,.071],SKIN,{'Neck':1},24)
body=B.build()

def dress_weights(p):
    if p.z>1.07:return {'Chest':1}
    if p.z>.91:return mix_weights('Spine','Chest',smooth((p.z-.91)/.16))
    if p.z>.76:return mix_weights('Pelvis','Spine',smooth((p.z-.76)/.15))
    thigh='Thigh.L' if p.x>=0 else 'Thigh.R';t=.13*smooth((.76-p.z)/.22)
    return {'Pelvis':1-t,thigh:t}
B=Builder('CH_Dress')
profile=[(.525,.306,.197),(.535,.317,.205),(.56,.316,.204),(.60,.307,.198),(.72,.279,.180),(.84,.251,.162),(.94,.231,.149),(1.04,.222,.143),(1.15,.220,.143),(1.21,.228,.143),(1.235,.20,.130),(1.255,.095,.074)]
lathe(B,profile,WHITE,dress_weights,64,False)
for z,rx,ry in [(.553,.315,.204),(.936,.234,.152)]:
    points=[(rx*sin(a),ry*cos(a),z) for a in np.linspace(0,2*pi,97)]
    curve(B,points,.0045,COLLAR,dress_weights)
for side in [-1,1]:
    rot=Quaternion((0,1,0),side*.25)
    ellipsoid(B,(side*.062,-.092,1.247),(.078,.035,.043),COLLAR,{'Chest':1},24,16,rotation=rot)
    ellipsoid(B,(side*.135,-.151,1.16),(.020,.010,.021),GOLD,{'Chest':1},20,12)
dress=B.build(1)
sol=dress.modifiers.new('CH_Dress_Thickness','SOLIDIFY');sol.thickness=.008;sol.offset=-1

FINGERS={}
for side,suffix in [(1,'L'),(-1,'R')]:
    def arm_weights(p,side=side,suffix=suffix):
        x=abs(p.x)
        if x<.29:return mix_weights('Chest','UpperArm.'+suffix,smooth((x-.20)/.09))
        return mix_weights('UpperArm.'+suffix,'Forearm.'+suffix,smooth((x-.48)/.11))
    B=Builder('CH_Arm_'+suffix)
    points=[];r=[]
    for j in range(37):
        t=j/36;x=.205+t*.575
        points.append((side*x,0,1.195));r.append(.068*(1-t)+.042*t)
    tube(B,points,r,SKIN,arm_weights,20)
    B.build(1)
    B=Builder('CH_Hand_'+suffix)
    ellipsoid(B,(side*.824,0,1.195),(.075,.052,.031),SKIN,{'Hand.'+suffix:1},28,16)
    descriptors=[]
    for name,yy,length,radius in [('Index',-.036,.105,.014),('Middle',-.011,.119,.0145),('Ring',.014,.109,.014),('Little',.037,.084,.012)]:
        a=Vector((side*.865,yy,1.195));b=Vector((side*(.865+length*.54),yy,1.195));c=Vector((side*(.865+length),yy,1.195))
        bone1=name+'.01.'+suffix;bone2=name+'.02.'+suffix
        def fw(p,a=a,b=b,c=c,bone1=bone1,bone2=bone2,suffix=suffix):
            t=abs(p.x)-abs(a.x)
            if t<.015:return mix_weights('Hand.'+suffix,bone1,smooth(t/.015))
            return mix_weights(bone1,bone2,smooth((t-abs(b.x-a.x)+.012)/.024))
        pts=[a.lerp(c,t) for t in np.linspace(0,1,13)]
        rr=[radius*(.95-.18*t)*max(.14,min(1,(1-t)*8))**.5 for t in np.linspace(0,1,13)]
        tube(B,pts,rr,SKIN,fw,12);descriptors.append((bone1,bone2,a,b,c))
    a=Vector((side*.803,-.040,1.19));b=Vector((side*.835,-.080,1.188));c=Vector((side*.875,-.098,1.188))
    tube(B,[a,a.lerp(b,.5),b,b.lerp(c,.5),c],[.020,.020,.018,.015,.009],SKIN,{'Thumb.01.'+suffix:.6,'Thumb.02.'+suffix:.4},14)
    descriptors.append(('Thumb.01.'+suffix,'Thumb.02.'+suffix,a,b,c));FINGERS[suffix]=descriptors
    B.build(1)
    def leg_weights(p,suffix=suffix):
        if p.z>.69:return mix_weights('Thigh.'+suffix,'Pelvis',smooth((p.z-.69)/.07)*.3)
        if p.z<.23:return mix_weights('Foot.'+suffix,'Shin.'+suffix,smooth((p.z-.17)/.06))
        return mix_weights('Shin.'+suffix,'Thigh.'+suffix,smooth((p.z-.38)/.10))
    B=Builder('CH_Leg_'+suffix)
    pts=[(side*.145,0,z) for z in np.linspace(.18,.765,38)]
    rr=[.059+.024*smooth((z-.25)/.48) for z in np.linspace(.18,.765,38)]
    tube(B,pts,rr,SKIN,leg_weights,24);B.build(1)

B=Builder('CH_Socks')
for side,suffix in [(1,'L'),(-1,'R')]:
    cx=side*.145
    pts=[(cx,0,z) for z in [.13,.15,.18,.24,.31,.32,.33]]
    tube(B,pts,[.064,.065,.065,.068,.074,.076,.073],SOCK,{'Shin.'+suffix:1},32)
    for i in range(20):
        a=2*pi*i/20
        points=[(cx+(.066+.009*t)*sin(a),(.066+.009*t)*cos(a),.17+.15*t) for t in np.linspace(0,1,10)]
        curve(B,points,.0018,COLLAR,{'Shin.'+suffix:1})
B.build()
B=Builder('CH_Shoes')
for side,suffix in [(1,'L'),(-1,'R')]:
    x=side*.145;w={'Foot.'+suffix:1}
    ellipsoid(B,(x,-.055,.065),(.098,.158,.060),SOLE,w,36,20,.7)
    ellipsoid(B,(x,-.115,.111),(.097,.112,.085),SHOE,w,36,20,.9)
    ellipsoid(B,(x,.042,.11),(.083,.085,.074),SHOE,w,28,16)
    points=[]
    for j in range(25):
        t=j/24;points.append((x-.089+.178*t,-.018,.139+.057*sin(t*pi)))
    tube(B,points,[.012]*25,SHOE,w,12)
    ellipsoid(B,(x+side*.088,-.019,.15),(.008,.012,.012),COLLAR,w,16,10)
B.build()

# Deformation skeleton: all meshes remain in an unmodified symmetrical T-pose at rest.
arm=bpy.data.armatures.new('CH_Skeleton');rig=bpy.data.objects.new('CH_Rig',arm);RIGCOL.objects.link(rig)
for o in bpy.context.selected_objects:o.select_set(False)
rig.select_set(True);bpy.context.view_layer.objects.active=rig
bpy.ops.object.mode_set(mode='EDIT')
def bone(name,head,tail,parent=None,connected=False):
    b=arm.edit_bones.new(name);b.head=head;b.tail=tail
    if parent:b.parent=arm.edit_bones[parent];b.use_connect=connected
    return b
bone('Root',(0,0,0),(0,0,.18))
bone('Pelvis',(0,0,.76),(0,0,.88),'Root')
bone('Spine',(0,0,.88),(0,0,1.045),'Pelvis',True)
bone('Chest',(0,0,1.045),(0,0,1.22),'Spine',True)
bone('Neck',(0,0,1.22),(0,0,1.33),'Chest',True)
bone('Head',(0,0,1.33),(0,0,1.84),'Neck',True)
for side,suffix in [(1,'L'),(-1,'R')]:
    bone('UpperArm.'+suffix,(side*.222,0,1.195),(side*.535,0,1.195),'Chest')
    bone('Forearm.'+suffix,(side*.535,0,1.195),(side*.778,0,1.195),'UpperArm.'+suffix,True)
    bone('Hand.'+suffix,(side*.778,0,1.195),(side*.882,0,1.195),'Forearm.'+suffix,True)
    bone('Thigh.'+suffix,(side*.145,0,.76),(side*.145,0,.43),'Pelvis')
    bone('Shin.'+suffix,(side*.145,0,.43),(side*.145,0,.17),'Thigh.'+suffix,True)
    bone('Foot.'+suffix,(side*.145,0,.17),(side*.145,-.16,.08),'Shin.'+suffix,True)
    for n1,n2,a,b,c in FINGERS[suffix]:
        bone(n1,a,b,'Hand.'+suffix);bone(n2,b,c,n1,True)
bpy.ops.object.mode_set(mode='OBJECT')
rig.show_in_front=True
arm.display_type='OCTAHEDRAL'
for o in GEO.objects:
    o.parent=rig
    m=o.modifiers.new('CH_Skinning','ARMATURE');m.object=rig;m.use_deform_preserve_volume=False
for p in rig.pose.bones:p.rotation_mode='QUATERNION'
rig.location=(2.95,-1.85,.255)
rig.rotation_euler.z=math.atan2(1.4-2.95,-(-1.0+1.85))
rig['Reference_turnaround']='Cute Character Turnaround and Parts Sheet(1).png'
rig['Reference_original']='_ (1).jpeg'
rig['Rest_pose']='T-pose; +Z up, character faces -Y, anatomical left is +X.'
rig['Scale']='metres; approximately 1.94 m including hair; rig and mesh object scales are 1.'
rig['Binding']='Analytic normalized skin weights; no external rigging dependency.'
rig['Usage']='Move CH_Rig to move the complete character. Clear action and pose transforms to inspect T-pose.'
with open(OUT+'/character-build.json','w') as f:json.dump({'meshes':[o.name for o in GEO.objects],'bones':[b.name for b in arm.bones],'location':list(rig.location),'rotation_z':rig.rotation_euler.z,'source_project':bpy.data.filepath},f,indent=2)
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
print(json.dumps({'stage':'model_rig_created','mesh_objects':len(GEO.objects),'bones':len(arm.bones),'vertices':sum(len(o.data.vertices) for o in GEO.objects),'bounds_height':max(v.co.z for o in GEO.objects for v in o.data.vertices)}))
