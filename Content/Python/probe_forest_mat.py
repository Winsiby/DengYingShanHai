# -*- coding: utf-8 -*-
import json, os, unreal, traceback
REPORT = r"D:\灯影山海\Saved\Audit-2026-10-23-Performance\forest-material-probe.json"
LEVEL = "/Game/DengYingShanHai/Maps/L_DY_Main"
out = {}
try:
    les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    les.load_level(LEVEL)
    forest = None
    for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors():
        if a.get_actor_label() == "M3_RuntimeForest":
            forest = a
    out["class"] = forest.get_class().get_name()
    mi = unreal.EditorAssetLibrary.load_asset("/Game/DengYingShanHai/Dev/ForestArt/Materials/MI_DY_ForestCanopyInk")
    out["mi_path"] = mi.get_path_name() if mi else None
    # immediate set/read
    forest.set_editor_property("canopy_material", mi)
    out["read_after_set"] = str(forest.get_editor_property("canopy_material"))
    # branch mesh slots
    for prop in ("branch_mesh", "canopy_mesh"):
        mesh = forest.get_editor_property(prop)
        out[prop] = mesh.get_path_name() if mesh else None
        if mesh:
            mats = []
            for i in range(len(mesh.get_editor_property("static_materials"))):
                m = mesh.get_editor_property("static_materials")[i]
                mi2 = m.get_editor_property("material_interface")
                mats.append(mi2.get_path_name() if mi2 else None)
            out[prop + "_slots"] = mats
    # branch materials on existing components
    comps = forest.get_editor_property("canopy_components") if hasattr(forest, "canopy_components") else None
    out["has_canopy_components_attr"] = comps is not None
    # try material library on mesh
    bm = forest.get_editor_property("branch_mesh")
    if bm:
        try:
            out["branch_mat0"] = str(unreal.MaterialEditingLibrary.get_material_instance_parent(bm))
        except Exception as e:
            out["branch_mat0_err"] = str(e)
    out["ok"] = True
except Exception:
    out["ok"] = False
    out["errors"] = traceback.format_exc()
finally:
    os.makedirs(os.path.dirname(REPORT), exist_ok=True)
    json.dump(out, open(REPORT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("PROBE_DONE " + json.dumps({"ok": out.get("ok")}))
    unreal.SystemLibrary.quit_editor()
