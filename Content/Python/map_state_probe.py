# -*- coding: utf-8 -*-
import json, traceback, unreal
OUT = "D:/灯影山海/Saved/Audit-2026-10-23-Performance/map-state.json"
R = {"ok": False, "error": None}
try:
    les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    les.load_level("/Game/DengYingShanHai/Maps/L_DY_Main")
    ACT = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    labels = {}
    comp_cls = unreal.load_class(None, "/Script/DengYingShanHai.DYPuppetPerformanceComponent")
    for a in ACT.get_all_level_actors():
        lb = a.get_actor_label()
        if lb in ("ART_EXT_RearBase", "ART_EXT_RearBase_R", "M2_Puppet_P02_Controlled",
                  "ART_B1_Mountain_Near_B", "ART_ZhuRiTitleGlyph"):
            info = {"class": a.get_class().get_name(), "loc": [round(v,2) for v in a.get_actor_location().to_tuple()]}
            for c in a.get_components_by_class(comp_cls) if comp_cls else []:
                info["performance_data"] = bool(c.get_editor_property("performance_data"))
            for c in a.get_components_by_class(unreal.StaticMeshComponent):
                info.setdefault("profiles", []).append(c.get_collision_profile_name())
            labels[lb] = info
    R["actors"] = labels
    R["ok"] = all(k in labels for k in ("ART_EXT_RearBase", "ART_EXT_RearBase_R", "M2_Puppet_P02_Controlled"))
    R["perf_bound"] = bool(labels.get("M2_Puppet_P02_Controlled", {}).get("performance_data"))
except Exception:
    R["error"] = traceback.format_exc()
open(OUT, "w", encoding="utf-8").write(json.dumps(R, ensure_ascii=False, indent=2))
print("MAP_STATE", R["ok"], R.get("perf_bound"), (R["error"] or "")[:120])
unreal.SystemLibrary.quit_editor()
