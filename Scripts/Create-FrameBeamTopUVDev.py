"""Independent B-map clone: change only its passive beam's mesh reference.

This editor-only author/observer never edits a source world, mesh, material,
gameplay Blueprint, camera, sound, or global configuration. Probe and verify are
read-only. Create can save only the absent, explicitly named new Dev map.
"""
import copy
import hashlib
import json
import os
import traceback
import unreal

ROOT = os.path.realpath(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir()))
AUDIT = os.path.join(ROOT, 'Saved', 'Audit-2026-10-13-FrameBeamTopUVDev')
SOURCE = '/Game/DengYingShanHai/Dev/FrameBeamCandidate/Maps/LV_FrameBeamCandidateLab'
MAP = '/Game/DengYingShanHai/Dev/FrameBeamTopUV/Maps/LV_FrameBeamTopUVLab'
OLD = '/Game/DengYingShanHai/Dev/FrameBeamAsset/Meshes/SM_DY_FrameBeam_Source'
NEW = '/Game/DengYingShanHai/Dev/FrameBeamTopUV/Meshes/SM_DY_FrameBeam_TopUV'
LABEL = 'DEV_FrameBeam_RightJoint'
OUT = os.environ.get('DY_TOPUV_DEV_OUT', os.environ.get('DY_BEAM_DEV_OUT'))
PHASE = os.environ.get('DY_TOPUV_DEV_PHASE', os.environ.get('DY_BEAM_DEV_PHASE'))
ALLOWED = frozenset(('/scene_contract/DEV_FrameBeam_RightJoint/static_meshes/0/mesh', '/beam/mesh'))
CPP_FILES = frozenset(('Source\\DengYingShanHai\\Private\\Core\\DYDevEntryPlayerController.cpp',
                       'Source\\DengYingShanHai\\Private\\Tests\\DYEntryLoopAutomationTests.cpp'))
R = dict(success=False, phase=PHASE, source=SOURCE, map=MAP, saved=[], assets_saved=[],
         map_saved=False, checks=[], actor_count=35, mesh_reference_writes=0,
         visual_acceptance=False, formal_scale=False, candidate_adopted=False,
         physical_blocking=False, joinery_or_load_accepted=False, gameplay_changed=False,
         material_changed=False)


def req(value, message):
    if not value:
        raise RuntimeError(message)
    R['checks'].append(message)
    return value


def restricted_guard(filename):
    req(os.path.normcase(os.path.abspath(filename)) != os.path.normcase(
        os.path.join(ROOT, 'Docs', 'LICENSES.md')), 'Restricted register excluded BEFORE content access')


def read(filename):
    restricted_guard(filename)
    with open(filename, encoding='utf-8-sig') as stream:
        return json.load(stream)


def sha(filename):
    restricted_guard(filename)
    digest = hashlib.sha256()
    with open(filename, 'rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest().upper()


def relative_path(relative):
    req(isinstance(relative, str) and relative and not os.path.isabs(relative)
        and '..' not in relative.replace('\\', '/').split('/'), 'Bounded relative frozen filename')
    filename = os.path.abspath(os.path.join(ROOT, relative))
    req(os.path.commonpath((filename, ROOT)) == ROOT, 'Frozen filename remains inside project')
    restricted_guard(filename)
    return filename


def protect():
    before = read(os.path.join(AUDIT, 'BEFORE.json'))
    req(len(before['Files']) == 348, 'Exact frozen 348 original products before this map step')
    published = read(os.path.join(AUDIT, 'CPP-PUBLISHED.json'))
    req(published['Status'] == 'PASS-TWO-CPP-PUBLICATION-ONLY'
        and len(published['Files']) == 2
        and {row['Relative'] for row in published['Files']} == CPP_FILES,
        'Only the exact two approved C++ publication overrides')
    overrides = {row['Relative']: row['PublishedSHA256'] for row in published['Files']}
    for row in before['Files']:
        req(sha(relative_path(row['Relative'])) == overrides.get(row['Relative'], row['SHA256']),
            'Frozen original product ' + row['Relative'])
    for row in before['Raw'] + before['Isolated']:
        req(sha(relative_path(row['Relative'])) == row['SHA256'], 'Frozen source ' + row['Relative'])


def object_path(package):
    return package + '.' + package.rsplit('/', 1)[1]


def load_native_reader():
    filename = os.path.join(ROOT, 'Scripts', 'Create-FrameBeamCandidateDev.py')
    req(sha(filename) == 'C8ECCA70C228A9D8A2AD92C4C5A4438831F0059147D96DE9B93E450F22E77594',
        'Frozen B observer definitions bytes')
    with open(filename, encoding='utf-8-sig') as stream:
        code = stream.read()
    req(code.count('\ntry:\n') == 1, 'Unique B main boundary; original author/main never executed')
    # These aliases exist only in this isolated editor child process. All old
    # definitions-only namespaces expect them, but none of their mains execute.
    for prefix in ('DY_BEAM_DEV', 'DY_FRAMEPOST', 'DY_READABILITY'):
        os.environ[prefix + '_OUT'] = OUT
        os.environ[prefix + '_PHASE'] = PHASE
    namespace = {'__name__': 'topuv_b_native_observer_definitions_only'}
    exec(code.split('\ntry:\n')[0], namespace)
    # B's load_native_reader strips only the old placement DTO assertions after
    # gathering native fields. Its authors, protect and coordinate setters do
    # not execute. The new script applies an exact, separate frozen B contract.
    return namespace['load_native_reader']()


def exact_only_mesh(actual, baseline, candidate=False, prefix='', found=None):
    """Strict recursive comparison; no whole-value/string replacement allowed.

    Only two explicitly named scalar fields may differ, and only OLD -> NEW.
    JSON numeric and bool types are checked independently (True != 1 here).
    """
    if found is None:
        found = set()
    req(type(actual) is type(baseline), 'Exact recursive value type ' + prefix)
    if isinstance(baseline, dict):
        req(set(actual) == set(baseline), 'Exact recursive dictionary keys ' + prefix)
        for key, expected in baseline.items():
            exact_only_mesh(actual[key], expected, candidate, prefix + '/' + key, found)
    elif isinstance(baseline, list):
        req(len(actual) == len(baseline), 'Exact recursive list length ' + prefix)
        for index, expected in enumerate(baseline):
            exact_only_mesh(actual[index], expected, candidate, prefix + '/' + str(index), found)
    elif candidate and prefix in ALLOWED:
        req(baseline == object_path(OLD) and actual == object_path(NEW),
            'Only exact approved OLD to NEW beam mesh scalar ' + prefix)
        req(prefix not in found, 'Each allowed scalar observed once ' + prefix)
        found.add(prefix)
    else:
        req(actual == baseline, 'Frozen exact recursive scalar ' + prefix)
    if prefix == '':
        req(found == (set(ALLOWED) if candidate else set()), 'Exact two mesh paths, or zero for old source')
    return found


def validate_dto(dto, baseline):
    req(dto['Schema'] == 'FrameBeamTopUVDev.v1' and dto['Map'] == MAP and dto['SourceMap'] == SOURCE
        and dto['OriginalActors'] == dto['ExpectedActors'] == 35 and dto['Label'] == LABEL,
        'Exact independent TopUV Dev identity and 35 original Actors')
    req(dto['SourceMesh'] == OLD and dto['Mesh'] == NEW,
        'DTO permits only already accepted source and independent TopUV mesh')
    req(set(dto['OnlyMeshReferencePaths']) == {path.lstrip('/') for path in ALLOWED}
        and len(dto['OnlyMeshReferencePaths']) == 2,
        'DTO exact two allowed scalar paths')
    req(all(dto[name] is False for name in ('GameplayChanged', 'MaterialChanged',
                                           'FormalScaleAccepted', 'CandidateAdopted')),
        'DTO is not gameplay/material/formal scale/art adoption authorization')
    beam = baseline['beam']
    req(dto['LocationCm'] == beam['location'] and all(
        abs(value - dto['UniformScale']) < 1e-12 for value in beam['scale']),
        'DTO unchanged B native location and equal XYZ scale')
    req(len(dto['RotationDegrees']) == 3 and all(abs(a - b) < 1e-12 for a, b in
        zip(dto['RotationDegrees'], beam['rotation'])), 'DTO unchanged B native rotation')
    req(dto['ExpectedBoundsMinCm'] == beam['bounds']['min']
        and dto['ExpectedBoundsMaxCm'] == beam['bounds']['max'], 'DTO unchanged B native bounds')


def observe(package, candidate=False):
    current = P['scene']()
    req(P['path'](current[0]) == object_path(package), 'Exact current native source or own new world identity')
    req(len(current[1]) == 35 and set(current[3]) == set(COLD['scene_contract']),
        'Exactly 35 original Actors and all frozen actor, pawn and flow contract keys')
    beam_actors = [actor for actor in current[1] if actor.get_actor_label() == LABEL]
    req(len(beam_actors) == 1, 'Exactly one original passive beam actor')
    beam = P['beam_native_fields'](beam_actors[0])
    post = P['oldpost'](current)
    combined = dict(scene_contract=current[3], beam=beam, post=post)
    normalized = P['normalize'](combined, package)
    baseline = P['normalize']({name: COLD[name] for name in combined}, SOURCE)
    exact_only_mesh(normalized, baseline, candidate)
    R.update(combined, normalized_contract=normalized['scene_contract'], actor_count=35,
             inherited_contract_checks=len(P['R']['checks']), storage_probe=P['P']['storage'](current[0]))
    return current


def dirty_guard(allowed_maps=()):
    maps = [str(package.get_path_name()) for package in unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()]
    content = [str(package.get_path_name()) for package in unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages()]
    req(set(maps).issubset(set(allowed_maps)) and content == [],
        'Only own new map may be dirty, never source map or any content asset')
    R.setdefault('dirty_observations', []).append(dict(maps=maps, content=content))


def destination_absent():
    req(not unreal.EditorAssetLibrary.does_asset_exist(MAP) and not os.path.exists(
        os.path.join(ROOT, 'Content', MAP[6:] + '.umap')), 'Own independent destination absent; never overwrite')


try:
    req(PHASE in ('probe', 'create', 'verify'), 'Exact bounded source probe/new-map author/cold verify phases')
    req(isinstance(OUT, str) and os.path.commonpath((os.path.abspath(OUT), os.path.abspath(AUDIT))) ==
        os.path.abspath(AUDIT), 'Write result only in own task audit')
    protect()
    COLD = read(os.path.join(ROOT, 'Saved', 'Audit-2026-10-13-FrameBeamCandidateDev', 'verify-Run1', 'Result.json'))
    req(COLD['success'] is True and COLD['phase'] == 'verify' and COLD['actor_count'] == 35
        and COLD['map'] == SOURCE and COLD['saved'] == [] and COLD['map_saved'] is False,
        'Actual completed read-only native B cold baseline, never guessed placement')
    DTO = read(os.path.join(AUDIT, 'PLACEMENT.json'))
    validate_dto(DTO, COLD)
    P = load_native_reader()
    LEVELS = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    req(LEVELS.load_level(SOURCE), 'Cold load original B map read-only')
    observe(SOURCE)
    dirty_guard()
    R['source_observation'] = copy.deepcopy({name: R[name] for name in
        ('scene_contract', 'beam', 'post', 'normalized_contract', 'storage_probe')})
    if PHASE == 'probe':
        destination_absent()
        mesh = req(unreal.load_asset(NEW), 'Existing independently accepted TopUV mesh asset')
        req(P['path'](mesh) == object_path(NEW), 'Exact actual TopUV mesh identity')
        dirty_guard()
    elif PHASE == 'create':
        destination_absent()
        req(LEVELS.new_level_from_template(MAP, SOURCE), 'Native copy of unchanged B to own absent new map only')
        R['saved'].append(MAP)
        R['map_creation_api'] = 'LevelEditorSubsystem.new_level_from_template'
        current = observe(MAP)
        actor = next(value for value in current[1] if value.get_actor_label() == LABEL)
        component = req(actor.get_component_by_class(unreal.StaticMeshComponent), 'Copied passive beam native component')
        req(component.get_owner() == actor and len(actor.get_components_by_class(unreal.StaticMeshComponent)) == 1,
            'Unchanged unique passive actor/component ownership')
        mesh = req(unreal.load_asset(NEW), 'Reference existing candidate; never import or save a mesh')
        req(P['path'](mesh) == object_path(NEW), 'Actual exact new mesh object before reference mutation')
        req(P['path'](component.get_editor_property('static_mesh')) == object_path(OLD),
            'Only copied beam currently refers to original mesh')
        actor.modify()
        component.modify()
        req(component.set_static_mesh(mesh), 'Only allowed mutation: copied beam OLD mesh to NEW')
        R['mesh_reference_writes'] = 1
        observe(MAP, True)
        dirty_guard((MAP,))
        protect()
        req(LEVELS.save_current_level(), 'Save only own new map after complete exact native contract gates')
        R.update(map_saved=True, save_operations=2)
        dirty_guard()
    else:
        req(LEVELS.load_level(MAP), 'Independent cold load of actual saved TopUV Dev map')
        observe(MAP, True)
        dirty_guard()
        req(R['saved'] == [] and R['mesh_reference_writes'] == 0, 'Verifier has zero saves or mesh mutations')
    R['allowed_scalar_difference_paths'] = sorted(ALLOWED)
    protect()
    R['success'] = True
except Exception:
    R['error'] = traceback.format_exc()
    unreal.log_error(R['error'])
finally:
    with open(OUT, 'x', encoding='utf-8') as stream:
        json.dump(R, stream, ensure_ascii=False, indent=2)
