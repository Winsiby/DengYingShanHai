import unreal, json
try:
    MAP = "/Game/DengYingShanHai/Maps/L_DY_Main"
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).load_level(MAP)
    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    h0 = unreal.SystemLibrary.capsule_trace_single(world, unreal.Vector(-2600,-210,40), unreal.Vector(-2500,-210,40),
        34.0, 88.0, unreal.TraceTypeQuery.TRACE_TYPE_QUERY1, False, [], unreal.DrawDebugTrace.NONE, True)
    t = h0.to_tuple()
    print("TUPLE " + json.dumps([str(x)[:80] for x in t], ensure_ascii=False))
    print("DICT " + json.dumps({k: str(v)[:60] for k, v in h0.to_dict().items()}, ensure_ascii=False))
except Exception as e:
    print("ERR " + str(e))
finally:
    unreal.SystemLibrary.quit_editor()
