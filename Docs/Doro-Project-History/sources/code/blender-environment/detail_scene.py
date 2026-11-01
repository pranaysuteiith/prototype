import bpy, math, random, os, json, ast
import numpy as np
from mathutils import Vector
from math import sin,cos,pi
ROOT='/Users/pranay/Documents/Codex/2026-10-22/new-chat-6/outputs';KIT=ROOT+'/doro-unity'
S=bpy.context.scene;random.seed(59)
COL={c.name:c for c in bpy.data.collections};CURRENT='02_Terrace'
MAT=bpy.data.materials['Doro_Painted_Atlas'];WARM=bpy.data.materials['Doro_Warm_Window']
source=ast.parse(open(ROOT+'/../work/doro-build/build_scene.py').read())
exec(compile(ast.Module(body=[n for n in source.body if isinstance(n,ast.FunctionDef)],type_ignores=[]),'doro_helpers','exec'))

def leaf_cloud(name,centers,palette=(13,14,15,16,18),density=180):
    vv=[];ff=[];tiles=[]
    for center,rad in centers:
        center=Vector(center)
        for k in range(density):
            n=Vector((random.uniform(-1,1),random.uniform(-1,1),random.uniform(-1,1)))
            if n.length<.01:continue
            n.normalize();r=rad*random.uniform(.83,1.04)
            p=center+Vector((n.x*r,n.y*r,n.z*r*.85))
            u=n.cross(Vector((0,0,1)))
            if u.length<.01:u=n.cross(Vector((0,1,0)))
            u.normalize();v=n.cross(u).normalized()
            angle=random.random()*pi;u2=u*cos(angle)+v*sin(angle);v2=-u*sin(angle)+v*cos(angle)
            w=random.uniform(.10,.23)*rad;h=w*random.uniform(.55,1.4)
            ix=len(vv)
            vv.extend([p-u2*w,p+v2*h*.8,p+u2*w,p-v2*h,p+n*w*.1])
            ff.extend([(ix,ix+1,ix+4),(ix+1,ix+2,ix+4),(ix+2,ix+3,ix+4),(ix+3,ix,ix+4)])
            brightness=n.z*.4+n.x*-.18+random.uniform(-.35,.35)
            tile=palette[min(len(palette)-1,max(0,int((brightness+.8)/1.6*len(palette))))]
            tiles.extend([tile]*4)
    o=mesh(name,vv,ff,14);layer=o.data.uv_layers.active
    for poly,tile in zip(o.data.polygons,tiles):
        col,row=tile%8,tile//8
        coords=[(.05,.12),(.85,.15),(.45,.88)]
        for k,xy in zip(poly.loop_indices,coords):layer.data[k].uv=((col+xy[0])/8,(row+xy[1])/8)
    return o

def bush(name,x,y,z,r=.55):
    sphere(name+' painted mass',(x,y,z),(r,r,r*.7),17)
    leaf_cloud(name+' brush foliage',[((x,y,z),r)],(17,13,14,15),70)

def planter(x,y,w=1.1,d=.7,flowers=False):
    box('Cream planter',(x,y,.48),(w,d,.52),1,.04)
    box('Planter soil',(x,y,.76),(w-.12,d-.12,.055),31,.01)
    for i in range(max(1,int(w/.44))):
        xx=x-w*.34+i*.44;bush('Hedge',xx,y,.94,.38)
        if flowers:
            for j in range(4):sphere('White blossoms',(xx+random.uniform(-.25,.25),y+random.uniform(-.2,.2),1.15+random.uniform(-.06,.15)),(.045,.045,.045),random.choice([1,47,46]),8,4)

def tree(name,x,y,height=5.0,spread=1.65):
    base=.27
    bpy.ops.mesh.primitive_cone_add(vertices=9,radius1=.24,radius2=.13,depth=height*.58,location=(x,y,base+height*.29))
    o=move(bpy.context.object);o.name=name+' hand painted trunk';uv(o,19)
    centers=[]
    for i in range(8):
        angle=i*2*pi/7;rr=spread*.55 if i<7 else 0
        p=(x+cos(angle)*rr,y+sin(angle)*rr,base+height-spread*.4+random.uniform(-.25,.45))
        centers.append((p,spread*random.uniform(.57,.83)))
        rod(name+' fork',(x,y,base+height*.45),p,.075,19)
        sphere(name+' foliage underpainting',p,(spread*.68,spread*.68,spread*.63),random.choice([13,14]),12,8)
    leaf_cloud(name+' gouache leaf dabs',centers,density=170)
    box(name+' tree grate',(x,y,.27),(.95,.95,.07),2,.015)
    for dx in [-.33,-.17,0,.17,.33]:box('Tree grate bars',(x+dx,y,.315),(.035,.86,.01),12,.002)

def chair(name,x,y,angle=0):
    parts=[]
    parts.append(box(name+' seat',(x,y,.84),(.57,.57,.09),6,.025))
    for dx in [-.21,.21]:
        for dy in [-.21,.21]:parts.append(rod(name+' leg',(x+dx*1.15,y+dy*1.15,.28),(x+dx,y+dy,.82),.027,7))
    for dx in [-.23,.23]:parts.append(rod(name+' back',(x+dx,y+.23,.7),(x+dx,y+.23,1.5),.03,7))
    for z in [1.08,1.3,1.48]:parts.append(box(name+' backrest slat',(x,y+.23,z),(.56,.07,.1),6,.015))
    center=Vector((x,y,0))
    from mathutils import Matrix
    rot=Matrix.Rotation(angle,4,'Z')
    for p in parts:p.location=center+rot.to_3x3()@(p.location-center);p.rotation_euler.rotate_axis('Z',angle)

def table(x,y,roundtop=False):
    if roundtop:cyl('Round cafe tabletop',(x,y,1.1),.64,.10,6,24)
    else:
        for j in range(5):box('Table timber plank',(x,y-.54+j*.27,1.1),(1.4,.255,.09),random.choice([5,6,56]),.012)
    for dx in [-.49,.49]:
        for dy in [-.40,.40]:rod('Table steel legs',(x+dx,y+dy,.28),(x+dx*.85,y+dy*.85,1.05),.035,12)
    for xx,yy in [(x-.3,y),(x+.26,y+.2)]:
        cyl('Coffee saucer',(xx,yy,1.17),.1,.025,1,20)
        cyl('Coffee cup',(xx,yy,1.24),.065,.12,1,16)
        cyl('Coffee surface',(xx,yy,1.305),.055,.006,31,16)
    box('Table menu',(x+.3,y-.22,1.17),(.22,.30,.018),40,.006,rotation=.2)

CURRENT='02_Terrace'
for x,y in [(-5.9,-2.9),(-5.9,-1.6),(-7.8,.2),(-7.8,1.5),(3.25,-2.8),(3.25,0),(3.25,5.1),(-2.4,-3.6),(-.9,-3.6)]:planter(x,y,1.1,.65,True)
for x,y in [(-6.1,1.0),(-6.5,3.0),(-4.9,-2.55)]:
    table(x,y);chair('Cafe chair',x-.8,y,pi/2);chair('Cafe chair',x+.8,y,-pi/2)
# Umbrella: sixteen lightly irregular stitched panels.
rod('Umbrella wooden pole',(-6.4,2.9,.3),(-6.4,2.9,3.3),.045,5)
for i in range(16):
    a=i*pi/8;b=(i+1)*pi/8;r=1.28
    verts=[(-6.4,2.9,3.55),(-6.4+r*.55*cos(a),2.9+r*.55*sin(a),3.29),(-6.4+r*cos(a),2.9+r*sin(a),2.94),(-6.4+r*cos(b),2.9+r*sin(b),2.94),(-6.4+r*.55*cos(b),2.9+r*.55*sin(b),3.29)]
    mesh('Ivory parasol fabric',verts,[(0,1,4),(1,2,3,4)],1 if i%2 else 40)
    rod('Parasol seam',verts[0],verts[2],.012,37)
sphere('Parasol finial',(-6.4,2.9,3.59),(.08,.08,.10),5)
# Picnic bench near front of terrace.
for y in [-2.0,-2.8]:
    for j in range(3):box('Bench seat plank',(-.8,y+j*.09,.79),(2.5,.082,.07),6,.008)
    for x in [-1.7,.1]:box('Bench metal foot',(x,y+.1,.52),(.12,.4,.54),12,.02)
for j in range(5):box('Picnic tabletop',(-.8,-2.4+j*.15,1.1),(2.65,.14,.09),6,.014)
for x in [-1.7,.1]:rod('Picnic trestle',(x,-2.9,.28),(x,-2.15,1.06),.05,7)
# Blackboard sandwich board.
board=box('Chalkboard wood frame',(2.7,-3.4,.98),(.84,.12,1.25),5,.02);board.rotation_euler.x=-.1
box('Chalkboard painted face',(2.7,-3.48,1.02),(.72,.018,1.1),12,.008)
text('Menu heading','TODAY',(2.7,-3.50,1.31),.15,1)
text('Menu chalk','COFFEE\n& CAKE',(2.7,-3.51,1.00),.12,1)
for x in [2.38,3.02]:rod('Chalkboard feet',(x,-3.1,.26),(x,-3.42,1.6),.035,5)

CURRENT='03_Trees'
for args in [('Lime tree west',-6.0,5.7,5.5,1.55),('Lime tree terrace',-8.0,-1.7,4.0,1.22),('Lime tree east',3.5,4.9,4.3,1.25),('Background tree west',-13,8.2,5.5,1.6),('Background tree east',13.2,9,5.5,1.7),('Foreground tree',-5.5,-12.5,4.1,1.4),('Far tree',-1,12,5.5,1.5)]:tree(*args)
# Ivy on roof fascia and trailing down the sign's edges; actual leaves, no view-dependent decal.
for x in np.arange(-3.8,2.3,.34):
    leaf_cloud('Roof ivy brush dabs',[((float(x),-1.06,6.82),.25)],(17,13,14,15),35)
    if random.random()<.65:
        length=random.uniform(.4,1.4)
        for z in np.arange(6.7,6.7-length,-.20):leaf_cloud('Trailing ivy',[((float(x)+random.uniform(-.07,.07),-1.13,float(z)),.17)],(17,13,14,15),15)
for y in np.arange(-.7,4.9,.36):leaf_cloud('Side roof ivy',[((2.48,float(y),6.83),.24)],(17,13,14,15),28)
for x,y in [(3.35,1.5),(-4.5,-.5),(-4.5,4.5)]:
    cyl('Terracotta tree pot',(x,y,.58),.38,.65,6)
    bush('Potted topiary',x,y,1.45,.48)

def character(name,x,y,shirt=24,angle=0,seated=False):
    global CURRENT
    root=empty(name,(x,y,.27));parts=[]
    def sp(n,loc,sc,tile):
        o=sphere(name+' '+n,(0,0,0),sc,tile,12,8);o.parent=root;o.location=loc;parts.append(o);return o
    def rd(n,a,b,r,tile):
        o=rod(name+' '+n,a,b,r,tile);o.parent=root;parts.append(o);return o
    if seated:
        hip=.68;sp('trousers',(0,0,hip),(.17,.15,.15),22)
        for dx in [-.105,.105]:
            rd('thigh',(dx,0,hip),(dx,-.28,hip-.02),.075,22)
            rd('shin',(dx,-.28,hip-.02),(dx,-.28,.15),.065,22)
            sp('shoe',(dx,-.34,.11),(.09,.16,.07),21)
    else:
        hip=.79;sp('trousers',(0,0,hip),(.17,.13,.16),22)
        for dx,dy in [(-.10,.05),(.10,-.08)]:
            rd('trouser leg',(dx,0,hip),(dx,dy,.14),.078,22)
            sp('shoe',(dx,dy-.04,.09),(.10,.17,.075),21)
    sp('shirt',(0,0,hip+.32),(.23,.15,.33),shirt)
    rd('neck',(0,0,hip+.55),(0,0,hip+.67),.07,20)
    sp('head',(0,-.015,hip+.84),(.21,.18,.25),20)
    sp('sculpted dark hair',(0,.025,hip+.96),(.23,.185,.17),21)
    sp('hair fringe',(-.10,-.15,hip+.95),(.13,.07,.12),21)
    for dx in [-.075,.075]:sp('eye',(dx,-.184,hip+.86),(.018,.013,.025),21)
    sp('nose',(0,-.19,hip+.79),(.035,.038,.04),20)
    for dx in [-.24,.24]:
        elbow=(dx*1.15,-.04,hip+.23);hand=(dx*1.15,-.2,hip+.12) if seated else (dx*1.05,-.04,hip-.03)
        rd('sleeve',(dx,0,hip+.49),elbow,.085,shirt);rd('forearm',elbow,hand,.062,20);sp('hand',hand,(.069,.063,.08),20)
    root.rotation_euler.z=angle
    return root

CURRENT='06_Characters'
character('Customer mustard',.2,-2.15,23,.08)
character('Customer denim',.83,-2.05,24,-.1)
character('Customer coral',1.5,-2.0,25,.12)
character('Seated visitor blue',-6.9,1,24,-pi/2,True)
character('Seated visitor ivory',-5.7,3,1,pi/2,True)
character('Laptop visitor coral',-.7,-2.9,25,pi,True)
character('Pedestrian yellow',-7.9,-3.1,23,.4)
character('Pedestrian blue',2.1,-3.8,24,-.7)
character('Far pedestrian',12,2.2,25,.3)
CURRENT='02_Terrace'
box('Laptop keyboard',(-.65,-2.30,1.20),(.45,.34,.028),43,.008)
laptop=box('Laptop screen',(-.65,-2.12,1.37),(.45,.035,.31),21,.012);laptop.rotation_euler.x=-.16
box('Laptop lit display',(-.65,-2.145,1.37),(.38,.012,.25),43,.005)

def lamp(x,y):
    cyl('Streetlamp pedestal',(x,y,.46),.18,.40,12)
    cyl('Streetlamp shaft',(x,y,1.75),.055,2.45,12)
    cyl('Streetlamp collar',(x,y,2.94),.14,.08,12)
    sphere('Frosted streetlamp globe',(x,y,3.2),(.24,.24,.29),1,16,10)
    cyl('Streetlamp crown',(x,y,3.48),.11,.045,12)

def signal(x,y,rotation=0):
    cyl('Signal pole',(x,y,1.8),.06,3.1,12)
    box('Traffic light housing',(x,y,3.05),(.26,.22,.73),12,.035,rotation)
    for i,tile in enumerate([26,28,8]):
        sphere('Signal lens',(x,y-.125,3.26-i*.22),(.072,.025,.072),tile,12,6)

CURRENT='04_Street'
for x,y in [(-8.9,-3.8),(4.,-3.8),(-2,-3.9),(11.3,-3.5),(3.9,8.5),(-9,8),(-1,-10.5),(11.2,-11.)]:lamp(x,y)
for x,y in [(4.0,-4.0),(11.1,-10.1)]:signal(x,y)
for x,y in [(-8,-4),(3,-4),(4,-1),(11.3,-3),(11.2,-11.3),(1,-10.4)]:
    cyl('Iron bollard',(x,y,.68),.09,.8,12);sphere('Bollard cap',(x,y,1.08),(.1,.1,.09),12)

def car(name,x,y,color,angle=0):
    root=empty(name,(x,y,.11));parts=[]
    def bx(n,loc,sz,tile,b=.07):
        o=box(name+' '+n,(0,0,0),sz,tile,b);o.parent=root;o.location=loc;parts.append(o);return o
    bx('rounded body',(0,0,.56),(1.48,2.65,.68),color,.19)
    bx('cabin',(0,.10,1.10),(1.32,1.40,.68),color,.18)
    bx('windscreen',(0,-.61,1.17),(1.10,.045,.43),11,.03)
    bx('back window',(0,.81,1.17),(1.08,.045,.38),11,.03)
    for dx in [-.674,.674]:
        bx('side glass',(dx,.1,1.18),(.026,1.1,.4),11,.02)
        bx('window pillar',(dx,.08,1.2),(.04,.07,.45),color,.01)
        for yy in [-.86,.88]:
            o=cyl(name+' rubber tyre',(0,0,0),.29,.17,21,16);o.parent=root;o.location=(dx*1.12,yy,.31);o.rotation_euler.y=pi/2
            o=cyl(name+' wheel hub',(0,0,0),.14,.18,38,12);o.parent=root;o.location=(dx*1.14,yy,.31);o.rotation_euler.y=pi/2
    bx('front bumper',(0,-1.36,.41),(1.31,.10,.14),38,.035)
    for dx in [-.49,.49]:bx('headlamp',(dx,-1.36,.65),(.29,.04,.16),1,.045)
    bx('rear bumper',(0,1.35,.4),(1.3,.08,.13),38,.025)
    root.rotation_euler.z=angle
    return root

car('Red little hatchback',-7.0,-6.0,26,pi/2)
car('Blue little hatchback',8.8,1.1,27,0)
car('Yellow distant hatchback',6.1,10.5,28,pi)

def bicycle(x,y,color=8):
    wheels=[(x-.55,y,.63),(x+.55,y,.63)]
    for p in wheels:
        bpy.ops.mesh.primitive_torus_add(major_radius=.32,minor_radius=.024,major_segments=20,minor_segments=6,location=p,rotation=(pi/2,0,0))
        o=move(bpy.context.object);o.name='Bicycle tyre';uv(o,21)
        for a in np.arange(0,pi,pi/6):rod('Bicycle spoke',(p[0]-.30*cos(a),y,p[2]-.30*sin(a)),(p[0]+.30*cos(a),y,p[2]+.30*sin(a)),.006,38,6)
    a=(x-.55,y,.63);b=(x-.12,y,1.02);c=(x+.05,y,.61);d=(x+.35,y,1.04);e=(x+.55,y,.63)
    for p,q in [(a,b),(b,c),(c,a),(b,d),(d,c),(d,e)]:rod('Bicycle painted frame',p,q,.022,color)
    rod('Bicycle seatpost',b,(x-.15,y,1.16),.022,12)
    box('Bicycle saddle',(x-.15,y,1.17),(.23,.12,.065),21,.03)
    rod('Bicycle handlebar stem',d,(x+.32,y,1.26),.02,12)
    rod('Bicycle handlebar',(x+.32,y-.17,1.26),(x+.32,y+.17,1.26),.02,12)

CURRENT='02_Terrace'
for i in range(4):bicycle(1.4+i*.25,-3.9+i*.48,[8,28,12,26][i])
rod('Bicycle rack',(1,-4.05,.45),(3.4,-1.3,.45),.04,12)

def neighbour(name,x,y,w,d,h,awning):
    box(name+' painted facade',(x,y,.28+h/2),(w,d,h),random.choice([0,35,40]),.06)
    box(name+' roof rim',(x,y,h+.4),(w+.2,d+.2,.25),1,.04)
    box(name+' roof inset',(x,y,h+.55),(w-.3,d-.3,.08),30,.02)
    for xx in [x-w*.27,x+w*.27]:
        for z in [1.8,h-1.2]:
            box(name+' window frame',(xx,y-d/2-.06,z),(w*.31,.08,1.4),5,.02)
            box(name+' window',(xx,y-d/2-.11,z),(w*.27,.025,1.27),10,.01)
    for i in range(10):
        box(name+' stripe',(x-w/2+w*(i+.5)/10,y-d/2-.52,2.9),(w/10,.92,.12),awning if i%2 else 1,.01)

CURRENT='05_Neighbours'
neighbour('Bakery west',-13,4.8,5.2,5.6,5.0,28)
neighbour('Bookshop east',14,4.5,4.8,5.4,5.8,27)
neighbour('Townhouse back',-1.0,12.8,6.,4.,5.,25)
neighbour('Foreground atelier',-12,-13,5.5,4.5,4.,25)
neighbour('South east shop',14,-13,5.,4.5,4.2,27)
print('DORO_STAGE_2_OK',len(S.objects),'meshes',sum(o.type=='MESH' for o in S.objects))
bpy.ops.wm.save_as_mainfile(filepath=ROOT+'/doro-style.blend')
