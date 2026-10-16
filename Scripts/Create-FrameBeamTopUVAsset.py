"""One new FBX-derived Dev mesh; no map, shared material, or gameplay writes.

DY_TOPUV_PHASE=probe|create|verify and DY_TOPUV_OUT point to a fresh audit result.
Public UE Python/UFUNCTION readers are deliberately fail-closed. The probe must
pass before create. The create must pass before a separate cold verify session.
"""
import hashlib
import itertools
import json
import math
import os
import struct
import traceback
import unreal

ROOT = os.path.realpath(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir()))
AUDIT = os.path.join(ROOT, 'Saved', 'Audit-2026-10-13-FrameBeamTopUV')
OLD = '/Game/DengYingShanHai/Dev/FrameBeamAsset/Meshes/SM_DY_FrameBeam_Source'
NEW = '/Game/DengYingShanHai/Dev/FrameBeamTopUV/Meshes/SM_DY_FrameBeam_TopUV'
MI = '/Game/DengYingShanHai/Dev/FramePostAsset/Materials/MI_DY_FramePost_Wood'
MAT = '/Game/DengYingShanHai/Dev/FramePostAsset/Materials/M_DY_FramePost_Master'
SOURCE_NAME = 'frame-beam-topuv-calibrated.fbx'
SOURCE_SHA = '9D67085097B6EA5D18E098BFD5002D74148943F681182E2C17598EDC7835F999'
MAPPING_SHA = 'E1B811370CF28241D70DDEDF27444C04E21681B8AEBB17D324587ACC0D9F66B8'
PHASE = os.environ['DY_TOPUV_PHASE']
OUT = os.environ['DY_TOPUV_OUT']
R = dict(success=False, phase=PHASE, checks=[], saved=[], map_saved=False,
         actors_created=False, shared_material_changed=False, gameplay_tested=False,
         gpu_measured=False, art_accepted=False, packaged=False, shipping=False)
IMPORT_FIELDS = (
    'import_translation', 'import_rotation', 'import_uniform_scale',
    'convert_scene', 'force_front_x_axis', 'convert_scene_unit',
    'transform_vertex_to_absolute', 'bake_pivot_in_vertex', 'import_mesh_lods',
    'normal_import_method', 'normal_generation_method', 'compute_weighted_normals',
    'reorder_material_to_fbx_order', 'static_mesh_lod_group',
    'vertex_color_import_option', 'vertex_override_color', 'remove_degenerates',
    'build_reversed_index_buffer', 'build_nanite', 'generate_lightmap_u_vs',
    'one_convex_hull_per_ucx', 'auto_generate_collision', 'combine_meshes',
    'distance_field_resolution_scale')
BUILD_FIELDS = (
    'use_mikk_t_space', 'recompute_normals', 'recompute_tangents',
    'compute_weighted_normals', 'remove_degenerates', 'build_reversed_index_buffer',
    'use_high_precision_tangent_basis', 'use_full_precision_u_vs',
    'use_backwards_compatible_f16_trunc_u_vs', 'generate_lightmap_u_vs',
    'generate_distance_field_as_if_two_sided', 'support_face_remap',
    'min_lightmap_resolution', 'src_lightmap_index', 'dst_lightmap_index',
    'build_scale3d', 'distance_field_resolution_scale',
    'distance_field_replacement_mesh', 'max_lumen_mesh_cards')
MESH_FIELDS = (
    'allow_cpu_access', 'generate_mesh_distance_field', 'light_map_resolution',
    'light_map_coordinate_index', 'lod_for_collision', 'lod_group',
    'support_ray_tracing', 'support_uniformly_distributed_sampling',
    'support_gpu_uniformly_distributed_sampling', 'has_navigation_data',
    'positive_bounds_extension', 'negative_bounds_extension',
    'customized_collision', 'distance_field_self_shadow_bias')


def req(condition, message):
    if not condition:
        raise RuntimeError(message)
    R['checks'].append(message)
    return condition


def sha(filename):
    value = hashlib.sha256()
    with open(filename, 'rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            value.update(block)
    return value.hexdigest().upper()


def read(filename):
    with open(filename, encoding='utf-8-sig') as stream:
        return json.load(stream)


def object_path(value):
    return value.get_path_name() if value else None


def xyz(value):
    return [value.x, value.y, value.z]


def uv(value):
    return [value.x, value.y]


def scalar(value):
    if value is None or isinstance(value, (bool, int, float, str)):
        return value
    if isinstance(value, unreal.Object):
        return object_path(value)
    if isinstance(value, unreal.Vector):
        return xyz(value)
    if isinstance(value, unreal.Rotator):
        return [value.pitch, value.yaw, value.roll]
    if isinstance(value, unreal.Color):
        return [value.r, value.g, value.b, value.a]
    if hasattr(value, 'name'):
        return value.name
    return str(value)


def fields(obj, names):
    # Each property name is backed by installed 5.8 headers; no silent skips.
    return {name: scalar(obj.get_editor_property(name)) for name in names}


def protect():
    before = read(os.path.join(AUDIT, 'BEFORE.json'))
    req(before.get('MapSavesAllowed') is False and before.get('NewMaterialsAllowed') is False and
        before.get('NewTexturesAllowed') is False and before.get('SourceOnlyTopUV') is True,
        'Explicit no old map/source mutation baseline')
    rows = before['Files'] + before['Raw'] + before['Isolated'] + before['Archives']
    req(len(before['Files']) == 344 and len(before['Archives']) == 1026 and
        len(before['Raw']) == 15 and len(before['Isolated']) == 24,
        'Actual 344 product / 1026 archive / 15 raw / 24 isolated baseline')
    for row in rows:
        relative = row['Relative']
        target = os.path.abspath(os.path.join(ROOT, relative))
        req(os.path.commonpath([ROOT, target]) == ROOT and
            os.path.normcase(target) != os.path.normcase(os.path.join(ROOT, 'Docs', 'LICENSES.md')),
            'Exact permitted nonrestricted protected file')
        req(sha(target) == row['SHA256'], 'Protected ' + relative)
    if PHASE == 'verify':
        own = read(os.path.join(AUDIT, 'OWN-ASSET.json'))['File']
        req(own['Relative'] == 'Content\\DengYingShanHai\\Dev\\FrameBeamTopUV\\Meshes\\SM_DY_FrameBeam_TopUV.uasset' and
            sha(os.path.join(ROOT, own['Relative'])) == own['SHA256'],
            'Cold exact own package SHA before/after readonly verify')


def source_mapping():
    filename = os.path.join(AUDIT, 'Sources', SOURCE_NAME)
    mapping_name = os.path.join(AUDIT, 'Sources', 'POLYGON_MAPPING.json')
    req(sha(filename) == SOURCE_SHA and sha(mapping_name) == MAPPING_SHA,
        'Frozen independently reviewed source and actual on-disk mapping bytes')
    mapping = read(mapping_name)
    req(mapping['schema'] == 'FrameBeamTopUVPolygonMapping.v1' and
        mapping['candidate_sha256'] == SOURCE_SHA and
        mapping['source_sha256'] == 'D4CD58BDB649DB16C27D980BC9292160EF7EB69FA3B2BEF2453A0DCC3C59D628' and
        mapping['geometry_id'] == 512851073 and len(mapping['polygons']) == 10,
        'Exact original one beam, ten unchanged polygon contracts')
    corners = []
    for polygon in mapping['polygons']:
        req(len(polygon['corners']) == polygon['corner_count'], 'Actual corner count')
        for corner in polygon['corners']:
            corners.append(dict(corner, polygon=polygon['polygon']))
    req(len(corners) == 48 and sum(c['source_UV'] != c['candidate_UV'] for c in corners) == 2 and
        all(c['source_UV'] == c['candidate_UV'] for c in corners if c['polygon'] != 0),
        'Exactly two nonshared top-face UV corners changed, other nine faces exact')
    return filename, corners


def material():
    instance = req(unreal.load_asset(MI), 'Existing frozen wood instance')
    parent = req(unreal.load_asset(MAT), 'Existing frozen bounded wood parent')
    mel = unreal.MaterialEditingLibrary
    req(instance.get_editor_property('parent') == parent and
        mel.get_material_instance_scalar_parameter_value(instance, 'UVQuarterTurn') == 1.,
        'Exact existing quarter-turn instance, no new shader graph')
    req(parent.get_editor_property('material_domain') == unreal.MaterialDomain.MD_SURFACE and
        parent.get_editor_property('blend_mode') == unreal.BlendMode.BLEND_OPAQUE and
        parent.get_editor_property('shading_model') == unreal.MaterialShadingModel.MSM_DEFAULT_LIT and
        not parent.get_editor_property('two_sided') and parent.get_editor_property('tangent_space_normal'),
        'Actual Surface / Opaque / DefaultLit / single-sided / tangent-space parent')
    req(unreal.SystemLibrary.get_console_variable_int_value('r.Substrate') == 0,
        'Existing standard renderer retained')
    normal_root = mel.get_material_property_input_node(parent, unreal.MaterialProperty.MP_NORMAL)
    normal_inputs = list(mel.get_inputs_for_material_expression(parent, normal_root))
    req(len(normal_inputs) == 3 and normal_inputs[0], 'Existing normal lerp source remains readable')
    specs = [
        ('T_DY_FramePost_BaseColor', True, 'TC_DEFAULT',
         mel.get_material_property_input_node(parent, unreal.MaterialProperty.MP_BASE_COLOR)),
        ('T_DY_FramePost_NormalDX', False, 'TC_NORMALMAP', normal_inputs[0]),
        ('T_DY_FramePost_ARM', False, 'TC_MASKS',
         mel.get_material_property_input_node(parent, unreal.MaterialProperty.MP_ROUGHNESS))]
    records = []
    for name, srgb, compression, sample in specs:
        tex_path = '/Game/DengYingShanHai/Dev/FramePostAsset/Textures/' + name
        texture = req(unreal.load_asset(tex_path), 'Existing frozen PBR texture ' + name)
        before_size = [texture.blueprint_get_size_x(), texture.blueprint_get_size_y()]
        world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
        unreal.SystemLibrary.execute_console_command(world, 'Editor.AsyncAssetCompilationFinishAll', None)
        R.setdefault('texture_compilation_observations', []).append(dict(texture=name,
            before_dimensions=before_size,
            after_dimensions=[texture.blueprint_get_size_x(),texture.blueprint_get_size_y()],
            operation='Finish pending asset compilation only; no save or texture property writes'))
        source = scalar(sample.get_editor_property('sampler_source'))
        row = dict(path=object_path(texture), size=[texture.blueprint_get_size_x(), texture.blueprint_get_size_y()],
                   srgb=texture.get_editor_property('srgb'), compression=scalar(texture.get_editor_property('compression_settings')),
                   address_x=scalar(texture.get_editor_property('address_x')),
                   address_y=scalar(texture.get_editor_property('address_y')),
                   sampler_source=source, sampler_type=scalar(sample.get_editor_property('sampler_type')))
        R.setdefault('material_probe_rows', []).append(dict(row, sample_path=object_path(sample),
            sample_texture=object_path(sample.get_editor_property('texture')),
            texture_identity_equal=sample.get_editor_property('texture') == texture))
        req(sample.get_editor_property('texture') == texture and row['size'] == [2048, 2048] and
            row['srgb'] == srgb and row['compression'] == compression,
            'Actual frozen 2K texture / color space / compression ' + name)
        req(row['address_x'] == 'TA_WRAP' and row['address_y'] == 'TA_WRAP' and
            source in ('SSM_FROM_TEXTURE_ASSET', 'SSM_WRAP_WORLD_GROUP_SETTINGS'),
            'Actual repeating texture/sampler behavior (not assumed or edited) ' + name)
        records.append(row)
    R['material'] = dict(instance=MI, parent=MAT, textures=records, quarter_turn=1.,
                         new_permutations=0, graph_mutated=False, density_formal_accepted=False)
    return instance


def description(mesh):
    desc = req(mesh.get_static_mesh_description(0), 'Actual public MeshDescription wrapper')
    count = desc.get_vertex_instance_count()
    # Installed FbxStaticMeshImport.cpp:480-483 triangulates BEFORE assigning a
    # unique instance to each triangle corner (:894-905). Render welding is a
    # later stage, so this is 84 source instances, NOT 48 render vertices.
    req(count == 84 and desc.get_vertex_count() == 16 and desc.get_triangle_count() == 28 and
        desc.get_polygon_count() == 28,
        'Actual native imported 16 control points, 84 triangle-corner instances and 28 triangles/polygons')
    rows = []
    for index in range(count):
        identity = unreal.VertexInstanceID(id_value=index)
        req(desc.is_vertex_instance_valid(identity), 'Actual dense imported instance ID ' + str(index))
        vertex = desc.get_vertex_instance_vertex(identity)
        rows.append(dict(instance=index, vertex=vertex.get_editor_property('id_value'),
                         position=xyz(desc.get_vertex_position(vertex)),
                         uv0=uv(desc.get_vertex_instance_uv(identity, 0))))
    # get_num_tex_coords must remain EXACTLY 1, so channel0 is the full channel set.
    return dict(vertex_count=desc.get_vertex_count(), instance_count=count,
                triangle_count=desc.get_triangle_count(), polygon_count=desc.get_polygon_count(), rows=rows)


def mesh_record(mesh):
    req(mesh.get_class().get_name() == 'StaticMesh', 'Actual native static mesh, not a Blueprint')
    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    unreal.SystemLibrary.execute_console_command(world, 'Editor.AsyncAssetCompilationFinishAll', None)
    subsystem = unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
    bounds = mesh.get_bounds()
    build = subsystem.get_lod_build_settings(mesh, 0)
    import_data = req(mesh.get_editor_property('asset_import_data'), 'Actual saved FBX import data')
    req(import_data.get_class().get_name() == 'FbxStaticMeshImportData', 'Original legacy FBX importer settings')
    verts, triangles, normals, uvs, tangents = unreal.ProceduralMeshLibrary.get_section_from_static_mesh(mesh, 0, 0)
    req(len(verts) == len(normals) == len(uvs) == len(tangents) == 48 and len(triangles) == 84,
        'Actual public rendered section buffers: 48 vertices / 28 triangles')
    render = [dict(position=xyz(p), normal=xyz(n), uv0=uv(t),
                   tangent=xyz(g.get_editor_property('tangent_x')),
                   flip_tangent_y=g.get_editor_property('flip_tangent_y'))
              for p, n, t, g in zip(verts, normals, uvs, tangents)]
    static_materials = mesh.get_editor_property('static_materials')
    row = dict(object_path=object_path(mesh), bounds=dict(origin=xyz(bounds.origin), extent=xyz(bounds.box_extent),
               sphere_radius=bounds.sphere_radius), lod_count=mesh.get_num_lods(), vertices=mesh.get_num_vertices(0),
               triangles=mesh.get_num_triangles(0), uv_channels=mesh.get_num_tex_coords(0), sections=mesh.get_num_sections(0),
               slots=[dict(slot=str(s.get_editor_property('material_slot_name')),
                           imported_slot=str(s.get_editor_property('imported_material_slot_name')),
                           material=object_path(s.get_editor_property('material_interface'))) for s in static_materials],
               nanite=mesh.get_editor_property('nanite_settings').get_editor_property('enabled'),
               simple_collision_count=subsystem.get_simple_collision_count(mesh),
               section_collision=subsystem.is_section_collision_enabled(mesh, 0, 0),
               section_shadow=subsystem.is_section_cast_shadow_enabled(mesh, 0, 0),
               section_material_slot=subsystem.get_lod_material_slot(mesh, 0, 0),
               has_vertex_colors=subsystem.has_vertex_colors(mesh),
               auto_screen_sizes=mesh.is_lod_screen_size_auto_computed(),
               screen_sizes=list(subsystem.get_lod_screen_sizes(mesh)),
               mesh_settings=fields(mesh, MESH_FIELDS), build_settings=fields(build, BUILD_FIELDS),
               import_settings=fields(import_data, IMPORT_FIELDS),
               source_filenames=list(import_data.extract_filenames()),
               render_vertices=render, render_triangles=list(triangles), source_description=description(mesh))
    req(row['lod_count'] == 1 and row['vertices'] == 48 and row['triangles'] == 28 and
        row['uv_channels'] == 1 and row['sections'] == 1 and len(row['slots']) == 1 and
        row['slots'][0]['slot'] == '额枋' and row['slots'][0]['imported_slot'] == '额枋',
        'Exact one LOD, UV0-only, original 额枋 slot, source topology')
    req(row['simple_collision_count'] == 0 and not row['nanite'] and
        not row['mesh_settings']['generate_mesh_distance_field'],
        'No extra simple collision / Nanite / explicit distance-field generation')
    return row


def distance(a, b):
    return math.sqrt(sum((x-y)**2 for x, y in zip(a, b)))


def f32(value):
    return struct.unpack('f', struct.pack('f', value))[0]


def native_uv(values, flip_v, full_precision=True):
    # Installed FbxStaticMeshImport.cpp:758,926-927 explicitly casts each FBX
    # double to float BEFORE computing float(1.f - V) for DirectX.
    result = [f32(values[0]), f32(1. - f32(values[1])) if flip_v else f32(values[1])]
    if not full_precision:
        result = [struct.unpack('e', struct.pack('e', v))[0] for v in result]
    return result


def transformed(values, permutation, signs):
    return [values[permutation[i]] * signs[i] for i in range(3)]


def infer_conversion(old, corners):
    solutions = []
    for permutation in itertools.permutations(range(3)):
        for signs in itertools.product((-1, 1), repeat=3):
            for flip_v in (False, True):
                matches = []
                for vertex in old['render_vertices']:
                    found = []
                    for c in corners:
                        expected_uv = native_uv(c['source_UV'], flip_v)
                        if distance(vertex['position'], transformed(c['source_position_cm'], permutation, signs)) < .002 and \
                           distance(vertex['normal'], transformed(c['source_normal'], permutation, signs)) < .016 and \
                           distance(vertex['uv0'], expected_uv) < .0008:
                            found.append(c['corner'])
                    if len(found) != 1:
                        break
                    matches.append(found[0])
                if len(matches) == 48 and len(set(matches)) == 48:
                    solutions.append(dict(permutation=list(permutation), signs=list(signs), flip_v=flip_v, corners=matches))
    req(len(solutions) == 1, 'Unique source-to-native axis, handedness and V-flip conversion from actual 48 old render vertices')
    return solutions[0]


def compare(old, new, corners, conversion):
    mutable = {'object_path', 'source_filenames', 'render_vertices', 'source_description'}
    req(set(old) == set(new), 'Exact new/old native DTO keys')
    req(all(old[k] == new[k] for k in old if k not in mutable),
        'Bounds/topology/index order/UV channel/slot/material/build/import/collision/render flags EXACT old/new equality')
    req(new['slots'][0]['material'] == MI+'.'+MI.rsplit('/', 1)[1], 'Same frozen wood material object')
    # Actual unmodified geometry makes import metadata filename the only legal
    # import-info difference; no broad object path or property skip is used.
    req(len(old['source_filenames']) == len(new['source_filenames']) == 1 and
        sha(old['source_filenames'][0]) == 'D4CD58BDB649DB16C27D980BC9292160EF7EB69FA3B2BEF2453A0DCC3C59D628' and
        sha(new['source_filenames'][0]) == SOURCE_SHA, 'Only legal old/derived source-file import metadata difference')
    changed = []
    corner_by_id = {c['corner']: c for c in corners}
    precise = new['build_settings']['use_full_precision_u_vs']
    legacy_trunc = new['build_settings']['use_backwards_compatible_f16_trunc_u_vs']
    req(not legacy_trunc, 'Actual modern rounded half-float UV storage; no guessed legacy quantizer')
    for index, (a, b) in enumerate(zip(old['render_vertices'], new['render_vertices'])):
        c = corner_by_id[conversion['corners'][index]]
        req(a['position'] == b['position'] and a['normal'] == b['normal'], 'Exact rendered position/normal ' + str(index))
        req(a['flip_tangent_y'] == b['flip_tangent_y'], 'Same positive UV handedness ' + str(index))
        if c['polygon'] != 0:
            req(a['tangent'] == b['tangent'], 'Non-top tangent EXACTLY unchanged ' + str(index))
        else:
            tangent_quantum = .000055 if new['build_settings']['use_high_precision_tangent_basis'] else .016
            req(distance(a['tangent'], b['tangent']) <= tangent_quantum,
                'Positive axial-scale top tangent direction within actual 16/8-bit basis quantization bound ' + str(index))
        expected = native_uv(c['candidate_UV'], conversion['flip_v'], precise)
        req(b['uv0'] == expected, 'Actual render UV0 EXACT frozen source + installed float/half quantization ' + str(index))
        if a['uv0'] != b['uv0']:
            req(c['polygon'] == 0 and c['source_UV'] != c['candidate_UV'] and a['uv0'][0] == b['uv0'][0],
                'Only two polygon0 V components differ; U is untouched')
            changed.append(dict(render_vertex=index, source_corner=c['corner'], before=a['uv0'], after=b['uv0']))
        else:
            req(c['source_UV'] == c['candidate_UV'], 'Every unchanged render UV corresponds to unchanged source corner')
    req(len(changed) == 2, 'Exactly two actual changed rendered V values')
    a_desc, b_desc = old['source_description'], new['source_description']
    req(set(a_desc) == set(b_desc) and all(a_desc[k] == b_desc[k] for k in a_desc if k != 'rows'),
        'Source MeshDescription topology EXACT old/new equality')
    desc_changed = []
    for a, b in zip(a_desc['rows'], b_desc['rows']):
        req(a['instance'] == b['instance'] and a['vertex'] == b['vertex'] and a['position'] == b['position'],
            'Exact source instance identity/position ' + str(a['instance']))
        if a['uv0'] != b['uv0']:
            matches = [c for c in corners if distance(a['position'], transformed(c['source_position_cm'], conversion['permutation'], conversion['signs'])) < .002 and
                       a['uv0'] == native_uv(c['source_UV'], conversion['flip_v'])]
            req(len(matches) == 1 and matches[0]['polygon'] == 0 and matches[0]['source_UV'] != matches[0]['candidate_UV'] and a['uv0'][0] == b['uv0'][0],
                'Only top-face precise source V changed ' + str(a['instance']))
            c = matches[0]
            req(b['uv0'] == native_uv(c['candidate_UV'], conversion['flip_v']),
                'Precise source UV equals actual calibrated FBX + inferred native V conversion')
            desc_changed.append(dict(instance=a['instance'], source_corner=c['corner'], before=a['uv0'], after=b['uv0']))
        else:
            expected_changed = [c for c in corners if c['source_UV'] != c['candidate_UV'] and
                distance(a['position'], transformed(c['source_position_cm'], conversion['permutation'], conversion['signs'])) < .002 and
                a['uv0'] == native_uv(c['source_UV'], conversion['flip_v'])]
            req(not expected_changed, 'Every imported occurrence of a changed top corner actually changed')
    req({r['source_corner'] for r in desc_changed} == {c['corner'] for c in corners if c['source_UV'] != c['candidate_UV']},
        'Only the exact two top source corners changed across their native triangulated occurrences')
    return dict(changed_render_vertices=changed, changed_source_instances=desc_changed,
                non_top_uv_unchanged=True, topology_unchanged=True, normals_exact=True,
                tangents_same_direction_quantized=True, import_metadata_filename_only=True,
                source_axis_conversion=conversion, density_formal_accepted=False)


try:
    req(PHASE in ('probe', 'create', 'verify'), 'Only bounded native phases')
    req(os.path.commonpath([os.path.abspath(OUT), os.path.abspath(AUDIT)]) == os.path.abspath(AUDIT) and
        not os.path.exists(OUT), 'Fresh exact own audit result')
    protect()
    filename, corners = source_mapping()
    instance = material()
    req(hasattr(unreal, 'ProceduralMeshLibrary') and hasattr(unreal.ProceduralMeshLibrary, 'get_section_from_static_mesh'),
        'Already-installed default native ProceduralMesh reader is present; no plugin/config changes')
    old_mesh = req(unreal.load_asset(OLD), 'Original frozen source mesh')
    R['old_mesh'] = old = mesh_record(old_mesh)
    conversion = infer_conversion(old, corners)
    R['conversion'] = conversion
    if PHASE in ('probe', 'create'):
        req(not unreal.EditorAssetLibrary.does_asset_exist(NEW), 'Unique new TopUV package absent; never replace')
    if PHASE == 'create':
        probe_name = os.environ['DY_TOPUV_PROBE']
        probe_result = read(probe_name)
        req(probe_result['phase'] == 'probe' and probe_result['success'] is True and
            probe_result['old_mesh'] == old and probe_result['conversion'] == conversion,
            'Prior actual readonly native probe accepted this exact baseline')
        previous = unreal.SystemLibrary.get_console_variable_int_value('Interchange.FeatureFlags.Import.FBX')
        world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
        try:
            unreal.SystemLibrary.execute_console_command(world, 'Interchange.FeatureFlags.Import.FBX 0', None)
            options = unreal.FbxImportUI()
            options.set_editor_properties(dict(mesh_type_to_import=unreal.FBXImportType.FBXIT_STATIC_MESH,
                import_as_skeletal=False, import_mesh=True, import_animations=False, import_materials=False,
                import_textures=False, automated_import_should_detect_type=False, override_full_name=True))
            original_import = old_mesh.get_editor_property('asset_import_data')
            imports = options.get_editor_property('static_mesh_import_data')
            imports.set_editor_properties({name: original_import.get_editor_property(name) for name in IMPORT_FIELDS})
            req(imports.get_editor_property('import_uniform_scale') == 1. and
                imports.get_editor_property('normal_import_method') == unreal.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS and
                not imports.get_editor_property('auto_generate_collision') and
                not imports.get_editor_property('generate_lightmap_u_vs') and
                not imports.get_editor_property('build_nanite'), 'Exact old native import scale/normal/no-generated-assets policy')
            task = unreal.AssetImportTask()
            task.set_editor_properties(dict(filename=filename, destination_path=NEW.rsplit('/', 1)[0],
                destination_name=NEW.rsplit('/', 1)[1], factory=unreal.FbxFactory(), options=options,
                automated=True, replace_existing=False, save=False))
            unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
            req(list(task.get_editor_property('imported_object_paths')) == [NEW+'.'+NEW.rsplit('/', 1)[1]],
                'Only one new native mesh imported; no textures/materials/map')
            mesh = req(unreal.load_asset(NEW), 'Actual imported unique TopUV mesh')
            mesh.set_editor_property('generate_mesh_distance_field', old_mesh.get_editor_property('generate_mesh_distance_field'))
            mesh.set_material(0, instance)
        finally:
            unreal.SystemLibrary.execute_console_command(world, 'Interchange.FeatureFlags.Import.FBX '+str(previous), None)
            req(unreal.SystemLibrary.get_console_variable_int_value('Interchange.FeatureFlags.Import.FBX') == previous,
                'Restore process-only FBX importer flag, no Config writes')
    if PHASE in ('create', 'verify'):
        mesh = req(unreal.load_asset(NEW), 'Actual unique TopUV mesh')
        R['new_mesh'] = mesh_record(mesh)
        R['comparison'] = compare(old, R['new_mesh'], corners, conversion)
        if PHASE == 'create':
            req(object_path(mesh).split('.')[0] == NEW and
                unreal.EditorAssetLibrary.save_loaded_asset(mesh, only_if_is_dirty=False),
                'Save ONLY own single new TopUV mesh package')
            R['saved'] = [NEW]
        else:
            req(not R['saved'], 'Actual separate cold verify saves/reimports nothing')
    protect()
    R['success'] = True
except Exception:
    R['error'] = traceback.format_exc()
    unreal.log_error(R['error'])
finally:
    R['check_count'] = len(R['checks'])
    with open(OUT, 'x', encoding='utf-8') as stream:
        json.dump(R, stream, ensure_ascii=False, indent=2)
