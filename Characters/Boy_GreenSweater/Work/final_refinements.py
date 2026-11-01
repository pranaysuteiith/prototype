from pathlib import Path
p=Path('/Users/pranay/My project/Characters/Boy_GreenSweater/Work/build_boy.py');s=p.read_text()
# Replace raised cheek patches with a continuous sculpted cheek surface and a baked gradient.
start=s.index('# Blush patches conform');end=s.index("rigid_head(tube('CH_Mouth'",start)
s=s[:start]+'''# Cheek volumes are sculpted into the head; blush is baked, avoiding raised sticker-like patches.
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
''' +s[end:]
s=s.replace("texture=raw.name", "texture=raw.name")
# Bake a tangent-space normal texture from the same small-scale fabric/curl patterns.
old="noise=m.node_tree.nodes.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=260 if kind=='wool' else 150;noise.inputs['Detail'].default_value=2\n  bump=m.node_tree.nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.12;bump.inputs['Distance'].default_value=.00035;m.node_tree.links.new(noise.outputs['Fac'],bump.inputs['Height']);m.node_tree.links.new(bump.outputs['Normal'],bs.inputs['Normal'])"
new="""n=512;yy,xx=np.mgrid[0:n,0:n];h=np.sin(xx*2*pi/9)*np.sin(yy*2*pi/7) if kind=='wool' else np.sin((xx+7*np.sin(yy/15))*2*pi/21) if kind=='hair' else np.sin(xx*2*pi/5)*np.sin(yy*2*pi/5)
  dy,dx=np.gradient(h);norm=np.stack((-dx*.18,-dy*.18,np.ones_like(h)),axis=-1);norm/=np.linalg.norm(norm,axis=-1,keepdims=True);pixels=np.ones((n,n,4),dtype=np.float32);pixels[:,:,:3]=norm*.5+.5
  normal=bpy.data.images.new(name+'_Normal',width=n,height=n,alpha=False);normal.colorspace_settings.name='Non-Color';normal.pixels.foreach_set(pixels.ravel());normal.file_format='PNG';normal.filepath_raw=ROOT+'/Textures/'+name+'_Normal.png';normal.save();normal.pack()
  tn=m.node_tree.nodes.new('ShaderNodeTexImage');tn.image=normal;nm=m.node_tree.nodes.new('ShaderNodeNormalMap');nm.inputs['Strength'].default_value=.65;m.node_tree.links.new(tn.outputs['Color'],nm.inputs['Color']);m.node_tree.links.new(nm.outputs['Normal'],bs.inputs['Normal'])"""
s=s.replace(old,new)
# Use one row's stable latitude as the basis for every paired clump.
s=s.replace(" for i in range(count):\n  p=", " row_t=t\n for i in range(count):\n  p=").replace('t0=t;t=t0+', 't0=row_t;t=t0+')
p.write_text(s)
