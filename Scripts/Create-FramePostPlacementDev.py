"""One isolated Dev map, one passive post; original 33 actors and seven assets frozen."""
import hashlib
import json
import math
import os
import traceback
import unreal

ROOT = os.path.realpath(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir()))
AUDIT = os.path.join(ROOT, 'Saved', 'Audit-2026-10-12-FramePostPlacementDev')
SOURCE = '/Game/DengYingShanHai/Dev/EnvironmentStates/Maps/LV_EnvironmentStatesLab'
MAP = '/Game/DengYingShanHai/Dev/FramePostPlacement/Maps/LV_FramePostPlacementLab'
SM = '/Game/DengYingShanHai/Dev/FramePostAsset/Meshes/SM_DY_FramePost_Source'
WOOD = '/Game/DengYingShanHai/Dev/FramePostAsset/Materials/MI_DY_FramePost_Wood'
BASE_MI = '/Game/DengYingShanHai/Dev/FramePostAsset/Materials/MI_DY_FramePost_Base'
LABEL = 'DEV_FramePost_Right'
OUT = os.environ['DY_FRAMEPOST_OUT']
PHASE = os.environ['DY_FRAMEPOST_PHASE']
R = dict(success=False, phase=PHASE, saved=[], checks=[], map=MAP, source=SOURCE,
         visual_acceptance=False, physical_blocking=False, formal_scale=False)

def req(value, message):
    if not value:
        raise RuntimeError(message)
    R['checks'].append(message)
    return value

def path(value):
    return value.get_path_name() if value else None

def xyz(value):
    return [value.x, value.y, value.z]

def enum(value):
    return value.name if hasattr(value, 'name') else str(value).split('.')[-1]

def read(filename):
    with open(filename, encoding='utf-8-sig') as stream:
        return json.load(stream)

def sha(filename):
    filename = os.path.abspath(filename)
    req(os.path.normcase(filename) != os.path.normcase(os.path.join(ROOT, 'Docs', 'LICENSES.md')),
        'Never access restricted register')
    digest = hashlib.sha256()
    with open(filename, 'rb') as stream:
        for chunk in iter(lambda: stream.read(1024*1024), b''):
            digest.update(chunk)
    return digest.hexdigest().upper()

def protect():
    before = read(os.path.join(AUDIT, 'BEFORE.json'))
    current_file = os.path.join(AUDIT, 'CPP-PUBLISHED.json')
    publication = read(current_file) if os.path.isfile(current_file) else None
    current = {row['Relative']: row['PublishedSHA256'] for row in publication['Files']} if publication else {}
    for row in before['Files']:
        expected = current.get(row['Relative'], row['SHA256'])
        req(sha(os.path.join(ROOT, row['Relative'])) == expected, 'Protected ' + row['Relative'])
    for row in before['OldRaw'] + before['IsolatedSources']:
        req(sha(os.path.join(ROOT, row['Relative'])) == row['SHA256'], 'Frozen source ' + row['Relative'])
    req(not os.path.isfile(os.path.join(ROOT, 'Config', 'DefaultEditor.ini')), 'No unsolicited editor Config')

def load_reader():
    filename = os.path.join(ROOT, 'Scripts', 'Create-StageWingsDev.py')
    with open(filename, encoding='utf-8-sig') as stream:
        code = stream.read()
    req(code.count('\ntry:\n') == 1, 'Exact reviewed StageWings main boundary')
    namespace = {'__name__': 'framepost_contract_readonly'}
    exec(code.split('\ntry:\n')[0], namespace)
    return namespace

def scene():
    world, actors, stage, contract, floor, floor_mesh, floor_bounds = READER['scene']()
    req(len(actors) == len({a.get_actor_label() for a in actors}), 'No duplicate actor labels')
    R['inherited_reader_checks'] = len(READER['R']['checks'])
    return world, actors, stage, contract, floor, floor_mesh, floor_bounds

def normalize(value, package):
    prefix = package + '.' + package.rsplit('/', 1)[1] + ':'
    if isinstance(value, str):
        return '<CURRENT_LEVEL>:' + value[len(prefix):] if value.startswith(prefix) else value
    if isinstance(value, list):
        return [normalize(item, package) for item in value]
    if isinstance(value, dict):
        return {key: normalize(item, package) for key, item in value.items()}
    return value

def dependencies(world, actors, stage):
    director = stage.get_puzzle_director()
    forest = stage.get_forest_presentation_actor()
    environment = stage.get_stage_environment()
    refs = [stage, director, forest, environment, director.get_light_rig_actor(), director.get_puppet_actor()]
    for name in ('StaffProjectionScreen', 'NarrativeGroundLine', 'DevReceiver', 'DevGround'):
        refs.append(stage.get_editor_property(name))
    for value in refs:
        req(value and value.get_world() == world, 'Real scene dependency belongs to current world: ' + str(path(value)))
        if isinstance(value, unreal.Actor):
            req(value in actors, 'Real actor dependency is in current level inventory')
        elif isinstance(value, unreal.ActorComponent):
            req(value.get_owner() in actors, 'Real component dependency owner is in current level inventory')
    audio = req(next((a for a in actors if a.get_actor_label() == 'AudioDev_Presentation'), None), 'Existing Audio Actor')
    req(audio.get_editor_property('StagePresentation') == stage, 'Audio references real copied Stage')
    req(director.get_evaluation_frequency_hz() == 15 and not director.is_auto_start_on_begin_play()
        and director.is_act_sequence_enabled(), '15Hz/manual three-act flow unchanged')
    req(stage.is_five_state_environment_enabled(), 'Existing five-state opt-in retained')

def bounds(mesh):
    value = mesh.get_bounds()
    origin, extent = xyz(value.origin), xyz(value.box_extent)
    return dict(origin=origin, extent=extent, min=[a-b for a,b in zip(origin,extent)],
                max=[a+b for a,b in zip(origin,extent)], size=[2*v for v in extent])

def storage(world):
    level = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).get_current_level()
    req(level and level.get_outer() == world, 'Reflected current level belongs to exact current world')
    # MapBuildData has no Edit/Blueprint flag. Never bypass its rejected getter.
    # Supported one-shot live UObject inventory is independent evidence, not a
    # fabricated read of that protected field. Neither duplication flags nor a
    # save API name alone prove isolation; exact disk outputs are checked too.
    registry_class = req(unreal.load_class(None, '/Script/Engine.MapBuildDataRegistry'),
                         'Exact native map registry class for supported filtered inventory')
    default_registry = unreal.get_default_object(registry_class)
    registries = list(unreal.ObjectIterator(registry_class))
    live = [path(value) for value in registries if value != default_registry]
    result = dict(level=path(level), map_build_data_directly_observed=False,
                  registry_inventory=[path(value) for value in registries], live_registry_inventory=live,
                  use_external_actors=level.get_editor_property('use_external_actors'),
                  evidence_limit='Supported UObject inventory; not a protected MapBuildData field read')
    req(not live and result['use_external_actors'] is False,
        'No live map build registries or external-actor packaging in this isolated editor session')
    return result

def probe():
    world, actors, stage, contract, floor, floor_mesh, floor_bounds = scene()
    req(path(world) == SOURCE + '.' + SOURCE.rsplit('/',1)[1], 'Exact source world identity')
    req(len(actors) == 33 and LABEL not in contract, 'Exact 33-actor source')
    dependencies(world, actors, stage)
    req(not unreal.EditorAssetLibrary.does_asset_exist(MAP) and not os.path.exists(
        os.path.join(ROOT, 'Content', MAP[6:] + '.umap')), 'New isolated map absent; never overwrite')
    mesh = req(unreal.load_asset(SM), 'Existing accepted post mesh')
    mesh_info = bounds(mesh)
    req(abs(mesh_info['size'][2] - 2036.121966123581) < .001, 'Actual source height remains 20.36m')
    cdo = unreal.get_default_object(unreal.StaticMeshActor)
    component = req(cdo.get_component_by_class(unreal.StaticMeshComponent), 'Native default component for readonly API probe')
    properties = ['cast_hidden_shadow', 'cast_shadow', 'affect_dynamic_indirect_lighting',
                  'affect_distance_field_lighting', 'use_default_collision', 'body_instance']
    observations = {name: str(component.get_editor_property(name)) for name in properties}
    observations['stored_collision'] = enum(component.get_editor_property('body_instance').get_editor_property('collision_enabled'))
    api = {name: hasattr(component, name) for name in ('set_generate_overlap_events','get_generate_overlap_events','set_material','set_collision_response_to_all_channels')}
    api.update(actor_get_collision=hasattr(cdo, 'get_actor_enable_collision'), actor_set_collision=hasattr(cdo, 'set_actor_enable_collision'),
               interface_check=hasattr(unreal.SystemLibrary, 'does_implement_interface'))
    R['api_probe'] = api
    R['native_default_observations'] = observations
    R['overlap_property'] = component.get_editor_property('generate_overlap_events')
    R['storage_probe'] = storage(world)
    required = ['set_material','set_collision_response_to_all_channels','actor_get_collision',
                'actor_set_collision','interface_check']
    req(all(api[name] for name in required), 'Actual reflected collision/material/interface APIs exist')
    R['native_default_observations']['actor_collision_enabled'] = cdo.get_actor_enable_collision()
    req(unreal.load_asset(WOOD) and unreal.load_asset(BASE_MI), 'Both accepted existing constant instances')
    R.update(actor_count=33, scene_contract=contract, normalized_contract=normalize(contract,SOURCE),
             mesh_bounds=mesh_info, floor_bounds=floor_bounds, storage_probe=storage(world), api_probe=api,
             native_default_observations=observations, assets_saved=[])

def baseline(probe_data, extra):
    req(probe_data['success'] and probe_data['phase'] == 'probe' and probe_data['saved'] == []
        and probe_data['actor_count'] == 33, 'Actual successful immutable native source probe')
    current = scene()
    package = MAP if extra is not None else SOURCE
    req(path(current[0]) == package + '.' + package.rsplit('/',1)[1], 'Exact current source/destination world')
    expected = set(probe_data['scene_contract']) | ({LABEL} if extra else set())
    req(set(current[3]) == expected, 'Exact original 33 Actor and optional unique post inventory')
    original = {key:value for key,value in current[3].items() if key != LABEL}
    req(normalize(original,package) == probe_data['normalized_contract'],
        'Listed original transform/component/light/rail/flow/audio/forest contract unchanged after exact world-prefix normalization')
    dependencies(current[0], current[1], current[2])
    R['source_contract_preserved'] = True
    return current

def post_observation(actor):
    component = req(actor.get_component_by_class(unreal.StaticMeshComponent), 'One real post component')
    origin, extent = actor.get_actor_bounds(False)
    observed = dict(label=actor.get_actor_label(), object_path=path(actor), class_path=path(actor.get_class()),
                    component_path=path(component), actor_collision_enabled=actor.get_actor_enable_collision(),
                    location=xyz(actor.get_actor_location()), scale=xyz(actor.get_actor_scale3d()),
                    rotation=[actor.get_actor_rotation().pitch,actor.get_actor_rotation().yaw,actor.get_actor_rotation().roll],
                    bounds=dict(origin=xyz(origin),extent=xyz(extent),min=xyz(origin-extent),max=xyz(origin+extent)),
                    mesh=path(component.get_editor_property('static_mesh')),
                    materials=[path(component.get_material(i)) for i in range(component.get_num_materials())],
                    mobility=enum(component.get_editor_property('mobility')),
                    collision_enabled=enum(component.get_collision_enabled()),
                    stored_collision_enabled=enum(component.get_editor_property('body_instance').get_editor_property('collision_enabled')),
                    object_type=enum(component.get_collision_object_type()), collision_profile=str(component.get_collision_profile_name()),
                    use_default_collision=component.get_editor_property('use_default_collision'),
                    overlap=component.get_editor_property('generate_overlap_events'),
                    actor_tick_enabled=actor.is_actor_tick_enabled(),component_tick_enabled=component.is_component_tick_enabled(),
                    tags=[str(value) for value in actor.get_editor_property('tags')],
                    controllable=unreal.SystemLibrary.does_implement_interface(actor,unreal.DYControllable))
    observed.update({name:component.get_editor_property(name) for name in
                    ('cast_shadow','cast_hidden_shadow','affect_dynamic_indirect_lighting','affect_distance_field_lighting')})
    channels={value.value:value for name in dir(unreal.CollisionChannel)
              for value in [getattr(unreal.CollisionChannel,name)]
              if isinstance(value,unreal.CollisionChannel) and 0 <= value.value < 8}
    req(set(channels) == set(range(8)), 'Actual eight public collision channels')
    observed['public_collision_responses']={value.name:enum(component.get_collision_response_to_channel(value))
                                            for index,value in sorted(channels.items())}
    req(actor.get_class() == unreal.StaticMeshActor.static_class() and component.get_owner() == actor
        and len(actor.get_components_by_class(unreal.StaticMeshComponent)) == 1, 'Exact native passive Actor and component ownership')
    dto = read(os.path.join(AUDIT,'PLACEMENT.json'))
    req(all(abs(a-b) < 1.e-6 for a,b in zip(observed['location'],dto['LocationCm']))
        and all(abs(value-dto['UniformScale']) < 1.e-7 for value in observed['scale'])
        and all(abs(value)<1.e-6 for value in observed['rotation']), 'Exact frozen Dev placement and equal XYZ scale')
    req(observed['mesh'] == SM+'.'+SM.rsplit('/',1)[1] and observed['materials'] ==
        [WOOD+'.'+WOOD.rsplit('/',1)[1],BASE_MI+'.'+BASE_MI.rsplit('/',1)[1]], 'Existing accepted mesh/two MI references only')
    req(observed['mobility']=='STATIC' and observed['actor_collision_enabled']
        and observed['collision_enabled']==observed['stored_collision_enabled']=='NO_COLLISION'
        and observed['object_type']=='ECC_WORLD_STATIC' and observed['collision_profile']=='Custom'
        and observed['use_default_collision'] is False and observed['overlap'] is False,
        'Actual actor/component/stored-body/profile/ObjectType/overlap contract')
    req(all(value=='ECR_IGNORE' for value in observed['public_collision_responses'].values()), 'Eight actual public responses Ignore')
    req(all(observed[name] is False for name in ('cast_shadow','cast_hidden_shadow','affect_dynamic_indirect_lighting',
        'affect_distance_field_lighting','actor_tick_enabled','component_tick_enabled','controllable'))
        and not observed['tags'], 'No post gameplay/Tick/shadow contribution flags, without inferring screen-space isolation')
    req(abs(observed['bounds']['min'][2])<.001 and abs(observed['bounds']['max'][2]-800)<.001,
        'Actual world bounds bottom0/top800 within native float precision')
    req(observed['bounds']['min'][1]>470, 'Actual whole base remains outside protected core Y edge')
    observed.update(tick_capability_observed=False, physical_blocking_accepted=False, final_shadow_strategy=False)
    return observed

def author(probe_data):
    source=baseline(probe_data,None)
    dto=read(os.path.join(AUDIT,'PLACEMENT.json'))
    req(dto['Schema']=='FramePostPlacementDev.v1' and dto['Map']==MAP and dto['SourceMap']==SOURCE,
        'Frozen source/destination placement DTO')
    req(not unreal.EditorAssetLibrary.does_asset_exist(MAP) and not os.path.exists(os.path.join(ROOT,'Content',MAP[6:]+'.umap')),
        'Destination absent immediately before actual duplicate')
    storage(source[0])
    # Do not retain a live source or duplicate World across LoadMap/GC. The
    # native template API loads an untitled package and SaveMap names only the
    # absent destination. Its reviewed native code refuses an existing path.
    source=None
    req(hasattr(LEVELS,'new_level_from_template'), 'Supported reflected native template creation API')
    req(LEVELS.new_level_from_template(MAP,SOURCE), 'Native template copy saved only to own absent Dev map')
    R['map_creation_api']='LevelEditorSubsystem.new_level_from_template'
    R['saved'].append(MAP)
    current=baseline(probe_data,False)
    R['destination_storage_before_save']=storage(current[0])
    actor=req(unreal.get_editor_subsystem(unreal.EditorActorSubsystem).spawn_actor_from_class(
        unreal.StaticMeshActor,unreal.Vector(*dto['LocationCm']),unreal.Rotator(),False), 'Spawn one nontransient native post')
    actor.set_actor_label(LABEL)
    actor.set_editor_property('tags',[])
    actor.set_actor_enable_collision(True)
    actor.set_actor_tick_enabled(False)
    component=req(actor.get_component_by_class(unreal.StaticMeshComponent), 'Own new passive component')
    req(component.set_static_mesh(unreal.load_asset(SM)), 'Reference existing mesh without changing asset')
    component.set_material(0,unreal.load_asset(WOOD))
    component.set_material(1,unreal.load_asset(BASE_MI))
    actor.set_actor_scale3d(unreal.Vector(dto['UniformScale'],dto['UniformScale'],dto['UniformScale']))
    component.set_mobility(unreal.ComponentMobility.STATIC)
    component.set_collision_profile_name('NoCollision')
    component.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
    component.set_collision_response_to_all_channels(unreal.CollisionResponseType.ECR_IGNORE)
    component.set_editor_property('generate_overlap_events',False)
    component.set_editor_properties(dict(cast_shadow=False,cast_hidden_shadow=False,
        affect_dynamic_indirect_lighting=False,affect_distance_field_lighting=False))
    component.set_component_tick_enabled(False)
    current=baseline(probe_data,True)
    R['post']=post_observation(actor)
    R['destination_storage_before_save']=storage(current[0])
    protect()
    req(LEVELS.save_current_level(), 'Save only the own new Dev level after native storage and manifest gates')
    R['save_operations']=2
    R.update(actor_count=34,scene_contract=current[3],assets_saved=[],map_saved=True)

def verify(probe_data):
    baseline(probe_data,None)
    req(LEVELS.load_level(MAP), 'Cold load exact own new map')
    current=baseline(probe_data,True)
    actor=req(next((value for value in current[1] if value.get_actor_label()==LABEL),None), 'Exactly one saved new post')
    R.update(post=post_observation(actor),actor_count=34,scene_contract=current[3],assets_saved=[],map_saved=False,
             destination_storage_before_save=storage(current[0]))
    req(not R['saved'], 'Cold verifier never saves anything')

try:
    req(PHASE in ('probe','create','verify'), 'Exact bounded authoring/read-only phases')
    req(os.path.commonpath([os.path.abspath(OUT),os.path.abspath(AUDIT)]) == os.path.abspath(AUDIT), 'Own result directory only')
    protect()
    READER = load_reader()
    LEVELS = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    req(LEVELS.load_level(SOURCE), 'Load original map readonly')
    if PHASE == 'probe':
        probe()
    else:
        data=read(os.path.join(AUDIT,'probe-Run6','Result.json'))
        if PHASE=='create':
            author(data)
        else:
            verify(data)
    protect()
    R['success'] = True
except Exception:
    R['error'] = traceback.format_exc()
    unreal.log_error(R['error'])
finally:
    with open(OUT, 'x', encoding='utf-8') as stream:
        json.dump(R,stream,ensure_ascii=False,indent=2)
