"""Copy the frozen TopUV scene; only select a new GameMode and formal controller.

Probe/verify never save. Create saves only the two absent named destinations.
Use three fresh editor processes. This remains a technical entry, not final art.
"""
import copy
import hashlib
import json
import os
import traceback
import unreal

ROOT = os.path.realpath(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir()))
AUDIT = os.path.join(ROOT, 'Saved', 'Audit-2026-10-14-ReleaseEntry')
SOURCE = '/Game/DengYingShanHai/Dev/FrameBeamTopUV/Maps/LV_FrameBeamTopUVLab'
SOURCE_MODE = '/Game/DengYingShanHai/Dev/TheatreAudio/Core/BP_DYTheatreGameMode'
MAP = '/Game/DengYingShanHai/Maps/L_DY_Main'
MODE = '/Game/DengYingShanHai/Core/BP_DYReleaseGameMode'
OLD_CONTROLLER = '/Script/DengYingShanHai.DYDevEntryPlayerController'
CONTROLLER = '/Script/DengYingShanHai.DYReleaseEntryPlayerController'
OUT = os.environ.get('DY_RELEASE_ENTRY_OUT')
PHASE = os.environ.get('DY_RELEASE_ENTRY_PHASE')
PROBE = os.environ.get('DY_RELEASE_ENTRY_PROBE', os.path.join(AUDIT, 'probe-Run1', 'Result.json'))
COLD_FILE = os.path.join(ROOT, 'Saved', 'Audit-2026-10-13-FrameBeamTopUVDev', 'verify-Run1', 'Result.json')
ALLOWED = frozenset(('/scene_contract/_flow/gm', '/scene_contract/_flow/controller'))
FROZEN = {
    'Content/DengYingShanHai/Dev/FrameBeamTopUV/Maps/LV_FrameBeamTopUVLab.umap':
        '932D961A623DF9674D08D9F960A7632B4F73F72C59BF3BE27244E53D4C9F74DA',
    'Content/DengYingShanHai/Dev/TheatreAudio/Core/BP_DYTheatreGameMode.uasset':
        '08CEE30440BBCF060072F99FA698A2759947F70C345A0B98AA073653E1D20045',
    'Scripts/Create-FrameBeamTopUVDev.py':
        '6CE596AAF8931881B0EDB1B2824B351F46B4C5AD1444914CC7FD6E468D822F25',
    'Scripts/Create-FrameBeamCandidateDev.py':
        'C8ECCA70C228A9D8A2AD92C4C5A4438831F0059147D96DE9B93E450F22E77594',
    'Scripts/Create-FrameBeamPlacementDev.py':
        '18E96E5E3890A46584E49B85DC218986F044EC01758191AA363E0AB379E9E823',
    'Scripts/Create-FramePostPlacementDev.py':
        'ED0E257314B0F33C8F6EFFA14A94D19D59AE91AFD82B0BC0519AB017BE2C8A84',
    'Scripts/Create-StageWingsDev.py':
        '8539C32CDBEF250863791A221167C075989E3476D53F804B2CE07DDD0A00AFDD',
    'Scripts/Create-EnvironmentStates.py':
        'EC8938347506B9807F910742E64D4159959B9A74B6A70CDB37E4F798C06BF9A0',
    'Saved/Audit-2026-10-13-FrameBeamTopUVDev/verify-Run1/Result.json':
        'FD3F4E76F1C608090E66CA782B7E92C1F98E2D6E2500A3D7522A074DCD53033C',
}
MODE_DEFAULTS = ('default_pawn_class', 'hud_class', 'game_state_class', 'player_state_class',
                 'spectator_class', 'game_session_class', 'replay_spectator_player_controller_class')
R = dict(success=False, phase=PHASE, source=SOURCE, source_mode=SOURCE_MODE, map=MAP, mode=MODE,
         saved=[], assets_saved=[], map_saved=False, checks=[], actor_count=35, scene_keys=37,
         gameplay_changed=False, material_changed=False, input_changed=False, camera_changed=False,
         audio_changed=False, formal_art=False, runtime_python=False, mode_property_writes=0,
         world_settings_writes=0, allowed_scalar_difference_paths=sorted(ALLOWED))
OUTPUT_VALID = False


def req(value, message):
    if not value:
        raise RuntimeError(message)
    R['checks'].append(message)
    return value


def bounded(filename):
    result = os.path.realpath(os.path.abspath(filename))
    req(os.path.normcase(result) != os.path.normcase(os.path.join(ROOT, 'Docs', 'LICENSES.md')),
        'Restricted register excluded before any content access')
    return result


def sha(filename):
    filename = bounded(filename)
    digest = hashlib.sha256()
    with open(filename, 'rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest().upper()


def read(filename):
    with open(bounded(filename), encoding='utf-8-sig') as stream:
        return json.load(stream)


def protect_sources():
    observed = {}
    for relative, expected in FROZEN.items():
        observed[relative] = sha(os.path.join(ROOT, relative))
        req(observed[relative] == expected, 'Frozen original source/reader bytes ' + relative)
    return observed


def object_path(package):
    return package + '.' + package.rsplit('/', 1)[1]


def class_path(package):
    return object_path(package) + '_C'


def load_native_reader():
    # Execute only the reviewed function/import prefix, never old protected authors or mains.
    filename = os.path.join(ROOT, 'Scripts', 'Create-FrameBeamTopUVDev.py')
    with open(bounded(filename), encoding='utf-8-sig') as stream:
        code = stream.read()
    req(code.count('\ntry:\n') == 1, 'Exact frozen TopUV definitions-only main boundary')
    for prefix in ('DY_TOPUV_DEV', 'DY_BEAM_DEV', 'DY_FRAMEPOST', 'DY_READABILITY'):
        os.environ[prefix + '_OUT'] = OUT
        os.environ[prefix + '_PHASE'] = PHASE
    namespace = {'__name__': 'release_entry_frozen_reader_definitions_only'}
    exec(code.split('\ntry:\n')[0], namespace)
    return namespace['load_native_reader']()


def exact_only_flow(actual, baseline, release=False, prefix='', found=None):
    if found is None:
        found = set()
    req(type(actual) is type(baseline), 'Exact recursive field type ' + prefix)
    if isinstance(baseline, dict):
        req(set(actual) == set(baseline), 'Exact recursive keys ' + prefix)
        for key, expected in baseline.items():
            exact_only_flow(actual[key], expected, release, prefix + '/' + key, found)
    elif isinstance(baseline, list):
        req(len(actual) == len(baseline), 'Exact recursive array count ' + prefix)
        for index, expected in enumerate(baseline):
            exact_only_flow(actual[index], expected, release, prefix + '/' + str(index), found)
    elif release and prefix in ALLOWED:
        expected_pair = ((class_path(SOURCE_MODE), class_path(MODE)) if prefix.endswith('/gm')
                         else (OLD_CONTROLLER, CONTROLLER))
        req(baseline == expected_pair[0] and actual == expected_pair[1],
            'Only exact formal GameMode/controller scalar ' + prefix)
        req(prefix not in found, 'Allowed scalar observed only once ' + prefix)
        found.add(prefix)
    else:
        req(actual == baseline, 'Unchanged exact scalar ' + prefix)
    if prefix == '':
        req(found == (set(ALLOWED) if release else set()), 'Exactly two identity differences or zero source differences')
    return found


def observe(package, release=False):
    current = P['scene']()
    req(P['path'](current[0]) == object_path(package), 'Exact loaded current-world identity')
    req(len(current[1]) == 35 and len(current[3]) == 37 and set(current[3]) == set(COLD['scene_contract']),
        'Exactly 35 original Actors and 37 full scene/pawn/flow keys')
    beams = [actor for actor in current[1] if actor.get_actor_label() == 'DEV_FrameBeam_RightJoint']
    req(len(beams) == 1, 'One unchanged actual TopUV passive beam')
    combined = dict(scene_contract=current[3], beam=P['beam_native_fields'](beams[0]), post=P['oldpost'](current))
    normalized = P['normalize'](combined, package)
    baseline = P['normalize']({name: COLD[name] for name in combined}, SOURCE)
    exact_only_flow(normalized, baseline, release)
    storage = P['P']['storage'](current[0])
    req(storage['use_external_actors'] is False and storage['live_registry_inventory'] == [],
        'No external Actors or live map-build registry in this fresh process')
    return current, dict(combined, normalized_contract=normalized['scene_contract'], storage_probe=storage,
                         inherited_contract_checks=len(P['R']['checks']))


def dirty_guard(allowed_maps=(), allowed_content=()):
    maps = [str(value.get_path_name()) for value in unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()]
    content = [str(value.get_path_name()) for value in unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages()]
    req(set(maps).issubset(set(allowed_maps)) and set(content).issubset(set(allowed_content)),
        'Dirty packages bounded to own explicitly named new destinations')
    R.setdefault('dirty_observations', []).append(dict(maps=maps, content=content))


def destination_absent():
    for package, extension in ((MAP, '.umap'), (MODE, '.uasset')):
        req(not unreal.EditorAssetLibrary.does_asset_exist(package)
            and not os.path.exists(os.path.join(ROOT, 'Content', package[6:] + extension)),
            'Absent exact new destination; never overwrite ' + package)


def mode_defaults(mode):
    defaults = unreal.get_default_object(req(mode.generated_class(), 'Actual compiled GameMode class'))
    result = {name: P['path'](defaults.get_editor_property(name)) for name in MODE_DEFAULTS}
    result['player_controller_class'] = P['path'](defaults.get_editor_property('player_controller_class'))
    hud = defaults.get_editor_property('hud_class')
    req(hud and result['hud_class'] != '/Script/DengYingShanHai.DYDevInteractionHUD',
        'Existing explicit Chinese player HUD retained, never native debug HUD fallback')
    hud_defaults = unreal.get_default_object(hud)
    widget = req(hud_defaults.get_editor_property('widget_class'), 'Existing explicit Chinese HUD widget')
    result['hud_widget_class'] = P['path'](widget)
    result['hud_widget_font'] = P['path'](unreal.get_default_object(widget).get_editor_property('chinese_font'))
    req(result['hud_widget_font'], 'Actual bundled Chinese HUD font')
    return result


def check_mode_graphs(mode):
    errors = []
    for graph in unreal.BlueprintEditorLibrary.list_graphs(mode):
        errors.extend(unreal.BlueprintGraphEditor.get_graph_editor(graph).list_nodes_with_errors())
    req(errors == [], 'Own new GameMode has no compiled graph node errors')
    req(P['path'](mode.generated_class()) == class_path(MODE), 'Exact actual new generated GameMode class')


def compile_mode(mode):
    req(unreal.BlueprintEditorLibrary.compile_blueprint(mode), 'Compile only own new GameMode')
    check_mode_graphs(mode)


def assert_mode_contract(mode, source_defaults):
    expected = dict(source_defaults, player_controller_class=CONTROLLER)
    actual = mode_defaults(mode)
    req(actual == expected, 'All observed Pawn/HUD/font/state/session GameMode defaults unchanged except formal controller')
    req(P['path'](mode) == object_path(MODE), 'Only exact new GameMode asset identity')
    R['mode_defaults'] = actual


def approved_probe():
    req(os.path.commonpath((bounded(PROBE), bounded(AUDIT))) == bounded(AUDIT), 'Probe evidence remains inside own audit')
    data = read(PROBE)
    req(data['success'] is True and data['phase'] == 'probe' and data['map'] == MAP
        and data['source'] == SOURCE and data['saved'] == [] and data['assets_saved'] == []
        and data['map_saved'] is False and data['original_hashes_after'] == FROZEN,
        'Actual successful independent read-only probe, no guessed setup')
    req(data['source_observation']['normalized_contract'] == R['source_observation']['normalized_contract']
        and data['source_mode_defaults'] == R['source_mode_defaults'], 'Source contract and defaults still match actual probe')
    R['probe_evidence_sha256'] = sha(PROBE)
    return data


try:
    req(isinstance(OUT, str) and os.path.commonpath((bounded(OUT), bounded(AUDIT))) == bounded(AUDIT)
        and not os.path.exists(OUT), 'Write a fresh result only inside own task audit')
    OUTPUT_VALID = True
    req(PHASE in ('probe', 'create', 'verify'), 'Only three explicitly bounded phases')
    R['original_hashes_before'] = protect_sources()
    COLD = read(COLD_FILE)
    req(COLD['success'] is True and COLD['phase'] == 'verify' and COLD['map'] == SOURCE
        and COLD['actor_count'] == 35 and len(COLD['scene_contract']) == 37 and COLD['saved'] == []
        and COLD['assets_saved'] == [] and COLD['map_saved'] is False,
        'Actual immutable TopUV cold baseline, not an inferred Blueprint scene')
    P = load_native_reader()
    LEVELS = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    req(LEVELS.load_level(SOURCE), 'Load frozen original TopUV source read-only')
    current, source_observation = observe(SOURCE)
    R['source_observation'] = copy.deepcopy(source_observation)
    source_mode = req(unreal.load_asset(SOURCE_MODE), 'Actual existing Theatre GameMode Blueprint')
    req(P['path'](source_mode.generated_class()) == class_path(SOURCE_MODE), 'Exact actual source GameMode class')
    source_defaults = mode_defaults(source_mode)
    req(source_defaults['player_controller_class'] == OLD_CONTROLLER, 'Source GameMode retains old Dev controller')
    R['source_mode_defaults'] = copy.deepcopy(source_defaults)
    controller = req(unreal.load_class(None, CONTROLLER), 'New compiled native formal entry controller')
    req(P['path'](controller) == CONTROLLER, 'Exact actual native formal controller class')
    dirty_guard()
    current = None
    if PHASE == 'probe':
        destination_absent()
    elif PHASE == 'create':
        approved_probe()
        destination_absent()
        mode = req(unreal.EditorAssetLibrary.duplicate_asset(SOURCE_MODE, MODE), 'Copy only absent own GameMode')
        compile_mode(mode)
        req(mode_defaults(mode) == source_defaults, 'Copied GameMode defaults exactly match actual source before mutation')
        unreal.get_default_object(mode.generated_class()).set_editor_property('player_controller_class', controller)
        R['mode_property_writes'] = 1
        compile_mode(mode)
        assert_mode_contract(mode, source_defaults)
        dirty_guard((), (MODE,))
        req(unreal.EditorAssetLibrary.save_loaded_asset(mode, only_if_is_dirty=False), 'Save only exact new GameMode')
        R['saved'].append(MODE)
        R['assets_saved'].append(MODE)
        dirty_guard()
        req(LEVELS.new_level_from_template(MAP, SOURCE), 'Native template copy saves only absent new main map')
        R['saved'].append(MAP)
        R['map_creation_api'] = 'LevelEditorSubsystem.new_level_from_template'
        current, before_selection = observe(MAP)
        settings = current[0].get_world_settings()
        settings.modify()
        settings.set_editor_property('default_game_mode', mode.generated_class())
        R['world_settings_writes'] = 1
        req(settings.get_editor_property('default_game_mode') == mode.generated_class(), 'Copied world selects only explicit formal GameMode')
        current, observation = observe(MAP, True)
        R.update(observation)
        current = None
        settings = None
        dirty_guard((MAP,), ())
        protect_sources()
        req(LEVELS.save_current_level(), 'Save only new main map after exact two-scalar contract checks')
        R.update(map_saved=True, save_operations=3, requires_cold_verify=True)
        dirty_guard()
    else:
        approved_probe()
        mode = req(unreal.load_asset(MODE), 'Independent cold load of saved new GameMode')
        check_mode_graphs(mode)
        assert_mode_contract(mode, source_defaults)
        req(LEVELS.load_level(MAP), 'Independent cold load of saved formal main map')
        current, observation = observe(MAP, True)
        req(current[0].get_world_settings().get_editor_property('default_game_mode') == mode.generated_class(),
            'Cold world references exact saved formal GameMode')
        R.update(observation)
        current = None
        dirty_guard()
        req(R['saved'] == [] and R['assets_saved'] == [] and R['map_saved'] is False
            and R['mode_property_writes'] == R['world_settings_writes'] == 0, 'Cold verifier has zero writes or saves')
    R['original_hashes_after'] = protect_sources()
    req(R['original_hashes_before'] == R['original_hashes_after'], 'All original source maps/GM/reader/cold bytes preserved')
    R['success'] = True
except Exception:
    R['error'] = traceback.format_exc()
    unreal.log_error(R['error'])
finally:
    if OUTPUT_VALID:
        with open(OUT, 'x', encoding='utf-8') as stream:
            json.dump(R, stream, ensure_ascii=False, indent=2)
    else:
        unreal.log_error('Release entry result destination was rejected; no file written.')
