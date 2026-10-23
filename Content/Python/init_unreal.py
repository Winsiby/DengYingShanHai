# -*- coding: utf-8 -*-
"""Dev-only helper hook for automated editor work.

Activated only by environment variables so normal editor sessions are untouched:
  DY_SCRIPT=<path.py>  execute that file once, ~4 s after the editor settles
  DY_VIEW=<index>      load L_DY_Main, hide cutaway pieces, frame a review view
                       numeric = technical check in unlit, e0/e1/e2 = exterior lit review
"""
import unreal, os

_view = os.environ.get('DY_VIEW', '')
_script = os.environ.get('DY_SCRIPT', '')

if _view or _script:
    _state = {'tick': 0, 'done': False}

    _HIDE_PREFIX = (
        'DYTheater_Roof', 'DYTheater_Beam', 'DYTheater_Rafter',
        'DYTheater_Wall_', 'DYTheater_Pilaster', 'DYTheater_FrontWall',
        'DYTheater_RearWall',
    )
    _HIDE_EXACT = (
        'DEV_LeftBoundary', 'DEV_RightBoundary', 'DEV_CameraWall',
        'DEV_InnerCornerA', 'DEV_InnerCornerB', 'DEV_LowCeiling',
        'DEV_LowCeilingPostA', 'DEV_LowCeilingPostB',
    )
    _VIEWS = {
        '0': ((2500, -2700, 2300), (200, 0, 350)),
        '1': ((2050, -150, 280), (900, 0, 620)),
        '2': ((700, 0, 420), (2100, 0, 420)),
        '3': ((-2600, -2200, 900), (-300, 0, 300)),
    }
    _VIEWS_EXT = {
        'e0': ((-4600, -210, 160), (-1800, -210, 520)),
        'e1': ((-4300, -210, 200), (-1800, -210, 1100)),
        'e2': ((-3000, 1800, 700), (-1800, -210, 420)),
        'e3': ((-4600, -210, 160), (-2600, -2100, 1400)),
    }

    def _setup_view(view):
        unreal.EditorLoadingAndSavingUtils.load_map('/Game/DengYingShanHai/Maps/L_DY_Main')
        eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
        hide_cutaway = view not in _VIEWS_EXT
        hidden = 0
        if hide_cutaway:
            for actor in eas.get_all_level_actors():
                try:
                    label = actor.get_actor_label()
                except Exception:
                    continue
                if label.startswith(_HIDE_PREFIX) or label in _HIDE_EXACT:
                    actor.set_is_temporarily_hidden_in_editor(True)
                    hidden += 1
        loc, target = _VIEWS.get(view, None) or _VIEWS_EXT.get(view) or _VIEWS['0']
        rot = unreal.MathLibrary.find_look_at_rotation(unreal.Vector(*loc), unreal.Vector(*target))
        les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
        les.set_level_viewport_camera_info(unreal.Vector(*loc), rot, '')
        try:
            world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
            if hide_cutaway:
                unreal.SystemLibrary.execute_console_command(world, 'viewmode unlit')
            else:
                unreal.SystemLibrary.execute_console_command(world, 'viewmode lit')
        except Exception as mode_exc:
            unreal.log_warning('DY_OVERVIEW viewmode failed: %s' % mode_exc)
        unreal.log('DY_OVERVIEW DONE view=%s hidden=%d loc=%s' % (view, hidden, loc))
        if view.startswith('e'):
            _state['shot'] = 0
            _state['want_shot'] = True
            unreal.register_slate_post_tick_callback(_on_shot_tick)

    def _on_shot_tick(delta_seconds):
        if not _state.get('want_shot'):
            return
        _state['shot'] = _state.get('shot', 0) + 1
        if _state['shot'] < 180:  # ~3 s for TAA/Lumen to settle
            return
        if _state['shot'] > 181:
            return
        try:
            world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
            unreal.SystemLibrary.execute_console_command(world, 'HighResShot 1')
            unreal.log('DY_SHOT requested')
        except Exception as exc:
            unreal.log_warning('DY_SHOT failed: %s' % exc)

    def _setup_script(path):
        with open(path, 'r', encoding='utf-8') as handle:
            code = handle.read()
        scope = {'__name__': '__dy_script__', '__file__': path}
        exec(compile(code, path, 'exec'), scope)
        unreal.log('DY_SCRIPT DONE %s' % path)

    def _on_tick(delta_seconds):
        if _state['done']:
            return
        _state['tick'] += 1
        if _state['tick'] < 240:
            return
        _state['done'] = True
        try:
            if _view:
                _setup_view(_view)
            if _script:
                _setup_script(_script)
        except Exception as exc:
            import traceback
            unreal.log_error('DY_HOOK FAILED: %s\n%s' % (exc, traceback.format_exc()))

    unreal.register_slate_post_tick_callback(_on_tick)