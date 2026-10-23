# -*- coding: utf-8 -*-
import json, unreal
LEVEL = "/Game/DengYingShanHai/Maps/L_DY_Main"
out = {"stage": [], "planes": [], "errors": []}
try:
    les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    les.load_level(LEVEL)
    eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    for a in eas.get_all_level_actors():
        cls = a.get_class().get_name()
        lbl = a.get_actor_label()
        if "StagePresentation" in cls or "StagePresentation" in lbl:
            rec = {"actor": lbl, "cls": cls}
            try:
                sp = a.get_editor_property("staff_projection_screen")
                rec["staff_projection_screen"] = sp.get_actor_label() if sp else None
            except Exception as e:
                rec["err"] = repr(e)
            out["stage"].append(rec)
    for a in eas.get_all_level_actors():
        if a.get_class().get_name() == "StaticMeshActor":
            try:
                o, e = a.get_actor_bounds(False)
                ext = [(e.x - o.x) / 2.0, (e.y - o.y) / 2.0, (e.z - o.z) / 2.0]
                if min(ext) < 6 and max(ext) > 150:
                    out["planes"].append({"name": a.get_actor_label(), "origin": [round(o.x + ext[0], 1), round(o.y + ext[1], 1), round(o.z + ext[2], 1)], "ext": [round(x, 1) for x in ext]})
            except Exception:
                pass
except Exception:
    import traceback
    out["errors"].append(traceback.format_exc())
open(r"C:\dy_build\probe_screen.json", "w", encoding="utf-8").write(json.dumps(out, ensure_ascii=False, indent=1))
print("PROBE_DONE")