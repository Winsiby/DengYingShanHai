import unreal, json
out = {"rows": []}
try:
    MAP = "/Game/DengYingShanHai/Maps/L_DY_Main"
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).load_level(MAP)
    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    h0 = unreal.SystemLibrary.capsule_trace_single(world, unreal.Vector(-2600,-210,40), unreal.Vector(-2500,-210,40),
        34.0, 88.0, unreal.TraceTypeQuery.TRACE_TYPE_QUERY1, False, [], unreal.DrawDebugTrace.NONE, True)
    print("ATTRS " + json.dumps([n for n in dir(h0) if not n.startswith("_")], ensure_ascii=False))
    print("SAMPLE " + json.dumps({"comp": str(h0.get_editor_property("component")), "loc": str(h0.get_editor_property("location"))}, ensure_ascii=False))
except Exception as e:
    print("ERR " + str(e))
finally:
    unreal.SystemLibrary.quit_editor()
