import json
import sys
from pathlib import Path
import bpy
from mathutils import Vector

root=Path(sys.argv[sys.argv.index('--')+1])
out=root/'Sam-Pose-Inspection.json'
assert not out.exists()
records=[]
for name in ['sam-idle.glb','sam-walk.glb']:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene=bpy.context.scene
    scene.render.fps=30
    assert bpy.ops.import_scene.gltf(filepath=str(root/'Sam-Original'/name),import_pack_images=True)=={'FINISHED'}
    objects=list(scene.objects)
    rig=[o for o in objects if o.type=='ARMATURE']
    assert len(rig)==1
    frames=[]
    for frame in [0,1,7,13,14,20,26,27,33,39,40,46,52,53]:
        scene.frame_set(frame)
        bpy.context.view_layer.update()
        dg=bpy.context.evaluated_depsgraph_get()
        meshdata=[]
        for obj in objects:
            if obj.type!='MESH': continue
            evaluated=obj.evaluated_get(dg)
            mesh=evaluated.to_mesh()
            pts=[obj.matrix_world@v.co for v in mesh.vertices]
            low=[min(p[i] for p in pts) for i in range(3)]
            high=[max(p[i] for p in pts) for i in range(3)]
            meshdata.append(dict(name=obj.name,hide_render=obj.hide_render,hidden=obj.hide_get(),bounds=[low,high],scale=list(obj.scale)))
            evaluated.to_mesh_clear()
        bones={n:dict(head=list(rig[0].matrix_world@rig[0].pose.bones[n].head),tail=list(rig[0].matrix_world@rig[0].pose.bones[n].tail))
               for n in ['Root','pelvis','foot_l','foot_r','ball_l','ball_r','thigh_l','thigh_r']}
        frames.append(dict(frame=frame,bones=bones,meshes=meshdata))
    records.append(dict(file=name,frames=frames,actions=[dict(name=a.name,range=list(a.frame_range)) for a in bpy.data.actions]))
out.write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf-8')
print('Pose inspection saved:',out)
