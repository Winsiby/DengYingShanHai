"""Create/cold-read exactly two isolated wide-leaf Dev packages; reuse the existing leaf Material.

The runner supplies frozen SOURCE.json/FBX hashes and owns the native process.
No map, live session, existing Blueprint/material, component or gameplay writes.
"""
import ast
import hashlib
import itertools
import json
import math
import os
from pathlib import Path
import re
import struct
import sys
import traceback
import zlib

ROOT = Path('D:/灯影山海')
AUDIT = ROOT / 'Saved/Audit-2026-10-14-ArtAppearance'
SOURCE_ROOT = ROOT / 'Assets/Sources/DengYingArt/ForestCanopyWide-20261016'
SOURCE = SOURCE_ROOT / 'forest-branch-leafed.fbx'
META = SOURCE_ROOT / 'SOURCE.json'
NODE_REFERENCE = ROOT / 'Assets/Sources/DengYingArt/ForestBranch-20261016/forest-branch-tapered.fbx'
NODE_REFERENCE_SHA = '7B722B42346A81EEA4872D7EA137300192E45FB8E8088926CCF54826CFD952D6'
MESH = '/Game/DengYingShanHai/Dev/ForestCanopyWide/Meshes/SM_DY_ForestBranch_WideLeaf'
LEAF = '/Game/DengYingShanHai/Dev/ForestCanopy/Materials/M_DY_ForestLeaf'
BP = '/Game/DengYingShanHai/Dev/ForestCanopyWide/Presentation/BP_DYForestCanopy_WideLeaf'
OWN = (MESH, BP)
TAPERED_BP = '/Game/DengYingShanHai/Dev/ForestArt/Presentation/BP_DYForestArt_Tapered'
TAPERED_MESH = '/Game/DengYingShanHai/Dev/ForestArt/Meshes/SM_DY_ForestBranch_Tapered'
GRAY_BP = '/Game/DengYingShanHai/Dev/M3/Forest/BP_DYForestPresentation_Dev'
REFERENCE = '/Game/DengYingShanHai/Dev/FrameBeamTopUV/Meshes/SM_DY_FrameBeam_TopUV'
MI = '/Game/DengYingShanHai/Dev/FramePostAsset/Materials/MI_DY_FramePost_Wood'
MAT = '/Game/DengYingShanHai/Dev/FramePostAsset/Materials/M_DY_FramePost_Master'
READER = ROOT / 'Scripts/Create-FrameBeamTopUVAsset.py'
PARSER = ROOT / 'Saved/Audit-2026-10-12-FrameBeamAsset/Inspect-Pavilion.py'
OLD_AUTHOR = ROOT / 'Scripts/Create-P03ForestDevAsset.py'
HELPERS = {
    READER: 'A03B249E8FF0CA051FCC4153906CFEEAB916DAB371675E421FE19AB1AC8A4DD0',
    PARSER: '07009683AE115BCC73188206477EA74CB9A0B87675742CEBAD3CDC28D8F48F9A',
    OLD_AUTHOR: '15F52C9CB8B7BD293BDBFA98EB7445B6F974F10117B4E0747C34C477E0B807C0',
}
INPUTS = [TAPERED_BP, TAPERED_MESH, GRAY_BP, REFERENCE, MI, MAT, LEAF] + [
    '/Game/DengYingShanHai/Dev/FramePostAsset/Textures/T_DY_FramePost_' + name
    for name in ('BaseColor', 'NormalDX', 'ARM')]
SLOTS = ['Wood0', 'Leaf1']
LEAF_COLOR = (.08, .18, .045)
R = dict(success=False, saved=[], checks=[], maps_saved=False, actors_spawned=False,
         old_assets_saved=False, shared_material_changed=False, gameplay_changed=False,
         runtime_components_replaced=False, art_accepted=False, packaged=False)


def req(value, message):
    if not value:
        raise RuntimeError(message)
    R['checks'].append(message)
    return value


def sha(file):
    req(Path(file).resolve() != (ROOT / 'Docs/LICENSES.md').resolve(), 'Never access restricted license register')
    return hashlib.sha256(Path(file).read_bytes()).hexdigest().upper()


def asset_file(package):
    req(package in INPUTS + list(OWN), 'Exact existing input or two isolated own packages')
    return ROOT / 'Content' / (package[6:] + '.uasset')


def path(value):
    return value.get_path_name() if value else None


def xyz(value):
    return [value.x, value.y, value.z]


def definitions(file, functions, constants, namespace):
    req(file in HELPERS and sha(file) == HELPERS[file], 'Exact reviewed helper hash ' + file.name)
    tree = ast.parse(file.read_text(encoding='utf-8-sig'))
    picked, found_functions, found_constants = [], set(), set()
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name in functions:
            req(not node.decorator_list and node.name not in found_functions, 'Unique undecorated helper ' + node.name)
            picked.append(node)
            found_functions.add(node.name)
        elif isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name) and node.targets[0].id in constants:
            value = ast.literal_eval(node.value)
            req(isinstance(value, tuple) and all(isinstance(item, str) for item in value), 'Literal property-name tuple')
            picked.append(node)
            found_constants.add(node.targets[0].id)
    req(found_functions == functions and found_constants == constants, 'Only exact helper definitions; no old module import/main/save')
    exec(compile(ast.Module(body=picked, type_ignores=[]), str(file), 'exec'), namespace)


def source_geometry(source_sha, meta_sha):
    req(sha(SOURCE) == source_sha and sha(META) == meta_sha, 'Explicit runner-frozen new FBX and source metadata hashes')
    meta = json.loads(META.read_text(encoding='utf-8-sig'))
    spec = meta['source_mesh']
    req(meta['schema'] == 'ForestCanopySource.v1' and meta['fbx']['sha256'] == source_sha
        and meta['fbx']['bytes'] == SOURCE.stat().st_size and Path(meta['fbx']['path']).name == SOURCE.name,
        'Reviewed source schema and exact FBX identity/size/hash')
    req(all(isinstance(spec[name], int) and not isinstance(spec[name], bool) and spec[name] > 0 for name in ('vertices', 'triangles'))
        and spec['uv_layers'] == 1 and spec['material_slots'] == SLOTS,
        'Actual metadata counts, UV0 and ordered Wood0/Leaf1 slots; no guessed topology counts')
    ns = dict(math=math, struct=struct, zlib=zlib)
    definitions(PARSER, {'require', 'parse_fbx', 'child', 'named_properties'}, set(), ns)
    version, roots = ns['parse_fbx'](SOURCE.read_bytes())
    child = ns['child']
    objects = child({'children': roots}, 'Objects')['children']
    geometries = [item for item in objects if item['name'] == 'Geometry']
    models = [item for item in objects if item['name'] == 'Model']
    materials = {item['properties'][0]: item for item in objects if item['name'] == 'Material'}
    req(version == 7400 and len(geometries) == len(models) == 1 and len(materials) == 2
        and models[0]['properties'][2] == 'Mesh'
        and not any(item['name'] in ('Texture', 'Video', 'Deformer') or item['name'].startswith('Animation') for item in objects),
        'Raw FBX one mesh/model, two materials, no texture/skin/animation objects')
    connections = [item['properties'] for item in child({'children': roots}, 'Connections')['children'] if item['name'] == 'C']
    material_ids = [row[1] for row in connections if row[0] == 'OO' and row[1] in materials and row[2] == models[0]['properties'][0]]
    material_names = [materials[identity]['properties'][1].split('\x00\x01')[0] for identity in material_ids]
    req(material_names == SLOTS, 'Raw FBX model material connection order is exactly Wood0 then Leaf1')
    geometry = geometries[0]
    raw_positions = child(geometry, 'Vertices')['properties'][0]
    positions = [raw_positions[i:i+3] for i in range(0, len(raw_positions), 3)]
    indices = child(geometry, 'PolygonVertexIndex')['properties'][0]
    req(len(raw_positions) % 3 == 0 and len(positions) == spec['vertices']
        and len(indices) == 3 * spec['triangles']
        and all((value < 0) == (index % 3 == 2) for index, value in enumerate(indices)),
        'Raw source point count and complete triangle corner count match reviewed metadata')
    req(len([item for item in geometry['children'] if item['name'] == 'LayerElementUV']) == 1
        and len([item for item in geometry['children'] if item['name'] == 'LayerElementNormal']) == 1,
        'Raw source has exactly one UV0 and one normal layer')
    layers = [child(geometry, name) for name in ('LayerElementUV', 'LayerElementNormal')]
    for layer in layers:
        req(child(layer, 'MappingInformationType')['properties'] == ['ByPolygonVertex']
            and child(layer, 'ReferenceInformationType')['properties'] == ['IndexToDirect'],
            'Actual indexed polygon-corner UV and normal layouts')
    uv_raw = child(layers[0], 'UV')['properties'][0]
    uvs = [uv_raw[i:i+2] for i in range(0, len(uv_raw), 2)]
    uv_indices = child(layers[0], 'UVIndex')['properties'][0]
    normal_raw = child(layers[1], 'Normals')['properties'][0]
    normals = [normal_raw[i:i+3] for i in range(0, len(normal_raw), 3)]
    normal_indices = child(layers[1], 'NormalsIndex')['properties'][0]
    material_layer = child(geometry, 'LayerElementMaterial')
    req(child(material_layer, 'MappingInformationType')['properties'] == ['ByPolygon']
        and child(material_layer, 'ReferenceInformationType')['properties'] == ['IndexToDirect'],
        'Raw FBX explicit material index for every triangle')
    material_indices = child(material_layer, 'Materials')['properties'][0]
    req(len(material_indices) == spec['triangles'] and set(material_indices) == {0, 1}
        and len(uv_indices) == len(normal_indices) == len(indices), 'Both material sections used; all UV/normal corner indices present')
    source_triangles = []
    for triangle, slot in enumerate(material_indices):
        corners = []
        control_indices = []
        for corner in range(3):
            index = triangle*3+corner
            vertex = -indices[index]-1 if indices[index] < 0 else indices[index]
            req(0 <= vertex < len(positions) and 0 <= uv_indices[index] < len(uvs)
                and 0 <= normal_indices[index] < len(normals), 'Every raw source corner index bounded')
            normal = normals[normal_indices[index]]
            req(abs(distance(normal, [0, 0, 0])-1) < .01, 'Every actual source normal finite and near-unit')
            corners.append(dict(position=positions[vertex], normal=normal, uv=uvs[uv_indices[index]]))
            control_indices.append(vertex)
        source_triangles.append(dict(slot=slot, control_indices=control_indices, corners=corners))
    bounds = {side: [fn(point[axis] for point in positions) for axis in range(3)] for side, fn in (('min', min), ('max', max))}
    req(all(abs(bounds[side][axis]-spec['bounds_cm'][side][axis]) < 1e-5 for side in ('min', 'max') for axis in range(3))
        and abs(bounds['min'][2]+50) < 1e-5 and abs(bounds['max'][2]-50) < 1e-5
        and all(abs(bounds['min'][axis]+bounds['max'][axis]) < 1e-5 for axis in (0, 1))
        and all(any(distance(point, endpoint) < 1e-5 for point in positions) for endpoint in ([0, 0, -50], [0, 0, 50])),
        'Raw centered-XY bounds and actual wood axis root/tip remain (0,0,-50)/(0,0,50)')
    settings = ns['named_properties'](child({'children': roots}, 'GlobalSettings'))
    model = ns['named_properties'](models[0])
    req(sha(NODE_REFERENCE) == NODE_REFERENCE_SHA, 'Exact previously cold-verified tapered FBX axis-calibration reference')
    reference_version, reference_roots = ns['parse_fbx'](NODE_REFERENCE.read_bytes())
    reference_models = [item for item in child({'children': reference_roots}, 'Objects')['children'] if item['name'] == 'Model']
    req(reference_version == 7400 and len(reference_models) == 1, 'Actual reference one-model FBX7400')
    reference_model = ns['named_properties'](reference_models[0])
    reference_settings = ns['named_properties'](child({'children': reference_roots}, 'GlobalSettings'))
    defaults = {'Lcl Translation': [0, 0, 0], 'Lcl Rotation': [0, 0, 0], 'Lcl Scaling': [1, 1, 1]}
    actual_transform = {name: model.get(name, default) for name, default in defaults.items()}
    reference_transform = {name: reference_model.get(name, default) for name, default in defaults.items()}
    req(settings['UpAxis'] == [2] and settings['UpAxisSign'] == [1] and abs(settings['UnitScaleFactor'][0]-1) < 1e-6
        and all(settings[name] == reference_settings[name] for name in ('UpAxis', 'UpAxisSign', 'FrontAxis', 'FrontAxisSign', 'CoordAxis', 'CoordAxisSign'))
        and abs(settings['UnitScaleFactor'][0]-reference_settings['UnitScaleFactor'][0]) < 1e-6
        and all(len(actual_transform[name]) == len(reference_transform[name]) == 3
            and distance(actual_transform[name], reference_transform[name]) < 1e-6 for name in defaults),
        'Actual model uses the exact established tapered-FBX exporter node-axis conversion and Z-up centimeter frame')
    req(len(spec['vertex_positions_cm']) == len(positions)
        and all(distance(a, b) < 1e-5 for a, b in zip(spec['vertex_positions_cm'], positions)), 'Every raw source control point matches reviewed author metadata')
    authored = spec['loop_triangles']
    req(len(authored) == len(source_triangles)
        and [sum(row['material_index'] == slot for row in authored) for slot in range(2)]
        == [material_indices.count(slot) for slot in range(2)], 'Reviewed author triangle/material totals agree with independent FBX parse')
    by_indices = {}
    for index, triangle in enumerate(authored):
        ids = triangle['indices']
        req(len(ids) == len(triangle['uv0']) == len(triangle['corner_normals']) == 3
            and all(isinstance(vertex, int) and 0 <= vertex < len(positions) for vertex in ids), 'Complete reviewed author triangle indices/UV0/smooth corner normals')
        key = min(tuple(ids[offset:]+ids[:offset]) for offset in range(3))
        by_indices.setdefault(key, set()).add(index)
    unused = set(range(len(authored)))
    author_correspondence = []
    for index, triangle in enumerate(source_triangles):
        ids = triangle['control_indices']
        key = min(tuple(ids[offset:]+ids[:offset]) for offset in range(3))
        found = None
        for candidate in sorted(by_indices.get(key, set()) & unused):
            author = authored[candidate]
            for offset in range(3):
                order = [(offset+corner)%3 for corner in range(3)]
                if (author['material_index'] == triangle['slot'] and [author['indices'][corner] for corner in order] == ids
                    and all(distance(raw['uv'], author['uv0'][corner]) < 1e-6
                        and distance(raw['normal'], author['corner_normals'][corner]) < 2e-6
                        for raw, corner in zip(triangle['corners'], order))):
                    found = dict(raw_fbx_triangle=index, author_triangle=candidate, author_cyclic_corner_order=order)
                    break
            if found:
                break
        req(found, 'Every raw FBX triangle matches reviewed author connectivity/winding/material/UV0/smooth corner normals')
        unused.remove(found['author_triangle'])
        author_correspondence.append(found)
    req(not unused, 'Every reviewed author triangle/corner accounted for exactly once; global triangle reorder allowed, winding reversal not allowed')
    return source_triangles, dict(version=version, vertices=len(positions), triangles=len(source_triangles),
        bounds=bounds, uv_channels=1, material_slots=material_names,
        triangles_by_material=[material_indices.count(slot) for slot in range(2)],
        author_triangle_correspondence=author_correspondence,
        node_axis_calibration=dict(reference_source=str(NODE_REFERENCE), reference_sha256=NODE_REFERENCE_SHA,
            reference_transform=reference_transform, actual_transform=actual_transform,
            explanation='Applied-identity Blender mesh may export a non-identity axis-conversion Model node. Only the same measured transform as the previously verified tapered source is accepted; native full-corner conversion must still be unique.'),
        model=model, global_settings=settings, source_sha256=source_sha, metadata_sha256=meta_sha)


def distance(a, b):
    return math.sqrt(sum((x-y)**2 for x, y in zip(a, b)))


def native_uv(uv, full):
    def f32(value):
        return struct.unpack('<f', struct.pack('<f', value))[0]
    result = [f32(uv[0]), f32(1-f32(uv[1]))]
    return result if full else [struct.unpack('<e', struct.pack('<e', value))[0] for value in result]


def match_section(section, source, axes, signs, full):
    converted = [[dict(position=[corner['position'][axes[i]]*signs[i] for i in range(3)],
                       normal=[corner['normal'][axes[i]]*signs[i] for i in range(3)], uv0=native_uv(corner['uv'], full))
                  for corner in triangle['corners']] for triangle in source if triangle['slot'] == section['material_slot']]
    if len(converted)*3 != len(section['indices']):
        return None
    by_uv = {}
    for index, triangle in enumerate(converted):
        for corner in triangle:
            by_uv.setdefault(tuple(corner['uv0']), set()).add(index)
    unused = set(range(len(converted)))
    matched = []
    for start in range(0, len(section['indices']), 3):
        actual = [section['render'][index] for index in section['indices'][start:start+3]]
        found = None
        for index in sorted(by_uv.get(tuple(actual[0]['uv0']), set()) & unused):
            for order in itertools.permutations(range(3)):
                expected = [converted[index][corner] for corner in order]
                if all(a['uv0'] == b['uv0'] and distance(a['position'], b['position']) < .002
                       and distance(a['normal'], b['normal']) < .02 for a, b in zip(actual, expected)):
                    found = dict(actual_triangle=start//3, source_section_triangle=index, corner_order=list(order),
                        position_max_error_cm=max(distance(a['position'], b['position']) for a, b in zip(actual, expected)),
                        normal_max_vector_error=max(distance(a['normal'], b['normal']) for a, b in zip(actual, expected)))
                    break
            if found:
                break
        if not found:
            return None
        unused.remove(found['source_section_triangle'])
        matched.append(found)
    return matched if not unused else None


def validate_render(record, source):
    full = record['build_settings']['use_full_precision_u_vs']
    req(not record['build_settings']['use_backwards_compatible_f16_trunc_u_vs'], 'Actual modern rounded native UV storage')
    solutions = []
    for axes in ((0, 1, 2), (1, 0, 2)):
        for sx, sy in itertools.product((-1, 1), repeat=2):
            signs = (sx, sy, 1)
            matches = [match_section(section, source, axes, signs, full) for section in record['render_sections']]
            if all(match is not None for match in matches):
                solutions.append((axes, signs, matches))
    req(len(solutions) == 1, 'Unique actual source/native axis conversion; complete per-slot triangle/corner bijections')
    axes, signs, matches = solutions[0]
    for section, correspondence in zip(record['render_sections'], matches):
        section['source_triangle_corner_correspondence'] = correspondence
        for vertex in section['render']:
            req(all(math.isfinite(x) for name in ('position', 'normal', 'uv0', 'tangent') for x in vertex[name])
                and abs(distance(vertex['normal'], [0, 0, 0])-1) < .02
                and abs(distance(vertex['tangent'], [0, 0, 0])-1) < .02
                and abs(sum(a*b for a, b in zip(vertex['normal'], vertex['tangent']))) < .04,
                'All actual section vertices finite with near-unit orthogonal imported normals/Mikk tangents')
    source_bounds = R['source_geometry']['bounds']
    expected = dict(min=[], max=[])
    for axis, sign in zip(axes, signs):
        values = [source_bounds[side][axis]*sign for side in ('min', 'max')]
        expected['min'].append(min(values))
        expected['max'].append(max(values))
    req(all(abs(record['bounds'][side][axis]-expected[side][axis]) < .002 for side in ('min', 'max') for axis in range(3)),
        'Actual full native mesh bounds match independently transformed source bounds')
    R['source_to_native'] = dict(permutation=list(axes), signs=list(signs),
        all_sections_checked=True, every_triangle_and_corner_matched_bijectively=True,
        every_render_vertex_referenced=True, uv_float32_vflip_and_actual_storage=True)


def leaf_record(material, unreal):
    mel = unreal.MaterialEditingLibrary
    req(material.get_class().get_name() == 'Material'
        and material.get_editor_property('material_domain') == unreal.MaterialDomain.MD_SURFACE
        and material.get_editor_property('blend_mode') == unreal.BlendMode.BLEND_OPAQUE
        and material.get_editor_property('shading_model') == unreal.MaterialShadingModel.MSM_DEFAULT_LIT
        and not material.get_editor_property('two_sided') and material.get_editor_property('tangent_space_normal')
        and not material.get_editor_property('use_material_attributes'), 'Leaf Surface/Opaque/DefaultLit/single-sided standard surface')
    nodes = list(mel.get_material_expressions(material))
    color = req(mel.get_material_property_input_node(material, unreal.MaterialProperty.MP_BASE_COLOR), 'Actual leaf BaseColor input')
    metallic = req(mel.get_material_property_input_node(material, unreal.MaterialProperty.MP_METALLIC), 'Actual leaf Metallic input')
    roughness = req(mel.get_material_property_input_node(material, unreal.MaterialProperty.MP_ROUGHNESS), 'Actual leaf Roughness input')
    req(len(nodes) == 3 and {path(node) for node in nodes} == {path(color), path(metallic), path(roughness)}
        and color.get_class().get_name() == 'MaterialExpressionConstant3Vector'
        and all(node.get_class().get_name() == 'MaterialExpressionConstant' for node in (metallic, roughness))
        and not any(mel.get_inputs_for_material_expression(material, node) for node in nodes), 'Exactly three input-free constants; no texture/function/parameter/static switch')
    value = color.get_editor_property('constant')
    actual = [value.r, value.g, value.b]
    req(all(math.isfinite(x) and 0 <= x <= 1 and abs(x-y) < 1e-6 for x, y in zip(actual, LEAF_COLOR))
        and metallic.get_editor_property('r') == 0 and abs(roughness.get_editor_property('r')-.85) < 1e-6,
        'Finite leaf color (.08,.18,.045), Metallic0, Roughness.85')
    for name in ('MP_SPECULAR', 'MP_NORMAL', 'MP_EMISSIVE_COLOR', 'MP_OPACITY', 'MP_OPACITY_MASK', 'MP_WORLD_POSITION_OFFSET', 'MP_MATERIAL_ATTRIBUTES'):
        req(mel.get_material_property_input_node(material, getattr(unreal.MaterialProperty, name)) is None, 'No leaf override/input ' + name)
    req(not mel.get_material_used_textures(material), 'Actual leaf uses no textures')
    return dict(package=LEAF, domain='Surface', blend='Opaque', shading='DefaultLit', two_sided=False,
        base_color_linear=actual, metallic=0, roughness=roughness.get_editor_property('r'), specular='Factory default; unconnected',
        expressions=[node.get_class().get_name() for node in nodes], textures=0, transparency=False,
        WPO=False, emissive=False, static_switches=False, new_dynamic_instances=False)


def graph_record(bp, unreal):
    result = {}
    for graph in unreal.BlueprintEditorLibrary.list_graphs(bp):
        editor = unreal.BlueprintGraphEditor.get_graph_editor(graph)
        nodes = list(editor.list_all_nodes())
        req(not editor.list_nodes_with_errors(), 'No saved Blueprint compiler errors')
        req(all(node.get_class().get_name() in ('K2Node_Event', 'K2Node_FunctionEntry', 'K2Node_FunctionResult') for node in nodes)
            and not any(pin.list_connected_pins() for node in nodes for pin in node.list_all_pins()), 'Only unconnected factory placeholders; no execution logic')
        result[graph.get_name()] = [node.get_class().get_name() for node in nodes]
    return result


def cdo_state(cdo, layout_rows):
    return dict(mesh=path(cdo.get_editor_property('branch_mesh')), material=path(cdo.get_editor_property('branch_material')),
                layout=layout_rows(cdo.get_editor_property('branch_layout')), session=cdo.has_forest_session(),
                components=[path(item) for item in cdo.get_branch_mesh_components()],
                sample_branches=len(cdo.get_forest_geometry_sample().get_editor_property('branches')),
                tick_enabled=cdo.is_actor_tick_enabled())


def run(phase, source_sha, meta_sha):
    import unreal
    req(Path(os.path.realpath(unreal.SystemLibrary.get_project_directory())) == ROOT.resolve(), 'Exact current project')
    req(not unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world()
        and not unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()
        and not unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages(), 'No game world or unsaved user packages')
    source, R['source_geometry'] = source_geometry(source_sha, meta_sha)
    frozen = {str(file): sha(file) for file in list(HELPERS)+[SOURCE, META, NODE_REFERENCE]+[asset_file(package) for package in INPUTS]}
    own_before = {package: sha(asset_file(package)) for package in OWN} if phase == 'verify' else {}
    for package in OWN:
        exists = asset_file(package).exists() or unreal.EditorAssetLibrary.does_asset_exist(package)
        req(exists if phase == 'verify' else not exists, 'Exact own package ' + ('exists for cold verify' if phase == 'verify' else 'absent, never overwrite'))
        if phase == 'verify':
            req(unreal.find_object(None, package+'.'+package.rsplit('/', 1)[1]) is None, 'Own cold asset absent from memory before load')
    ns = dict(unreal=unreal, R=R, req=req, MI=MI, MAT=MAT, object_path=path)
    definitions(READER, {'xyz', 'uv', 'scalar', 'fields', 'material'}, {'IMPORT_FIELDS', 'BUILD_FIELDS', 'MESH_FIELDS'}, ns)
    layout_ns = {}
    definitions(OLD_AUTHOR, {'layout_rows'}, set(), layout_ns)
    layout_rows = layout_ns['layout_rows']
    parent = req(unreal.load_class(None, '/Script/DengYingShanHai.DYForestPresentationActor'), 'Existing native cosmetic forest parent')
    tapered = unreal.get_default_object(req(unreal.load_asset(TAPERED_BP), 'Current tapered data Blueprint').generated_class())
    gray = unreal.get_default_object(req(unreal.load_asset(GRAY_BP), 'Original graybox data Blueprint').generated_class())
    native = unreal.get_default_object(parent)
    originals = [(name, cdo, cdo_state(cdo, layout_rows)) for name, cdo in (('tapered', tapered), ('graybox', gray), ('native', native))]
    old_rows = layout_rows(tapered.get_editor_property('branch_layout'))
    req(len(old_rows) == 15 and unreal.DYForestGeometryLibrary.is_forest_layout_valid(tapered.get_editor_property('branch_layout'))
        and path(tapered.get_editor_property('branch_mesh')) == TAPERED_MESH+'.'+TAPERED_MESH.rsplit('/', 1)[1]
        and path(tapered.get_editor_property('branch_material')) == MI+'.'+MI.rsplit('/', 1)[1],
        'Current tapered BP exactly 15 valid definitions and its accepted mesh/Wood references')
    req(all(not state['session'] and not state['components'] and not state['sample_branches'] and not state['tick_enabled']
            for name, cdo, state in originals)
        and originals[-1][2]['mesh'] is None and originals[-1][2]['material'] is None and originals[-1][2]['layout'] == [],
        'All old/native CDO sessions remain empty; native CDO authoring empty and no Tick')
    reference = req(unreal.load_asset(REFERENCE), 'Existing frozen import/build policy reference')
    wood = ns['material']()
    mesh_editor = unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
    leaf = req(unreal.load_asset(LEAF), 'Reuse frozen existing A leaf Material; never create/compile/save it')
    if phase == 'create':
        flag = 'Interchange.FeatureFlags.Import.FBX'
        world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
        previous = unreal.SystemLibrary.get_console_variable_int_value(flag)
        try:
            unreal.SystemLibrary.execute_console_command(world, flag+' 0', None)
            options = unreal.FbxImportUI()
            options.set_editor_properties(dict(mesh_type_to_import=unreal.FBXImportType.FBXIT_STATIC_MESH,
                import_as_skeletal=False, import_mesh=True, import_animations=False, import_materials=False,
                import_textures=False, automated_import_should_detect_type=False, override_full_name=True))
            imports = options.get_editor_property('static_mesh_import_data')
            imports.set_editor_properties({name: reference.get_editor_property('asset_import_data').get_editor_property(name) for name in ns['IMPORT_FIELDS']})
            imports.set_editor_property('reorder_material_to_fbx_order', True)
            req(imports.get_editor_property('normal_import_method') == unreal.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS
                and imports.get_editor_property('import_uniform_scale') == 1
                and not any(imports.get_editor_property(name) for name in ('auto_generate_collision', 'build_nanite', 'generate_lightmap_u_vs')),
                'Import source normals at unit scale, explicit FBX slot order, no auto collision/Nanite/UV/material/texture')
            task = unreal.AssetImportTask()
            task.set_editor_properties(dict(filename=str(SOURCE), destination_path=MESH.rsplit('/', 1)[0], destination_name=MESH.rsplit('/', 1)[1],
                factory=unreal.FbxFactory(), options=options, automated=True, replace_existing=False, save=False))
            unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
            req(list(task.get_editor_property('imported_object_paths')) == [MESH+'.'+MESH.rsplit('/', 1)[1]], 'Import only one own dual-slot mesh, no extra packages')
            mesh = req(unreal.load_asset(MESH), 'Own unsaved leafed mesh')
            mesh.set_editor_properties({name: reference.get_editor_property(name) for name in ns['MESH_FIELDS']})
            mesh_editor.set_lod_build_settings(mesh, 0, mesh_editor.get_lod_build_settings(reference, 0))
            req([str(slot.get_editor_property('imported_material_slot_name')) for slot in mesh.get_editor_property('static_materials')] == SLOTS,
                'Actual imported material slots preserve Wood0/Leaf1 before assignment')
            mesh.set_material(0, wood)
            mesh.set_material(1, leaf)
        finally:
            unreal.SystemLibrary.execute_console_command(world, flag+' '+str(previous), None)
            req(unreal.SystemLibrary.get_console_variable_int_value(flag) == previous, 'Process-only FBX flag restored; no Config changes')
        factory = unreal.BlueprintFactory()
        factory.set_editor_property('parent_class', parent)
        bp = req(unreal.AssetToolsHelpers.get_asset_tools().create_asset(BP.rsplit('/', 1)[1], BP.rsplit('/', 1)[0], unreal.Blueprint, factory), 'New native-parent data-only leafed BP')
        req(unreal.BlueprintEditorLibrary.compile_blueprint(bp), 'Compile own factory BP')
        cdo = unreal.get_default_object(bp.generated_class())
        cdo.set_editor_property('branch_mesh', mesh)
        cdo.set_editor_property('branch_material', wood)
        cdo.set_editor_property('branch_layout', tapered.get_editor_property('branch_layout'))
        req(unreal.BlueprintEditorLibrary.compile_blueprint(bp), 'Compile copied authoring defaults without graphs/components')
    mesh, bp = (req(unreal.load_asset(package), 'Actual own new asset '+package) for package in OWN)
    unreal.SystemLibrary.execute_console_command(unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world(), 'Editor.AsyncAssetCompilationFinishAll', None)
    R['leaf_material'] = leaf_record(leaf, unreal)
    build = ns['fields'](mesh_editor.get_lod_build_settings(mesh, 0), ns['BUILD_FIELDS'])
    imports = ns['fields'](mesh.get_editor_property('asset_import_data'), ns['IMPORT_FIELDS'])
    desc = req(mesh.get_static_mesh_description(0), 'Actual native source MeshDescription')
    bounds = mesh.get_bounds()
    slots = [dict(name=str(slot.get_editor_property('material_slot_name')), imported_name=str(slot.get_editor_property('imported_material_slot_name')),
        material=path(slot.get_editor_property('material_interface'))) for slot in mesh.get_editor_property('static_materials')]
    record = dict(bounds=dict(min=xyz(bounds.origin-bounds.box_extent), max=xyz(bounds.origin+bounds.box_extent)),
        source_vertices=desc.get_vertex_count(), source_instances=desc.get_vertex_instance_count(), source_triangles=desc.get_triangle_count(),
        source_polygons=desc.get_polygon_count(), source_groups=desc.get_polygon_group_count(), lods=mesh.get_num_lods(),
        triangles=mesh.get_num_triangles(0), render_vertices=mesh.get_num_vertices(0), uv_channels=mesh.get_num_tex_coords(0),
        section_count=mesh.get_num_sections(0), slots=slots, simple_collision=mesh_editor.get_simple_collision_count(mesh),
        nanite=mesh.get_editor_property('nanite_settings').get_editor_property('enabled'), build_settings=build,
        import_settings=imports, source_filenames=list(mesh.get_editor_property('asset_import_data').extract_filenames()), render_sections=[])
    expected = R['source_geometry']
    req(record['source_vertices'] == expected['vertices'] and record['source_instances'] == expected['triangles']*3
        and record['source_triangles'] == record['source_polygons'] == record['triangles'] == expected['triangles']
        and record['source_groups'] == record['section_count'] == 2 and record['lods'] == record['uv_channels'] == 1,
        'Actual complete source topology, two native polygon groups/sections, single LOD and UV0 match reviewed FBX')
    req([slot['name'] for slot in slots] == [slot['imported_name'] for slot in slots] == SLOTS
        and [slot['material'] for slot in slots] == [path(wood), path(leaf)]
        and record['simple_collision'] == 0 and not record['nanite']
        and not build['generate_lightmap_u_vs'] and not build['recompute_normals'] and build['recompute_tangents'] and build['use_mikk_t_space']
        and imports['normal_import_method'] == 'FBXNIM_IMPORT_NORMALS' and imports['reorder_material_to_fbx_order']
        and len(record['source_filenames']) == 1 and Path(os.path.realpath(record['source_filenames'][0])) == SOURCE.resolve(),
        'Actual Wood0/Leaf1 resources/order, imported normals/Mikk tangents, no collision/Nanite/extra UV and exact source metadata')
    for section in range(2):
        vertices, indices, normals, uvs, tangents = unreal.ProceduralMeshLibrary.get_section_from_static_mesh(mesh, 0, section)
        slot = mesh_editor.get_lod_material_slot(mesh, 0, section)
        req(slot == section and len(vertices) == len(normals) == len(uvs) == len(tangents)
            and len(indices) == expected['triangles_by_material'][slot]*3
            and all(0 <= index < len(vertices) for index in indices)
            and set(indices) == set(range(len(vertices))) and mesh_editor.is_section_cast_shadow_enabled(mesh, 0, section),
            'Complete actual render section indices/vertices, correct material slot and real shadow eligibility '+str(section))
        record['render_sections'].append(dict(section=section, material_slot=slot, indices=list(indices), casts_shadow=True,
            render=[dict(position=xyz(p), normal=xyz(n), uv0=[uv.x, uv.y], tangent=xyz(t.get_editor_property('tangent_x')),
                         flip_tangent_y=t.get_editor_property('flip_tangent_y')) for p, n, uv, t in zip(vertices, normals, uvs, tangents)]))
    validate_render(record, source)
    req(abs(record['bounds']['min'][2]+50) < .002 and abs(record['bounds']['max'][2]-50) < .002
        and all(abs(record['bounds']['min'][axis]+record['bounds']['max'][axis]) < .002 for axis in (0, 1)),
        'Actual native centered-XY local-Z root/tip bounds remain compatible')
    req(unreal.BlueprintEditorLibrary.get_blueprint_parent_class(bp) == parent, 'Exact direct native forest parent')
    cdo = unreal.get_default_object(req(bp.generated_class(), 'Generated leafed forest class'))
    state = cdo_state(cdo, layout_rows)
    req(state == dict(mesh=path(mesh), material=path(wood), layout=old_rows, session=False, components=[], sample_branches=0, tick_enabled=False),
        'Exact original 15 parent/offset/diameter/growth definitions; slot0 override only, no CDO session/components/Tick')
    graphs = graph_record(bp, unreal)
    sub, sdl = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem), unreal.SubobjectDataBlueprintFunctionLibrary
    handles = sub.k2_gather_subobject_data_for_blueprint(bp)
    req(not any(sdl.is_component(sdl.get_data(handle)) and not sdl.is_native_component(sdl.get_data(handle))
                and not sdl.is_inherited_component(sdl.get_data(handle)) for handle in handles), 'No local SCS components or branch templates')
    req(all(cdo_state(old_cdo, layout_rows) == before for name, old_cdo, before in originals), 'Current tapered/old graybox/native CDO resources, layouts and empty sessions unchanged')
    req(all(sha(file) == expected_hash for file, expected_hash in frozen.items()), 'All frozen source/helpers/old assets unchanged before save')
    req(not unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages(), 'No map dirtied')
    dirty = {package.get_path_name() for package in unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages()}
    req(dirty.issubset(set(OWN)) if phase == 'create' else not dirty, 'Only own two packages may be dirty; existing leaf remains clean; cold verify clean')
    if phase == 'create':
        for package, asset in ((MESH, mesh), (BP, bp)):
            req(path(asset).split('.')[0] == package and unreal.EditorAssetLibrary.save_loaded_asset(asset, only_if_is_dirty=False), 'Save exact own new package '+package)
            R['saved'].append(package)
    else:
        req(all(sha(asset_file(package)) == before for package, before in own_before.items()), 'Cold own packages unchanged; no reimport/compile/save')
    req(all(sha(file) == expected_hash for file, expected_hash in frozen.items())
        and not unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()
        and not unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages(), 'All old files unchanged and no dirty packages after operation')
    R.update(success=True, mesh=record, blueprint=dict(package=BP, parent=path(parent), layout=old_rows, graph_placeholders=graphs,
        connected_logic=False, local_scs_components=0, session=False, runtime_components=0),
        protected_before_after=frozen, protected_cdos=[dict(name=name, state=before) for name, old_cdo, before in originals],
        own_sha256={package: sha(asset_file(package)) for package in OWN}, cold_verified=phase == 'verify')


if __name__ == '__main__':
    if '--self-check' in sys.argv:
        tree = ast.parse(Path(__file__).read_text(encoding='utf-8'))
        calls = {node.func.attr for node in ast.walk(tree) if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)}
        assert not calls & {'load_level', 'save_current_level', 'spawn_actor_from_class', 'set_normalized_value', 'save_directory', 'save_asset', 'save_package', 'recompile_material', 'create_material_expression', 'connect_material_property'}
        assert sum(isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == 'save_loaded_asset' for node in ast.walk(tree)) == 1
        assert len(set(OWN)) == 2 and all('/Dev/ForestCanopyWide/' in package for package in OWN)
        assert LEAF in INPUTS and LEAF not in OWN
        assert all(package not in INPUTS for package in OWN) and SLOTS == ['Wood0', 'Leaf1']
        assert native_uv([.25, .75], True) == [.25, .25] and all(math.isfinite(value) and 0 <= value <= 1 for value in LEAF_COLOR)
        corners = [dict(position=p, normal=[.1, .2, math.sqrt(.95)], uv=u) for p, u in zip(
            ([.7, 1.2, -3], [2.1, 1.6, -1], [.2, 3.8, 2.4]), ([.1, .2], [.3, .4], [.6, .8]))]
        source = [dict(slot=0, corners=corners)]
        section = dict(material_slot=0, indices=[0, 1, 2], render=[dict(position=c['position'], normal=c['normal'], uv0=native_uv(c['uv'], True)) for c in corners])
        assert match_section(section, source, (0, 1, 2), (1, 1, 1), True) is not None
        assert match_section(dict(section, material_slot=1), source, (0, 1, 2), (1, 1, 1), True) is None
        assert match_section(section, source, (0, 1, 2), (-1, 1, 1), True) is None
        print('PASS static scope, two exact save identities, frozen reused leaf with no material mutation, finite leaf settings, native UV storage and per-material complete triangle matching/rejection; no Unreal or source file executed')
    else:
        phase = os.environ['DY_FOREST_CANOPY_PHASE']
        out = Path(os.environ['DY_FOREST_CANOPY_OUT'])
        source_sha = os.environ['DY_FOREST_CANOPY_SOURCE_SHA']
        meta_sha = os.environ['DY_FOREST_CANOPY_META_SHA']
        req(phase in ('create', 'verify') and out.is_absolute() and out.parent.is_dir() and out.suffix == '.json'
            and out.resolve().is_relative_to(AUDIT.resolve()) and not out.exists()
            and re.fullmatch(r'[0-9A-F]{64}', source_sha) and re.fullmatch(r'[0-9A-F]{64}', meta_sha), 'Explicit phase/frozen hashes and fresh bounded audit result before native action')
        R['phase'] = phase
        try:
            run(phase, source_sha, meta_sha)
        except Exception:
            R['error'] = traceback.format_exc()
        with out.open('x', encoding='utf-8') as stream:
            json.dump(R, stream, ensure_ascii=False, indent=2)
        req(R['success'], 'Native canopy operation failed; preserve evidence, never overwrite or auto-restore')


