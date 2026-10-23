import unreal, json, os
OUT = r"D:/灯影山海/Saved/Audit-2026-10-23-Performance"
r = {"ok": False, "errors": []}
p = os.path.join(OUT, "forest-actor-probe.json")
def write(o):
    with open(p, "w", encoding="utf-8") as f:
        json.dump(o, f, ensure_ascii=False, indent=1)
write(r)
try:
    les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    les.load_level("/Game/DengYingShanHai/Maps/L_DY_Main")
    actors = eas.get_all_level_actors()
    forest = None
    for a in actors:
        if str(a.get_actor_label()) == "M3_RuntimeForest":
            forest = a
            break
    r["class"] = str(forest.get_class().get_name()) if forest else None
    if forest:
        for name in ("branch_mesh", "branch_material", "canopy_mesh", "canopy_world_scale"):
            try:
                v = forest.get_editor_property(name)
                r[name] = str(v)
            except Exception as e:
                r["errors"].append(name + ": " + str(e))
        try:
            layout = forest.get_editor_property("branch_layout")
            r["branch_layout_count"] = len(layout)
            items = []
            for b in layout:
                try:
                    items.append({"yaw": round(float(b.get_editor_property("yaw_degrees")),1),
                                  "length": round(float(b.get_editor_property("length")),1),
                                  "radius": round(float(b.get_editor_property("radius")),2),
                                  "pitch": round(float(b.get_editor_property("pitch_degrees")),1),
                                  "spread": round(float(b.get_editor_property("spread")),2)})
                except Exception as e:
                    items.append({"err": str(e)})
            r["branch_layout"] = items
        except Exception as e:
            r["errors"].append("layout: " + str(e))
        try:
            r["canopy_branches"] = [int(x) for x in forest.get_editor_property("canopy_branches")]
        except Exception as e:
            r["errors"].append("canopy: " + str(e))
    r["ok"] = forest is not None
except Exception as e:
    r["errors"].append("FATAL " + str(e))
finally:
    write(r)
    print("FOREST_ACTOR " + json.dumps(r, ensure_ascii=False)[:1800])
    unreal.SystemLibrary.quit_editor()
