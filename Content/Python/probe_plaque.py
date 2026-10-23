# -*- coding: utf-8 -*-
import json, traceback, unreal
out = {"error": None}
try:
    unreal.EditorLoadingAndSavingUtils.load_map("/Game/DengYingShanHai/Maps/L_DY_Main")
    ACT = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    for a in ACT.get_all_level_actors():
        if a.get_actor_label() == "ART_ZhuRiTitleGlyph":
            s = a.get_actor_scale3d(); r = a.get_actor_rotation()
            c, e = a.get_actor_bounds(False)
            out["plane"] = dict(scale=[round(s.x,3), round(s.y,3), round(s.z,3)],
                                rot=[round(r.pitch,1), round(r.yaw,1), round(r.roll,1)],
                                center=[round(c.x,1), round(c.y,1), round(c.z,1)],
                                extent=[round(e.x,1), round(e.y,1), round(e.z,1)],
                                loc=[round(v,1) for v in (a.get_actor_location().x, a.get_actor_location().y, a.get_actor_location().z)])
            for comp in a.get_components_by_class(unreal.StaticMeshComponent):
                out["mesh"] = comp.get_editor_property("static_mesh").get_path_name() if comp.get_editor_property("static_mesh") else None
                out["materials"] = [m.get_path_name() for m in comp.get_materials()]
            out["tags"] = [str(t) for t in a.get_editor_property("tags")]
except Exception:
    out["error"] = traceback.format_exc()
finally:
    open("D:/灯影山海/Saved/Audit-2026-10-22-FourAct/plaque.json", "w", encoding="utf-8").write(json.dumps(out, ensure_ascii=False, indent=2))
    print("PLAQUE", json.dumps(out, ensure_ascii=False)[:700])
    unreal.SystemLibrary.quit_editor()
