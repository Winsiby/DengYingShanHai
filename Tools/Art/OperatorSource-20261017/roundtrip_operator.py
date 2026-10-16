import ast
import json
import sys
from pathlib import Path

root=Path(sys.argv[sys.argv.index('--')+1])
out=root/'Operator-RoundTrip-Run1'
assert not out.exists()
out.mkdir()
# Reuse only our reviewed import/check/render functions; do not execute their CLI entry point.
tool=Path(__file__).with_name('preview_sam.py')
tree=ast.parse(tool.read_text(encoding='utf-8'))
definitions=ast.Module(body=[n for n in tree.body if isinstance(n,(ast.Import,ast.ImportFrom,ast.FunctionDef))],type_ignores=[])
namespace={}
exec(compile(ast.fix_missing_locations(definitions),str(tool),'exec'),namespace)
prepared=root/'Operator-Prepared-Run1'
source=json.loads((prepared/'SOURCE.json').read_text(encoding='utf-8'))
for record in source['files']:
    assert namespace['sha']((prepared/record['file']).read_bytes())==record['sha256']
glb=prepared/'SK_DY_Operator_Source.glb'
metadata=namespace['read_glb'](glb)
assert {c['name'] for c in metadata['clips']}=={'Idle_Standing','Run'}
results=[]
for name in ['Idle_Standing','Run']:
    record=dict(metadata,clip_to_preview=name)
    namespace['preview'](glb,out,record,name=='Run')
    results.append(record)
bpy=namespace['bpy']
assert bpy.ops.wm.open_mainfile(filepath=str(prepared/'DY_Operator_Source.blend'),load_ui=False)=={'FINISHED'}
assert {a.name for a in bpy.data.actions}=={'Idle_Standing','Run'}
assert len([o for o in bpy.context.scene.objects if o.type=='ARMATURE'])==1
assert all(im.packed_file for im in bpy.data.images if im.source=='FILE')
report=dict(schema='DYOperatorSourceRoundTrip.v1',prepared_files_rehashed=True,cold_blend_open_succeeded=True,
            both_clips_actually_rendered=True,source_records=results,UE_imported=False,game_changed=False,final_art_accepted=False)
(out/'ROUNDTRIP.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(dict(schema=report['schema'],actual_renders=sum(len(r['blender']['captures']) for r in results),cold_blend_open=True)))
