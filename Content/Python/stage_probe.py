import unreal, json, os
out = {}
def name_of(o):
    try:
        return o.get_name() if o else None
    except Exception:
        return None
try:
    les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    les.load_level("/Game/DengYingShanHai/Maps/L_DY_Main")
    eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    actors = eas.get_all_level_actors()
    pres = []
    forest = []
    for a in actors:
        cls = a.get_class().get_name()
        if "Presentation" in cls or "Forest" in a.get_actor_label():
            entry = {"label": a.get_actor_label(), "class": cls}
            try:
                entry["forest"] = name_of(a.get_editor_property("forest_presentation_actor"))
                entry["screen"] = name_of(a.get_editor_property("staff_projection_screen"))
                entry["ground"] = name_of(a.get_editor_property("narrative_ground_line"))
                entry["director"] = name_of(a.get_editor_property("puzzle_director"))
                entry["bEnableStaffContactPresentation"] = bool(a.get_editor_property("b_enable_staff_contact_presentation"))
                entry["bEnableFiveState"] = bool(a.get_editor_property("b_enable_five_state_dev_environment"))
            except Exception as e:
                entry["err"] = str(e)[:200]
            pres.append(entry)
    out["presentations"] = pres
    out["ok"] = True
except Exception as e:
    out["ok"] = False
    out["error"] = repr(e)
os.makedirs(r"D:/灯影山海/Saved/Audit-2026-10-23-Performance", exist_ok=True)
with open(r"D:/灯影山海/Saved/Audit-2026-10-23-Performance/stage-probe.json", "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
print("STAGE_PROBE " + json.dumps(out, ensure_ascii=False)[:1500])
