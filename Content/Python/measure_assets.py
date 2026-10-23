# -*- coding: utf-8 -*-
"""Measure imported puppet assets at scale 1 and report the active cast component state."""
import json, traceback
import unreal
AUDIT = "D:/灯影山海/Saved/Audit-2026-10-22-FourAct"
EAL = unreal.EditorAssetLibrary
S = dict(ok=False, assets={}, errors=[])
try:
    unreal.EditorLoadingAndSavingUtils.load_map("/Game/DengYingShanHai/Maps/L_DY_Main")
    eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    for i, name in enumerate(("Jingwei", "Xingtian", "Zhulong", "Kuafu_M01_LeftGrip_v04")):
        path = "/Game/DengYingShanHai/Puppets/Meshes/SK_DY_" + name
        if not EAL.does_asset_exist(path):
            path = "/Game/DengYingShanHai/Dev/KuafuAppearance/Meshes/SK_DY_" + name
        asset = unreal.load_asset(path)
        if asset is None:
            S["assets"][name] = "missing"; continue
        a = eas.spawn_actor_from_class(unreal.SkeletalMeshActor, unreal.Vector(0.0, 4000.0 + i * 800.0, 0.0), unreal.Rotator(0.0, 0.0, 0.0), False)
        c = a.get_component_by_class(unreal.SkeletalMeshComponent)
        c.set_skeletal_mesh_asset(asset)
        center, extent = a.get_actor_bounds(False)
        S["assets"][name] = dict(path=path, extent=[round(float(extent.x), 2), round(float(extent.y), 2), round(float(extent.z), 2)], size=[round(float(extent.x) * 2, 2), round(float(extent.y) * 2, 2), round(float(extent.z) * 2, 2)])
        eas.destroy_actor(a)
    puppet = None
    for a in eas.get_all_level_actors():
        if "KuafuPuppet" in a.get_class().get_name():
            puppet = a
    if puppet:
        center, extent = puppet.get_actor_bounds(False)
        S["puppet_actor"] = dict(location=[round(float(puppet.get_actor_location().x), 2), round(float(puppet.get_actor_location().y), 2), round(float(puppet.get_actor_location().z), 2)], extent=[round(float(extent.x), 2), round(float(extent.y), 2), round(float(extent.z), 2)])
        sc = puppet.get_actor_scale3d(); S["puppet_scale"] = [round(float(sc.x), 3), round(float(sc.y), 3), round(float(sc.z), 3)]
        cmps = []
        for c in puppet.get_components_by_class(unreal.SkeletalMeshComponent):
            m = c.get_editor_property("skeletal_mesh_asset")
            cmps.append(dict(name=c.get_name(), mesh=m.get_path_name() if m else None, visible=bool(c.is_visible()), visible_in_game=bool(c.get_editor_property("visible")), cast_shadow=str(c.get_editor_property("cast_shadow")), scale=[round(float(c.get_relative_scale3d().x), 3), round(float(c.get_relative_scale3d().y), 3), round(float(c.get_relative_scale3d().z), 3)], loc=[round(float(c.get_relative_location().x), 2), round(float(c.get_relative_location().y), 2), round(float(c.get_relative_location().z), 2)]))
        S["components"] = cmps
    S["ok"] = True
except Exception:
    S["errors"].append(traceback.format_exc())
with open(AUDIT + "/asset-measure.json", "w", encoding="utf-8") as f:
    json.dump(S, f, ensure_ascii=False, indent=2, default=str)
print("MEASURE", json.dumps({k: S[k] for k in ("ok", "assets")}, ensure_ascii=False))
unreal.SystemLibrary.quit_editor()
