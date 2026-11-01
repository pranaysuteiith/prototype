import bpy,math,random,ast
from mathutils import Vector
from math import pi,sin,cos
ROOT='/Users/pranay/Documents/Codex/2026-10-22/new-chat-6/outputs';S=bpy.context.scene
COL={c.name:c for c in bpy.data.collections};CURRENT='03_Trees';MAT=bpy.data.materials['Doro_Painted_Atlas']
source=ast.parse(open(ROOT+'/../work/doro-build/build_scene.py').read())
exec(compile(ast.Module(body=[n for n in source.body if isinstance(n,ast.FunctionDef)],type_ignores=[]),'helpers','exec'))
random.seed(715)
tiles=[13,14,15,18]
for canopy in [o for o in list(S.objects) if 'gouache leaf dabs' in o.name]:
    prefix=canopy.name.split(' gouache')[0]
    lobes=[o for o in S.objects if o.name.startswith(prefix+' foliage underpainting')]
    verts=[];faces=[];mi=[]
    for lobe in lobes:
        center=lobe.location.copy();r=lobe.scale.x
        for k in range(650):
            n=Vector((random.uniform(-1,1),random.uniform(-1,1),random.uniform(-1,1))).normalized()
            p=center+Vector((n.x*r*1.04,n.y*r*1.04,n.z*r*.96))*random.uniform(.97,1.035)
            u=n.cross(Vector((0,0,1)))
            if u.length<.01:u=n.cross(Vector((0,1,0)))
            u.normalize();v=n.cross(u).normalized()
            a=random.random()*pi;uu=u*cos(a)+v*sin(a);vv=-u*sin(a)+v*cos(a)
            w=r*random.uniform(.065,.12);h=w*random.uniform(.6,1.25);ix=len(verts)
            for j in range(8):
                t=j*math.tau/8;verts.append(p+uu*w*cos(t)+vv*h*sin(t))
            verts.append(p+n*w*.07)
            bright=n.z*.5-n.x*.2+random.uniform(-.45,.4)
            tile=15 if bright>.48 else (18 if bright>.05 else (14 if bright>-.35 else 13))
            for j in range(8):faces.append((ix+j,ix+(j+1)%8,ix+8));mi.append(tiles.index(tile))
    m=bpy.data.meshes.new(prefix+' dense painted canopy');m.from_pydata(verts,[],faces);m.update()
    for t in tiles:m.materials.append(bpy.data.materials['Doro_Leaf_'+str(t)])
    layer=m.uv_layers.new(name='PaintedUV')
    for p,matidx in zip(m.polygons,mi):
        p.material_index=matidx
        for k,xy in zip(p.loop_indices,[(.15,.15),(.85,.15),(.5,.85)]):layer.data[k].uv=xy
    canopy.data=m
# Continuous undergrowth behind individual ivy leaves, plus visible trailing vines.
for x in [-3.8+i*.27 for i in range(24)]:
    o=sphere('Dense roof ivy hedge',(x,-1.015,6.81),(.21,.22,.18),14,10,6)
    o.data.materials.clear();o.data.materials.append(bpy.data.materials['Doro_Leaf_14'])
for y in [-.8+i*.27 for i in range(22)]:
    o=sphere('Dense side roof ivy hedge',(2.45,y,6.81),(.21,.21,.18),14,10,6)
    o.data.materials.clear();o.data.materials.append(bpy.data.materials['Doro_Leaf_14'])
for x,length in [(-3.8,1.2),(-3.3,.7),(-2.9,.45),(-1.7,.85),(-.9,.65),(.3,.6),(1.5,1),(2.2,1.3)]:
    rod('Ivy trailing vine',(x,-1.17,6.76),(x,-1.17,6.76-length),.016,17)
    for j in range(int(length/.12)):
        o=sphere('Ivy paired leaves',(x+(.07 if j%2 else -.07),-1.19,6.68-j*.12),(.095,.032,.075),14,8,5)
        o.data.materials.clear();o.data.materials.append(bpy.data.materials['Doro_Leaf_'+str(random.choice([13,14,18]))])
S.render.resolution_percentage=100;S.cycles.samples=32
bpy.ops.wm.save_as_mainfile(filepath=ROOT+'/doro-style.blend')
bpy.ops.render.render(write_still=True)
print('DORO_FINAL_FOLIAGE_OK')
