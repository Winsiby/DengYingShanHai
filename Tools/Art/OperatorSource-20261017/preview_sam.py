import argparse
import hashlib
import json
import math
import struct
import sys
from pathlib import Path

import bpy
from mathutils import Vector


def sha(data):
    return hashlib.sha256(data).hexdigest().upper()


def read_glb(path):
    data = path.read_bytes()
    magic, version, length = struct.unpack_from('<III', data)
    assert magic == 0x46546C67 and version == 2 and length == len(data)
    offset, chunks = 12, {}
    while offset < length:
        size, kind = struct.unpack_from('<II', data, offset)
        assert size % 4 == 0 and offset + 8 + size <= length and kind not in chunks
        chunks[kind] = data[offset + 8:offset + 8 + size]
        offset += 8 + size
    assert offset == length and 0x4E4F534A in chunks and 0x004E4942 in chunks
    doc = json.loads(chunks[0x4E4F534A])
    binary = chunks[0x004E4942]
    assert len(doc['buffers']) == 1 and 'uri' not in doc['buffers'][0]
    assert all('uri' not in image for image in doc.get('images', []))
    assert 0 <= len(binary) - doc['buffers'][0]['byteLength'] < 4

    def accessor(index):
        a = doc['accessors'][index]
        assert 'sparse' not in a
        v = doc['bufferViews'][a['bufferView']]
        fmt = {5120: 'b', 5121: 'B', 5122: 'h', 5123: 'H', 5125: 'I', 5126: 'f'}[a['componentType']]
        width = {'SCALAR': 1, 'VEC2': 2, 'VEC3': 3, 'VEC4': 4, 'MAT4': 16}[a['type']]
        size = struct.calcsize('<' + fmt * width)
        step = v.get('byteStride', size)
        start = v.get('byteOffset', 0) + a.get('byteOffset', 0)
        assert start + (a['count'] - 1) * step + size <= len(binary)
        return [struct.unpack_from('<' + fmt * width, binary, start + i * step) for i in range(a['count'])]

    primitives = []
    for mesh in doc['meshes']:
        for p in mesh['primitives']:
            assert p.get('mode', 4) == 4
            pos = accessor(p['attributes']['POSITION'])
            indices = accessor(p['indices']) if 'indices' in p else [(i,) for i in range(len(pos))]
            assert len(indices) % 3 == 0 and all(0 <= x[0] < len(pos) for x in indices)
            primitives.append(dict(mesh=mesh.get('name'), vertices=len(pos), triangles=len(indices) // 3,
                                   material=doc['materials'][p['material']].get('name'),
                                   position_sha=sha(json.dumps(pos).encode()),
                                   skinned=('JOINTS_0' in p['attributes'] and 'WEIGHTS_0' in p['attributes'])))
    assert primitives and any(p['skinned'] for p in primitives)
    skins = []
    for s in doc.get('skins', []):
        assert all(0 <= j < len(doc['nodes']) for j in s['joints'])
        binds = accessor(s['inverseBindMatrices'])
        assert len(binds) == len(s['joints'])
        skins.append(dict(joints=[doc['nodes'][j].get('name') for j in s['joints']],
                          inverse_bind_sha=sha(json.dumps(binds).encode())))
    clips = []
    for a in doc.get('animations', []):
        times = [x[0] for sampler in a['samplers'] for x in accessor(sampler['input'])]
        assert times and all(math.isfinite(x) for x in times)
        varying = []
        for channel in a['channels']:
            sampler = a['samplers'][channel['sampler']]
            values = accessor(sampler['output'])
            if sampler.get('interpolation') == 'CUBICSPLINE':
                values = values[1::3]
            delta = max(max(v[i] for v in values) - min(v[i] for v in values) for i in range(len(values[0])))
            if delta > 1e-8:
                varying.append(dict(node=doc['nodes'][channel['target']['node']].get('name'), path=channel['target']['path'], max_component_delta=delta))
        clips.append(dict(name=a.get('name'), channels=len(a['channels']), varying_channels=varying, start=min(times), end=max(times),
                          duration=max(times) - min(times),
                          interpolations=sorted(set(s.get('interpolation', 'LINEAR') for s in a['samplers']))))
    assert clips and all(c['duration'] > 0 for c in clips)
    images = []
    for im in doc.get('images', []):
        v = doc['bufferViews'][im['bufferView']]
        raw = binary[v.get('byteOffset', 0):v.get('byteOffset', 0) + v['byteLength']]
        images.append(dict(name=im.get('name'), mime=im.get('mimeType'), bytes=len(raw), sha256=sha(raw)))
    return dict(file=path.name, bytes=len(data), sha256=sha(data), generator=doc['asset'].get('generator'),
                primitives=primitives, skins=skins, clips=clips, images=images,
                materials=[dict(name=m.get('name'), alpha=m.get('alphaMode', 'OPAQUE'),
                                two_sided=m.get('doubleSided', False), pbr=m.get('pbrMetallicRoughness')) for m in doc.get('materials', [])])


def aim(obj, target):
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat('-Z', 'Y').to_euler()


def preview(path, out, metadata, walk):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.render.fps = 30
    result = bpy.ops.import_scene.gltf(filepath=str(path), import_pack_images=True)
    assert result == {'FINISHED'}
    character = list(scene.objects)
    if metadata.get('clip_to_preview'):
        for obj in character:
            if not obj.animation_data:
                continue
            tracks = [t for t in obj.animation_data.nla_tracks if t.name == metadata['clip_to_preview'] and t.strips]
            if tracks:
                obj.animation_data.action = tracks[0].strips[0].action
                obj.animation_data.action_slot = tracks[0].strips[0].action_slot
    rigs = [o for o in character if o.type == 'ARMATURE']
    custom_shapes = {bone.custom_shape for rig in rigs for bone in rig.pose.bones if bone.custom_shape}
    meshes = [o for o in character if o.type == 'MESH' and o not in custom_shapes]
    assert meshes and rigs
    scene.frame_set(1)
    bpy.context.view_layer.update()
    deps = bpy.context.evaluated_depsgraph_get()
    corners = [o.matrix_world @ Vector(corner) for o in meshes for corner in o.evaluated_get(deps).bound_box]
    low = Vector([min(c[i] for c in corners) for i in range(3)])
    high = Vector([max(c[i] for c in corners) for i in range(3)])
    height = high.z - low.z
    assert height > 0 and math.isfinite(height)
    middle = (low + high) / 2
    before = [[[[float(x) for x in row] for row in b.matrix] for b in rig.pose.bones] for rig in rigs]
    scene.frame_set(14)
    bpy.context.view_layer.update()
    after = [[[[float(x) for x in row] for row in b.matrix] for b in rig.pose.bones] for rig in rigs]
    animated = any(any(any(abs(float(x) - float(y)) > 1e-6 for x, y in zip(row1, row2))
                        for row1, row2 in zip(bone1, bone2))
                   for rig1, rig2 in zip(before, after) for bone1, bone2 in zip(rig1, rig2))
    diagnostic = dict(file=path.name, rigs=[dict(name=r.name, action=r.animation_data.action.name if r.animation_data and r.animation_data.action else None) for r in rigs],
                      before=before, after=after, animated=animated)
    (out / (path.stem + '-animation-diagnostic.json')).write_text(json.dumps(diagnostic), encoding='utf-8')
    assert animated, 'Imported animation must actually change bone matrices'
    scene.render.engine = 'CYCLES'
    scene.cycles.device = 'CPU'
    scene.cycles.samples = 16
    scene.cycles.use_denoising = True
    scene.render.resolution_x, scene.render.resolution_y = 1024, 1280
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = 'PNG'
    scene.render.image_settings.color_mode = 'RGB'
    scene.world = bpy.data.worlds.new('NeutralWorld')
    scene.world.use_nodes = True
    scene.world.node_tree.nodes['Background'].inputs['Color'].default_value = (0.22, 0.22, 0.22, 1)
    scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value = 0.65
    floor_material = bpy.data.materials.new('QA_Floor')
    floor_material.diffuse_color = (0.21, 0.21, 0.21, 1)
    bpy.ops.mesh.primitive_plane_add(size=height * 10, location=(middle.x, middle.y, low.z - height * 0.001))
    bpy.context.object.data.materials.append(floor_material)
    for name, offset, energy, size in [('Key', (2, -3, 4), 550, 3), ('Fill', (-3, -1, 2), 250, 3), ('Rim', (0, 3, 3), 400, 2)]:
        data = bpy.data.lights.new(name, 'AREA')
        data.energy, data.shape, data.size = energy, 'DISK', size
        light = bpy.data.objects.new(name, data)
        scene.collection.objects.link(light)
        light.location = middle + Vector(offset) * height / 1.8
        aim(light, middle)
    data = bpy.data.cameras.new('QA_Camera')
    data.type, data.ortho_scale = 'ORTHO', height * 1.18
    camera = bpy.data.objects.new('QA_Camera', data)
    scene.collection.objects.link(camera)
    scene.camera = camera
    moving_frames = [0, 5, 10, 15] if path.stem == 'sam-run' or metadata.get('clip_to_preview') == 'Run' else [0, 7, 13, 20]
    shots = [('front', 1, (0, -4, 0.15)), ('rear', 1, (0, 4, 0.15)), ('side', 1, (4, 0, 0.15))] if not walk else [
        ('move-%02d' % frame, frame, (3, -2, 0.15)) for frame in moving_frames]
    captures = []
    for name, frame, offset in shots:
        scene.frame_set(frame)
        bpy.context.view_layer.update()
        camera.location = middle + Vector(offset) * height
        aim(camera, middle)
        image = out / (path.stem + '-' + name + '.png')
        scene.render.filepath = str(image)
        bpy.ops.render.render(write_still=True)
        raw = image.read_bytes()
        assert raw[:8] == b'\x89PNG\r\n\x1a\n' and struct.unpack_from('>II', raw, 16) == (1024, 1280)
        captures.append(dict(file=image.name, frame=frame, seconds=frame / 30, bytes=len(raw), sha256=sha(raw),
                             camera=list(camera.location), target=list(middle)))
    metadata['blender'] = dict(meshes=[dict(name=o.name, vertices=len(o.data.vertices), polygons=len(o.data.polygons)) for o in meshes],
                               rigs=[dict(name=o.name, bones=len(o.data.bones)) for o in rigs],
                               actions=[dict(name=a.name, frames=list(a.frame_range)) for a in bpy.data.actions],
                               bounds_m=[list(low), list(high)], bone_matrices_actually_animated=animated,
                               excluded_custom_shapes=[o.name for o in custom_shapes],
                               captures=captures, renderer='Blender Cycles CPU,16 samples,denoising,AgX; no post-editing')


parser = argparse.ArgumentParser()
parser.add_argument('--source', required=True)
parser.add_argument('--out', required=True)
parser.add_argument('--run-comparison', action='store_true')
args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:])
source, out = Path(args.source), Path(args.out)
assert source.is_dir() and out.is_dir() and not (out / 'SOURCE_CHECK.json').exists()
paths = [source / 'Sam-Original' / 'sam-idle.glb', source / 'Sam-Run-Original' / 'sam-run.glb'] if args.run_comparison else [source / name for name in ('sam-idle.glb', 'sam-walk.glb')]
records = [read_glb(path) for path in paths]
for record, path in zip(records, paths):
    download = json.loads((path.parent / 'DOWNLOAD.json').read_text(encoding='utf-8'))
    expected = [r for r in download['Files'] if r['File'] == path.name]
    assert len(expected) == 1 and record['sha256'] == expected[0]['SHA256']
initial = dict(schema='DYPlayerSourceCheck.v1', source_files=records,
               skeletons_identical=records[0]['skins'] == records[1]['skins'],
               geometry_identical=records[0]['primitives'] == records[1]['primitives'],
               actual_native_UE_import=False, art_accepted=False, original_game_changed=False)
(out / 'SOURCE_METADATA.json').write_text(json.dumps(initial, ensure_ascii=False, indent=2), encoding='utf-8')
for record, path in zip(records, paths):
    preview(path, out, record, record['file'] != 'sam-idle.glb')
(out / 'SOURCE_CHECK.json').write_text(json.dumps(initial, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps(dict(result='SOURCE_CHECK.json', actual_renders=sum(len(r['blender']['captures']) for r in records),
                      skeletons_identical=initial['skeletons_identical'], geometry_identical=initial['geometry_identical'])))
