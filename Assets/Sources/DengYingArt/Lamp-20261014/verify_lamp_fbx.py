"""Cold-read exported meshes, exact local bounds, normals, UVs and emitter clearance."""
import bpy
import json
from pathlib import Path
from mathutils import Vector
OUT=Path(__file__).resolve().parent
results=[]
for name,pivot in [('SM_DY_LampBody_Source',(0,0,0)),('SM_DY_LampStand_Source',(0,0,-.95))]:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=str(OUT/(name+'.fbx')))
    meshes=[o for o in bpy.context.scene.objects if o.type=='MESH']
    assert len(meshes)==1
    ob=meshes[0]
    pts=[ob.matrix_world@v.co for v in ob.data.vertices]
    actor_pts=[p+Vector(pivot) for p in pts]
    assert len(ob.data.uv_layers)==2
    assert all(len(p.vertices)>=3 for p in ob.data.polygons)
    assert all(p.area>0 for p in ob.data.polygons)
    assert all(abs(p.normal.length-1)<1e-3 for p in ob.data.polygons)
    assert max(p.x for p in actor_pts)<.45
    uv1=ob.data.uv_layers[1]
    assert all(-.001<=v.uv.x<=1.001 and -.001<=v.uv.y<=1.001 for v in uv1.data)
    result={'file':name+'.fbx','mesh_objects':len(meshes),'vertices':len(ob.data.vertices),'triangles':sum(len(p.vertices)-2 for p in ob.data.polygons),'uv_layers':[u.name for u in ob.data.uv_layers],'uv1_in_0_1':True,'bounds_local_cm':{'min':[round(min(p[i] for p in pts)*100,4) for i in range(3)],'max':[round(max(p[i] for p in pts)*100,4) for i in range(3)]},'bounds_actor_local_cm':{'min':[round(min(p[i] for p in actor_pts)*100,4) for i in range(3)],'max':[round(max(p[i] for p in actor_pts)*100,4) for i in range(3)]},'exported_material_slots':[m.name for m in ob.data.materials],'all_faces_nonzero_area':True,'unit_normals':True,'forward_halfspace_clearance_cm':round((.45-max(p.x for p in actor_pts))*100,4)}
    results.append(result)
body=results[0];stand=results[1]
assert max(body['bounds_actor_local_cm']['max'][0],stand['bounds_actor_local_cm']['max'][0])<45
assert abs(stand['bounds_actor_local_cm']['min'][2]+310)<.1
(OUT/'LAMP_FBX_COLD_READBACK.json').write_text(json.dumps({'status':'PASS_SOURCE_GEOMETRY_FBX_UV_UNITS','not_verified':'UE import, engine material rebuild, in-map visual shadows, actor rail extremes, packaged rendering','meshes':results},ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(results,ensure_ascii=False))
