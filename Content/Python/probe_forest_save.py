# -*- coding: utf-8 -*-
import json, os, unreal, traceback
REPORT = r"D:\灯影山海\Saved\Audit-2026-10-23-Performance\forest-save-probe.json"
LEVEL = "/Game/DengYingShanHai/Maps/L_DY_Main"
out = {}
try:
    les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    les.load_level(LEVEL)
    forest = None
    for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors():
        if a.get_actor_label() == "M3_RuntimeForest":
            forest = a
    mi = unreal.EditorAssetLibrary.load_asset("/Game/DengYingShanHai/Dev/ForestArt/Materials/MI_DY_ForestCanopyInk")
    out["before"] = str(forest.get_editor_property("canopy_material"))
    forest.set_editor_property("canopy_material", mi)
    out["after_set"] = str(forest.get_editor_property("canopy_material"))
    out["save"] = les.save_current_level()
    out["after_save"] = str(forest.get_editor_property("canopy_material"))
    out["scales_after_save"] = len(forest.get_editor_property("canopy_scales"))
    out["layout_after_save"] = len(forest.get_editor_property("branch_layout"))
    out["ok"] = True
except Exception:
    out["ok"] = False
    out["errors"] = traceback.format_exc()
finally:
    os.makedirs(os.path.dirname(REPORT), exist_ok=True)
    json.dump(out, open(REPORT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("SAVE_PROBE_DONE")
    unreal.SystemLibrary.quit_editor()
