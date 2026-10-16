"""Extend only the straight span of the frozen CC0 TopUV beam, as FBX data.

No Blender/UE, downloads, D-drive writes, source overwrite, material edits or
normal/tangent regeneration. Only new local source artifacts are generated.
"""
import argparse
import ast
import copy
import hashlib
import json
import math
from pathlib import Path
import re
import struct
import zlib


HERE = Path(__file__).resolve().parent
SOURCE = Path('D:/灯影山海/Saved/Audit-2026-10-13-FrameBeamTopUV/Sources/frame-beam-topuv-calibrated.fbx')
PARSER = Path('D:/灯影山海/Saved/Audit-2026-10-12-FrameBeamAsset/Inspect-Pavilion.py')
ENCODER = PARSER.with_name('Extract-FrameBeam.py')
EXPECTED = {
    SOURCE: '9D67085097B6EA5D18E098BFD5002D74148943F681182E2C17598EDC7835F999',
    PARSER: '07009683AE115BCC73188206477EA74CB9A0B87675742CEBAD3CDC28D8F48F9A',
    ENCODER: '9FBEE15E9A51843BFEC664822133A0D04B918DD0BD8AE34B051F718540D82E17',
}
SCALE = .39290377163557627
ACTOR_LOCATION = [950., 66.77584636395318, 816.7876838516025]
RIGHT_WORLD_Y = 583.5516927279066
LEFT_EXTENSION_WORLD_CM = 133.55169272790636
LONG_FACES = (0, 1, 2, 9)
LEFT_IDS = [0, 1, 2, 3, 8, 9, 10, 11]
CHECKS = []


def req(value, message):
    if not value:
        raise AssertionError(message)
    CHECKS.append(message)
    return value


def digest(raw):
    return hashlib.sha256(raw).hexdigest().upper()


def functions_only(path, wanted, namespace):
    tree = ast.parse(path.read_text(encoding='utf-8'))
    nodes = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in wanted]
    req(len(nodes) == len(wanted), 'Exact reviewed function whitelist from '+path.name)
    exec(compile(ast.Module(body=nodes, type_ignores=[]), str(path), 'exec'), namespace)


def replace_double_array(node, values):
    original = node['_property_bytes']
    req(original[:1] == b'd' and len(node['properties']) == 1, 'Single existing double array '+node['name'])
    count, encoding, length = struct.unpack_from('<III', original, 1)
    req(count == len(values) == len(node['properties'][0]) and encoding in (0, 1)
        and length+13 == len(original), 'Array count/encoding and bounded payload preserved')
    raw = struct.pack('<'+'d'*len(values), *values)
    encoded = zlib.compress(raw) if encoding else raw
    node['properties'] = [values]
    node['_property_bytes'] = b'd'+struct.pack('<III', count, encoding, len(encoded))+encoded


def data(child, geometry):
    coordinates = child(geometry, 'Vertices')['properties'][0]
    vertices = [coordinates[i:i+3] for i in range(0, len(coordinates), 3)]
    layer = child(geometry, 'LayerElementUV')
    req(child(layer, 'MappingInformationType')['properties'] == ['ByPolygonVertex']
        and child(layer, 'ReferenceInformationType')['properties'] == ['IndexToDirect'], 'Exact indexed corner UV layout')
    raw_uv = child(layer, 'UV')['properties'][0]
    uv = [raw_uv[i:i+2] for i in range(0, len(raw_uv), 2)]
    ui = child(layer, 'UVIndex')['properties'][0]
    raw_indices = child(geometry, 'PolygonVertexIndex')['properties'][0]
    polygons, current = [], []
    for corner, value in enumerate(raw_indices):
        index = -value-1 if value < 0 else value
        req(0 <= index < len(vertices) and 0 <= ui[corner] < len(uv), 'Valid corner vertex/UV index')
        current.append((corner, index))
        if value < 0:
            polygons.append(current)
            current = []
    req(not current and len(vertices) == 16 and len(polygons) == 10
        and len(raw_indices) == len(ui) == 48 and len(uv) == 38, 'Frozen 16-point/10-face/48-corner/38-UV topology')
    return vertices, polygons, uv, ui


def geometry_of(child, roots):
    objects = child({'children': roots}, 'Objects')['children']
    geometries = [n for n in objects if n['name'] == 'Geometry']
    req(len(objects) == 3 and len(geometries) == 1
        and geometries[0]['properties'][0] == 512851073, 'One frozen original Geometry/Model/Material')
    return geometries[0]


def long_edge_gradients(vertices, polygon, uv, indices):
    result = []
    for (ca, va), (cb, vb) in zip(polygon, polygon[1:]+polygon[:1]):
        a, b = vertices[va], vertices[vb]
        if a[1:] == b[1:] and a[0] != b[0]:
            gradient = [(uv[indices[cb]][k]-uv[indices[ca]][k])/(b[0]-a[0]) for k in range(2)]
            result.append(dict(corners=[ca, cb], gradient=gradient,
                               density_source2K_texels_per_world_m=math.hypot(*gradient)*2048*100/SCALE))
    req(len(result) == 2, 'Exactly two pure source-X long edges')
    return result


def bounds_world(vertices):
    # Existing native importer observation: local=(sourceX,sourceZ,sourceY), then actor Yaw90.
    world = [[ACTOR_LOCATION[0]-p[2]*SCALE, ACTOR_LOCATION[1]+p[0]*SCALE,
              ACTOR_LOCATION[2]+p[1]*SCALE] for p in vertices]
    return dict(min=[min(p[i] for p in world) for i in range(3)],
                max=[max(p[i] for p in world) for i in range(3)])


def compare_nodes(left_roots, right_roots):
    changed = []
    rows = []
    def walk(a, b, path):
        req(a['name'] == b['name'] and len(a['children']) == len(b['children'])
            and len(a['properties']) == len(b['properties']), 'Same FBX tree structure '+path)
        equal = a['_property_bytes'] == b['_property_bytes']
        rows.append(dict(path=path, identical=equal, before=digest(a['_property_bytes']), after=digest(b['_property_bytes'])))
        if not equal:
            changed.append(path)
        counts = {}
        for aa, bb in zip(a['children'], b['children']):
            number = counts.get(aa['name'], 0)
            counts[aa['name']] = number+1
            walk(aa, bb, path+'/'+aa['name']+'['+str(number)+']')
    req(len(left_roots) == len(right_roots), 'Same root node count')
    counts = {}
    for a, b in zip(left_roots, right_roots):
        number = counts.get(a['name'], 0)
        counts[a['name']] = number+1
        walk(a, b, '/'+a['name']+'['+str(number)+']')
    req(set(changed) == {'/Objects[0]/Geometry[0]/Vertices[0]',
                         '/Objects[0]/Geometry[0]/LayerElementUV[0]/UV[0]'}
        and len(changed) == 2, 'Only Vertices and UV array properties differ in entire FBX tree')
    return changed, rows


def verify_geometry(source_data, derived_data, shift):
    old, polygons, uv, ui = source_data
    new, new_polygons, new_uv, new_ui = derived_data
    req(polygons == new_polygons and ui == new_ui, 'All polygon and UV indices exactly unchanged')
    req([i for i, p in enumerate(old) if p[0] < 0] == LEFT_IDS, 'Exact existing left endpoint membership')
    for i, (a, b) in enumerate(zip(old, new)):
        req(a[1:] == b[1:] and (b[0] == a[0]+shift if i in LEFT_IDS else a == b), 'Only intended left X translation vertex '+str(i))
    end_faces = [p for i,p in enumerate(polygons) if i not in LONG_FACES]
    req(len(end_faces) == 6, 'Exactly six original beveled end faces')
    for polygon in end_faces:
        ids = [index for _,index in polygon]
        req(all(i in LEFT_IDS for i in ids) or all(i not in LEFT_IDS for i in ids), 'End face belongs entirely to one rigid endpoint')
        for i in ids:
            req(max(abs((new[i][k]-new[ids[0]][k])-(old[i][k]-old[ids[0]][k])) for k in range(3)) < 1e-10,
                'Beveled end internal shape/cross-section preserved')
    req(all(math.isfinite(v) for p in new_uv for v in p), 'Extended UVs finite without clamp')
    density = []
    for pi in LONG_FACES:
        before = long_edge_gradients(old, polygons[pi], uv, ui)
        after = long_edge_gradients(new, polygons[pi], new_uv, new_ui)
        residual = [a['density_source2K_texels_per_world_m']-b['density_source2K_texels_per_world_m'] for a,b in zip(after,before)]
        req(max(abs(v) for v in residual) < .0001, 'Long-face source texture density retained to 0.0001 texel/m face '+str(pi))
        density.append(dict(face=pi,before=before,after=after,residual_texels_per_world_m=residual))
    world = bounds_world(new)
    req(abs(world['min'][1]+RIGHT_WORLD_Y) < 1e-9 and abs(world['max'][1]-RIGHT_WORLD_Y) < 1e-9,
        'Derived world endpoints symmetric, old right endpoint held')
    req(abs(world['min'][2]-800) < 1e-4, 'Original world beam-bottom Z800 held within native-coordinate precision')
    return density, world


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', required=True, type=Path)
    out = parser.parse_args().out
    req(out.is_absolute() and out.resolve().parent == HERE
        and re.fullmatch(r'Source-Run[1-9][0-9]*', out.name)
        and not out.exists(), 'Explicit absent local Source-RunN output; no other directory writes')
    author_path = Path(__file__).resolve()
    author_code = author_path.read_bytes()
    input_bytes = {path: path.read_bytes() for path in EXPECTED}
    req(all(digest(raw) == EXPECTED[path] for path,raw in input_bytes.items()), 'Exact source/parser/encoder hashes before execution')
    namespace = {'struct':struct,'math':math,'zlib':zlib}
    functions_only(PARSER, {'require','parse_fbx','child'}, namespace)
    functions_only(ENCODER, {'encode'}, namespace)
    child, parse, encode = namespace['child'], namespace['parse_fbx'], namespace['encode']
    raw = input_bytes[SOURCE]
    version, roots = parse(raw)
    req(version == 7400 and len(raw) == 15211, 'Exact source narrow-offset FBX7400')
    source_geometry = geometry_of(child, roots)
    source_data = data(child, source_geometry)
    vertices, polygons, uv, ui = source_data
    shift = -LEFT_EXTENSION_WORLD_CM/SCALE
    req(abs(shift-(-339.9094189703463)) < 1e-10, 'Extension calculated from actual world delta and unchanged uniform scale')
    next_vertices, next_uv = copy.deepcopy(vertices), copy.deepcopy(uv)
    for index in LEFT_IDS:
        next_vertices[index][0] += shift
    uvset = lambda pi: {ui[c] for c,_ in polygons[pi]}
    groups = {
        0: uvset(4)|uvset(6),
        1: {ui[c] for c,v in polygons[1] if v in LEFT_IDS},
        2: {ui[c] for c,v in polygons[2] if v in LEFT_IDS},
        9: uvset(7),
    }
    expected_groups = {0:{0,2,19,29,33,35},1:{1,9,22,32},2:{5,15,16,31},9:{6,10,26,36}}
    req(groups == expected_groups and sum(len(v) for v in groups.values()) == 18
        and len(set.union(*groups.values())) == 18, 'Exact four disjoint left UV islands; 18 pairs affected')
    shifts = []
    for pi, indices in groups.items():
        edges = long_edge_gradients(vertices, polygons[pi], uv, ui)
        gradient = [sum(e['gradient'][i] for e in edges)/len(edges) for i in range(2)]
        delta = [shift*v for v in gradient]
        for index in indices:
            next_uv[index] = [a+b for a,b in zip(next_uv[index],delta)]
        # End-island translation, not scaling/shear: every internal UV vector remains intact.
        anchor = min(indices)
        req(max(abs((next_uv[i][k]-next_uv[anchor][k])-(uv[i][k]-uv[anchor][k]))
                for i in indices for k in range(2)) < 1e-15, 'Rigid UV island translation face '+str(pi))
        shifts.append(dict(long_face=pi,uv_pair_indices=sorted(indices),gradient_mean_dUV_dSourceX=gradient,translation_uv=delta))
    moved_uv = set.union(*groups.values())
    req(all(next_uv[i] == uv[i] for i in set(range(38))-moved_uv), 'Right twenty UV pairs byte-value unchanged')
    req(all(next_uv[i] != uv[i] for i in moved_uv), 'Exactly eighteen left UV pairs changed')
    derived = copy.deepcopy(roots)
    geometry = geometry_of(child, derived)
    replace_double_array(child(geometry,'Vertices'), [v for p in next_vertices for v in p])
    replace_double_array(child(child(geometry,'LayerElementUV'),'UV'), [v for p in next_uv for v in p])
    encoded = bytearray(raw[:27])
    for node in derived:
        encoded += encode(node, len(encoded))
    encoded += bytes(13)+raw[roots[-1]['_end']+13:]
    reread_version, reread = parse(bytes(encoded))
    req(reread_version == version and bytes(encoded[:27]) == raw[:27]
        and bytes(encoded[reread[-1]['_end']+13:]) == raw[roots[-1]['_end']+13:], 'FBX header/version/footer bytes preserved')
    changed_nodes, node_rows = compare_nodes(roots, reread)
    density, world = verify_geometry(source_data, data(child,geometry_of(child,reread)), shift)
    old_world = bounds_world(vertices)
    req(all(world[side][i] == old_world[side][i] for side in ('min','max') for i in (0,2)), 'World X/Z extents exactly retained')
    req(all(path.read_bytes() == input_bytes[path] for path in EXPECTED) and author_path.read_bytes() == author_code, 'All exact inputs and author code unchanged before output')
    out.mkdir()
    fbx_path = out/'frame-beam-fullspan.fbx'
    with fbx_path.open('xb') as stream:
        stream.write(encoded)
    # Fresh disk read/parse is separate from the modified in-memory node tree.
    cold_raw = fbx_path.read_bytes()
    cold_version, cold_roots = parse(cold_raw)
    req(cold_version == version and cold_raw == bytes(encoded), 'Independent cold physical FBX bytes/parse match generated payload')
    cold_changed, _ = compare_nodes(roots,cold_roots)
    cold_density, cold_world = verify_geometry(source_data,data(child,geometry_of(child,cold_roots)),shift)
    req(cold_changed == changed_nodes and cold_density == density and cold_world == world, 'Independent cold parse reproduces geometry/UV/extent contracts')
    report = dict(status='PASS-LOCAL-DERIVED-FULLSPAN-SOURCE-NATIVE-AND-ART-PENDING',
        source=str(SOURCE),source_bytes=len(raw),source_sha256=digest(raw),
        output=str(fbx_path),output_bytes=len(cold_raw),output_sha256=digest(cold_raw),
        author_tool=dict(path=str(author_path),sha256=digest(author_code),source_utf8=author_code.decode('utf-8')),
        parser=dict(path=str(PARSER),sha256=EXPECTED[PARSER],functions=['require','parse_fbx','child']),
        encoder=dict(path=str(ENCODER),sha256=EXPECTED[ENCODER],functions=['encode']),
        old_module_mains_executed=False,source_x_translation=shift,source_vertex_ids=LEFT_IDS,
        world_left_extension_cm=LEFT_EXTENSION_WORLD_CM,actor_location_cm=ACTOR_LOCATION,
        actor_yaw_degrees=90,uniform_scale=SCALE,source_to_native_local_axes='sourceX,sourceZ,sourceY; previously observed actual importer',
        old_world_bounds=old_world,derived_world_bounds=world,world_bounds_are_offline_not_native=True,
        topology=dict(vertices=16,polygons=10,corners=48,fan_triangles=28,uv_pairs=38),
        unchanged_right_vertex_count=8,unchanged_right_uv_pair_count=20,
        rigid_original_end_faces=[3,4,5,6,7,8],changed_long_faces=list(LONG_FACES),
        uv_island_shifts=shifts,density_source2K=density,
        uv_bounds=dict(min=[min(p[i] for p in next_uv) for i in range(2)],max=[max(p[i] for p in next_uv) for i in range(2)]),
        uv_outside_0_1_allowed='Existing texture Wrap, no clamp, material/texture edits or scale',
        changed_property_nodes=changed_nodes,all_node_property_rows=node_rows,
        cold_physical_parse=True,normals_recomputed=False,tangents_recomputed=False,
        source_provenance='Existing CC0 VVayToyek Chinese Four-corner Pavilion beam + existing CC0 Poly Haven Dark Wood; see project FRAME_BEAM_ASSET_SOURCES.md / FRAME_POST_ASSET_SOURCES.md',
        ai_assistance='Codex data-only modeling adaptation: extend straight span, preserve bevels/cross-section, extend UV islands; not original pavilion authorship or historical reconstruction',
        scope=dict(D_writes=False,UE=False,old_asset_changed=False,shared_material_changed=False,
                   new_download=False,paid_asset=False,restricted_register_access=False,native_verified=False,art_accepted=False),
        checks=CHECKS,check_count=len(CHECKS))
    with (out/'DERIVATION.json').open('x',encoding='utf-8') as stream:
        json.dump(report,stream,ensure_ascii=False,indent=2)
    with (out/'README.md').open('x',encoding='utf-8') as stream:
        stream.write('# FullSpan beam: local source artifact\n\n'
            'Reuses the existing CC0 VVayToyek Chinese Four-corner Pavilion beam and existing CC0 Poly Haven Dark Wood texture family. '
            'Upstream source and license evidence remain in project Docs/FRAME_BEAM_ASSET_SOURCES.md and FRAME_POST_ASSET_SOURCES.md; '
            'this task did not access the restricted register. No download, payment or new texture.\n\n'
            'Codex assisted with data-only adaptation: translate the left beveled end rigidly, extend only four straight faces, '
            'translate four left UV islands to retain existing wood sampling density. Original pavilion authorship is not claimed. '
            'No historical joinery, load-bearing structure or particular shadow-theater tradition is asserted.\n\n'
            'DERIVATION.json contains exact source/tool/helper/output hashes, the complete author-tool source, '
            'all node-property comparisons and a fresh physical FBX parse. Only Vertices and UV array properties change. '
            'This is source-only validation, not native import, gameplay, collision, final lighting, GPU or artistic acceptance.\n')
    print(json.dumps({k:report[k] for k in ('status','output','output_sha256','source_x_translation','derived_world_bounds','check_count')},indent=2))


if __name__ == '__main__':
    main()
