import unreal, json
MAP = "/Game/DengYingShanHai/Maps/L_DY_Main"
unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).load_level(MAP)
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
actors = eas.get_all_level_actors()
def fv(v): return [round(float(v.x),1), round(float(v.y),1), round(float(v.z),1)]
rows = []
for a in actors:
    try:
        org, ext = a.get_actor_bounds(False)
        org = fv(org); ext = fv(ext)
    except Exception:
        continue
    comps = []
    for c in a.get_components_by_class(unreal.PrimitiveComponent):
        try:
            en = str(c.get_collision_enabled())
            pr = str(c.get_collision_profile_name())
        except Exception:
            continue
        comps.append([c.get_class().get_name(), pr, en])
    if not comps:
        continue
    rows.append({"l": a.get_actor_label(), "c": a.get_class().get_name(), "loc": fv(a.get_actor_location()),
                 "org": org, "ext": ext, "comps": comps})
out = {"actors": len(actors), "rows": rows}
with open(r"D:\灯影山海\Saved\Audit-2026-10-22-FourAct\collision-audit.json", "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
print("AUDIT2 rows=" + str(len(rows)))
unreal.SystemLibrary.quit_editor()
