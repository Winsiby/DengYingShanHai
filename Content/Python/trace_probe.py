import unreal, json
try:
    MAP = "/Game/DengYingShanHai/Maps/L_DY_Main"
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).load_level(MAP)
    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    print("WORLD " + world.get_name())
    print("TRACE_FNS " + json.dumps([n for n in dir(unreal.SystemLibrary) if "trace" in n.lower()], ensure_ascii=False))
    hr = unreal.HitResult()
    try:
        res = unreal.SystemLibrary.capsule_trace_single(world, unreal.Vector(-6900,-210,110), unreal.Vector(-6850,-210,110), 34.0, 88.0,
            unreal.TraceTypeQuery.TRACE_TYPE_QUERY1, False, unreal.DrawDebugTrace.NONE, None, unreal.LinearColor(1,0,0,1), hr, True)
        print("CAPS " + json.dumps({"ret": str(res), "who": hr.actor.get_actor_label() if hr.actor else None, "loc": str(hr.location)}, ensure_ascii=False))
    except Exception as e:
        print("CAPS_ERR " + str(e))
    try:
        hr2 = unreal.HitResult()
        res2 = unreal.SystemLibrary.line_trace_single(world, unreal.Vector(-2600,-210,110), unreal.Vector(-2550,-210,110),
            unreal.TraceTypeQuery.TRACE_TYPE_QUERY1, False, unreal.DrawDebugTrace.NONE, None, unreal.LinearColor(1,0,0,1), hr2, True)
        print("LINE " + json.dumps({"ret": str(res2), "who": hr2.actor.get_actor_label() if hr2.actor else None}, ensure_ascii=False))
    except Exception as e:
        print("LINE_ERR " + str(e))
except Exception as e:
    print("FATAL " + str(e))
finally:
    unreal.SystemLibrary.quit_editor()
