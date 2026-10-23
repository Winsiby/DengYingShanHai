# -*- coding: utf-8 -*-
"""Assign the performance data asset on the placed puppet actor so the continuous show is data-driven."""
import json, traceback, unreal

DA = "/Game/DengYingShanHai/Puppets/DA_DYPuppetPerformance.DA_DYPuppetPerformance"
OUT = "D:/灯影山海/Saved/Audit-2026-10-23-Performance/perf-bind.json"
R = {"ok": False, "error": None, "puppets": []}
try:
    unreal.EditorLoadingAndSavingUtils.load_map("/Game/DengYingShanHai/Maps/L_DY_Main")
    ACT = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    data = unreal.EditorAssetLibrary.load_asset(DA)
    if data is None:
        raise RuntimeError("DA missing")
    comp_cls = unreal.load_class(None, "/Script/DengYingShanHai.DYPuppetPerformanceComponent")
    for a in ACT.get_all_level_actors():
        comps = a.get_components_by_class(comp_cls) if comp_cls else []
        for c in comps:
            before = c.get_editor_property("performance_data")
            c.set_editor_property("performance_data", data)
            after = c.get_editor_property("performance_data")
            R["puppets"].append(dict(actor=a.get_actor_label(),
                                     before=str(before) if before else None,
                                     after=str(after) if after else None))
    if not R["puppets"]:
        raise RuntimeError("no performance component placed")
    R["saved"] = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
    R["ok"] = bool(R["saved"]) and all(p["after"] for p in R["puppets"])
except Exception:
    R["error"] = traceback.format_exc()
open(OUT, "w", encoding="utf-8").write(json.dumps(R, ensure_ascii=False, indent=2))
print("PERF_BIND", R["ok"], len(R["puppets"]), (R["error"] or "")[:160])
unreal.SystemLibrary.quit_editor()
