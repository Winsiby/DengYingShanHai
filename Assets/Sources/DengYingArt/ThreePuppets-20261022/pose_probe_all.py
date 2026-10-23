"""Silhouette distance probe for every character and pose."""
from pathlib import Path
import bpy, json, math, sys
from mathutils import Vector
ROOT=Path(__file__).resolve().parent
RUN=ROOT/(sys.argv[sys.argv.index('--')+1]); OUT=ROOT/'Probe'; OUT.mkdir(exist_ok=True)

def scene_for(model):
    bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
    black=bpy.data.materials.new('SIL');black.use_nodes=True
    black.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(0.02,0.02,0.02,1)
    obs=[]
    for p in model['parts']:
        me=bpy.data.meshes.new(p['name']);me.from_pydata(p['vertices'],[],p['faces']);me.update()
        o=bpy.data.objects.new(p['name'],me);bpy.context.collection.objects.link(o);me.materials.append(black)
        g=o.vertex_groups.new(name=p['bone']);g.add(list(range(len(me.vertices))),1,'REPLACE');obs.append(o)
    data=bpy.data.armatures.new('A');arm=bpy.data.objects.new('Armature',data);bpy.context.collection.objects.link(arm)
    bpy.context.view_layer.objects.active=arm;bpy.ops.object.mode_set(mode='EDIT')
    for b in model['bones']:
        eb=data.edit_bones.new(b['name']);eb.head=b['pivot_cm'];eb.tail=Vector(b['pivot_cm'])+Vector((0,0,8))
        if b['parent']:eb.parent=data.edit_bones[b['parent']]
    bpy.ops.object.mode_set(mode='OBJECT')
    for o in obs:
        o.parent=arm;m=o.modifiers.new('a','ARMATURE');m.object=arm
    h=model['height_cm'];w=model['width_cm']
    bpy.ops.object.camera_add(location=(600,0,h*.5));cam=bpy.context.object;cam.data.type='ORTHO'
    cam.data.ortho_scale=max(w*1.35,h*1.6);cam.rotation_euler=(Vector((0,0,h*.5))-cam.location).to_track_quat('-Z','Y').to_euler()
    bpy.context.scene.camera=cam
    bpy.ops.object.light_add(type='AREA',location=(400,0,h));l=bpy.context.object;l.data.energy=3e6;l.data.size=400
    l.rotation_euler=(Vector((0,0,h*.5))-l.location).to_track_quat('-Z','Y').to_euler()
    sc=bpy.context.scene;sc.render.engine='BLENDER_EEVEE_NEXT';sc.world=sc.world or bpy.data.worlds.new('W');sc.world.use_nodes=True
    sc.world.node_tree.nodes['Background'].inputs['Color'].default_value=(1,1,1,1);sc.world.node_tree.nodes['Background'].inputs['Strength'].default_value=1.4
    return arm,cam,sc

for body in ('Jingwei','Zhulong'):
    model=json.loads((RUN/body/'prepared.json').read_text(encoding='utf8'))
    spec=json.loads((ROOT/(body.lower()+'_spec.json')).read_text(encoding='utf-8-sig'))
    arm,cam,sc=scene_for(model)
    for p in spec['poses']:
        for b in arm.pose.bones:
            b.rotation_mode='XYZ';b.rotation_euler=(math.radians(p.get('angles_deg',{}).get(b.name,0)),0,0);b.scale=(1,1,1)
            if b.name=='Eyelid':b.scale=(1,1,1) if p['name']=='Night' else (.0001,)*3
        bpy.context.view_layer.update()
        for wpx in (420,180):
            sc.render.resolution_x=wpx;sc.render.resolution_y=int(wpx*1.25)
            sc.render.filepath=str(OUT/('%s_%s_%d.png'%(body,p['name'],wpx)));bpy.ops.render.render(write_still=True)
print('PROBE_OK')
