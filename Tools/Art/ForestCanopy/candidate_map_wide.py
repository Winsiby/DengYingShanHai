"""Save-as one independent wide-canopy Dev map, or cold-verify that saved map.

Only the forest data Actor is replaced. The old map is never saved. One explicit
EditorLoadingAndSavingUtils.save_map(World, NEW) call creates the absent target;
no duplicate-asset save, template auto-save, content save, PIE or CDO mutation.
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
SOURCE = '/Game/DengYingShanHai/Dev/StageArtComposition/Maps/LV_StageArtCompositionLab'
MAP = '/Game/DengYingShanHai/Dev/ForestCanopyWide/Maps/LV_ForestCanopyWideLab'
FOREST = 'M3_RuntimeForest'
STAGE = 'Readability_StagePresentation'
BP = '/Game/DengYingShanHai/Dev/ForestCanopyWide/Presentation/BP_DYForestCanopy_WideLeaf'
MESH = '/Game/DengYingShanHai/Dev/ForestCanopyWide/Meshes/SM_DY_ForestBranch_WideLeaf'
LEAF = '/Game/DengYingShanHai/Dev/ForestCanopy/Materials/M_DY_ForestLeaf'
WOOD = '/Game/DengYingShanHai/Dev/FramePostAsset/Materials/MI_DY_FramePost_Wood'
BASE = AUDIT / 'StagePropsMapLightVerify-Run1/RESULT.json'
BASE_SHA = '376B3D333E6AF40EA8C680914CE99AA18E8FFE6666B915BBFC474D64F612D355'
READER = Path('C:/Users/lenovo/Documents/ChatGPT/数媒游戏开发 2/ArtIntegration-20261014/StageProps/revise_stage_map.py')
READER_SHA = 'DBF885DB46C60EEF2E7BED49D6618F95482227797EC8BF746FC6ED73326C11E2'
R = dict(success=False, saved=[], old_map_saved=False, content_saved=False,
         gameplay_changed=False, formal_map_changed=False, layout_changed=False,
         lights_changed=False, pp_changed=False, packaged=False, art_accepted=False)


def req(value, message):
    if not value:
        raise RuntimeError(message)
    return value


def sha(file):
    file = Path(file)
    req(file.resolve() != (ROOT / 'Docs/LICENSES.md').resolve(), 'Never read or hash restricted license register')
    return hashlib.sha256(file.read_bytes()).hexdigest().upper()


def path(value):
    return value.get_path_name() if value else None


def object_path(package):
    return package + '.' + package.rsplit('/', 1)[1]


def package_file(package, map_package=False):
    req(package in (SOURCE, MAP, BP, MESH, LEAF, WOOD), 'Only fixed source/new map and art inputs')
    return ROOT / 'Content' / (package[6:] + ('.umap' if map_package else '.uasset'))


def load_helpers():
    req(sha(READER) == READER_SHA, 'Reviewed scene helper source-file SHA; never execute its author/main')
    tree = ast.parse(READER.read_text(encoding='utf-8-sig'))
    functions = {'load_observer', 'extra_contract', 'graph_gate', 'replace_identity'}
    constants = {'COMPOSE_SHA', 'WINGS_SHA', 'ENV_SHA'}
    nodes = [node for node in tree.body
             if isinstance(node, ast.FunctionDef) and node.name in functions
             or isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name) and node.targets[0].id in constants]
    req({node.name for node in nodes if isinstance(node, ast.FunctionDef)} == functions
        and {node.targets[0].id for node in nodes if isinstance(node, ast.Assign)} == constants, 'Exact four read-only helper functions and hash constants')
    scope = dict(os=os, ast=ast, Path=Path, ROOT=ROOT, MAP=SOURCE, sha=sha, req=req)
    exec(compile(ast.Module(body=nodes, type_ignores=[]), str(READER), 'exec'), scope)
    return scope


def derive(original, forest_identity, replace_identity):
    req(len([key for key in original if not key.startswith('_')]) == 36
        and original['_flow']['hz'] == 15.0 and len(original[FOREST]['forest_authoring']['layout']) == 15,
        'Actual fixed 36-actor/15Hz/15-branch baseline')
    result = replace_identity(copy.deepcopy(original), original[FOREST]['object_path'], forest_identity)
    result[FOREST]['class_path'] = object_path(BP) + '_C'
    result[FOREST]['forest_authoring']['mesh'] = object_path(MESH)
    # BranchMaterial still overrides slot0 only; the new mesh owns its leaf slot1.
    req(result[FOREST]['forest_authoring']['material'] == object_path(WOOD), 'Keep original slot0 wood override')
    return result


def create_report(file):
    req(file.resolve().is_relative_to(AUDIT.resolve()) and file.name == 'RESULT.json', 'Explicit bounded successful wide-map create evidence')
    created = json.loads(file.read_text(encoding='utf-8-sig'))
    req(created['success'] is True and created['phase'] == 'create' and created['map'] == MAP
        and created['source'] == SOURCE and created['saved'] == [MAP], 'Only the successful first save of this independent wide map')
    return created, dict(path=str(file), sha256=sha(file), success=True)


def run(phase, out):
    import unreal
    req(Path(os.path.realpath(unreal.SystemLibrary.get_project_directory())) == ROOT.resolve(), 'Exact physical project')
    levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    editor = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
    actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    req(not editor.get_game_world() and not unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()
        and not unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages(), 'No PIE or unsaved user state to discard')
    req(sha(BASE) == BASE_SHA, 'Actual independent 36-actor source/cold worklight report')
    base = json.loads(BASE.read_text(encoding='utf-8-sig'))
    req(base['success'] and base['phase'] == 'verify' and base['cold_verified']
        and base['map'] == SOURCE and base['actor_count'] == 36, 'Exact current source, not an old 34/41-actor snapshot')
    frozen_file = Path(os.environ['DY_ART_FROZEN'])
    req(frozen_file.resolve().is_relative_to(AUDIT.resolve()), 'Explicit full product baseline')
    frozen = json.loads(frozen_file.read_text(encoding='utf-8-sig'))
    req(len(frozen) >= 423, 'At least the complete current 423-product baseline')

    def protect():
        for row in frozen:
            relative = row['Relative'].replace('\\', '/')
            req(not Path(relative).is_absolute() and '..' not in relative.split('/')
                and relative.lower() != 'docs/licenses.md', 'Only bounded unrestricted frozen products')
            file = ROOT / relative
            req(file.stat().st_size == row['Bytes'] and sha(file) == row['SHA256'], 'Frozen product ' + relative)

    protect()
    source_sha = sha(package_file(SOURCE, True))
    art_hashes = {package: sha(package_file(package)) for package in (BP, MESH, LEAF, WOOD)}
    own_file = package_file(MAP, True)
    if phase == 'create':
        req(not own_file.exists() and not unreal.EditorAssetLibrary.does_asset_exist(MAP), 'Destination map wholly absent; never replace')
    else:
        req(own_file.is_file() and unreal.EditorAssetLibrary.does_asset_exist(MAP)
            and unreal.find_object(None, object_path(MAP)) is None, 'Saved new map not yet loaded for independent cold verification')
    own_before = sha(own_file) if phase == 'verify' else None
    lib = load_helpers()
    observer = lib['load_observer'](unreal, out, 'verify')
    req(levels.load_level(SOURCE), 'Cold-load old source without any save')
    source_scene, source_labels, original = observer['current'](SOURCE)
    req(len(source_labels) == 36 and original == base['saved_contract'], 'Actual original 36 actor/general contracts still exact')
    req(path(source_scene[0]) == object_path(SOURCE), 'Exact current old world before any authoring')
    source_extra = lib['extra_contract'](source_labels, unreal, observer['normalize'])
    staff_before = observer['staff'](source_labels['M2_Puppet_P02_Controlled'])

    def level_graph(scene, labels):
        level = labels['DEV_Floor'].get_outer()
        req(all(actor.get_outer() == level for actor in scene[1]), 'Only the same persistent-level actor set')
        blueprints = [bp for bp in unreal.ObjectIterator(unreal.Blueprint) if bp.get_outer() == level]
        scripts = [actor for actor in unreal.ObjectIterator(unreal.LevelScriptActor) if actor.get_outer() == level]
        req(len(blueprints) <= 1 and len(scripts) <= 1
            and all(bp.get_class().get_name() == 'LevelScriptBlueprint' for bp in blueprints), 'Actual loaded LevelBP inventory, no synthetic LevelBP creation')
        bp = blueprints[0] if blueprints else None
        req(not scripts or unreal.BlueprintEditorLibrary.get_blueprint_for_class(scripts[0].get_class()) == bp, 'Actual LevelScriptActor source agrees')
        return lib['graph_gate'](bp, unreal)

    def extra(package, labels):
        lib['MAP'] = package
        return lib['extra_contract'](labels, unreal, observer['normalize'])

    def visuals(package, labels):
        lights, pp = {}, {}
        for label, actor in labels.items():
            lights[label] = []
            for light in actor.get_components_by_class(unreal.SpotLightComponent):
                color = light.get_editor_property('light_color')
                channels = light.get_editor_property('lighting_channels')
                lights[label].append(dict(component=observer['normalize'](path(light), package),
                    world=observer['namespace']['transform'](light.get_world_transform()),
                    properties={name: str(light.get_editor_property(name)) for name in ('mobility', 'intensity_units', 'intensity',
                        'use_inverse_squared_falloff', 'attenuation_radius', 'inner_cone_angle', 'outer_cone_angle', 'source_radius',
                        'cast_shadows', 'allow_mega_lights', 'volumetric_scattering_intensity', 'indirect_lighting_intensity', 'visible', 'hidden_in_game')},
                    color=[color.r, color.g, color.b, color.a], channels=[channels.get_editor_property('bChannel' + str(i)) for i in range(3)]))
            if isinstance(actor, unreal.PostProcessVolume):
                pp[label] = dict(settings=re.sub(r'\s*\(0x[0-9a-fA-F]+\)', '', str(actor.get_editor_property('settings'))),
                    properties={name: actor.get_editor_property(name) for name in ('priority', 'blend_radius', 'blend_weight', 'enabled', 'unbound')})
        return dict(spotlights={key: value for key, value in lights.items() if value}, post_process=pp)

    source_graph = level_graph(source_scene, source_labels)
    source_visuals = visuals(SOURCE, source_labels)
    req(sum(len(value) for value in source_visuals['spotlights'].values()) == 6, 'Actual original main Spot plus five stage/work Spots')
    bp, mesh, leaf, wood = [req(unreal.load_asset(package), 'Already admitted canopy resource ' + package) for package in (BP, MESH, LEAF, WOOD)]
    req(unreal.BlueprintEditorLibrary.get_blueprint_parent_class(bp) == unreal.DYForestPresentationActor.static_class(), 'New data BP has unchanged direct native forest parent')
    R['forest_graphs'] = lib['graph_gate'](bp, unreal)
    cdo = unreal.get_default_object(req(bp.generated_class(), 'Actual saved generated canopy class'))
    req(cdo.get_editor_property('BranchMesh') == mesh and cdo.get_editor_property('BranchMaterial') == wood
        and cdo.get_editor_property('BranchLayout') == source_labels[FOREST].get_editor_property('BranchLayout')
        and len(cdo.get_editor_property('BranchLayout')) == 15 and not cdo.has_forest_session() and not cdo.get_branch_mesh_components(), 'Saved resources only, original exact 15 definitions and empty CDO session')
    req(len(mesh.get_editor_property('static_materials')) == mesh.get_num_sections(0) == 2
        and mesh.get_material(0) == wood and mesh.get_material(1) == leaf, 'Actual canopy Wood slot0 / leaf slot1')
    if phase == 'create':
        old = source_labels[FOREST]
        req(source_scene[2].get_forest_presentation_actor() == old and not old.has_forest_session()
            and not old.get_branch_mesh_components() and not old.get_owner() and not old.get_attach_parent_actor(), 'Only explicit Stage binding to a clean independent forest may change')
        for actor in source_scene[1]:
            req(actor.get_owner() != old and actor.get_attach_parent_actor() != old, 'No foreign actor owned by/attached to old forest')
            for component in actor.get_components_by_class(unreal.SceneComponent):
                parent = component.get_attach_parent()
                req(not parent or parent.get_owner() != old or parent.get_owner() == actor, 'No foreign component attached to old forest')
        new = req(actors.spawn_actor_from_class(bp.generated_class(), old.get_actor_location(), old.get_actor_rotation()), 'Only the admitted canopy forest replacement')
        req(new.set_actor_transform(old.get_actor_transform(), False, True), 'Exact source transform, no text-rounding duplicate')
        new.set_editor_property('tags', old.get_editor_property('tags'))
        new.set_editor_property('hidden', old.get_editor_property('hidden'))
        new.set_actor_enable_collision(old.get_actor_enable_collision())
        source_scene[2].set_editor_property('ForestPresentationActor', new, notify_mode=unreal.PropertyAccessChangeNotifyMode.NEVER)
        req(source_scene[2].get_forest_presentation_actor() == new, 'Explicit Stage pointer readback without Construction Script rerun')
        req(actors.destroy_actor(old), 'Only replaced RAM forest removed')
        new.set_actor_label(FOREST, False)
        scene, labels, actual = observer['current'](SOURCE)
        expected = derive(original, actual[FOREST]['object_path'], lib['replace_identity'])
        req(len(labels) == 36 and actual == expected, 'Only exact forest class/resource/Stage identity delta before any save')
        before_save_extra = extra(SOURCE, labels)
        expected_extra = lib['replace_identity'](source_extra, original[FOREST]['object_path'], actual[FOREST]['object_path'])
        req(before_save_extra == expected_extra and visuals(SOURCE, labels) == source_visuals
            and level_graph(scene, labels) == source_graph, 'All actor flags/tags/attachments/channels, six Spots, PP and empty LevelBP unchanged')
        req(not unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages(), 'No CDO/content resource dirtied')
        dirty = [package.get_path_name() for package in unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()]
        req(dirty == [SOURCE] and path(editor.get_editor_world()) == object_path(SOURCE), 'Only our isolated source-world RAM copy dirty before SaveAs')
        protect()
        req(hasattr(unreal.EditorLoadingAndSavingUtils, 'save_map'), 'Installed reflected SaveMap API exists')
        req(unreal.EditorLoadingAndSavingUtils.save_map(scene[0], MAP), 'One explicit save to exact absent new map; never save source path')
        R['saved'].append(MAP)
        own_ram_dirty = [package.get_path_name() for package in unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()]
        req(sha(package_file(SOURCE, True)) == source_sha and set(own_ram_dirty).issubset({SOURCE})
            and not unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages(),
            'Only this process-owned source RAM copy may be dirty; original disk and all content remain unchanged')
        R['discarded_only_own_ram_source'] = own_ram_dirty
        req(levels.load_level(MAP), 'Explicitly load saved new destination; SaveMap does not change the editor current world')
        scene, labels, actual = observer['current'](MAP)
        req(path(editor.get_editor_world()) == object_path(MAP) and scene[0].get_outer().get_path_name() == MAP, 'Loaded new world and package are exactly the new target')
        req(actual == expected and extra(MAP, labels) == expected_extra and visuals(MAP, labels) == source_visuals
            and level_graph(scene, labels) == source_graph, 'Exact normalized post-SaveAs full preservation')
    else:
        created_file = Path(os.environ['DY_CANOPY_MAP_CREATED'])
        created, evidence = create_report(created_file)
        R['prior_create'] = evidence
        req(created['source_contract'] == original and created['source_extra'] == source_extra
            and created['source_visuals'] == source_visuals and created['source_graphs'] == source_graph,
            'Source remains exactly equal to actual successful create observation')
        req(not unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()
            and not unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages(), 'Source cold read clean before new map load')
        req(levels.load_level(MAP), 'Independent cold new map load, no save')
        scene, labels, actual = observer['current'](MAP)
        expected = derive(original, actual[FOREST]['object_path'], lib['replace_identity'])
        expected_extra = lib['replace_identity'](source_extra, original[FOREST]['object_path'], actual[FOREST]['object_path'])
        req(actual == expected and extra(MAP, labels) == expected_extra
            and visuals(MAP, labels) == source_visuals and level_graph(scene, labels) == source_graph, 'Cold exact new map contracts, full passive flags, lights, PP and LevelBP')
        req(actual == created['saved_contract'] and expected_extra == created['saved_extra'], 'Cold map also matches actual successful create observation')
    req(len(labels) == 36 and scene[2].get_forest_presentation_actor() == labels[FOREST]
        and labels[FOREST].get_class() == bp.generated_class() and not labels[FOREST].has_forest_session()
        and not labels[FOREST].get_branch_mesh_components(), 'Exactly one clean same-world leafed forest owner and 36 actors')
    req(observer['staff'](labels['M2_Puppet_P02_Controlled']) == staff_before, 'Actual Staff endpoints and local bounds unchanged')
    req(sha(package_file(SOURCE, True)) == source_sha and all(sha(package_file(package)) == value for package, value in art_hashes.items()), 'Old map disk and all data/material/CDO packages byte-unchanged')
    req(not unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages()
        and not unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages(), 'No dirty map/content left; no prompt or automatic source save')
    protect()
    req(phase != 'verify' or sha(own_file) == own_before, 'Read-only cold new-map bytes unchanged')
    R.update(success=True, map=MAP, source=SOURCE, actor_count=36, saved_contract=actual,
             saved_extra=extra(MAP, labels), source_contract=original, source_extra=source_extra,
             source_visuals=source_visuals, source_graphs=source_graph,
             source_map_sha256=source_sha, new_map_sha256=sha(own_file), art_input_sha256=art_hashes,
             native_world=path(scene[0]), native_outer=scene[0].get_outer().get_path_name(),
             cold_verified=phase == 'verify', save_api='EditorLoadingAndSavingUtils.save_map(World, exact_new_path)')


if __name__ == '__main__':
    if '--self-check' in sys.argv:
        req(sha(BASE) == BASE_SHA, 'Actual current cold source report')
        original = json.loads(BASE.read_text(encoding='utf-8-sig'))['saved_contract']
        lib = load_helpers()
        untouched = copy.deepcopy(original)
        expected = derive(original, '<world>:PersistentLevel.NewCanopy', lib['replace_identity'])
        assert original == untouched and len(expected) == len(original)
        assert expected[FOREST]['forest_authoring']['layout'] == original[FOREST]['forest_authoring']['layout']
        assert expected[STAGE]['bindings']['forest'] == '<world>:PersistentLevel.NewCanopy'
        assert all(expected[name] == value for name, value in original.items() if name not in (FOREST, STAGE))
        assert MAP == '/Game/DengYingShanHai/Dev/ForestCanopyWide/Maps/LV_ForestCanopyWideLab'
        assert BP == '/Game/DengYingShanHai/Dev/ForestCanopyWide/Presentation/BP_DYForestCanopy_WideLeaf'
        assert MESH == '/Game/DengYingShanHai/Dev/ForestCanopyWide/Meshes/SM_DY_ForestBranch_WideLeaf'
        assert LEAF == '/Game/DengYingShanHai/Dev/ForestCanopy/Materials/M_DY_ForestLeaf'
        assert package_file(MAP, True).suffix == '.umap' and package_file(BP).suffix == '.uasset'
        tree = ast.parse(Path(__file__).read_text(encoding='utf-8'))
        calls = [node.func.attr for node in ast.walk(tree) if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)]
        assert calls.count('save_map') == 1 and not set(calls) & {'save_current_level', 'save_loaded_asset', 'new_level_from_template',
            'duplicate_asset', 'save_all_dirty_levels', 'compile_blueprint', 'set_view_target', 'editor_request_begin_play'}
        print('PASS: independent Wide map, actual 36-actor source-derived contracts, exact 15 layout/diameters, fixed shared leaf material, one absent-map SaveMap plus explicit load; no Unreal or new create report read')
    else:
        phase, output = os.environ['DY_CANOPY_MAP_PHASE'], Path(os.environ['DY_CANOPY_MAP_OUT'])
        req(phase in ('create', 'verify') and output.is_absolute() and output.parent.is_dir() and output.name == 'RESULT.json'
            and output.resolve().is_relative_to(AUDIT.resolve()) and not output.exists(), 'Bounded phase and fresh report')
        R.update(phase=phase, map=MAP, source=SOURCE)
        try:
            run(phase, output)
        except Exception:
            R['error'] = traceback.format_exc()
        with output.open('x', encoding='utf-8') as stream:
            json.dump(R, stream, ensure_ascii=False, indent=2)
        req(R['success'], 'Canopy map operation failed; preserve evidence, no automatic save or restoration')
