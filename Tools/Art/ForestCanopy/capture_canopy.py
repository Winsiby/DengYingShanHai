"""Observe the separate leafed-canopy Dev candidate map's real three-act -> contact -> forest Blueprint.

Dev PIE fixture only: turn on this PIE Director's auto-start, then supply the
unchanged Definition targets through public controls. Never drive Staff, cue,
contact, forest growth or tokens. QA SceneCapture never owns player POV.
"""
import ast
import hashlib
import json
import math
import os
from pathlib import Path
import struct
import sys
import time
import traceback
import zlib

ROOT = Path('D:/灯影山海')
AUDIT = ROOT / 'Saved/Audit-2026-10-14-ArtAppearance'
MAP = '/Game/DengYingShanHai/Dev/ForestCanopy/Maps/LV_ForestCanopyLab'
FOREST_BP = '/Game/DengYingShanHai/Dev/ForestCanopy/Presentation/BP_DYForestCanopy_Leafed'
FOREST_MESH = '/Game/DengYingShanHai/Dev/ForestCanopy/Meshes/SM_DY_ForestBranch_Leafed'
LEAF = '/Game/DengYingShanHai/Dev/ForestCanopy/Materials/M_DY_ForestLeaf'
MATERIAL = '/Game/DengYingShanHai/Dev/FramePostAsset/Materials/MI_DY_FramePost_Wood'
OLD_FOREST = '/Game/DengYingShanHai/Dev/M3/Forest/BP_DYForestPresentation_Dev'
PNG_HELPER = Path('C:/Users/lenovo/Documents/ChatGPT/数媒游戏开发 2/ArtIntegration-20261014/StageComposition/capture_composition.py')
PNG_HELPER_SHA = '52EDF7FD7D39E3ACF631DCDDF80A4C9B23B8EC279BA49DF31B0CCA00585EDA98'
SIZE = 1536


def req(value, message):
    if not value:
        raise RuntimeError(message)
    return value


def sha(file):
    return hashlib.sha256(Path(file).read_bytes()).hexdigest().upper()


def vec(value):
    return [value.x, value.y, value.z]


def path(value):
    return value.get_path_name() if value else None


def tf(value):
    return dict(location=vec(value.translation), scale=vec(value.scale3d),
                rotation=[value.rotation.x, value.rotation.y, value.rotation.z, value.rotation.w])


def same_qa_frame(actual, expected):
    # Restoring an Actor transform can renormalize the quaternion by roundoff.
    # This is only a QA camera comparison, never a gameplay/projection tolerance.
    return (max(abs(a-b) for a,b in zip(actual['location'], expected['location'])) <= 1e-7
        and max(abs(a-b) for a,b in zip(actual['scale'], expected['scale'])) <= 1e-10
        and min(max(abs(a-sign*b) for a,b in zip(actual['rotation'], expected['rotation']))
                for sign in (-1, 1)) <= 1e-10)


def layout(actor):
    return [dict(parent=int(b.parent_index), start=[b.start_screen_offset.x, b.start_screen_offset.y],
                 end=[b.end_screen_offset.x, b.end_screen_offset.y], diameter=b.diameter_world,
                 begin=b.growth_begin, end_progress=b.growth_end) for b in actor.get_editor_property('branch_layout')]


def png_readers():
    req(sha(PNG_HELPER) == PNG_HELPER_SHA, 'Exact reviewed safe PNG helper source-file SHA')
    tree = ast.parse(PNG_HELPER.read_text(encoding='utf-8-sig'))
    functions = [node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name in ('rgb_bytes', 'png_integrity')]
    req(len(functions) == 2, 'Only two pure PNG readers; no source capture main')
    scope = dict(req=req, hashlib=hashlib, struct=struct, zlib=zlib)
    exec(compile(ast.Module(body=functions, type_ignores=[]), str(PNG_HELPER), 'exec'), scope)
    return scope['png_integrity'], scope['rgb_bytes']


def run():
    factor = float(os.environ.get('DY_CANOPY_DIAMETER_FACTOR', '1'))
    req(factor in (1.0, 2.4), 'Only unchanged authoring or explicit 2.4x diameter diagnostic')
    out = Path(os.environ['DY_FOREST_CAPTURE_OUT'])
    req(out.is_absolute() and out.is_dir() and out.resolve().is_relative_to(AUDIT.resolve())
        and not (out / 'RESULT.json').exists(), 'Fresh existing bounded audit folder')
    validate_png, rgb = png_readers()
    import unreal
    req(Path(os.path.realpath(unreal.SystemLibrary.get_project_directory())) == ROOT.resolve(), 'Exact project')
    levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    editor = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
    statics = unreal.get_default_object(unreal.GameplayStatics.static_class())
    report = dict(success=False, saved=[], captures=[], timeline=[], gameplay_acceptance=False,
                  art_acceptance=False, packaged=False, manual_menu_start_tested=False,
                  temporary_pie_auto_start=True, cue_driven_by_python=False,
                  player_pov_changed=False, fixture_only=True,
                  diameter_factor=factor, diameter_override_saved=False,
                  limitations=['Diagnostic square images including actual emerging branches and oblique geometry, not viewport/UI or full player acceptance',
                               'PIE Director auto-start and original public control values are fixtures; optional diameter comparison is editor-RAM-only before PIE and explicitly recorded',
                               'Whole-main-light visibility AB is not an isolated forest-shadow pixel mask'])
    state = dict(phase='start', frames=0, callback=None, deadline=time.monotonic() + 180,
                 error=None, resolve_delegate=None, first=False, mid=False, last_act=-1, grid=False, growth_frames=set())

    def dirty():
        return [path(package) for package in list(unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages())
                + list(unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages())]

    def hashes():
        return {package: sha(ROOT / 'Content' / (package[6:] + ('.umap' if package == MAP else '.uasset')))
                for package in (MAP, FOREST_BP, FOREST_MESH, MATERIAL, LEAF, OLD_FOREST)}

    def pov():
        manager, pc = state['manager'], state['pc']
        rotation = manager.get_camera_rotation()
        return dict(controller=path(pc), target=path(pc.get_view_target()), manager=path(manager),
                    location=vec(manager.get_camera_location()), rotation=[rotation.pitch, rotation.yaw, rotation.roll],
                    fov=manager.get_fov_angle(), pawn=path(unreal.GameplayStatics.get_player_pawn(state['world'], 0)))

    def unchanged_pov():
        req(pov() == state['pov'], 'Actual player camera manager/view target/POV unchanged')

    def sample():
        director, stage, forest = state['director'], state['stage'], state['forest']
        sequence, resolved = director.get_act_sequence_snapshot(), director.get_resolved_puzzle_snapshot()
        contact, geometry = stage.get_staff_contact_presentation_snapshot(), forest.get_forest_geometry_sample()
        staff = state['puppet'].get_staff_geometry_snapshot()
        components = list(forest.get_branch_mesh_components())
        key = state['key']
        return dict(game_seconds=unreal.GameplayStatics.get_time_seconds(state['world']),
            act=int(sequence.act_index), phase=str(sequence.phase), puzzle=str(director.get_current_puzzle_id()),
            resolved=bool(resolved.is_resolved), token=resolved.token.to_string(),
            token_current=director.is_resolved_token_current(resolved.token),
            cue={name: bool(stage.get_editor_property(name)) for name in ('CueOwned', 'Dropping', 'Growing', 'Completed', 'Ended')},
            contact=bool(contact.has_contact), contact_token=contact.token.to_string(),
            contact_world=vec(contact.contact_world_position), forest_session=forest.has_forest_session(),
            geometry_status=str(geometry.status), root=vec(geometry.physical_root), shadow_root=vec(geometry.shadow_root),
            portions=[b.portion for b in geometry.branches], visible=[bool(b.visible) for b in geometry.branches],
            branch_bounds=[dict(min=[b.projected_min.x, b.projected_min.y], max=[b.projected_max.x, b.projected_max.y]) for b in geometry.branches],
            staff_A=vec(staff.get_editor_property('EndAWorld')), staff_B=vec(staff.get_editor_property('EndBWorld')),
            staff_transform=tf(staff.get_editor_property('ComponentTransform')),
            lamp_transform=tf(state['lamp'].get_actor_transform()), puppet_transform=tf(state['puppet'].get_actor_transform()),
            branch_components=[dict(path=path(c), mesh=path(c.get_editor_property('static_mesh')), material=path(c.get_material(0)),
                materials=[path(c.get_material(i)) for i in range(2)],
                transform=tf(c.get_world_transform()), visible=bool(c.get_editor_property('visible')), hidden=bool(c.get_editor_property('hidden_in_game')),
                casts_shadow=bool(c.get_editor_property('cast_shadow')), collision=str(c.get_collision_enabled())) for c in components],
            main_light=dict(visible=bool(key.get_editor_property('visible')), world=tf(key.get_world_transform()),
                mobility=str(key.get_editor_property('mobility')), casts_shadow=bool(key.get_editor_property('cast_shadows')),
                intensity=float(key.get_editor_property('intensity')), units=str(key.get_editor_property('intensity_units')),
                attenuation=float(key.get_editor_property('attenuation_radius')), source_radius=float(key.get_editor_property('source_radius'))))

    def geometry_grid():
        forest = state['forest']
        contact = state['stage'].get_staff_contact_presentation_snapshot()
        req(contact.has_contact and state['director'].is_resolved_token_current(contact.token),
            'Geometry probe uses actual accepted contact/current token; no invented identity')
        mesh = forest.get_editor_property('branch_mesh')
        bounds = mesh.get_bounds()
        low, high = bounds.origin - bounds.box_extent, bounds.origin + bounds.box_extent
        definitions = forest.get_editor_property('branch_layout')
        progresses = {0.0, 1.0}
        for branch in definitions:
            begin, end = branch.growth_begin, branch.growth_end
            for local in (0.0, 1e-7, .01, .1, .5, 1.0):
                progresses.add(begin + (end - begin) * local)
        rows = []
        for progress in sorted(progresses):
            result = unreal.DYForestGeometryLibrary.sample_forest_geometry(contact, definitions, progress, low, high)
            req(result.status == unreal.DYForestGeometryStatus.VALID and len(result.branches) == 15,
                'Every branch boundary/emergence/1/10/50/100-percent pure sample has valid full eight-corner envelope')
            identity = dict(progress=progress, sampled_token=result.contact_token.to_string(),
                accepted_token=contact.token.to_string(), wrapper_equality=bool(result.contact_token == contact.token),
                physical_root=vec(result.physical_root), actual_A=vec(contact.projection.staff.end_a_world),
                shadow_root=vec(result.shadow_root), accepted_contact=vec(contact.contact_world_position))
            report.setdefault('geometry_identity_observations', []).append(identity)
            req(identity['sampled_token'] == identity['accepted_token'], 'Exact GUID value string, not Python wrapper identity')
            req(max(abs(a-b) for a,b in zip(identity['physical_root'], identity['actual_A'])) < 1e-7,
                'Pure sample physical root is actual accepted A')
            req(max(abs(a-b) for a,b in zip(identity['shadow_root'], identity['accepted_contact'])) < 1e-7,
                'Pure sample screen root is actual accepted contact')
            maximum = 0.0
            for branch in result.branches:
                if branch.visible:
                    a = unreal.MathLibrary.transform_location(branch.mesh_world_transform, unreal.Vector(bounds.origin.x, bounds.origin.y, low.z))
                    b = unreal.MathLibrary.transform_location(branch.mesh_world_transform, unreal.Vector(bounds.origin.x, bounds.origin.y, high.z))
                    error = max(abs(x-y) for x,y in zip(vec(a)+vec(b), vec(branch.start_world)+vec(branch.end_world)))
                    req(error < 1e-7, 'Actual native transform minZ/maxZ axis endpoints remain on authored start/end')
                    maximum = max(maximum, error)
            rows.append(dict(progress=progress, portions=[b.portion for b in result.branches],
                             visible=[bool(b.visible) for b in result.branches], endpoint_max_error_cm=maximum))
        report['geometry_grid'] = dict(actual_contact_token=contact.token.to_string(),
            bounds=dict(min=vec(low), max=vec(high)), count=len(rows), samples=rows,
            pure_observation_only=True, applied_to_runtime=False)
        state['grid'] = True

    def export(name):
        unchanged_pov()
        forest, cdo = state['forest'], state['cdo']
        req(layout(forest) == state['layout'] and layout(cdo) == state['original_layout']
            and not cdo.has_forest_session() and not cdo.get_branch_mesh_components(), 'Actual tested layout and original saved defaults remain separate/unchanged')
        capture = state['capture']
        req(same_qa_frame(tf(capture.get_world_transform()), state['capture_transform'])
            and capture.get_editor_property('fov_angle') == 70.0, 'One fixed QA capture framing across all four images')
        measured = sample()
        for component in measured['branch_components']:
            req(component['materials'] == [MATERIAL + '.' + MATERIAL.rsplit('/', 1)[1], LEAF + '.' + LEAF.rsplit('/', 1)[1]],
                'Actual native dynamic component retains wood slot0 and leaf slot1')
        capture.capture_scene()
        file = out / (name + '.png')
        req(not file.exists(), 'Never overwrite evidence')
        unreal.ImageWriteBlueprintLibrary.export_to_disk(capture.get_editor_property('texture_target'), str(file),
            unreal.ImageWriteOptions(format=unreal.DesiredImageFormat.PNG, compression_quality=100, overwrite_file=False, async_=False))
        info = validate_png(file.read_bytes())
        req([info['width'], info['height']] == [SIZE, SIZE], 'Actual image dimensions and CRC/IEND/no-tail validation')
        req(sample() == measured, 'No world/geometry tick during synchronous native capture/export')
        report['captures'].append(dict(name=name, path=str(file), png=info, actual=measured,
            camera_transform=tf(capture.get_world_transform()), requested_fixed_frame=state['capture_transform'],
            fov=70.0, player_pov=pov()))
        return file

    def export_oblique():
        unchanged_pov()
        actor, capture = state['capture_actor'], state['capture']
        original = state['capture_original_transform']
        before = sample()
        try:
            location, target = unreal.Vector(180, -260, 290), unreal.Vector(600, 30, 285)
            actor.set_actor_location(location, False, False)
            actor.set_actor_rotation(unreal.MathLibrary.find_look_at_rotation(location, target), False)
            capture.capture_scene()
            file = out / '05_ActualForestComplete_Oblique.png'
            req(not file.exists(), 'Fresh oblique evidence')
            unreal.ImageWriteBlueprintLibrary.export_to_disk(capture.get_editor_property('texture_target'), str(file),
                unreal.ImageWriteOptions(format=unreal.DesiredImageFormat.PNG, compression_quality=100, overwrite_file=False, async_=False))
            info = validate_png(file.read_bytes())
            req([info['width'], info['height']] == [SIZE, SIZE] and sample() == before,
                'Oblique capture observes same completed causal geometry synchronously')
            report['captures'].append(dict(name='05_ActualForestComplete_Oblique', path=str(file), png=info,
                actual=before, camera_transform=tf(capture.get_world_transform()), fov=70.0, player_pov=pov()))
        finally:
            actor.set_actor_transform(original, False, False)
        report['qa_frame_restoration'] = dict(actual=tf(capture.get_world_transform()), expected=state['capture_transform'],
            location_tolerance_cm=1e-7, scale_and_quaternion_tolerance=1e-10, gameplay_tolerance_changed=False)
        req(same_qa_frame(tf(capture.get_world_transform()), state['capture_transform']), 'Restore QA framing within recorded numerical roundoff; player POV never owned')
        unchanged_pov()

    def on_resolved(puzzle_id, result):
        try:
            if state.get('director') is None or state['director'].get_act_sequence_snapshot().act_index != 2:
                return
            req(not state['first'], 'One actual third-act Resolve notification')
            actual = sample()
            req(actual['resolved'] and actual['token_current'] and not actual['contact'] and not actual['forest_session']
                and not actual['branch_components'], 'Actual native third-act Resolve before contact/forest')
            state['resolve_token'] = actual['token']
            state['resolve_A'] = actual['staff_A']
            export('01_ActualResolve_BeforeContact')
            state['first'] = True
            report['timeline'].append(dict(event='P03ActualResolveObserved', puzzle=str(puzzle_id), actual=actual))
        except Exception:
            state['error'] = traceback.format_exc()

    def setup():
        all_actors = list(unreal.GameplayStatics.get_all_actors_of_class(state['world'], unreal.Actor))
        stages = [actor for actor in all_actors if isinstance(actor, unreal.DYStagePresentation)]
        stage = req(stages[0] if len(stages) == 1 else None, 'One actual saved Stage')
        director, forest = stage.get_puzzle_director(), stage.get_forest_presentation_actor()
        req(director and forest and forest.get_class() == unreal.load_asset(FOREST_BP).generated_class()
            and forest.get_world() == stage.get_world() == state['world'], 'Map already explicitly binds the saved new forest class; no replacement/spawn fixture')
        req(director.get_evaluation_frequency_hz() == 15 and director.is_act_sequence_enabled()
            and not director.is_auto_start_on_begin_play(), 'Original manual-start 15Hz three-act contract')
        cdo = unreal.get_default_object(forest.get_class())
        original_cdo = unreal.get_default_object(unreal.load_asset(OLD_FOREST).generated_class())
        req(layout(forest) == state['tested_layout'] and layout(cdo) == layout(original_cdo) and len(layout(forest)) == 15
            and forest.get_editor_property('branch_mesh') == unreal.load_asset(FOREST_MESH)
            and forest.get_editor_property('branch_material') == unreal.load_asset(MATERIAL)
            and not forest.has_forest_session() and not forest.get_branch_mesh_components(), 'Exact art resources/tested 15 definitions; clean actual instance with declared diameter fixture')
        pc = req(unreal.GameplayStatics.get_player_controller(state['world'], 0), 'Actual local controller')
        state.update(stage=stage, director=director, forest=forest, cdo=cdo, layout=layout(forest), original_layout=layout(cdo),
            lamp=director.get_light_rig_actor(), puppet=director.get_puppet_actor(), pc=pc,
            manager=unreal.GameplayStatics.get_player_camera_manager(state['world'], 0))
        state['key'] = state['lamp'].get_editor_property('KeyLight')
        state['key_visible'] = state['key'].get_editor_property('visible')
        req(state['key_visible'] and state['key'].get_editor_property('cast_shadows'), 'Original real main shadow light is on')
        state['pov'] = pov()
        transform = unreal.Transform()
        actor = req(statics.call_method('BeginDeferredActorSpawnFromClass', args=(state['world'], unreal.SceneCapture2D, transform,
            unreal.SpawnActorCollisionHandlingMethod.ALWAYS_SPAWN, None, unreal.SpawnActorScaleMethod.MULTIPLY_WITH_ROOT)), 'Only one transient QA SceneCapture actor')
        req(statics.call_method('FinishSpawningActor', args=(actor, transform, unreal.SpawnActorScaleMethod.MULTIPLY_WITH_ROOT)) == actor, 'QA capture spawned')
        location, target = unreal.Vector(100, -430, 300), unreal.Vector(750, 0, 310)
        actor.set_actor_location(location, False, False)
        actor.set_actor_rotation(unreal.MathLibrary.find_look_at_rotation(location, target), False)
        capture = actor.get_editor_property('capture_component2d')
        capture.set_editor_properties(dict(capture_every_frame=False, capture_on_movement=False, always_persist_rendering_state=True,
            post_process_blend_weight=0.0, capture_source=unreal.SceneCaptureSource.SCS_FINAL_COLOR_LDR, fov_angle=70.0))
        capture.set_editor_property('texture_target', unreal.RenderingLibrary.create_render_target2d(state['world'], SIZE, SIZE,
            unreal.TextureRenderTargetFormat.RTF_RGBA8, unreal.LinearColor(0, 0, 0, 1), False, False))
        state.update(capture=capture, capture_actor=actor, capture_transform=tf(capture.get_world_transform()),
                     capture_original_transform=actor.get_actor_transform())
        report.update(pie_world=path(state['world']), stage_class=path(stage.get_class()), director=path(director),
            forest_class=path(forest.get_class()), actual_layout=state['layout'], initial_player_pov=state['pov'],
            world_pp=[str(a.get_editor_property('settings')) for a in all_actors if isinstance(a, unreal.PostProcessVolume)])
        code = ROOT / 'Source/DengYingShanHai/Private/Puzzles/DYPuzzleDirector.cpp'
        guard = 'if (!bAutoStartOnBeginPlay && IsActSequenceEnabled()\n\t\t&& CurrentActIndex == INDEX_NONE && !bAcceptingManualStart) { return; }'
        req(code.read_text(encoding='utf-8-sig').count(guard) == 1, 'Actual current source contains the manual-start guard')
        director.start_current_puzzle()
        req(director.get_act_sequence_snapshot().act_index == -1 and not director.get_resolved_puzzle_snapshot().is_resolved,
            'Actual guarded public start is inert before the explicit PIE-only fixture opt-in')
        report['guard_probe'] = dict(source_sha256=sha(code), inactive_start_rejected=True,
                                      controller_panel=str(pc.get_entry_panel()))
        delegate = director.get_editor_property('on_puzzle_resolved')
        delegate.add_callable(on_resolved)
        state['resolve_delegate'] = delegate
        director.set_editor_property('bAutoStartOnBeginPlay', True)
        req(director.is_auto_start_on_begin_play(), 'Only actual PIE Director gets temporary auto-start')
        director.start_current_puzzle()
        req(director.get_act_sequence_snapshot().act_index == 0, 'Real first act starts; never skip to P03')

    def finish():
        if state['callback'] is not None:
            unreal.unregister_slate_post_tick_callback(state['callback'])
            state['callback'] = None
        report.update(success=not bool(state['error']), error=state['error'], actual_pie_ended=not bool(editor.get_game_world()))
        with (out / 'RESULT.json').open('x', encoding='utf-8') as stream:
            json.dump(report, stream, ensure_ascii=False, indent=2)
        unreal.EditorPythonScripting.set_keep_python_script_alive(False)

    def teardown():
        if state.get('resolve_delegate') is not None:
            state['resolve_delegate'].remove_callable(on_resolved)
            state['resolve_delegate'] = None
        if state.get('key') and unreal.SystemLibrary.is_valid(state['key']):
            state['key'].set_visibility(state['key_visible'], False)
        if state.get('capture') and unreal.SystemLibrary.is_valid(state['capture']):
            state['capture'].set_editor_property('texture_target', None)
        levels.editor_request_end_play()
        state.update(phase='wait_end', deadline=time.monotonic() + 30)

    def tick(delta):
        try:
            req(time.monotonic() < state['deadline'], 'Bounded diagnostic/EndPIE deadline')
            if state['error'] and state['phase'] != 'wait_end':
                teardown()
                return
            phase = state['phase']
            if phase == 'start':
                req(not editor.get_game_world() and not dirty(), 'No live PIE or unsaved editor state')
                req('nullrhi' not in unreal.SystemLibrary.get_command_line().lower(), 'Actual full-RHI rendering, not NullRHI')
                state['hashes'] = hashes()
                req(levels.load_level(MAP) and not dirty(), 'Read exact saved art map without edits')
                authored = [a for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
                            if isinstance(a, unreal.DYForestPresentationActor)]
                req(len(authored) == 1 and authored[0].get_class() == unreal.load_asset(FOREST_BP).generated_class(),
                    'One exact editor-only fixture target before PIE, not a runtime session/component replacement')
                fixture = authored[0]
                original_rows = layout(fixture)
                if factor != 1:
                    values = []
                    for old in fixture.get_editor_property('branch_layout'):
                        value = unreal.DYForestBranchDefinition()
                        value.set_editor_properties(dict(parent_index=old.parent_index,
                            start_screen_offset=old.start_screen_offset, end_screen_offset=old.end_screen_offset,
                            diameter_world=old.diameter_world*factor, growth_begin=old.growth_begin, growth_end=old.growth_end))
                        values.append(value)
                    fixture.set_editor_property('branch_layout', values, notify_mode=unreal.PropertyAccessChangeNotifyMode.NEVER)
                    req(unreal.DYForestGeometryLibrary.is_forest_layout_valid(values), 'Only scaled physical diameters; original topology and timing remain valid')
                expected_rows = [dict(row, diameter=row['diameter']*factor) for row in original_rows]
                req(layout(fixture) == expected_rows
                    and layout(unreal.get_default_object(fixture.get_class())) == original_rows,
                    'Exact sole authoring delta is diameter; no saved CDO change')
                state['tested_layout'] = expected_rows
                report['editor_only_diameter_fixture'] = dict(factor=factor, original=original_rows, tested=expected_rows,
                    before_begin_play=True, applied_to_live_components=False, saved=False)
                levels.editor_request_begin_play()
                state['phase'] = 'wait_world'
            elif phase == 'wait_world':
                world = editor.get_game_world()
                if world and unreal.GameplayStatics.get_game_state(world) and unreal.GameplayStatics.get_game_state(world).has_begun_play():
                    req('UEDPIE_' in path(world) and levels.is_in_play_in_editor(), 'Actual begun-play PIE world')
                    state.update(world=world, phase='settle', frames=0)
            elif phase == 'settle':
                pawn = unreal.GameplayStatics.get_player_pawn(state['world'], 0)
                resting = bool(pawn and max(abs(v) for v in vec(pawn.get_velocity())) < .01)
                state['frames'] = state['frames'] + 1 if resting else 0
                if state['frames'] >= 30:
                    setup()
                    state['phase'] = 'observe'
            elif phase == 'observe':
                unchanged_pov()
                state['capture'].capture_scene()
                director = state['director']
                sequence = director.get_act_sequence_snapshot()
                if sequence.phase == unreal.DYActSequencePhase.PLAYING and sequence.act_index != state['last_act']:
                    definition = director.get_editor_property('puzzle_definition')
                    for field, actor, component in (('light_position', state['lamp'], 'LightControl'), ('puppet_position', state['puppet'], 'PuppetControl')):
                        condition = definition.get_editor_property(field)
                        if condition.get_editor_property('enabled'):
                            actor.get_editor_property(component).set_normalized_value(condition.get_editor_property('target'))
                    state['last_act'] = sequence.act_index
                    report['timeline'].append(dict(event='OriginalTargetsSupplied', act=sequence.act_index, puzzle=str(director.get_current_puzzle_id()),
                        definition=path(definition), hold_seconds=definition.get_editor_property('required_hold_seconds'), evaluation_hz=director.get_evaluation_frequency_hz()))
                forest = state['forest']
                if forest.has_forest_session():
                    if not state['grid']:
                        geometry_grid()
                    actual = sample()
                    growing = [p for p in actual['portions'][1:] if 0 < p < 1]
                    for key, threshold in (('Early', .1), ('Middle', .5)):
                        if key not in state['growth_frames'] and growing and max(growing) >= threshold:
                            export('02_' + key + '_ActualNonRootGrowth')
                            state['growth_frames'].add(key)
                    upper = [p for p in actual['portions'][5:] if .15 <= p <= .85]
                    if upper and 'Upper' not in state['growth_frames']:
                        export('02_UpperForest_ActualGrowth')
                        state['growth_frames'].add('Upper')
                    req(state['first'] and actual['contact'] and actual['contact_token'] == state['resolve_token'] == actual['token']
                        and actual['token_current'] and len(actual['branch_components']) == len(actual['portions']) == 15,
                        'Real third-act Resolve token -> accepted actual contact -> native 15-branch session')
                    resolved = state['stage'].get_resolved_staff_presentation_snapshot()
                    req(resolved.has_snapshot and max(abs(a - b) for a, b in zip(vec(resolved.projection.staff.end_a_world), state['resolve_A'])) < 1e-5,
                        'Resolve image really predates Staff displacement, not a substituted pose')
                    if not state['mid'] and any(actual['visible']) and any(portion < 1 for portion in actual['portions']):
                        export('02_ActualContact_Growing')
                        state['mid'] = True
                    if actual['cue']['Completed'] and sequence.phase == unreal.DYActSequencePhase.COMPLETE:
                        req(state['mid'] and all(portion == 1 for portion in actual['portions']), 'All actual branches complete after a measured growth state')
                        state.update(phase='final_settle', frames=0)
            elif phase in ('final_settle', 'oblique_settle', 'off_settle'):
                unchanged_pov()
                state['capture'].capture_scene()
                state['frames'] += 1
                if state['frames'] >= 45:
                    if phase == 'final_settle':
                        state['on_image'] = export('03_ActualForestComplete_MainOn')
                        state['on_sample'] = sample()
                        actor = state['capture_actor']
                        location, target = unreal.Vector(180, -260, 290), unreal.Vector(600, 30, 285)
                        actor.set_actor_location(location, False, False)
                        actor.set_actor_rotation(unreal.MathLibrary.find_look_at_rotation(location, target), False)
                        state.update(phase='oblique_settle', frames=0)
                    elif phase == 'oblique_settle':
                        export_oblique()
                        state['key'].set_visibility(False, False)
                        state.update(phase='off_settle', frames=0)
                    else:
                        off = export('04_ActualForestComplete_MainOff')
                        now, before = sample(), dict(state['on_sample'])
                        # Game clock and the deliberately toggled main visibility are not geometry.
                        for value in (now, before):
                            value.pop('game_seconds')
                            value['main_light'] = dict(value['main_light'])
                            value['main_light'].pop('visible')
                        req(now == before, 'Main light AB has identical completed causal geometry, branches and framing')
                        a, b = rgb(state['on_image'].read_bytes()), rgb(off.read_bytes())
                        changed = sum(max(abs(x - y) for x, y in zip(a[i:i + 3], b[i:i + 3])) > 8 for i in range(0, len(a), 3))
                        req(changed > 0, 'Actual decoded rendered pixels respond to real main light visibility')
                        report['light_ab'] = dict(changed_pixels_over_8=changed, total_pixels=SIZE * SIZE,
                            same_completed_geometry=True, whole_main_light_not_shadow_only_mask=True)
                        teardown()
            elif phase == 'wait_end' and not editor.get_game_world():
                req(not levels.is_in_play_in_editor() and (not dirty() or factor != 1 and dirty() == [MAP]),
                    'Actual EndPIE; only our explicitly unsaved diameter-fixture map may be dirty')
                req(hashes() == state['hashes'] and sha(PNG_HELPER) == PNG_HELPER_SHA, 'Saved input assets/map and source helper unchanged')
                req((len(report['captures']) >= 5 and state['grid']) or state['error'], 'Core causal frames, oblique frame and pure geometry grid required for success')
                report['input_hashes'] = state['hashes']
                finish()
        except Exception:
            error = traceback.format_exc()
            if state['error'] or state['phase'] == 'wait_end':
                state['error'] = (state['error'] or '') + '\n' + error
                finish()
            else:
                state['error'] = error
                if editor.get_game_world():
                    teardown()
                else:
                    finish()

    unreal.EditorPythonScripting.set_keep_python_script_alive(True)
    state['callback'] = unreal.register_slate_post_tick_callback(tick)


if __name__ == '__main__':
    if '--self-check' in sys.argv:
        validate, decode = png_readers()
        tree = ast.parse(Path(__file__).read_text(encoding='utf-8'))
        calls = {node.func.attr for node in ast.walk(tree) if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)}
        assert not calls & {'save_current_level', 'save_loaded_asset', 'begin_forest_presentation', 'try_accept_staff_contact',
                            'set_forest_normalized_growth', 'set_view_target', 'set_view_target_with_blend', 'evaluate_puzzle_now'}
        assert 'export_to_disk' in calls and 'add_callable' in calls and 'remove_callable' in calls
        assert MAP.startswith('/Game/DengYingShanHai/Dev/') and FOREST_BP != OLD_FOREST
        print('PASS: leafed candidate; exact PNG reader source hash and definitions-only reuse, no save/contact/growth/POV/15Hz override APIs; no Unreal invoked')
    else:
        run()
