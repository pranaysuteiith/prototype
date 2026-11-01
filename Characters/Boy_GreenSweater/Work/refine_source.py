from pathlib import Path
p=Path('/Users/pranay/My project/Characters/Boy_GreenSweater/Work/build_boy.py');s=p.read_text()
s=s.replace("n=512;yy,xx=np.mgrid[0:n,0:n];rng=np.random.default_rng(41)","color=tuple(12.92*v if v<=.0031308 else 1.055*v**(1/2.4)-.055 for v in color)\n n=512;yy,xx=np.mgrid[0:n,0:n];rng=np.random.default_rng(41)")
s=s.replace("(0,.003,.929),(.190,.147,.178)","(0,.003,.949),(.190,.147,.163)")
s=s.replace("rigid_head(mesh('CH_Cheeks',*combine([sphere_data((s*.113,-.132,.864),(.028,.004,.014),16,8) for s in [-1,1]]),'MAT_Skin_Blush'))",'''# Blush patches conform exactly to the rounded head, with a soft baked color falloff.
parts=[]
for side in [-1,1]:
 vv=[];ff=[];n=20
 for back in [False,True]:
  for j in range(1,5):
   r=j/4
   for i in range(n):
    a=2*pi*i/n;x=side*.108+.027*r*cos(a);z=.869+.014*r*sin(a)
    term=max(.01,1-(abs(x)/.190)**(2/.84)-(abs(z-.949)/.163)**(2/.84))
    y=.003-.147*term**(.84/2)+(.001 if back else -.0003);vv.append((x,y,z))
 for base in [0,80]:
  ff.append(tuple(base+i for i in range(n-1,-1,-1)))
  for j in range(3):
   for i in range(n):a=base+j*n+i;b=base+j*n+(i+1)%n;ff.append((a,b,b+n,a+n))
 for i in range(n):a=60+i;b=60+(i+1)%n;ff.append((a,b,b+80,a+80))
 parts.append((vv,ff))
cheeks=rigid_head(mesh('CH_Cheeks',*combine(parts),'MAT_Skin_Blush'))
n=256;yy,xx=np.mgrid[0:n,0:n];u=(xx/(n-1)-.5)*2;v=(yy/(n-1)-.5)*2;blend=.26*np.exp(-3.5*(u*u+v*v))
base=np.array([240,189,150])/255;pink=np.array([230,125,115])/255;px=np.ones((n,n,4),dtype=np.float32);px[:,:,:3]=base*(1-blend[:,:,None])+pink*blend[:,:,None]
img=bpy.data.images.new('Skin_Blush_Gradient',width=n,height=n,alpha=False);img.pixels.foreach_set(px.ravel());img.file_format='PNG';img.filepath_raw=ROOT+'/Textures/Skin_Blush_Gradient.png';img.save();img.pack()
node=M['MAT_Skin_Blush'].node_tree.nodes.new('ShaderNodeTexImage');node.image=img;M['MAT_Skin_Blush'].node_tree.links.new(node.outputs['Color'],next(n for n in M['MAT_Skin_Blush'].node_tree.nodes if n.type=='BSDF_PRINCIPLED').inputs['Base Color'])
for poly in cheeks.data.polygons:
 for k in poly.loop_indices:
  co=cheeks.data.vertices[cheeks.data.loops[k].vertex_index].co;center=.108 if co.x>0 else -.108;cheeks.data.uv_layers.active.data[k].uv=((co.x-center)/.054+.5,(co.z-.869)/.028+.5)
''')
s=s.replace("(.22,5),(.52,10),(.82,14),(1.10,16),(1.39,18),(1.68,16),(1.98,12),(2.20,8)","(.22,4),(.56,8),(.92,10),(1.25,12),(1.57,12),(1.89,10),(2.17,8)")
s=s.replace("p=2*pi*(i+.5*(j%2))/count;back=(sin(p)+1)/2", "p=2*pi*(i+.5*(j%2))/count;back=(sin(p)+1)/2;t0=t;t=t0+.028*cos(2*p)*sin(j*2)")
s=s.replace("r=.028*(1+.12*cos(i*2*pi/count*4+j))", "r=.035*(1+.10*cos(4*p)*cos(j*.7))")
s=s.replace("vv,ff=sphere_data(c,(r*1.1,r*.90,r*.91),10,5,.9)", "vv,ff=sphere_data(c,(r*1.12,r*.94,r*.94),12,6,1)")
s=s.replace("x+.003*sin((z-c[2])/max(r,.001)*pi)","x+math.copysign(1,cos(p))*.004*sin((z-c[2])/max(r,.001)*pi)")
s=s.replace("vv=[(x+math.copysign", "vv=[(x+math.copysign")
s=s.replace("parts.append((vv,ff))\nrigid_head(mesh('CH_Hair_Clumps'", "parts.append((vv,ff));t=t0\nrigid_head(mesh('CH_Hair_Clumps'")
s=s.replace("x=.081+.075*cos(a);z=.936+.046*sin(a)+.010*max(0,cos(a))*max(0,sin(a))", "x=.081+.075*math.copysign(abs(cos(a))**.65,cos(a));z=.936+.046*math.copysign(abs(sin(a))**.78,sin(a))+.010*max(0,cos(a))*max(0,sin(a))")
s=s.replace("mat('MAT_Sunglasses_Lenses','191713',.21)","mat('MAT_Sunglasses_Lenses','191713',.38)")
s=s.replace("r=1+.024*cos(a*16)","r=1+.009*cos(a*16)")
s=s.replace("(0,0,.771),(0,0,1),.076,.060,.047,48", "(0,0,.759),(0,0,1),.076,.060,.050,32")
s=s.replace("((x,-.101,.036),(.048,.031,.023)", "((x,-.088,.039),(.052,.047,.015)")
s=s.replace("(x-.023,y+.006,.077),(x,y,.087),(x+.023,y-.006,.077)","(x-.023,y+.006,.089),(x,y,.096),(x+.023,y-.006,.089)")
s=s.replace("sin(2*pi*(t+.5*(s<0)))", "cos(2*pi*(t+.5*(s<0)))")
s=s.replace("d['LowerArm.R']=delta('LowerArm.R',(0,0,1),envelope*(.72+.20*sin(8*pi*t)))\n   d['Hand.R']=delta('Hand.R',(0,0,1),envelope*.22*sin(10*pi*t))", "baseline=standing()['UpperArm.R'];fore=Vector((-1,0,0)).rotation_difference(Vector((-.035,-.01,.14)))@rest['LowerArm.R'];d['LowerArm.R']=baseline.slerp(fore,envelope)\n   hand=Quaternion(Vector((-.035,-.01,.14)).normalized(),pi/2+.25*sin(10*pi*t))@fore;d['Hand.R']=baseline.slerp(hand,envelope)")
s=s.replace("d['UpperLeg.'+side]=delta('UpperLeg.'+side,(1,0,0),-1.35*u)\n    d['LowerLeg.'+side]=Quaternion((1,0,0),.10*u)@rest['LowerLeg.'+side]\n    d['Foot.'+side]=rest['Foot.'+side]", "solve_leg(d,side,(s*.068,-.19*u,.09),off)")
p.write_text(s)
