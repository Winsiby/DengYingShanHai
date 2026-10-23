"""Bounded editor authoring: six new assets, then ONE passive right-wing actor.

Separate processes/phases: probe (read), assets (new saves, no map),
asset_inspect (read-only recovery of this own failed six-asset import),
place (map only after actual bounds and placement DTO are frozen), verify (read).
No puzzle/input/camera/light/old-material edits. Not a runtime Python dependency.
"""
import hashlib
import json
import math
import os
import traceback
from urllib.parse import urlparse
import unreal

ROOT = os.path.realpath(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir()))
AUDIT = os.path.join(ROOT, 'Saved', 'Audit-2026-10-11-StageWings')
MAP = '/Game/DengYingShanHai/Dev/EnvironmentStates/Maps/LV_EnvironmentStatesLab'
BASE = '/Game/DengYingShanHai/Dev/StageWings/'
SM = BASE + 'Meshes/SM_DY_WingScreen'
MAT = BASE + 'Materials/M_DY_WingScreen_Master'
MI = BASE + 'Materials/MI_DY_WingScreen_Dev'
LABEL = 'DEV_WingScreen_Right'
SOURCE_DIR = os.path.join(ROOT, 'Assets/Sources/PolyHaven/chinese_screen_panels')
SPECS = [
    ('T_DY_WingScreen_BaseColor', 'Diffuse', True, 'TC_DEFAULT', 'SAMPLERTYPE_COLOR', 'BaseColor'),
    ('T_DY_WingScreen_NormalDX', 'nor_dx', False, 'TC_NORMALMAP', 'SAMPLERTYPE_NORMAL', 'NormalDX'),
    ('T_DY_WingScreen_ARM', 'arm', False, 'TC_MASKS', 'SAMPLERTYPE_MASKS', 'ARM')]
ASSETS = sorted([SM, MAT, MI] + [BASE + 'Textures/' + s[0] for s in SPECS])
OUT = os.environ['DY_READABILITY_OUT']
PHASE = os.environ['DY_READABILITY_PHASE']
R = dict(success=False, phase=PHASE, saved=[], checks=[], assets=ASSETS, map=MAP)
MEL = unreal.MaterialEditingLibrary
CORE_MIN, CORE_MAX = [-440., -470., -70.], [975., 470., 770.]


def req(value, message):
    if not value:
        raise RuntimeError(message)
    R['checks'].append(message)
    return value


def path(value):
    return value.get_path_name() if value else None


def xyz(value):
    return [value.x, value.y, value.z]


def enum_name(value):
    return value.name if hasattr(value, 'name') else str(value).split('.')[-1]


def transform(value):
    q = value.rotation
    return dict(location=xyz(value.translation), scale=xyz(value.scale3d),
                rotation=[q.x, q.y, q.z, q.w])


def sha(filename):
    digest = hashlib.sha256()
    with open(filename, 'rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest().upper()


def read_json(filename):
    with open(filename, encoding='utf-8-sig') as stream:
        return json.load(stream)


def project_file(relative):
    value = os.path.abspath(os.path.join(ROOT, relative))
    req(os.path.commonpath([value, os.path.abspath(ROOT)]) == os.path.abspath(ROOT),
        'File remains inside exact project')
    req(os.path.normcase(value) != os.path.normcase(os.path.join(ROOT, 'Docs/LICENSES.md')),
        'Never access restricted existing license register')
    return value


def protect():
    before = read_json(os.path.join(AUDIT, 'BEFORE.json'))
    for row in before['Files']:
        if row['Relative'] not in before['Approved']:
            req(sha(project_file(row['Relative'])) == row['SHA256'], 'Protected ' + row['Relative'])
    for row in before['OldRaw']:
        req(sha(project_file(row['Relative'])) == row['SHA256'], 'Existing raw source ' + row['Relative'])
    for row in read_json(os.path.join(AUDIT, 'RAW-SOURCES.json')):
        req(sha(project_file(row['Relative'])) == row['SHA256'], 'New raw source ' + row['Relative'])


def save_asset(asset):
    package = path(asset).split('.')[0]
    req(package in ASSETS, 'Exact six-package asset save allowlist')
    req(unreal.EditorAssetLibrary.save_loaded_asset(asset, only_if_is_dirty=False), 'Save own ' + package)
    R['saved'].append(package)


def component_row(component):
    result = dict(name=component.get_name(), object_path=path(component),
                  class_path=path(component.get_class()), relative_transform=transform(component.get_relative_transform()),
                  world_transform=transform(component.get_world_transform()), mobility=enum_name(component.get_editor_property('mobility')))
    if isinstance(component, unreal.StaticMeshComponent):
        result.update(mesh=path(component.get_editor_property('static_mesh')),
            materials=[path(component.get_material(i)) for i in range(component.get_num_materials())],
            collision_profile=str(component.get_collision_profile_name()), collision_enabled=enum_name(component.get_collision_enabled()),
            cast_shadow=component.get_editor_property('cast_shadow'),
            affect_dynamic_indirect_lighting=component.get_editor_property('affect_dynamic_indirect_lighting'),
            affect_distance_field_lighting=component.get_editor_property('affect_distance_field_lighting'))
    if isinstance(component, unreal.LightComponentBase):
        color = component.get_light_color()
        result.update(intensity=component.get_editor_property('intensity'), color=[color.r, color.g, color.b, color.a],
                      casts_shadows=component.get_editor_property('cast_shadows'))
    if isinstance(component, unreal.LocalLightComponent):
        result.update(intensity_units=enum_name(component.get_editor_property('intensity_units')),
                      attenuation_radius=component.get_editor_property('attenuation_radius'))
    if isinstance(component, unreal.PointLightComponent):
        result['source_radius'] = component.get_editor_property('source_radius')
    if isinstance(component, unreal.SpotLightComponent):
        result.update(inner_cone=component.get_editor_property('inner_cone_angle'), outer_cone=component.get_editor_property('outer_cone_angle'))
    return result


def scene():
    # Load only the old read-only function prefix, never its authoring entry point.
    code = open(os.path.join(ROOT, 'Scripts/Create-EnvironmentStates.py'), encoding='utf-8-sig').read()
    namespace = {'__name__': 'stage_wings_scene_reader'}
    exec(code.split('\ntry:\n')[0], namespace)
    world, actors, stage, contract = namespace['contract']()
    req(len({a.get_actor_label() for a in actors}) == len(actors), 'Unique saved actor labels, no silent dictionary overwrite')
    for actor in actors:
        row = contract[actor.get_actor_label()]
        row['object_path'] = path(actor)
        row['tick_enabled'] = actor.is_actor_tick_enabled()
        row['static_meshes'] = [component_row(c) for c in actor.get_components_by_class(unreal.StaticMeshComponent)]
        row['lights'] = [component_row(c) for c in actor.get_components_by_class(unreal.LightComponentBase)]
    director = stage.get_puzzle_director()
    light, puppet = director.get_light_rig_actor(), director.get_puppet_actor()
    for actor, component_name in [(light, 'LightControl'), (puppet, 'PuppetControl')]:
        component = req(actor.get_editor_property(component_name), 'Explicit existing rail component')
        value = dict(object_path=path(component), world_travel_axis=xyz(component.get_editor_property('WorldTravelAxis')),
            travel_distance=component.get_editor_property('TravelDistance'), initial_value=component.get_editor_property('InitialNormalizedValue'),
            normalized_units_per_second=component.get_editor_property('NormalizedUnitsPerSecond'))
        if component_name == 'PuppetControl':
            value['pose_ids'] = [str(v) for v in component.get_editor_property('PoseIds')]
        contract[actor.get_actor_label()]['rail'] = value
    forest = req(stage.get_forest_presentation_actor(), 'Explicit existing forest owner')
    rows = []
    for item in forest.get_editor_property('BranchLayout'):
        start, end = item.get_editor_property('StartScreenOffset'), item.get_editor_property('EndScreenOffset')
        rows.append(dict(parent_index=item.get_editor_property('ParentIndex'), start=[start.x, start.y], end=[end.x, end.y],
            diameter=item.get_editor_property('DiameterWorld'), begin=item.get_editor_property('GrowthBegin'), finish=item.get_editor_property('GrowthEnd')))
    contract[forest.get_actor_label()]['forest_authoring'] = dict(mesh=path(forest.get_editor_property('BranchMesh')),
        material=path(forest.get_editor_property('BranchMaterial')), layout=rows,
        has_session=forest.has_forest_session(), runtime_components=[path(c) for c in forest.get_branch_mesh_components()])
    contract[stage.get_actor_label()]['bindings'] = dict(director=path(director), environment=path(stage.get_stage_environment()), forest=path(forest),
        screen=path(stage.get_editor_property('StaffProjectionScreen')), ground=path(stage.get_editor_property('NarrativeGroundLine')),
        dev_receiver=path(stage.get_editor_property('DevReceiver')), dev_ground=path(stage.get_editor_property('DevGround')),
        five_state=stage.is_five_state_environment_enabled(), staff_enabled=stage.get_editor_property('bEnableStaffContactPresentation'),
        alignment_enabled=stage.get_editor_property('bEnablePlayerAlignmentFeedback'))
    audio = req(next((a for a in actors if a.get_actor_label() == 'AudioDev_Presentation'), None), 'Exact existing audio owner')
    contract[audio.get_actor_label()]['audio_binding'] = dict(stage=path(audio.get_editor_property('StagePresentation')),
        enabled=audio.get_editor_property('bEnableDevelopmentAudio'), theatre_reverb=audio.get_editor_property('bEnableTheatreReverb'))
    floor = req(next((a for a in actors if a.get_actor_label() == 'DEV_Floor'), None), 'Exact existing floor')
    component = floor.get_component_by_class(unreal.StaticMeshComponent)
    origin, extent = floor.get_actor_bounds(False)
    return world, actors, stage, contract, floor, component, dict(origin=xyz(origin), extent=xyz(extent))


def baseline(probe_data, allow_wing):
    req(probe_data['success'] and probe_data['phase'] == 'probe' and not probe_data['saved'], 'Frozen successful read-only probe')
    current = scene()
    expected = probe_data['scene_contract']
    req(len([k for k in expected if not k.startswith('_')]) == 32 and LABEL not in expected, 'Exact 32 actor baseline')
    expected_keys = set(expected) | ({LABEL} if allow_wing else set())
    req(set(current[3]) == expected_keys, 'Only the exact one new actor label is permitted')
    req(all(current[3][key] == value for key, value in expected.items()), 'Every original actor identity and full component/rail/flow contract preserved')
    R['source_contract_preserved'] = True
    return current


def wood_floor_contract():
    # Reuse all audited material/texture/render observations, NOT the obsolete
    # pre-wood-floor scene comparison. Full current scene preservation is above.
    filename = os.path.join(ROOT, 'Scripts/Create-WoodFloorDev.py')
    code = open(filename, encoding='utf-8-sig').read().split('\ntry:\n')[0]
    old_line = "    req(comparable(contract)==comparable(probe_data['scene_contract']),'Frozen scene unchanged except exact floor slot zero')\n"
    req(code.count(old_line) == 1, 'Exact reviewed old wood comparison statement')
    namespace = {'__name__': 'stage_wings_inherited_wood_reader'}
    exec(code.replace(old_line, ''), namespace)
    namespace['scene'] = scene
    namespace['verify']({})
    result = namespace['R']
    result.update(success=True, phase='verify', saved=[], scene_contract_preservation_owner='StageWings full 32-actor baseline')
    return result


def sources():
    data = read_json(os.path.join(SOURCE_DIR, 'ACQUISITION.json'))
    req(data['Status'] == 'PASS' and data['Source'] == 'https://polyhaven.com/a/chinese_screen_panels'
        and data['License'] == 'CC0-1.0' and data['PreviewRendersUsed'] is False, 'Actual successful CC0 acquisition manifest')
    req(len(data['Files']) == 4 and {row['Kind'] for row in data['Files']} == {'fbx', 'Diffuse', 'nor_dx', 'arm'}, 'Exactly four official source files')
    result = {}
    for row in data['Files']:
        req(os.path.basename(row['Name']) == row['Name'] and urlparse(row['URL']).hostname == 'dl.polyhaven.org', 'Bounded official raw filename/host')
        filename = os.path.join(SOURCE_DIR, row['Name'])
        req(os.path.getsize(filename) == row['Bytes'] and sha(filename) == row['SHA256'], 'Raw bytes/SHA256 ' + row['Kind'])
        if row['Kind'] != 'fbx':
            req(row['Dimensions'] == [2048, 2048], 'Official 2K PNG input ' + row['Kind'])
        result[row['Kind']] = dict(row, project_relative=os.path.relpath(filename, ROOT), physical=filename)
    R['source_files'] = [{k: v for k, v in row.items() if k != 'physical'} for row in result.values()]
    return result


def mesh_contract(mesh):
    bounds = mesh.get_bounds()
    origin, extent = xyz(bounds.origin), xyz(bounds.box_extent)
    lower = [a-b for a, b in zip(origin, extent)]
    upper = [a+b for a, b in zip(origin, extent)]
    size = [2*v for v in extent]
    req(all(math.isfinite(v) for v in origin+extent) and all(v > 0 for v in extent), 'Actual finite nonzero imported mesh bounds')
    lods = mesh.get_num_lods()
    req(lods > 0, 'Actual imported render LOD')
    info = dict(package=SM, object_path=path(mesh), local_bounds=dict(origin=origin, extent=extent, min=lower, max=upper), dimensions_cm=size,
        lods=[dict(index=i, vertices=mesh.get_num_vertices(i), triangles=mesh.get_num_triangles(i), uv_channels=mesh.get_num_tex_coords(i), sections=mesh.get_num_sections(i)) for i in range(lods)],
        materials=[path(slot.get_editor_property('material_interface')) for slot in mesh.get_editor_property('static_materials')],
        nanite_enabled=mesh.get_editor_property('nanite_settings').get_editor_property('enabled'),
        simple_collision_count=req(unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem),
            'StaticMeshEditorSubsystem must be initialized in full editor; no commandlet guess').get_simple_collision_count(mesh),
        generate_mesh_distance_field=mesh.get_editor_property('generate_mesh_distance_field'),
        flat_horizontal_axis='X' if size[0] < size[1] else 'Y', placement_yaw_approved=False)
    req(all(lod['vertices'] > 0 and lod['triangles'] > 0 and lod['uv_channels'] > 0 for lod in info['lods']), 'Real render triangles/vertices/UVs, not website polycount')
    req(not info['nanite_enabled'] and info['simple_collision_count'] == 0, 'No Nanite or generated simple collision')
    return info


def probe():
    world, actors, stage, contract, floor, component, bounds = scene()
    req(len(actors) == 32 and LABEL not in contract, 'Exactly current 32 actors before additions')
    req(stage.is_five_state_environment_enabled(), 'Accepted five-state opt-in unchanged')
    req(all(not unreal.EditorAssetLibrary.does_asset_exist(p) for p in ASSETS), 'Six destinations absent before authoring')
    api = dict(fbx_factory=hasattr(unreal, 'FbxFactory'), fbx_options=hasattr(unreal, 'FbxImportUI'),
        fbx_static_type=enum_name(unreal.FBXImportType.FBXIT_STATIC_MESH),
        mesh_bounds=hasattr(unreal.StaticMesh, 'get_bounds'), mesh_triangles=hasattr(unreal.StaticMesh, 'get_num_triangles'),
        mesh_vertices=hasattr(unreal.StaticMesh, 'get_num_vertices'), mesh_uvs=hasattr(unreal.StaticMesh, 'get_num_tex_coords'),
        mesh_lods=hasattr(unreal.StaticMesh, 'get_num_lods'),
        fbx_feature_flag=unreal.SystemLibrary.get_console_variable_int_value('Interchange.FeatureFlags.Import.FBX'))
    req(all(api[k] for k in ('fbx_factory','fbx_options','mesh_bounds','mesh_triangles','mesh_vertices','mesh_uvs','mesh_lods')), 'Actual reflected mesh/import APIs')
    options = unreal.FbxImportUI()
    imports = options.get_editor_property('static_mesh_import_data')
    api['static_import_options'] = {name: str(imports.get_editor_property(name)) for name in
        ('combine_meshes','auto_generate_collision','build_nanite','convert_scene','convert_scene_unit','import_uniform_scale','normal_import_method')}
    R.update(scene_contract=contract, actor_count=len(actors), floor_bounds=bounds, api=api, wood_floor_contract=wood_floor_contract())


def create_assets(probe_data):
    world = baseline(probe_data, False)[0]
    reused = {}
    resume_name = os.environ.get('DY_STAGEWINGS_RESUME')
    if resume_name:
        resume = read_json(resume_name)
        expected = [BASE+'Textures/'+spec[0] for spec in SPECS]
        req(resume['schema'] == 'StageWingsResume.v1' and resume['NoOverwrite'] is True,
            'Exact own failed-three-texture resume contract')
        failed_file = project_file(resume['FailedResult'])
        req(sha(failed_file) == resume['FailedResultSHA256'], 'Immutable original failed assets evidence')
        failed = read_json(failed_file)
        req(failed['success'] is False and failed['phase'] == 'assets' and failed['saved'] == expected
            and 'Failed to find property' in failed['error'] and 'import_ui' in failed['error'],
            'Only actual factory-property failure after exactly own three texture saves')
        req(len(resume['Files']) == 3 and [row['Package'] for row in resume['Files']] == expected,
            'Only the three actual failed-run texture packages can be reused')
        for row in resume['Files']:
            rel = 'Content/'+row['Package'][6:]+'.uasset'
            req(os.path.normcase(os.path.normpath(row['Relative'])) == os.path.normcase(os.path.normpath(rel)),
                'Resume names the exact own texture disk file')
            req(sha(project_file(row['Relative'])) == row['SHA256'], 'Own saved texture frozen before resume')
            texture = req(unreal.load_asset(row['Package']), 'Actual reused own texture exists')
            spec = next(spec for spec in SPECS if BASE+'Textures/'+spec[0] == row['Package'])
            req([texture.blueprint_get_size_x(),texture.blueprint_get_size_y()] == [2048,2048]
                and texture.get_editor_property('srgb') == spec[2]
                and enum_name(texture.get_editor_property('compression_settings')) == spec[3],
                'Verify reused texture size/color/compression without import or save')
            reused[row['Package']] = dict(row, texture=texture)
        req(all(not unreal.EditorAssetLibrary.does_asset_exist(p) for p in ASSETS if p not in reused),
            'All other own three asset destinations remain absent; never overwrite')
        R.update(reused_assets=expected, resume_contract={k:v for k,v in resume.items()},
                 reused_assets_overwritten=False)
    else:
        req(all(not unreal.EditorAssetLibrary.does_asset_exist(p) for p in ASSETS), 'Never overwrite an existing asset during import')
        R['reused_assets'] = []
    inputs = sources()
    tools = unreal.AssetToolsHelpers.get_asset_tools()
    textures = []
    for name, kind, srgb, compression, sampler, parameter in SPECS:
        package = BASE+'Textures/'+name
        if package in reused:
            textures.append(reused[package]['texture'])
            continue
        task = unreal.AssetImportTask()
        task.set_editor_properties(dict(filename=inputs[kind]['physical'], destination_path=BASE+'Textures', destination_name=name,
            automated=True, replace_existing=False, save=False))
        tools.import_asset_tasks([task])
        expected = BASE+'Textures/'+name+'.'+name
        req(list(task.get_editor_property('imported_object_paths')) == [expected], 'Exactly one named new texture import')
        texture = req(unreal.load_asset(expected), 'Imported actual texture')
        texture.set_editor_properties(dict(srgb=srgb, compression_settings=getattr(unreal.TextureCompressionSettings, compression)))
        save_asset(texture)
        textures.append(texture)
    # Child-process CVar only; native headers confirm legacy FBX option names.
    previous = unreal.SystemLibrary.get_console_variable_int_value('Interchange.FeatureFlags.Import.FBX')
    unreal.SystemLibrary.execute_console_command(world, 'Interchange.FeatureFlags.Import.FBX 0', None)
    req(unreal.SystemLibrary.get_console_variable_int_value('Interchange.FeatureFlags.Import.FBX') == 0, 'Child-only explicit legacy FBX import path')
    options = unreal.FbxImportUI()
    options.set_editor_properties(dict(mesh_type_to_import=unreal.FBXImportType.FBXIT_STATIC_MESH,
        import_as_skeletal=False, import_mesh=True, import_animations=False, import_materials=False, import_textures=False,
        automated_import_should_detect_type=False, override_full_name=True))
    imports = options.get_editor_property('static_mesh_import_data')
    imports.set_editor_properties(dict(combine_meshes=True, auto_generate_collision=False, build_nanite=False,
        generate_lightmap_u_vs=False, convert_scene=True, convert_scene_unit=True, import_uniform_scale=1.,
        transform_vertex_to_absolute=True, bake_pivot_in_vertex=False,
        normal_import_method=unreal.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS))
    factory = unreal.FbxFactory()
    # UFbxFactory::FactoryCreateFile (FbxFactory.cpp:345-353) explicitly accepts
    # UFbxImportUI through AssetImportTask.Options. ImportUI is not Python-exposed.
    task = unreal.AssetImportTask()
    task.set_editor_properties(dict(filename=inputs['fbx']['physical'], destination_path=BASE+'Meshes', destination_name=SM.rsplit('/',1)[1],
        factory=factory, options=options, automated=True, replace_existing=False, save=False))
    tools.import_asset_tasks([task])
    req(list(task.get_editor_property('imported_object_paths')) == [SM+'.'+SM.rsplit('/',1)[1]], 'Exactly one combined static mesh, no generated FBX materials/textures')
    mesh = req(unreal.load_asset(SM), 'Actual imported mesh')
    mesh.set_editor_property('generate_mesh_distance_field', False)
    material = req(tools.create_asset(MAT.rsplit('/',1)[1], MAT.rsplit('/',1)[0], unreal.Material, unreal.MaterialFactoryNew()), 'New bounded screen material')
    material.set_editor_properties(dict(material_domain=unreal.MaterialDomain.MD_SURFACE,
        blend_mode=unreal.BlendMode.BLEND_OPAQUE, shading_model=unreal.MaterialShadingModel.MSM_DEFAULT_LIT,
        two_sided=False, tangent_space_normal=True, use_material_attributes=False))
    req(unreal.SystemLibrary.get_console_variable_int_value('r.Substrate') == 0, 'Preserve actual standard PBR renderer')
    nodes = []
    def node(cls, **properties):
        result = req(MEL.create_material_expression(material, cls, len(nodes)%6*220, len(nodes)//6*200), 'Own material node '+cls.__name__)
        result.set_editor_properties(properties)
        nodes.append(result)
        return result
    def connect(a, output, b, slot):
        req(MEL.connect_material_expressions(a, output, b, slot), 'Actual graph link '+slot)
    uv = node(unreal.MaterialExpressionTextureCoordinate, coordinate_index=0)
    u = node(unreal.MaterialExpressionScalarParameter, parameter_name='TilingU', default_value=1.)
    v = node(unreal.MaterialExpressionScalarParameter, parameter_name='TilingV', default_value=1.)
    pair = node(unreal.MaterialExpressionAppendVector)
    connect(u,'',pair,'A'); connect(v,'',pair,'B')
    scaled = node(unreal.MaterialExpressionMultiply)
    connect(uv,'',scaled,'A'); connect(pair,'',scaled,'B')
    samples = []
    for texture, spec in zip(textures, SPECS):
        sample = node(unreal.MaterialExpressionTextureSampleParameter2D, parameter_name=spec[5], texture=texture,
                      sampler_type=getattr(unreal.MaterialSamplerType,spec[4]))
        connect(scaled,'',sample,'UVs')
        samples.append(sample)
    for sample, output, prop in [(samples[0],'RGB',unreal.MaterialProperty.MP_BASE_COLOR),
        (samples[1],'RGB',unreal.MaterialProperty.MP_NORMAL), (samples[2],'G',unreal.MaterialProperty.MP_ROUGHNESS),
        (samples[2],'R',unreal.MaterialProperty.MP_AMBIENT_OCCLUSION), (samples[2],'B',unreal.MaterialProperty.MP_METALLIC)]:
        req(MEL.connect_material_property(sample,output,prop), 'Actual standard PBR root '+enum_name(prop))
    specular = node(unreal.MaterialExpressionConstant,r=.5)
    req(MEL.connect_material_property(specular,'',unreal.MaterialProperty.MP_SPECULAR), 'Default dielectric specular .5')
    req(not list(MEL.recompile_material(material)), 'Own legacy PBR compiles without shader errors')
    save_asset(material)
    instance = req(tools.create_asset(MI.rsplit('/',1)[1],MI.rsplit('/',1)[0],unreal.MaterialInstanceConstant,
                   unreal.MaterialInstanceConstantFactoryNew()), 'New constant material instance')
    MEL.set_material_instance_parent(instance,material)
    for name in ('TilingU','TilingV'):
        MEL.set_material_instance_scalar_parameter_value(instance,name,1.)
        req(MEL.get_material_instance_scalar_parameter_value(instance,name) == 1., 'Actual UV1 scalar readback '+name)
    MEL.update_material_instance(instance)
    save_asset(instance)
    slots = len(mesh.get_editor_property('static_materials'))
    req(slots > 0, 'Actual FBX material slots present')
    for index in range(slots):
        mesh.set_material(index,instance)
    save_asset(mesh)
    unreal.SystemLibrary.execute_console_command(world,'Interchange.FeatureFlags.Import.FBX '+str(previous),None)
    baseline(probe_data,False)
    R.update(mesh=mesh_contract(mesh), legacy_fbx_import=dict(child_only=True, previous_flag=previous,
        restored_flag=unreal.SystemLibrary.get_console_variable_int_value('Interchange.FeatureFlags.Import.FBX'),
        source_sha256=inputs['fbx']['SHA256'], import_materials=False, import_textures=False,
        import_uniform_scale=1., convert_scene_unit=True, combine_meshes=True), map_saved=False, actor_count=32)
    verify_assets()
    req(set(R['saved']) | set(R['reused_assets']) == set(ASSETS)
        and len(R['saved']) + len(R['reused_assets']) == 6, 'All exact six own assets accounted for once')
    for row in reused.values():
        req(sha(project_file(row['Relative'])) == row['SHA256'], 'Own reused texture was not overwritten or resaved')


def verify_assets():
    inputs = sources()
    mesh = req(unreal.load_asset(SM),'Cold exact mesh')
    instance, material = req(unreal.load_asset(MI),'Cold exact instance'), req(unreal.load_asset(MAT),'Cold exact parent')
    # Full editor can return async placeholder resources during startup. The
    # actual engine command waits for compilation, without saving or changing
    # renderer/async configuration (AssetCompilingManager.cpp / helpers).
    ready_textures=[req(unreal.load_asset(BASE+'Textures/'+spec[0]),'Load actual verification texture') for spec in SPECS]
    R['texture_sizes_before_native_finish']=[[t.blueprint_get_size_x(),t.blueprint_get_size_y()] for t in ready_textures]
    unreal.SystemLibrary.execute_console_command(unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world(),
        'Editor.AsyncAssetCompilationFinishAll',None)
    R['native_compilation_wait']='Editor.AsyncAssetCompilationFinishAll; no setting mutation or save'
    req(instance.get_editor_property('parent') == material,'Actual wing instance parent')
    req(unreal.SystemLibrary.get_console_variable_int_value('r.Substrate') == 0,'Unchanged legacy PBR renderer')
    req(MEL.get_material_property_input_node(material,unreal.MaterialProperty.MP_FRONT_MATERIAL) is None,'No inactive Substrate root')
    graph = {}
    for prop, param, channel, spec in [(unreal.MaterialProperty.MP_BASE_COLOR,'BaseColor','RGB',SPECS[0]),
        (unreal.MaterialProperty.MP_NORMAL,'NormalDX','RGB',SPECS[1]), (unreal.MaterialProperty.MP_ROUGHNESS,'ARM','G',SPECS[2]),
        (unreal.MaterialProperty.MP_AMBIENT_OCCLUSION,'ARM','R',SPECS[2]),(unreal.MaterialProperty.MP_METALLIC,'ARM','B',SPECS[2])]:
        expression = req(MEL.get_material_property_input_node(material,prop),'Actual wing root '+enum_name(prop))
        output = MEL.get_material_property_input_node_output_name(material,prop)
        req(str(expression.get_editor_property('parameter_name')) == param and output == channel,'Actual wing root channel '+param+'/'+channel)
        req(path(expression.get_editor_property('texture')) == BASE+'Textures/'+spec[0]+'.'+spec[0], 'Exact wing root texture')
        req(enum_name(expression.get_editor_property('sampler_type')) == spec[4],'Actual sampler interpretation')
        graph[enum_name(prop)] = dict(node=path(expression),output=output,texture=path(expression.get_editor_property('texture')))
    constant = req(MEL.get_material_property_input_node(material,unreal.MaterialProperty.MP_SPECULAR),'Specular root')
    req(constant.get_class().get_name() == 'MaterialExpressionConstant' and constant.get_editor_property('r') == .5,'Actual specular .5')
    tex_rows = []
    for spec in SPECS:
        texture = req(unreal.load_asset(BASE+'Textures/'+spec[0]),'Cold exact wing texture')
        size = [texture.blueprint_get_size_x(),texture.blueprint_get_size_y()]
        R.setdefault('texture_diagnostics',[]).append(dict(package=BASE+'Textures/'+spec[0],dimensions=size,
            srgb=texture.get_editor_property('srgb'),compression=enum_name(texture.get_editor_property('compression_settings'))))
        req(size == [2048,2048] and texture.get_editor_property('srgb') == spec[2]
            and enum_name(texture.get_editor_property('compression_settings')) == spec[3], 'Actual size/color/compression '+spec[0])
        req(MEL.get_material_instance_texture_parameter_value(instance,spec[5]) == texture,'Actual instance texture '+spec[5])
        tex_rows.append(dict(package=BASE+'Textures/'+spec[0], dimensions=size, srgb=spec[2], compression=spec[3], source_sha256=inputs[spec[1]]['SHA256']))
    req(material.get_editor_property('material_domain') == unreal.MaterialDomain.MD_SURFACE
        and material.get_editor_property('shading_model') == unreal.MaterialShadingModel.MSM_DEFAULT_LIT
        and material.get_editor_property('blend_mode') == unreal.BlendMode.BLEND_OPAQUE and not material.get_editor_property('two_sided')
        and material.get_editor_property('tangent_space_normal') and not material.get_editor_property('use_material_attributes'), 'Opaque single-sided tangent-space standard PBR')
    req(all(MEL.get_material_instance_scalar_parameter_value(instance,n) == 1. for n in ('TilingU','TilingV')),'Own original UV atlas 1x1')
    uv_inputs = list(MEL.get_inputs_for_material_expression(material, MEL.get_material_property_input_node(material,unreal.MaterialProperty.MP_BASE_COLOR)))
    req(len(uv_inputs) >= 1 and uv_inputs[0].get_class().get_name() == 'MaterialExpressionMultiply','Sample UV driven by bounded tiling')
    pair_inputs = list(MEL.get_inputs_for_material_expression(material,uv_inputs[0]))
    req(len(pair_inputs) == 2 and pair_inputs[0].get_class().get_name() == 'MaterialExpressionTextureCoordinate'
        and pair_inputs[0].get_editor_property('coordinate_index') == 0, 'Actual UV0 source')
    errors = list(MEL.recompile_material(material))
    req(not errors,'Cold wing material compile without shader errors')
    info = mesh_contract(mesh)
    req(info['materials'] and all(p == path(instance) for p in info['materials']), 'All real imported mesh slots bind exact wing instance')
    R.update(mesh=info,textures=tex_rows,graph_inputs=graph,shader_errors=errors,
        materials=dict(root_bsdf='StandardPBR',standard_pbr_verified=True,substrate_enabled=False,opaque=True,two_sided=False,
            normal_tangent_space=True,tiling_u=1.,tiling_v=1.,instance_parent=path(material),specular=.5,metallic_from_arm_b=True),
        render_settings=dict(substrate_cvar=0,use_material_attributes=False,front_material_root=None))


def owned_assets(data=None):
    snapshot = data if data is not None else read_json(os.environ['DY_STAGEWINGS_OWNED_SNAPSHOT'])
    req(snapshot['schema'] == 'StageWingsOwnedAssets.v1' and snapshot['NoOverwrite'] is True,
        'Exact immutable own-six-asset failed-import recovery snapshot')
    failed_file = project_file(snapshot['FailedResult'])
    resume_file = project_file(snapshot['Resume'])
    req(sha(failed_file) == snapshot['FailedResultSHA256'] and sha(resume_file) == snapshot['ResumeSHA256'],
        'Actual failed Assets2 and original three-texture resume evidence unchanged')
    failed = read_json(failed_file)
    req(failed['success'] is False and failed['phase'] == 'assets'
        and set(failed['saved']) | set(failed['reused_assets']) == set(ASSETS)
        and len(failed['saved']) == len(failed['reused_assets']) == 3
        and 'get_simple_collision_count' in failed['error'],
        'Recover only own completed import whose commandlet mesh subsystem was absent')
    req(len(snapshot['Files']) == 6 and {row['Package'] for row in snapshot['Files']} == set(ASSETS),
        'Exact six actual owned files, no old product or guessed destination')
    for row in snapshot['Files']:
        relative = 'Content/'+row['Package'][6:]+'.uasset'
        req(os.path.normcase(os.path.normpath(row['Relative'])) == os.path.normcase(os.path.normpath(relative)),
            'Owned snapshot exact six package/file mapping')
        req(sha(project_file(row['Relative'])) == row['SHA256'], 'Owned new asset stays byte-for-byte unchanged '+row['Package'])
    R['owned_asset_snapshot'] = snapshot
    return snapshot


def inspect_assets(probe_data):
    baseline(probe_data,False)
    frozen = owned_assets()
    verify_assets()
    baseline(probe_data,False)
    owned_assets(frozen)
    req(not R['saved'],'Asset inspection never reimports, overwrites or resaves own six assets')
    R.update(map_saved=False,actor_count=32,asset_import_recovered_read_only=True)


def placement_data():
    filename = os.environ['DY_STAGEWINGS_PLACEMENT']
    data = read_json(filename)
    assets_filename = os.environ['DY_STAGEWINGS_ASSETS_RESULT']
    asset_data = read_json(assets_filename)
    req(data['schema'] == 'StageWingsPlacement.v1' and data['mesh_package'] == SM,'Exact frozen placement DTO')
    req(asset_data['success'] and asset_data['phase'] in ('assets','asset_inspect') and asset_data['map_saved'] is False
        and sha(assets_filename) == data['assets_result_sha256'],'Placement derives from successful actual asset import')
    if asset_data['phase'] == 'asset_inspect':
        req(not asset_data['saved'] and asset_data['asset_import_recovered_read_only'] is True,
            'Actual successful read-only asset recovery is not falsified assets-phase success')
        owned_assets(asset_data['owned_asset_snapshot'])
    req(data['xy'] == [400.,650.] and data['uniform_scale'] == 1. and data['align_bottom_z'] == 0.,'Only approved X400 Y650 unscaled ground-aligned candidate')
    req(math.isfinite(data['yaw_degrees']) and data['yaw_degrees'] in (-180.,-90.,0.,90.,180.)
        and data['selection_evidence'],'Yaw explicitly selected after real geometry inspection, never guessed')
    current = mesh_contract(req(unreal.load_asset(SM),'Exact placement mesh'))
    req(current == asset_data['mesh'],'Mesh geometry/slots unchanged since assets measurement')
    return data,asset_data


def bounds_row(actor):
    origin,extent = actor.get_actor_bounds(False)
    origin,extent = xyz(origin),xyz(extent)
    return dict(origin=origin,extent=extent,min=[a-b for a,b in zip(origin,extent)],max=[a+b for a,b in zip(origin,extent)])


def verify_wing(probe_data):
    world,actors,stage,contract,floor,component,floor_bounds = baseline(probe_data,True)
    actor = req(next(a for a in actors if a.get_actor_label() == LABEL),'Exact one wing actor')
    req(actor.get_class() == unreal.StaticMeshActor.static_class(),'Pure static mesh actor, no new gameplay class')
    meshes = actor.get_components_by_class(unreal.StaticMeshComponent)
    req(len(meshes) == 1,'Exactly one passive mesh component')
    mesh = meshes[0]
    req(path(mesh.get_editor_property('static_mesh')) == SM+'.'+SM.rsplit('/',1)[1],'Actual wing actor mesh')
    req(mesh.get_editor_property('mobility') == unreal.ComponentMobility.STATIC,'Static authored wing')
    R['wing_collision_observed']=dict(enabled=enum_name(mesh.get_collision_enabled()),profile=str(mesh.get_collision_profile_name()))
    req(mesh.get_collision_enabled() == unreal.CollisionEnabled.NO_COLLISION and str(mesh.get_collision_profile_name()) == 'Custom','Collision disabled and exact native all-ignore custom profile')
    responses = {}
    channels = [getattr(unreal.CollisionChannel,name) for name in dir(unreal.CollisionChannel)
                if name.isupper() and isinstance(getattr(unreal.CollisionChannel,name),unreal.CollisionChannel)
                and getattr(unreal.CollisionChannel,name).value < 32]
    req(len(channels) == 8,'Exact eight publicly reflected collision channel inventory')
    for channel in channels:
        response = enum_name(mesh.get_collision_response_to_channel(channel))
        responses[enum_name(channel)] = response
        req(response == enum_name(unreal.CollisionResponseType.ECR_IGNORE),'No new collision-channel blocker '+enum_name(channel))
    req(not mesh.get_editor_property('cast_shadow') and not mesh.get_editor_property('affect_dynamic_indirect_lighting')
        and not mesh.get_editor_property('affect_distance_field_lighting'),'No new shadow, dynamic indirect or distance field contribution')
    # bCanEverTick is protected to Python (actual Place7 diagnosis). Do not
    # bypass it or label it observed; public enabled-state plus exact native
    # StaticMeshActor class prove this passive actor has no active Tick.
    req(not actor.is_actor_tick_enabled() and not mesh.is_component_tick_enabled(),'Actual public actor/component Tick disabled')
    req(not list(actor.get_editor_property('tags')),'No gameplay or generated interaction tags')
    bounds = bounds_row(actor)
    req(any(bounds['max'][i] < CORE_MIN[i] or bounds['min'][i] > CORE_MAX[i] for i in range(3)), 'Actual wing bounds disjoint from protected core box')
    req(abs(bounds['min'][2]) < 1.e-5,'Real imported bottom aligned to floor Z0')
    location = xyz(actor.get_actor_location())
    R['wing_transform_observed']=transform(actor.get_actor_transform())
    req(location[:2] == [400.,650.] and xyz(actor.get_actor_scale3d()) == [1.,1.,1.],'Unchanged frozen placement XY and scale')
    dto,asset_data = placement_data()
    req(abs(actor.get_actor_rotation().yaw-dto['yaw_degrees']) < 1.e-5,'Actual saved selected yaw')
    req(all(path(mesh.get_material(i)) == MI+'.'+MI.rsplit('/',1)[1] for i in range(mesh.get_num_materials())),'Actual wing component materials')
    R.update(scene_contract=contract, actor_count=len(actors), original_actor_count=32, added_actor_labels=[LABEL],
        added_actor_count=1, core_scene_preserved=True, wing=dict(label=LABEL,object_path=path(actor),class_path=path(actor.get_class()),
            component_path=path(mesh),mesh=path(mesh.get_editor_property('static_mesh')),materials=[path(mesh.get_material(i)) for i in range(mesh.get_num_materials())],
            transform=transform(actor.get_actor_transform()),bounds=bounds,mobility='STATIC',collision_enabled='NO_COLLISION',collision_profile=str(mesh.get_collision_profile_name()),
            collision_responses=responses,collision_observation='Eight publicly reflected channels; hidden channels are not reported as observed',cast_shadow=False,affect_dynamic_indirect_lighting=False,affect_distance_field_lighting=False,
            actor_tick_enabled=actor.is_actor_tick_enabled(),actor_can_ever_tick=None,
            tick_capability_observed=False,tick_capability_note='Protected bCanEverTick not read; exact native class and public enabled-state verified',
            component_tick_enabled=mesh.is_component_tick_enabled(),tags=[],core_box_disjoint=True,ground_aligned=True),
        protected_core_box=dict(min=CORE_MIN,max=CORE_MAX),placement_contract=dto,
        visual_acceptance=False,physical_keys_verified=False,formal_art=False)


def place(probe_data):
    baseline(probe_data,False)
    dto,asset_data = placement_data()
    verify_assets()
    actor = req(unreal.get_editor_subsystem(unreal.EditorActorSubsystem).spawn_actor_from_class(
        unreal.StaticMeshActor,unreal.Vector(),unreal.Rotator(pitch=0.,yaw=dto['yaw_degrees'],roll=0.),False),'New one passive wing actor')
    actor.set_actor_label(LABEL)
    actor.set_editor_property('tags',[])
    mesh = req(actor.get_component_by_class(unreal.StaticMeshComponent),'Own new mesh component')
    req(mesh.set_static_mesh(unreal.load_asset(SM)),'Assign measured imported mesh')
    mesh.set_mobility(unreal.ComponentMobility.STATIC)
    mesh.set_collision_profile_name('NoCollision')
    mesh.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
    mesh.set_collision_response_to_all_channels(unreal.CollisionResponseType.ECR_IGNORE)
    mesh.set_editor_properties(dict(cast_shadow=False,affect_dynamic_indirect_lighting=False,affect_distance_field_lighting=False))
    actor.set_actor_tick_enabled(False)
    mesh.set_component_tick_enabled(False)
    # Native all-ignore changes the profile name to Custom. Do not reapply
    # NoCollision: that preset restores block responses on disabled channels.
    origin,extent = actor.get_actor_bounds(False)
    bottom = origin.z-extent.z
    actor.set_actor_location(unreal.Vector(dto['xy'][0],dto['xy'][1],-bottom),False,False)
    verify_wing(probe_data)
    req(unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level(),'Save only the existing explicitly approved Dev map')
    R['saved'].append(MAP)
    R['map_saved'] = True


try:
    req(PHASE in ('probe','assets','asset_inspect','place','verify'),'Exact bounded import/inspection/placement phases')
    req(os.path.commonpath([os.path.abspath(OUT),os.path.abspath(AUDIT)]) == os.path.abspath(AUDIT),'Exclusive result inside current audit')
    protect()
    req(unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).load_level(MAP),'Load only current existing Dev map')
    if PHASE == 'probe':
        probe()
    else:
        probe_data = read_json(os.environ['DY_READABILITY_PROBE'])
        if PHASE == 'assets':
            create_assets(probe_data)
        elif PHASE == 'asset_inspect':
            inspect_assets(probe_data)
        elif PHASE == 'place':
            place(probe_data)
        else:
            verify_wing(probe_data)
            verify_assets()
            req(not R['saved'],'Cold verifier never saves assets or map')
            R['map_saved'] = False
        R['wood_floor_contract'] = wood_floor_contract()
    protect()
    R['success'] = True
except Exception:
    R['error'] = traceback.format_exc()
    unreal.log_error(R['error'])
finally:
    with open(OUT,'x',encoding='utf-8') as stream:
        json.dump(R,stream,ensure_ascii=False,indent=2)
