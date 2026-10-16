"""Clone the frozen playable A world; change exactly seven observed Y scalars on its one passive beam."""
import ast
import copy
import hashlib
import json
import os
import traceback
import unreal

ROOT = os.path.realpath(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir()))
AUDIT = os.path.join(ROOT, 'Saved', 'Audit-2026-10-13-FrameBeamCandidateDev')
SOURCE = '/Game/DengYingShanHai/Dev/FrameBeamPlacement/Maps/LV_FrameBeamPlacementLab'
MAP = '/Game/DengYingShanHai/Dev/FrameBeamCandidate/Maps/LV_FrameBeamCandidateLab'
OUT = os.environ['DY_BEAM_DEV_OUT']
PHASE = os.environ['DY_BEAM_DEV_PHASE']
DELTA = 43.55169272790636
LABEL = 'DEV_FrameBeam_RightJoint'
R = dict(success=False, phase=PHASE, map=MAP, source=SOURCE, saved=[], assets_saved=[],
         map_saved=False, checks=[], actor_count=35, visual_acceptance=False, formal_scale=False,
         physical_blocking=False, joinery_or_load_accepted=False, candidate_adopted=False)
SCENE_Y = {'/DEV_FrameBeam_RightJoint/location/1',
           '/DEV_FrameBeam_RightJoint/static_meshes/0/relative_transform/location/1',
           '/DEV_FrameBeam_RightJoint/static_meshes/0/world_transform/location/1'}
BEAM_Y = {'/location/1', '/bounds/origin/1', '/bounds/min/1', '/bounds/max/1'}

def req(value, message):
    if not value:
        raise RuntimeError(message)
    R['checks'].append(message)
    return value

def read(path):
    req(os.path.normcase(os.path.abspath(path)) != os.path.normcase(os.path.join(ROOT, 'Docs', 'LICENSES.md')), 'Restricted register excluded before access')
    with open(path, encoding='utf-8-sig') as stream:
        return json.load(stream)

def sha(path):
    req(os.path.normcase(os.path.abspath(path)) != os.path.normcase(os.path.join(ROOT, 'Docs', 'LICENSES.md')), 'Restricted register excluded before hash')
    with open(path, 'rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest().upper()

def protect():
    before = read(os.path.join(AUDIT, 'BEFORE.json'))
    published = read(os.path.join(AUDIT, 'CPP-PUBLISHED.json'))
    req(published['Status'] == 'PASS-TWO-CPP-PUBLICATION-ONLY' and len(published['Files']) == 2, 'Actual exact two-CPP publication')
    overrides = {row['Relative']: row['PublishedSHA256'] for row in published['Files']}
    for row in before['Files']:
        req(sha(os.path.join(ROOT, row['Relative'])) == overrides.get(row['Relative'], row['SHA256']), 'Frozen original ' + row['Relative'])
    for row in before['Raw'] + before['Isolated']:
        req(sha(os.path.join(ROOT, row['Relative'])) == row['SHA256'], 'Frozen source ' + row['Relative'])

def load_native_reader():
    source_path = os.path.join(ROOT, 'Scripts', 'Create-FrameBeamPlacementDev.py')
    req(sha(source_path) == '18E96E5E3890A46584E49B85DC218986F044EC01758191AA363E0AB379E9E823', 'Frozen original reader bytes')
    with open(source_path, encoding='utf-8-sig') as stream:
        code = stream.read()
    req(code.count('\ntry:\n') == 1, 'Unique original main boundary; old author never executed')
    namespace = {'__name__': 'candidate_native_reader_only'}
    exec(code.split('\ntry:\n')[0], namespace)
    namespace['P'] = namespace['load_reader']()
    tree = ast.parse(code)
    functions = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'beam_observation']
    req(len(functions) == 1, 'Unique native beam reader')
    fn = copy.deepcopy(functions[0])
    cuts = [i for i, n in enumerate(fn.body) if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'dto' for t in n.targets)]
    req(len(cuts) == 1, 'Unique old placement assertion boundary; do not modify old assertions or old data')
    fn.name = 'beam_native_fields'
    fn.body = fn.body[:cuts[0]] + [ast.Return(value=ast.Name(id='result', ctx=ast.Load()))]
    module = ast.fix_missing_locations(ast.Module(body=[fn], type_ignores=[]))
    exec(compile(module, '<frozen-native-beam-field-reader>', 'exec'), namespace)
    return namespace

def exact_except_y(actual, baseline, delta, allowed, prefix=''):
    if isinstance(baseline, dict):
        req(isinstance(actual, dict) and set(actual) == set(baseline), 'Exact dictionary keys ' + prefix)
        for k, v in baseline.items():
            exact_except_y(actual[k], v, delta, allowed, prefix + '/' + k)
    elif isinstance(baseline, list):
        req(isinstance(actual, list) and len(actual) == len(baseline), 'Exact list count ' + prefix)
        for i, v in enumerate(baseline):
            exact_except_y(actual[i], v, delta, allowed, prefix + '/' + str(i))
    elif prefix in allowed and delta:
        req(isinstance(actual, (float, int)) and abs(actual - (baseline + delta)) < 1e-7, 'Only exact Y scalar changed ' + prefix)
    else:
        req(actual == baseline, 'Frozen exact scalar ' + prefix)

def observe(package, delta):
    current = P['scene']()
    req(P['path'](current[0]) == package + '.' + package.rsplit('/', 1)[1], 'Exact native world identity')
    req(len(current[1]) == 35, 'Exactly35 actual Actors; none added or removed')
    normalize = P['normalize']
    exact_except_y(normalize(current[3], package), normalize(COLD['scene_contract'], SOURCE), delta, SCENE_Y)
    actors = [a for a in current[1] if a.get_actor_label() == LABEL]
    req(len(actors) == 1, 'Exactly one existing passive beam')
    beam = P['beam_native_fields'](actors[0])
    exact_except_y(normalize(beam, package), normalize(COLD['beam'], SOURCE), delta, BEAM_Y)
    post = P['oldpost'](current)
    req(normalize(post, package) == normalize(COLD['post'], SOURCE), 'Original right post full native contract unchanged')
    R.update(scene_contract=current[3], beam=beam, post=post, normalized_contract=normalize(current[3], package),
             actor_count=35, inherited_contract_checks=len(P['R']['checks']), storage_probe=P['P']['storage'](current[0]))
    return current

def dirty_guard(allowed_maps):
    maps = [str(p.get_path_name()) for p in unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()]
    content = [str(p.get_path_name()) for p in unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages()]
    req(set(maps).issubset(set(allowed_maps)) and content == [], 'Only own candidate map may be dirty; no other asset')
    R.setdefault('dirty_observations', []).append(dict(maps=maps, content=content))

try:
    req(PHASE in ('probe', 'create', 'verify'), 'Bounded phases only')
    req(os.path.commonpath([os.path.abspath(OUT), os.path.abspath(AUDIT)]) == os.path.abspath(AUDIT), 'Result only in own audit')
    protect()
    DTO = read(os.path.join(AUDIT, 'PLACEMENT.json'))
    req(DTO['Schema'] == 'FrameBeamCandidateDev.v1' and DTO['Map'] == MAP and DTO['SourceMap'] == SOURCE
        and DTO['OriginalActors'] == DTO['ExpectedActors'] == 35 and DTO['DeltaYcm'] == DELTA, 'Frozen B identity, not a formal art adoption')
    COLD = read(os.path.join(ROOT, 'Saved', 'Audit-2026-10-12-FrameBeamPlacementDev', 'verify-Run1', 'Result.json'))
    req(COLD['success'] and COLD['actor_count'] == 35 and COLD['map'] == SOURCE, 'Frozen actual A cold read')
    P = load_native_reader()
    LEVELS = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    req(LEVELS.load_level(SOURCE), 'Load old source readonly')
    observe(SOURCE, 0.0)
    dirty_guard([])
    if PHASE == 'probe':
        req(not unreal.EditorAssetLibrary.does_asset_exist(MAP) and not os.path.exists(os.path.join(ROOT, 'Content', MAP[6:] + '.umap')), 'Absent independent destination')
    elif PHASE == 'create':
        req(not unreal.EditorAssetLibrary.does_asset_exist(MAP) and not os.path.exists(os.path.join(ROOT, 'Content', MAP[6:] + '.umap')), 'Never replace existing map')
        # observe() keeps no UObject globally. Release its returned tuple before world replacement.
        req(LEVELS.new_level_from_template(MAP, SOURCE), 'Native clone to own new map only')
        R['saved'].append(MAP)
        current = observe(MAP, 0.0)
        actor = next(a for a in current[1] if a.get_actor_label() == LABEL)
        req(callable(getattr(actor, 'modify', None)), 'Native UObject Modify available')
        actor.modify()
        req(actor.set_actor_location(unreal.Vector(*DTO['LocationCm']), False, True), 'Only beam Y changed on candidate clone')
        observe(MAP, DELTA)
        dirty_guard([MAP])
        protect()
        req(LEVELS.save_current_level(), 'Save only own new candidate map after exact contract validation')
        R.update(map_saved=True, save_operations=2, map_creation_api='LevelEditorSubsystem.new_level_from_template')
        dirty_guard([])
    else:
        req(LEVELS.load_level(MAP), 'Cold load candidate actually saved on disk')
        observe(MAP, DELTA)
        dirty_guard([])
    R['allowed_scalar_difference_paths'] = sorted(['scene_contract' + v for v in SCENE_Y] + ['beam' + v for v in BEAM_Y])
    protect()
    R['success'] = True
except Exception:
    R['error'] = traceback.format_exc()
    unreal.log_error(R['error'])
finally:
    with open(OUT, 'x', encoding='utf-8') as stream:
        json.dump(R, stream, ensure_ascii=False, indent=2)
