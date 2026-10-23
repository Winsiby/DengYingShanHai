# -*- coding: utf-8 -*-
import json, traceback, unreal
EAL = unreal.EditorAssetLibrary
MEL = unreal.MaterialEditingLibrary
OUT = "D:/灯影山海/Saved/Audit-2026-10-22-FourAct/plaque-inspect.json"
out = {"near_screen": [], "material": {}, "error": None}
try:
    unreal.EditorLoadingAndSavingUtils.load_map("/Game/DengYingShanHai/Maps/L_DY_Main")
    ACT = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    for a in ACT.get_all_level_actors():
        loc = a.get_actor_location()
        if abs(loc.x - 925.0) < 420 and loc.z > 620 and abs(loc.y) < 520:
            comps = []
            try:
                comps = a.get_components_by_class(unreal.StaticMeshComponent)
            except Exception:
                comps = []
            row = dict(label=a.get_actor_label(), cls=a.get_class().get_name(),
                       loc=[round(loc.x,1), round(loc.y,1), round(loc.z,1)], meshes=[])
            for c in comps:
                sm = c.get_editor_property("static_mesh")
                mats = []
                for i in range(c.get_num_materials()):
                    m = c.get_material(i)
                    mats.append(m.get_path_name() if m else None)
                row["meshes"].append(dict(mesh=sm.get_path_name() if sm else None, materials=mats))
            out["near_screen"].append(row)
except Exception:
    out["error"] = traceback.format_exc()
finally:
    with open(OUT, "w", encoding="utf-8") as h:
        json.dump(out, h, ensure_ascii=False, indent=2)
    print("NEAR", len(out["near_screen"]))
    unreal.SystemLibrary.quit_editor()
