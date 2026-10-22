import bpy, math, json
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
R=Path(__file__).resolve().parent
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
sc=bpy.context.scene;sc.render.engine='CYCLES';sc.cycles.samples=32;sc.cycles.use_denoising=True
sc.render.resolution_x=1600;sc.render.resolution_y=900;sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG'
sc.view_settings.view_transform='AgX';sc.world.color=(.055,.05,.045)
def mat(name,color,rough=.4,metal=0):
 m=bpy.data.materials.new(name);m.use_nodes=True;n=m.node_tree.nodes.get('Principled BSDF');n.inputs['Base Color'].default_value=(*color,1);n.inputs['Roughness'].default_value=rough;n.inputs['Metallic'].default_value=metal;return m
stone=mat('Dark warm limestone',(.032,.023,.018),.75);dark=mat('Obsidian marble',(.027,.022,.018),.24);gold=mat('Brushed warm bronze',(.43,.24,.10),.24,.8);wood=mat('Smoked walnut',(.045,.016,.008),.35)
for material,scale,strength in [(stone,7,.24),(dark,2.4,.12),(wood,18,.2)]:
 n=material.node_tree.nodes;l=material.node_tree.links;noise=n.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=scale;noise.inputs['Detail'].default_value=5
 bump=n.new('ShaderNodeBump');bump.inputs['Strength'].default_value=strength;bump.inputs['Distance'].default_value=.035;l.new(noise.outputs['Fac'],bump.inputs['Height']);l.new(bump.outputs[0],n.get('Principled BSDF').inputs['Normal'])
def box(name,loc,size,material,bevel=.025):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=name;o.dimensions=size;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(material)
 if bevel:mod=o.modifiers.new('Sculpted edge','BEVEL');mod.width=bevel;mod.segments=4;o.modifiers.new('Corner normals','WEIGHTED_NORMAL')
 return o
def cyl(name,loc,radius,depth,material):
 bpy.ops.mesh.primitive_cylinder_add(vertices=128,radius=radius,depth=depth,location=loc);o=bpy.context.object;o.name=name;o.data.materials.append(material);mod=o.modifiers.new('Polished lip','BEVEL');mod.width=.035;mod.segments=4;o.modifiers.new('Smooth rim normals','WEIGHTED_NORMAL');return o
box('Continuous dark hall',(0,0,-.18),(22,20,.3),dark)
box('Warm monumental back wall',(0,3,7),(20,.5,16),stone,.08)
# Repeated vertical reveals and stone joints keep depth in a single unified hall.
for x in [-7,-4.8,0,4.8,7]:box('Stone pier',(x,2.6,3.5),(.20,.30,7),stone,.04)
for x in [-6,-1,1,6]:box('Vertical bronze reveal',(x,2.39,3.6),(.018,.025,6.6),gold,.006)
for x in [-2.7,2.7]:
 cyl('Stepped black stone plinth',(x,0,.13),1.6,.26,dark);cyl('Bronze monument base',(x,0,.35),1.36,.20,gold);cyl('Dark top contact',(x,0,.475),1.29,.05,dark)
# Actual Grand Hotel outlines extruded as sculpture, not a substituted logo.
font=bpy.data.fonts.load(str(R/'grand-hotel-bound.ttf'))
for word,z,size in [('Kids',2.15,2.05),('Capsule',.65,1.40)]:
 curve=bpy.data.curves.new('Bound Grand Hotel '+word,'FONT');curve.body=word;curve.font=font;curve.align_x='CENTER';curve.size=size;curve.extrude=.12;curve.bevel_depth=.015;curve.bevel_resolution=4
 obj=bpy.data.objects.new('Kids font statue '+word,curve);bpy.context.collection.objects.link(obj);obj.location=(-2.7,-.12,z);obj.rotation_euler=(math.pi/2,0,0);obj.data.materials.append(gold)
# A real, shut architectural screen conceals the right monument at entry.
# Bronze support framework ties both word groups to the plinth.
for x in [-3.4,-2.0]:box('Wordmark support column',(x,.10,1.35),(.018,.045,1.7),gold,.006)
# Back stanchions support the lettering without visible crossbars.
for x in []:
 o=box('Sole contact shadow proxy',(x,-.04,.56),(.43,.42,.12),dark,.07);o.visible_camera=False
# Arched bronze surround continues the hall vocabulary of the other monument scenes.
for cx in [-2.7,2.7]:
 points=[(cx-1.72,.55,.5),(cx-1.72,.55,3.7)]
 for i in range(25):
  theta=math.pi-i*math.pi/24;points.append((cx+1.72*math.cos(theta),.55,3.7+1.3*math.sin(theta)))
 points.append((cx+1.72,.55,.5))
 cu=bpy.data.curves.new('Monument arch','CURVE');cu.dimensions='3D';cu.bevel_depth=.018;cu.bevel_resolution=3;sp=cu.splines.new('POLY');sp.points.add(len(points)-1)
 for p,co in zip(sp.points,points):p.co=(*co,1)
 ob=bpy.data.objects.new('Bronze architectural arch',cu);bpy.context.collection.objects.link(ob);ob.data.materials.append(gold)
doors=[]
for sign in [-1,1]:
 x=2.7+sign*.75;doors.append(box('Concealing walnut shutter',(x,-.25,2.52),(1.48,.14,4.08),wood,.05));doors.append(box('Bronze shutter edge',(2.7+sign*.018,-.335,2.52),(.018,.018,4.0),gold,.006))
# Large neutral frontal light follows canonical source illumination.
def light(name,loc,power,size,color,target):
 bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.name=name;o.data.energy=power;o.data.shape='DISK';o.data.size=size;o.data.color=color;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
light('Soft neutral character key',(-3,-6,7),600,5,(1,.96,.9),(2.7,0,2))
light('Bronze left edge',(-4,0,4.7),500,2,(1,.57,.26),(-2.7,0,1.8))
light('Warm back reveal',(2.7,2,5),500,2,(1,.65,.36),(2.7,0,2))
light('Frontal fill',(5,-5,4),95,4,(.80,.88,1),(2.7,0,2))
bpy.ops.object.camera_add(location=(0,-13.8,3.5));camera=bpy.context.object;camera.rotation_euler=(Vector((0,0,2.15))-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.type='PERSP';camera.data.lens=46;sc.camera=camera
def contacts(scale,cx):
 for ob in list(bpy.data.objects):
  if ob.name.startswith('Sole micro contact'):bpy.data.objects.remove(ob,do_unlink=True)
 w=sc.render.resolution_x;h=sc.render.resolution_y
 foot=world_to_camera_view(sc,camera,Vector((cx,0,.51)));fx=foot.x*w;fy=(1-foot.y)*h
 matrix=camera.calc_matrix_camera(bpy.context.evaluated_depsgraph_get(),x=w,y=h)@camera.matrix_world.inverted();inverse=matrix.inverted()
 def floor_point(px,py):
  v=inverse@Vector((2*px/w-1,1-2*py/h,0,1));point=Vector((v.x/v.w,v.y/v.w,v.z/v.w));direction=point-camera.location;t=(.501-camera.location.z)/direction.z;return camera.location+direction*t
 for sx,sy in [(414,1001),(620,1000)]:
  px=fx+(sx-512)*scale;py=fy+(sy-1005)*scale;pos=floor_point(px,py);edge=floor_point(px+55*scale,py)
  bpy.ops.mesh.primitive_uv_sphere_add(segments=48,ring_count=16,radius=1,location=(pos.x,pos.y,.503));o=bpy.context.object;o.name='Sole micro contact';o.scale=(abs(edge.x-pos.x),.115,.004);o.visible_camera=False;o.data.materials.append(dark)
sc.render.filepath=str(R/'hero-desktop-concealed-r5.png');bpy.ops.render.render(write_still=True)
for o in doors:o.hide_render=True
contacts(.55,2.7)
sc.render.filepath=str(R/'hero-desktop-world-r5.png');bpy.ops.render.render(write_still=True)
def placement(label,w,h,scale,cx):
 point=world_to_camera_view(sc,camera,Vector((cx,0,.51)));foot=[point.x*w,(1-point.y)*h]
 return {'resolution':[w,h],'character_foot_anchor':foot,'source_placement':{'x':round(foot[0]-512*scale),'y':round(foot[1]-1005*scale),'scale':scale}}
rows={'desktop':placement('desktop',1600,900,.55,2.7)}
# Mobile scene is authored separately; no crop drops either statue.
for ob in list(bpy.data.objects):
 if ob.type not in {'LIGHT','CAMERA'}:
  ob.location.x*=.60
  if ob.type=='MESH' and ('base' in ob.name or 'plinth' in ob.name or 'contact' in ob.name):ob.scale.x*=.85
  if ob.type=='FONT':ob.scale*=.88
  if 'shutter' in ob.name:ob.scale.x*=.84
  if 'support' in ob.name:ob.scale.x*=.7
  if 'arch' in ob.name:ob.scale.x*=.85
camera.location=(0,-12.4,3.2);camera.rotation_euler=(Vector((0,0,2.1))-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.lens=48
sc.render.resolution_x=900;sc.render.resolution_y=1200
for o in doors:o.hide_render=False
sc.render.filepath=str(R/'hero-mobile-concealed-r5.png');bpy.ops.render.render(write_still=True)
for o in doors:o.hide_render=True
top=world_to_camera_view(sc,camera,Vector((2.7*.60,0,4.48)));bottom=world_to_camera_view(sc,camera,Vector((2.7*.60,0,.51)));contact_scale=(top.y-bottom.y)*1200*.94/974
contacts(contact_scale,2.7*.60)
sc.render.filepath=str(R/'hero-mobile-world-r5.png');bpy.ops.render.render(write_still=True)
top=world_to_camera_view(sc,camera,Vector((2.7*.60,0,4.48)));bottom=world_to_camera_view(sc,camera,Vector((2.7*.60,0,.51)));mobile_scale=(top.y-bottom.y)*1200*.94/974
rows['mobile']=placement('mobile',900,1200,mobile_scale,2.7*.60)
(R/'hero-placement-r5.json').write_text(json.dumps(rows,indent=2)+'\n')
bpy.ops.wm.save_as_mainfile(filepath=str(R/'kids-statue-hero-r5.blend'))
