# -*- coding: utf-8 -*-
import json, os, unreal
import traceback

REPORT = r"D:\灯影山海\Saved\Audit-2026-10-23-Performance\dense-forest-apply.json"
LAYOUT = json.load(open(r"C:\dy_build\forest_layout3.json", encoding="utf-8"))
MI_DIR = "/Game/DengYingShanHai/Dev/ForestArt/Materials"
MI_NAME = "MI_DY_ForestCanopyInk"
MI_PATH = MI_DIR + "/" + MI_NAME
PARENT = "/Game/DengYingShanHai/Dev/ForestCanopyM04/Materials/M_DY_M04_CanopyConstantPBR"
LEVEL = "/Game/DengYingShanHai/Maps/L_DY_Main"

out = {"ok": False, "checks": [], "errors": []}
def ck(name, cond, detail=None):
    out["checks"].append({"name": name, "ok": bool(cond), "detail": detail})
    if not cond:
        out["errors"].append(name)

try:
    # 1. material instance
    if unreal.EditorAssetLibrary.does_asset_exist(MI_PATH):
        mi = unreal.EditorAssetLibrary.load_asset(MI_PATH)
    else:
        parent = unreal.EditorAssetLibrary.load_asset(PARENT)
        ck("parent material", parent is not None, PARENT)
        tools = unreal.AssetToolsHelpers.get_asset_tools()
        mi = tools.create_asset(MI_NAME, MI_DIR, unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
        unreal.MaterialEditingLibrary.set_material_instance_parent(mi, parent)
    ck("mi loaded", mi is not None, MI_PATH)
    unreal.MaterialEditingLibrary.set_material_instance_vector_parameter_value(mi, "BaseColor", unreal.LinearColor(0.045, 0.058, 0.034, 1.0))
    unreal.MaterialEditingLibrary.set_material_instance_scalar_parameter_value(mi, "Roughness", 0.9)
    unreal.MaterialEditingLibrary.set_material_instance_scalar_parameter_value(mi, "Metallic", 0.0)
    unreal.MaterialEditingLibrary.update_material_instance(mi)
    ck("mi saved", unreal.EditorAssetLibrary.save_asset(MI_PATH), MI_PATH)

    # 2. level + actor
    les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    ck("level loaded", les.load_level(LEVEL), LEVEL)
    forest = None
    for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors():
        if a.get_actor_label() == "M3_RuntimeForest":
            forest = a
            break
    ck("forest actor", forest is not None, "M3_RuntimeForest")

    # 3. layout
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

    canopy_branches = [int(c["branch"]) for c in LAYOUT["canopy"]]
    canopy_scales = [float(c["scale"]) for c in LAYOUT["canopy"]]
    forest.set_editor_property("branch_layout", defs)
    forest.set_editor_property("canopy_branches", canopy_branches)
    forest.set_editor_property("canopy_scales", canopy_scales)
    forest.set_editor_property("canopy_material", mi)
    forest.set_editor_property("canopy_world_scale", 1.0)
    forest.set_editor_property("world_offset", unreal.Vector(-40.0, 0.0, 0.0))
    branch_mat = unreal.EditorAssetLibrary.load_asset("/Game/DengYingShanHai/Stage/ArtMainline/Materials/MI_DY_FramePost_Wood")
    if branch_mat is None:
        branch_mat = unreal.EditorAssetLibrary.load_asset("/Game/DengYingShanHai/Dev/ForestArt/Materials/MI_DY_FramePost_Wood")
    ck("branch material", branch_mat is not None, str(branch_mat))
    if branch_mat is not None:
        forest.set_editor_property("branch_material", branch_mat)

    ck("saved level", les.save_current_level(), LEVEL)

    # 4. read back
    back = forest.get_editor_property("branch_layout")
    ck("branch count", len(back) == len(defs), [len(back), len(defs)])
    cb = forest.get_editor_property("canopy_branches")
    cs = forest.get_editor_property("canopy_scales")
    ck("canopy count", len(cb) == len(canopy_branches), [len(cb), len(canopy_branches)])
    ck("canopy scale count", len(cs) == len(canopy_scales), [len(cs), len(canopy_scales)])
    ck("canopy material", forest.get_editor_property("canopy_material") is not None)
    ck("branch material", forest.get_editor_property("branch_material") is not None)
    out["branches"] = len(back)
    out["canopies"] = len(cb)
    out["ok"] = len(out["errors"]) == 0
except Exception as e:
    out["errors"].append(traceback.format_exc())
finally:
    os.makedirs(os.path.dirname(REPORT), exist_ok=True)
    with open(REPORT, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print("DENSE_FOREST_DONE " + json.dumps({"ok": out["ok"], "checks": len(out["checks"]), "errors": out["errors"][:3]}))
    unreal.SystemLibrary.quit_editor()
