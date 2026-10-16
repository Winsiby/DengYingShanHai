import copy
import hashlib
import json
import struct
import sys
from pathlib import Path

import bpy


def digest(data):
    return hashlib.sha256(data).hexdigest().upper()


def read(path, expected):
    data=path.read_bytes()
    assert digest(data)==expected
    assert struct.unpack_from('<III',data)==(0x46546C67,2,len(data))
    size,kind=struct.unpack_from('<II',data,12)
    assert kind==0x4E4F534A
    doc=json.loads(data[20:20+size])
    pos=20+size
    count,kind=struct.unpack_from('<II',data,pos)
    assert kind==0x004E4942 and pos+8+count==len(data)
    assert len(doc['buffers'])==1 and 'uri' not in doc['buffers'][0]
    return doc,data[pos+8:]


root=Path(sys.argv[sys.argv.index('--')+1])
out=root/'Operator-Prepared-Run1'
assert not out.exists()
out.mkdir()
base,base_bin=read(root/'Sam-Original/sam-idle.glb','83FD621C92EB284585CD7D4F807697D59DCE723FCCA3910A48D0016D9F028AA6')
move,move_bin=read(root/'Sam-Run-Original/sam-run.glb','15BFD5C7E566A74447C246ABB24B60856AAC80CA1C4C661FBA3599380BB058C6')
assert len(base['animations'])==len(move['animations'])==1
assert base['animations'][0]['name']=='Idle_Standing' and move['animations'][0]['name']=='Run'
assert len(base['nodes'])==len(move['nodes'])
assert [n.get('name') for n in base['nodes']]==[n.get('name') for n in move['nodes']]
assert base['skins']==move['skins']
original=copy.deepcopy(base)
binary=bytearray(base_bin)
clip=copy.deepcopy(move['animations'][0])
accessor_ids=sorted({s[key] for s in clip['samplers'] for key in ['input','output']})
view_ids=sorted({move['accessors'][i]['bufferView'] for i in accessor_ids})
view_map={}
for index in view_ids:
    view=copy.deepcopy(move['bufferViews'][index])
    assert view.get('buffer',0)==0
    raw=move_bin[view.get('byteOffset',0):view.get('byteOffset',0)+view['byteLength']]
    assert len(raw)==view['byteLength']
    binary.extend(b'\0'*(-len(binary)%4))
    view['byteOffset']=len(binary)
    binary.extend(raw)
    view_map[index]=len(base['bufferViews'])
    base['bufferViews'].append(view)
accessor_map={}
for index in accessor_ids:
    a=copy.deepcopy(move['accessors'][index])
    assert 'sparse' not in a
    a['bufferView']=view_map[a['bufferView']]
    accessor_map[index]=len(base['accessors'])
    base['accessors'].append(a)
for sampler in clip['samplers']:
    for key in ['input','output']:
        sampler[key]=accessor_map[sampler[key]]
base['animations'].append(clip)
# Remove only the source's zero-size phone display, not its skeleton or animation hierarchy.
phones=[n for n in base['nodes'] if n.get('name')=='Phone' and 'mesh' in n]
assert len(phones)==1
phone=phones[0]
removed=dict(node=phone['name'],mesh=phone.pop('mesh'),skin=phone.pop('skin',None))
assert base['meshes']==original['meshes'] and base['materials']==original['materials'] and base['skins']==original['skins']
base['buffers'][0]['byteLength']=len(binary)
encoded=json.dumps(base,ensure_ascii=False,separators=(',',':')).encode()
encoded+=b' '*(-len(encoded)%4)
binary.extend(b'\0'*(-len(binary)%4))
data=struct.pack('<III',0x46546C67,2,28+len(encoded)+len(binary))+struct.pack('<II',len(encoded),0x4E4F534A)+encoded+struct.pack('<II',len(binary),0x004E4942)+binary
target=out/'SK_DY_Operator_Source.glb'
target.write_bytes(data)
assert bytes(binary[:len(base_bin)])==base_bin
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.context.scene.render.fps=30
assert bpy.ops.import_scene.gltf(filepath=str(target),import_pack_images=True)=={'FINISHED'}
rigs=[o for o in bpy.context.scene.objects if o.type=='ARMATURE']
assert len(rigs)==1
rig=rigs[0]
assert len(rig.data.bones)==56
actions={a.name:a for a in bpy.data.actions}
assert {'Idle_Standing','Run'}.issubset(actions)
assert abs(actions['Idle_Standing'].frame_range[1]-180)<1e-3 and abs(actions['Run'].frame_range[1]-40)<1e-3
assert not any(o.type=='MESH' and o.name=='Phone' for o in bpy.context.scene.objects)
custom_shapes={b.custom_shape for b in rig.pose.bones if b.custom_shape}
meshes=[o for o in bpy.context.scene.objects if o.type=='MESH' and o not in custom_shapes]
assert len(meshes)==11
bpy.context.scene.frame_set(0)
bpy.context.view_layer.update()
for image in bpy.data.images:
    if image.source=='FILE' and not image.packed_file:
        image.pack()
blend=out/'DY_Operator_Source.blend'
assert bpy.ops.wm.save_as_mainfile(filepath=str(blend))=={'FINISHED'}
record=dict(schema='DYOperatorPreparedSource.v1',author='Innerscene / MakeHuman-CC0 upstream; Codex-assisted curation for solo author',
            license='CC0-1.0',input_idle_sha256='83FD621C92EB284585CD7D4F807697D59DCE723FCCA3910A48D0016D9F028AA6',
            input_run_sha256='15BFD5C7E566A74447C246ABB24B60856AAC80CA1C4C661FBA3599380BB058C6',
            files=[dict(file=p.name,bytes=p.stat().st_size,sha256=digest(p.read_bytes())) for p in [target,blend]],
            changes=['Preserve original body/clothing/hair/shoes geometry, materials, textures, bone hierarchy, weights and scale',
                     'Append only same-rig original Run animation buffer views and accessors to Idle GLB; no duplicate textures',
                     'Remove collapsed phone mesh assignment only; keep original nodes, skin and animation hierarchy',
                     'Import curated GLB in Blender 4.5.14 with auto-execution disabled; save packed editable blend'],
            removed_phone_display=removed,body_mesh_objects=len(meshes),bones=len(rig.data.bones),
            actions=[dict(name=a.name,frames=list(a.frame_range)) for a in actions.values()],
            native_UE_import=False,animations_applied_to_game=False,art_accepted=False,gameplay_changed=False)
(out/'SOURCE.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(record,ensure_ascii=False))
