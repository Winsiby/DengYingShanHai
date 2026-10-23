# -*- coding: utf-8 -*-
import json, unreal
R = {"ok": False, "saved": False, "right": None, "error": None}
try:
    les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    les.load_level("/Game/DengYingShanHai/Maps/L_DY_Main")
    eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    base = None
    for a in eas.get_all_level_actors():
        if a.get_actor_label() == "ART_EXT_RearBase":
            base = a
        if a.get_actor_label() == "ART_EXT_RearBase_R":
            raise RuntimeError("right segment already exists")
    if base is None:
        raise RuntimeError("ART_EXT_RearBase missing")
    comp = base.get_component_by_class(unreal.StaticMeshComponent)
    mesh = comp.get_editor_property("static_mesh")
    mats = [comp.get_material(i) for i in range(comp.get_num_materials())]
    # transient must stay False so the actor is saved with the level
    right = eas.spawn_actor_from_class(unreal.StaticMeshActor, unreal.Vector(-1828.0, 675.0, 65.0), unreal.Rotator(0.0, 0.0, 0.0), False)
    if right is None:
        raise RuntimeError("spawn returned none")
    right.set_actor_label("ART_EXT_RearBase_R")
    rc = right.get_component_by_class(unreal.StaticMeshComponent)
    rc.set_editor_property("static_mesh", mesh)
    rc.set_editor_property("mobility", unreal.ComponentMobility.STATIC)
    for i, m in enumerate(mats):
        if m:
            rc.set_material(i, m)
    right.set_actor_scale3d(unreal.Vector(0.36, 11.1, 1.3))
    org, ext = right.get_actor_bounds(False)
    R["right"] = {"label": right.get_actor_label(), "loc": [round(float(org.x),1), round(float(org.y),1), round(float(org.z),1)],
                  "y_range": [round(float(org.y-ext.y),1), round(float(org.y+ext.y),1)],
                  "z_range": [round(float(org.z-ext.z),1), round(float(org.z+ext.z),1)],
                  "mesh": mesh.get_path_name() if mesh else None}
    R["saved"] = bool(les.save_current_level())
    R["ok"] = R["saved"]
except Exception as e:
    import traceback
    R["error"] = traceback.format_exc()
open("D:/灯影山海/Saved/Audit-2026-10-22-FourAct/rearbase-right-fix.json", "w", encoding="utf-8").write(json.dumps(R, ensure_ascii=False, indent=2))
print("REARBASE_FIX " + json.dumps({"ok": R["ok"], "saved": R["saved"], "right": R["right"], "err": (R["error"] or "")[:200]}, ensure_ascii=False))
unreal.SystemLibrary.quit_editor()
