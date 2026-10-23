import unreal
try:
    MAP = "/Game/DengYingShanHai/Maps/L_DY_Main"
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).load_level(MAP)
    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    print("DOC " + (unreal.SystemLibrary.capsule_trace_single.__doc__ or "")[:400])
    for cand in ("unreal.Array(unreal.Actor)", "unreal.Array(unreal.Object)", "unreal.Array(unreal.Actor())"):
        try:
            arr = eval(cand)
            hr = unreal.HitResult()
            ok = unreal.SystemLibrary.capsule_trace_single(world, unreal.Vector(-2600,-210,110), unreal.Vector(-2500,-210,110),
                34.0, 88.0, unreal.TraceTypeQuery.TRACE_TYPE_QUERY1, False, unreal.DrawDebugTrace.NONE,
                arr, unreal.LinearColor(1,0,0,1), hr, True)
            print("TRY " + cand + " -> " + str(ok) + " who=" + (hr.actor.get_actor_label() if hr.actor else "None"))
        except Exception as e:
            print("TRY " + cand + " ERR " + str(e)[:160])
except Exception as e:
    print("FATAL " + str(e))
finally:
    unreal.SystemLibrary.quit_editor()
