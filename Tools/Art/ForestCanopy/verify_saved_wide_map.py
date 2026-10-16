"""Independent zero-save cold verification of the map left by failed Wide create.

The actual exit-3 creation stays failed. Only reviewed reader definitions are
reused; no successful create report, authoring branch or save API is executed.
"""
import ast
import copy
import hashlib
import json
import os
from pathlib import Path
import re
import sys
import traceback

ROOT = Path('D:/灯影山海')
AUDIT = ROOT / 'Saved/Audit-2026-10-14-ArtAppearance'
READER = Path('C:/Users/lenovo/Documents/ChatGPT/数媒游戏开发 2/ArtIntegration-20261014/ForestCanopy/candidate_map_wide.py')
READER_SHA = 'CA91F448C69993104D4DAC0C7ECBFCFDA6FD31B2E523E100857996C4E60CA970'
CRASH = AUDIT / 'ForestCanopyWideMapCreate-Run1'
CRASH_SHA = {
    'Editor-EXIT.json': '66CA4A6DC6C635EF296099B9F7B38C10FEC68F2F0D24BC8B3DD3C51642BEB64B',
    'DISK-DELTA.json': 'CF86784E690CB89C3662947D1315F2BBC29D9F41BF3F62DCE326B4E791DC9D5A',
    'Session.log': '0583AB7FB7DA42B9BA706EBB18C4AA7502EBA6C5F3954F0CE2C164EB19756664',
}
MAP_RELATIVE = 'Content/DengYingShanHai/Dev/ForestCanopyWide/Maps/LV_ForestCanopyWideLab.umap'
MAP_SHA = 'FE49571ED7EB5F0E36C8BD5D55B149651B94901D22572D36FACEA0829727336A'
R = dict(success=False, phase='verify', saved=[], independent_cold_verified=False,
         prior_creation_failed_exit3=False, creation_was_successful=False,
         gameplay_changed=False, formal_map_changed=False, old_map_saved=False,
         content_saved=False, layout_changed=False, lights_changed=False,
         pp_changed=False, packaged=False, art_accepted=False)


def req(value, message):
    if not value:
        raise RuntimeError(message)
    return value


def sha(file):
    file = Path(file)
    req(file.resolve() != (ROOT / 'Docs/LICENSES.md').resolve(), 'Never access restricted license register')
    return hashlib.sha256(file.read_bytes()).hexdigest().upper()


def crash_evidence():
    hashes = {name: sha(CRASH / name) for name in CRASH_SHA}
    req(hashes == CRASH_SHA and not (CRASH / 'RESULT.json').exists(), 'Exact terminal crash evidence, no fabricated creation result')
    exit_record = json.loads((CRASH / 'Editor-EXIT.json').read_text(encoding='utf-8-sig'))
    delta = json.loads((CRASH / 'DISK-DELTA.json').read_text(encoding='utf-8-sig'))
    req(exit_record['ActualExitCode'] == 3 and exit_record['ExitWasNull'] is False
        and exit_record['NativeHandleCaptured'] is True and delta['ActualExit'] == 3
        and delta['FrozenCount'] == 425 and delta['FrozenUnchanged'] is True
        and delta['NewFiles'] == [MAP_RELATIVE.replace('/', '\\')]
        and sha(ROOT / MAP_RELATIVE) == MAP_SHA,
        'Real exit3, original425 unchanged and exactly this one saved map')
    return dict(directory=str(CRASH), actual_exit=3, success=False,
                evidence_sha256=hashes, saved_map_sha256=MAP_SHA, original_failure_preserved=True)


def readers():
    req(sha(READER) == READER_SHA, 'Exact reviewed Wide reader file, including future-create package-reference repair')
    tree = ast.parse(READER.read_text(encoding='utf-8-sig'))
    functions = {'path', 'object_path', 'package_file', 'load_helpers', 'derive'}
    constants = {'ROOT', 'AUDIT', 'SOURCE', 'MAP', 'FOREST', 'STAGE', 'BP', 'MESH', 'LEAF', 'WOOD',
                 'BASE', 'BASE_SHA', 'READER', 'READER_SHA'}
    nodes = [node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name in functions
             or isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name) and node.targets[0].id in constants]
    req({node.name for node in nodes if isinstance(node, ast.FunctionDef)} == functions
        and {node.targets[0].id for node in nodes if isinstance(node, ast.Assign)} == constants,
        'Only five pure helpers and fixed source/target/hash constants; no run/create_report/main')
    native_run = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == 'run')
    observation_names = {'level_graph', 'extra', 'visuals'}
    observations = [node for node in native_run.body if isinstance(node, ast.FunctionDef) and node.name in observation_names]
    req({node.name for node in observations} == observation_names, 'Only three native read-only observations, never a save branch')
    scope = dict(Path=Path, ast=ast, copy=copy, hashlib=hashlib, json=json, os=os, re=re, req=req, sha=sha)
    exec(compile(ast.Module(body=nodes + observations, type_ignores=[]), str(READER), 'exec'), scope)
    scope['lib'] = scope['load_helpers']()
    return scope


def run(out):
    import unreal
    s = readers()
    R.update(map=s['MAP'], source=s['SOURCE'])
    R['prior_creation'] = crash_evidence()
    R['prior_creation_failed_exit3'] = True
    req(os.environ['DY_CANOPY_MAP_PHASE'] == 'verify', 'Independent verifier cannot create')
    req(Path(os.path.realpath(unreal.SystemLibrary.get_project_directory())) == ROOT.resolve(), 'Exact physical project')
    editor = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
    levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)

    def clean():
        req(not editor.get_game_world() and not unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()
            and not unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages(), 'No PIE, dirty package, discard or save prompt')

    clean()
    req(unreal.find_object(None, s['object_path'](s['MAP'])) is None, 'Wide map initially not loaded in this fresh native process')
    frozen_file = Path(os.environ['DY_ART_FROZEN'])
    req(frozen_file.resolve().is_relative_to(AUDIT.resolve()), 'Explicit bounded full426 baseline from runner')
    frozen = json.loads(frozen_file.read_text(encoding='utf-8-sig'))
    req(len(frozen) >= 426 and len([row for row in frozen if row['Relative'].replace('\\', '/') == MAP_RELATIVE
        and row['SHA256'] == MAP_SHA]) == 1, 'Complete426 products including the exact saved map')

    def protect():
        for row in frozen:
            relative = row['Relative'].replace('\\', '/')
            req(not Path(relative).is_absolute() and '..' not in relative.split('/') and relative.lower() != 'docs/licenses.md',
                'Bounded unrestricted product row')
            file = ROOT / relative
            req(file.stat().st_size == row['Bytes'] and sha(file) == row['SHA256'], 'Frozen product ' + relative)

    protect()
    req(sha(s['BASE']) == s['BASE_SHA'], 'Exact actual source36 cold report')
    baseline = json.loads(s['BASE'].read_text(encoding='utf-8-sig'))
    req(baseline['success'] and baseline['cold_verified'] and baseline['phase'] == 'verify'
        and baseline['actor_count'] == 36 and baseline['map'] == s['SOURCE'], 'Independent original source map, not a fabricated create result')
    s.update(unreal=unreal, observer=s['lib']['load_observer'](unreal, out, 'verify'))

    def observe(package):
        # Return only Python value contracts; do not retain old world/package wrappers across LoadLevel.
        clean()
        req(levels.load_level(package), 'Cold read only ' + package)
        scene, labels, contract = s['observer']['current'](package)
        req(len(labels) == 36 and s['path'](editor.get_editor_world()) == s['object_path'](package)
            and scene[0].get_outer().get_path_name() == package, 'Exact36 persistent-level world and outer')
        extra = s['extra'](package, labels)
        visuals = s['visuals'](package, labels)
        req(sum(len(value) for value in visuals['spotlights'].values()) == 6, 'Original main plus five passive art/work Spots')
        forest = labels[s['FOREST']]
        req(scene[2].get_forest_presentation_actor() == forest and not forest.has_forest_session()
            and not forest.get_branch_mesh_components(), 'Explicit same-world Stage owner, clean forest and no runtime session')
        result = dict(contract=contract, extra=extra, visuals=visuals, graphs=s['level_graph'](scene, labels),
                      staff=s['observer']['staff'](labels['M2_Puppet_P02_Controlled']),
                      world=s['path'](scene[0]), outer=scene[0].get_outer().get_path_name())
        if package == s['MAP']:
            bp, mesh, leaf, wood = [req(unreal.load_asset(s[name]), 'Saved admitted ' + name) for name in ('BP', 'MESH', 'LEAF', 'WOOD')]
            req(unreal.BlueprintEditorLibrary.get_blueprint_parent_class(bp) == unreal.DYForestPresentationActor.static_class()
                and forest.get_class() == bp.generated_class(), 'Independent Wide data-only forest class with native parent')
            cdo = unreal.get_default_object(bp.generated_class())
            req(forest.get_editor_property('BranchLayout') == cdo.get_editor_property('BranchLayout')
                and len(cdo.get_editor_property('BranchLayout')) == 15 and not cdo.has_forest_session()
                and not cdo.get_branch_mesh_components() and cdo.get_editor_property('BranchMesh') == mesh
                and cdo.get_editor_property('BranchMaterial') == wood, 'Saved CDO exact15 layout and resources, no mutable session')
            req(len(mesh.get_editor_property('static_materials')) == mesh.get_num_sections(0) == 2
                and mesh.get_material(0) == wood and mesh.get_material(1) == leaf, 'Native wood0 and existing leaf1 only')
            result['forest_graphs'] = s['lib']['graph_gate'](bp, unreal)
        clean()
        return result

    source = observe(s['SOURCE'])
    req(source['contract'] == baseline['saved_contract'], 'Actual source36 unchanged against independent cold baseline')
    actual = observe(s['MAP'])
    original, contract = source['contract'], actual['contract']
    expected = s['derive'](original, contract[s['FOREST']]['object_path'], s['lib']['replace_identity'])
    expected_extra = s['lib']['replace_identity'](source['extra'], original[s['FOREST']]['object_path'], contract[s['FOREST']]['object_path'])
    req(contract == expected and actual['extra'] == expected_extra and actual['visuals'] == source['visuals']
        and actual['graphs'] == source['graphs'] and actual['staff'] == source['staff'],
        'All36 contracts: only Wide forest identity/class/mesh and Stage pointer delta; exact15 layout/diameters/15Hz/6Spots/PP/flags/LevelBP')
    protect()
    req(sha(ROOT / MAP_RELATIVE) == MAP_SHA and crash_evidence() == R['prior_creation'], 'New map and original failed evidence remain byte-identical')
    R.update(success=True, independent_cold_verified=True, cold_verified=True, actor_count=36,
             saved_contract=contract, saved_extra=actual['extra'], source_contract=original,
             source_extra=source['extra'], source_visuals=source['visuals'], source_graphs=source['graphs'],
             forest_graphs=actual['forest_graphs'], native_world=actual['world'], native_outer=actual['outer'],
             new_map_sha256=MAP_SHA, reader_sha256=READER_SHA)


if __name__ == '__main__':
    if '--self-check' in sys.argv:
        s = readers()
        failure = crash_evidence()
        original = json.loads(s['BASE'].read_text(encoding='utf-8-sig'))['saved_contract']
        before = copy.deepcopy(original)
        expected = s['derive'](original, '<world>:PersistentLevel.WideForest', s['lib']['replace_identity'])
        assert original == before and failure['actual_exit'] == 3 and failure['success'] is False
        assert expected[s['FOREST']]['forest_authoring']['layout'] == original[s['FOREST']]['forest_authoring']['layout']
        assert all(expected[name] == row for name, row in original.items() if name not in (s['FOREST'], s['STAGE']))
        calls = {node.func.attr for node in ast.walk(ast.parse(Path(__file__).read_text(encoding='utf-8')))
                 if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)}
        assert not calls & {'save_map', 'save_current_level', 'save_loaded_asset', 'duplicate_asset', 'set_editor_property',
                            'spawn_actor_from_class', 'destroy_actor', 'new_level_from_template', 'editor_request_begin_play'}
        print('PASS: exact terminal exit3/map/log/delta hashes, pure source36 contracts and reader-only AST scope; no Unreal, create result or save')
    else:
        out = Path(os.environ['DY_CANOPY_MAP_OUT'])
        req(out.is_absolute() and out.resolve().is_relative_to(AUDIT.resolve()) and out.name == 'RESULT.json'
            and out.parent.is_dir() and not out.exists(), 'Fresh bounded cold verification output')
        try:
            run(out)
        except Exception:
            R['error'] = traceback.format_exc()
        with out.open('x', encoding='utf-8') as stream:
            json.dump(R, stream, ensure_ascii=False, indent=2)
        req(R['success'], 'Independent cold verification failed; original creation crash stays failed, never save or repair here')
