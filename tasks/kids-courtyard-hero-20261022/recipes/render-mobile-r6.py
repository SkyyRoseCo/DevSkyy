import bpy,json
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(R/'kids-statue-hero-r5.blend'))
sc=bpy.context.scene
doors=[]
for ob in bpy.data.objects:
 if ob.name.startswith('Concealing walnut shutter'):
  sign=-1 if ob.location.x<1.62 else 1
  ob.scale.x*=.95/.84
  ob.location.x=1.62+sign*(1.48*.95/2+.01)
 if 'shutter' in ob.name:doors.append(ob)
 if ob.name.startswith('Bronze architectural arch'):
  points=ob.data.splines[0].points
  center=(min(p.co.x for p in points)+max(p.co.x for p in points))/2
  ob.location.x=center*(.60-.85)
light=bpy.data.objects['Warm back reveal'];light.location.x=1.62;light.rotation_euler=(Vector((1.62,0,2))-light.location).to_track_quat('-Z','Y').to_euler()
for ob in doors:ob.hide_render=False
sc.render.filepath=str(R/'hero-mobile-concealed-r6.png');bpy.ops.render.render(write_still=True)
for ob in doors:ob.hide_render=True
sc.render.filepath=str(R/'hero-mobile-world-r6.png');bpy.ops.render.render(write_still=True)
(R/'hero-placement-r6.json').write_text((R/'hero-placement-r5.json').read_text())
bpy.ops.wm.save_as_mainfile(filepath=str(R/'kids-statue-hero-mobile-r6.blend'))
