import unreal, json, os
OUT = r"D:/灯影山海/Saved/Audit-2026-10-23-Performance"
r = {"ok": False, "errors": []}
p = os.path.join(OUT, "forest-offset-bind.json")
def write(o):
    with open(p, "w", encoding="utf-8") as f:
        json.dump(o, f, ensure_ascii=False, indent=1)
write(r)
try:
    les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    les.load_level("/Game/DengYingShanHai/Maps/L_DY_Main")
    forest = None
    for a in eas.get_all_level_actors():
        if str(a.get_actor_label()) == "M3_RuntimeForest":
            forest = a
            break
    if forest is None:
        raise RuntimeError("M3_RuntimeForest not found")
    r["before"] = str(forest.get_editor_property("world_offset"))
    forest.set_editor_property("world_offset", unreal.Vector(-40.0, 0.0, 0.0))
    r["after"] = str(forest.get_editor_property("world_offset"))
    r["saved"] = bool(les.save_current_level())
    r["ok"] = r["saved"]
except Exception as e:
    r["errors"].append("FATAL " + str(e))
finally:
    write(r)
    print("FOREST_OFFSET " + json.dumps(r, ensure_ascii=False))
    unreal.SystemLibrary.quit_editor()
