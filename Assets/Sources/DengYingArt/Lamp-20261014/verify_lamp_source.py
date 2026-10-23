import bpy
import json
import hashlib
from pathlib import Path
OUT=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(OUT/'DY_HeroSpotlight_Source.blend'))
root=bpy.data.objects.get('Root_Back_Source')
assert root is not None and root.type=='EMPTY'
assert root.location.length<1e-6
parts=[o for o in bpy.context.scene.objects if o.type=='MESH' and o.get('Export_Group') in {'BODY','STAND'}]
assert len(parts)==57 and all(o.parent==root for o in parts)
assert bpy.context.scene.unit_settings.scale_length==1.0
assert all(len(o.data.uv_layers)>0 for o in parts)
assert all(p.area>0 for o in parts for p in o.data.polygons)
expected=json.loads((OUT/'LAMP_ORIGINAL_TEXTURE_CHECK.json').read_text(encoding='utf-8'))
images=[]
for f in expected['files']:
    img=bpy.data.images[f['file']]
    assert img.packed_file is not None
    digest=hashlib.sha256(img.packed_file.data).hexdigest().upper()
    assert digest==f['sha256']
    images.append({'name':img.name,'pixels':list(img.size),'packed_original_sha256':digest,'same_as_original':True})
tri=[{'name':o.name,'group':o['Export_Group'],'triangles':sum(len(p.vertices)-2 for p in o.data.polygons)} for o in parts]
tri.sort(key=lambda x:x['triangles'],reverse=True)
total=sum(p['triangles'] for p in tri)
for p in tri:p['percent_total']=round(p['triangles']/total*100,2)
result={'status':'PASS_EDITABLE_BLEND_COLD_READ','source_root':'Root_Back_Source','unit_scale_meter':1.0,'editable_part_count':len(parts),'packed_images':images,'source_triangles':total,'triangles_by_part':tri,'not_checked':'UE or published runtime'}
(OUT/'LAMP_BLEND_COLD_READBACK.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'status':result['status'],'total':total,'top_parts':tri[:24]},ensure_ascii=False))
