"""Analytic resampling variant. Complete source files stay unchanged; no decimation."""
from pathlib import Path
import hashlib
import json
import re
SOURCE=Path(__file__).resolve().parent.parent
VARIANT=Path(__file__).resolve().parent
protected=['build_lamp.py','DY_HeroSpotlight_Source.blend','SM_DY_LampBody_Source.fbx','SM_DY_LampStand_Source.fbx','Lamp_Head_Review.png','Lamp_Full_Review.png','Lamp_Side_Review.png']
before={name:hashlib.sha256((SOURCE/name).read_bytes()).hexdigest() for name in protected}
code=(SOURCE/'build_lamp.py').read_text(encoding='utf-8')
def replace_once(old,new):
    global code
    assert code.count(old)==1,(old,code.count(old))
    code=code.replace(old,new)
replace_once("OUT/'Sources'/name","SOURCE/'Sources'/name")
replace_once("axis='Z',vertices=96","axis='Z',vertices=48")
replace_once('segments=128):','segments=64):')
replace_once('vertices=96,radius1=','vertices=48,radius1=')
replace_once('mod.segments=4','mod.segments=3')
replace_once("bpy.ops.mesh.primitive_torus_add(major_segments=128,minor_segments=16,location=loc,major_radius=major,minor_radius=minor)","bpy.ops.mesh.primitive_torus_add(major_segments=(80 if name=='Lamp_RolledFrontRim' else 64 if name=='Lamp_OpticalWindowRetainer' else 48),minor_segments=(12 if name=='Lamp_RolledFrontRim' else 8),location=loc,major_radius=major,minor_radius=minor)")
counts={'32':0,'48':0,'64':0}
mapping={'32':'24','48':'32','64':'32'}
def small_samples(match):
    n=match.group(1);counts[n]+=1
    return ','+mapping[n]+')'
code=re.sub(r',(32|48|64)\)',small_samples,code)
assert all(v>0 for v in counts.values())
code=code.replace('DY_HeroSpotlight_Source.blend','DY_HeroSpotlight_RuntimeVariant.blend')
exec(compile(code,str(SOURCE/'build_lamp.py'),'exec'),globals())
after={name:hashlib.sha256((SOURCE/name).read_bytes()).hexdigest() for name in protected}
assert before==after,'Complete source was modified'
record={'method':'Analytic primitive/profile resampling, never decimation; visual fidelity approximation, not lossless','source_preserved':before==after,'source_hashes':before,'parameter_diff':{'lathe_circumference':[128,64],'default_cylinder_circumference':[96,48],'wood_mast_circumference':[96,48],'small_cylinder_32':[32,24],'small_cylinder_48':[48,32],'small_cylinder_64':[64,32],'edge_bevel_segments':[4,3],'front_rim_major_minor':[[128,16],[80,12]],'optics_retainer_major_minor':[[128,16],[64,8]],'other_torus_major_minor':[[128,16],[48,8]]},'parameters_retained':['All profile positions and radii','All thicknesses, edge widths, component pivots, and source anchors','All named parts and material partitions','Physical wood UV direction and analytical shell UV formula','Same review camera/light/world/exposure/shader configuration'],'ab_head_camera':{'position_m':[2.4,-2.8,.85],'target_m':[0,0,-.17],'type':'ORTHO','ortho_scale_m':1.47,'resolution':[1920,1440],'cycles_samples':80,'view_transform':'AgX','exposure':0.0},'small_sample_literal_occurrences':counts}
(VARIANT/'RUNTIME_PARAMETER_DIFF.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
print('RUNTIME_ANALYTIC_RESAMPLE_COMPLETE; source preserved=',before==after)
