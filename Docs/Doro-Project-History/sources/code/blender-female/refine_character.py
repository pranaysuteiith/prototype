import bpy,numpy as np,math,ast
from mathutils import Vector,Quaternion
from math import sin,cos,pi
BASE='/Users/pranay/Documents/Codex/2026-10-22/new-chat-6';OUT=BASE+'/outputs/Characters/CH_Female_v001'
GEO=bpy.data.collections['CH_Female_Geometry']
for k,n in [('SKIN','CH_Skin_Peach'),('HAIR','CH_Hair_SatinBlack')]:globals()[k]=bpy.data.materials[n]
source=ast.parse(open(BASE+'/work/character-build/model_character.py').read())
exec(compile(ast.Module(body=[n for n in source.body if isinstance(n,(ast.FunctionDef,ast.ClassDef))],type_ignores=[]),'char_helpers','exec'))
# Image pixels are sRGB albedo; encode the linear skin values to match the solid skin material.
im=bpy.data.images['CH_Face_Albedo_SRGB'];pixels=np.array(im.pixels[:],dtype=np.float32).reshape(512,1024,4)
rgb=pixels[:,:,:3];pixels[:,:,:3]=np.where(rgb<=.0031308,rgb*12.92,1.055*np.power(rgb,1/2.4)-.055)
im.pixels.foreach_set(pixels.ravel());im.filepath_raw=OUT+'/CH_Face_Albedo.png';im.save();im.pack()
bs=next(n for n in HAIR.node_tree.nodes if n.type=='BSDF_PRINCIPLED');bs.inputs['Roughness'].default_value=.45
if 'Specular IOR Level' in bs.inputs:bs.inputs['Specular IOR Level'].default_value=.25
for name in ['CH_Shoes_PolishedBlack','CH_Eye_GlossBlack']:
    bs=next(n for n in bpy.data.materials[name].node_tree.nodes if n.type=='BSDF_PRINCIPLED');bs.inputs['Roughness'].default_value=.28
# Replace only the newly created fringe mesh. Side tendrils remain separate volumes in the same component.
B=Builder('CH_FrontHair_Refinement')
for side in [-1,1]:
    points=[(side*(.28+.05*sin(t*pi*.75)),-.155-.065*sin(t*pi/2),1.78-.44*t) for t in np.linspace(0,1,24)]
    radii=[.043*(1-.55*t) for t in np.linspace(0,1,24)]
    tube(B,points,radii,HAIR,{'Head':1},16,[r*.65 for r in radii])
control=[(-.36,1.65),(-.30,1.70),(-.19,1.79),(-.12,1.80),(-.08,1.755),(-.025,1.79),(.045,1.75),(.14,1.758),(.21,1.77),(.30,1.70),(.36,1.65)]
def lower(x):
    for i in range(len(control)-1):
        if control[i][0]<=x<=control[i+1][0]:
            t=(x-control[i][0])/(control[i+1][0]-control[i][0]);t=t*t*(3-2*t)
            return control[i][1]*(1-t)+control[i+1][1]*t
    return control[-1][1]
vv=[];ff=[];cols,rows=97,21
for j in range(rows):
    t=j/(rows-1)
    for i in range(cols):
        x=-.36+.72*i/(cols-1);top=1.938-.22*(abs(x)/.38)**2
        z=top*(1-t)+lower(x)*t
        y=-.025-(.287*math.sqrt(max(.06,1-(x/.4)**2))-.025)*sin(t*pi/2)
        y-=.013*sin(t*pi)
        vv.append((x,y,z))
for j in range(rows-1):
    for i in range(cols-1):
        a=j*cols+i;ff.append((a,a+cols,a+cols+1,a+1))
B.add(vv,ff,HAIR,{'Head':1})
temp=B.build();target=bpy.data.objects['CH_Hair_Front'];target.data=temp.data
bpy.data.objects.remove(temp,do_unlink=True)
thickness=target.modifiers.new('CH_Fringe_Thickness','SOLIDIFY');thickness.thickness=.022;thickness.offset=-.1
# Smooth shoulder transitions without changing the horizontal T-pose or skeleton.
for side,suffix in [(1,'L'),(-1,'R')]:
    B=Builder('CH_ArmRefine_'+suffix)
    def aw(p):
        x=abs(p.x)
        if x<.29:return mix_weights('Chest','UpperArm.'+suffix,smooth((x-.18)/.11))
        return mix_weights('UpperArm.'+suffix,'Forearm.'+suffix,smooth((x-.48)/.11))
    points=[(side*(.205+t*.575),0,1.195) for t in np.linspace(0,1,37)]
    tube(B,points,[.068*(1-t)+.042*t for t in np.linspace(0,1,37)],SKIN,aw,20)
    ellipsoid(B,(side*.225,0,1.195),(.074,.067,.067),SKIN,aw,28,18)
    temp=B.build();old=bpy.data.objects['CH_Arm_'+suffix]
    # Match the group index order before replacing mesh data.
    old.vertex_groups.clear()
    for vg in temp.vertex_groups:old.vertex_groups.new(name=vg.name)
    old.data=temp.data;bpy.data.objects.remove(temp,do_unlink=True)
face=bpy.data.objects['CH_Face']
center=Vector((0,-.268,1.515))
for v in list(face.data.vertices)[:273]:v.co=center+(v.co-center)*.58
for name in ['CH_Hair_Front','CH_Arm_L','CH_Arm_R','CH_Face']:bpy.data.objects[name].data.update()
studio=bpy.data.scenes['CH_Character_Preview_Studio'];studio.render.filepath=OUT+'/CH_Front_TPose.png'
bpy.ops.render.render(write_still=True,scene=studio.name)
print('CHARACTER_REFINEMENT_RENDER_READY')
