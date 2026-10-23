# -*- coding: utf-8 -*-
import json, os, traceback, unreal
REPORT = r"D:\灯影山海\Saved\Audit-2026-10-23-Performance\forest-restore-run150.json"
LAYOUT = json.load(open(r"C:\dy_build\forest_layout_run150.json", encoding="utf-8"))
MI_PATH = "/Game/DengYingShanHai/Dev/ForestArt/Materials/MI_DY_ForestCanopyInk"
LEVEL = "/Game/DengYingShanHai/Maps/L_DY_Main"
BP_PATH = "/Game/DengYingShanHai/Dev/M3/Forest/BP_DYForestPresentation_Dev"
out = {"ok": False, "checks": [], "errors": []}
def ck(n, c, d=None):
    out["checks"].append({"name": n, "ok": bool(c), "detail": d})
    if not c: out["errors"].append(n)
try:
    mi = unreal.EditorAssetLibrary.load_asset(MI_PATH)
    ck("mi", mi is not None, MI_PATH)
    # recompile + resave the forest blueprint so cooked CDO matches new native class
    bp = unreal.EditorAssetLibrary.load_asset(BP_PATH)
    ck("bp", bp is not None, BP_PATH)
    try:
        unreal.BlueprintEditorLibrary.compile_blueprint(bp)
        ck("bp compile", True)
    except Exception as e:
        ck("bp compile", False, repr(e))
    ck("bp save", unreal.EditorAssetLibrary.save_loaded_asset(bp), BP_PATH)
    les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    ck("level", les.load_level(LEVEL), LEVEL)
    forest = None
    for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors():
        if a.get_actor_label() == "M3_RuntimeForest":
            forest = a; break
    ck("forest", forest is not None)
    defs = []
    for b in LAYOUT["layout"]:
        d = unreal.DYForestBranchDefinition()
        d.set_editor_property("parent_index", int(b["parent"]))
        d.set_editor_property("start_screen_offset", unreal.Vector2D(float(b["start"][0]), float(b["start"][1])))
        d.set_editor_property("end_screen_offset", unreal.Vector2D(float(b["end"][0]), float(b["end"][1])))
        d.set_editor_property("diameter_world", float(b["diam"]))
        d.set_editor_property("growth_begin", float(b["growthBegin"]))
        d.set_editor_property("growth_end", float(b["growthEnd"]))
        defs.append(d)
    ck("layout valid", unreal.DYForestGeometryLibrary.is_forest_layout_valid(defs), len(defs))
    forest.set_editor_property("branch_layout", defs)
    forest.set_editor_property("canopy_branches", [int(c["branch"]) for c in LAYOUT["canopy"]])
    forest.set_editor_property("canopy_scales", [])
    forest.set_editor_property("canopy_material", None)
    forest.set_editor_property("canopy_world_scale", 0.9)
    forest.set_editor_property("world_offset", unreal.Vector(-40.0, 0.0, 0.0))
    ck("level saved", les.save_current_level(), LEVEL)
    back = forest.get_editor_property("branch_layout")
    ck("branch count", len(back) == len(defs), [len(back), len(defs)])
    ck("canopy material default", forest.get_editor_property("canopy_material") is None)
    out["ok"] = len(out["errors"]) == 0
except Exception:
    out["errors"].append(traceback.format_exc())
finally:
    os.makedirs(os.path.dirname(REPORT), exist_ok=True)
    with open(REPORT, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print("DENSE5_DONE " + json.dumps({"ok": out["ok"], "n": len(out["checks"]), "err": out["errors"][:3]}))
    unreal.SystemLibrary.quit_editor()
