# -*- coding: utf-8 -*-
import json, traceback
import unreal
AUDIT = "D:/灯影山海/Saved/Audit-2026-10-22-FourAct"
S = dict(ok=False, errors=[])
def v(x):
    return [round(float(x.x), 2), round(float(x.y), 2), round(float(x.z), 2)]
try:
    unreal.EditorLoadingAndSavingUtils.load_map("/Game/DengYingShanHai/Maps/L_DY_Main")
    eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    actors = eas.get_all_level_actors()
    S["screen"] = []
    S["cams"] = []
    S["big"] = []
    for a in actors:
        label = a.get_actor_label()
        low = label.lower()
        if "screen" in low or "curtain" in low or "seat" in low or "audience" in low:
            c, e = a.get_actor_bounds(False)
            S["screen"].append(dict(label=label, cls=a.get_class().get_name(), center=v(c), extent=v(e),
                                    rot=[round(a.get_actor_rotation().pitch,1), round(a.get_actor_rotation().yaw,1), round(a.get_actor_rotation().roll,1)]))
        if "camera" in low:
            S["cams"].append(dict(label=label, cls=a.get_class().get_name(), loc=v(a.get_actor_location())))
        if label.startswith(("DEV_", "M2_", "BP_DY")):
            c, e = a.get_actor_bounds(False)
            if abs(c.x) < 3000:
                S["big"].append(dict(label=label, cls=a.get_class().get_name(), center=v(c), extent=v(e)))
    puppet = next((a for a in actors if "Puppet_P02" in a.get_actor_label()), None)
    if puppet:
        rows = []
        for i, name in enumerate(("Kuafu", "Jingwei", "Xingtian", "Zhulong")):
            puppet.apply_chapter_figure(i, True)
            mesh = puppet.find_component_by_class(unreal.SkeletalMeshComponent)
            if not mesh:
                comps = puppet.get_components_by_class(unreal.SkeletalMeshComponent)
                mesh = comps[0] if comps else None
            rows.append(dict(
                chapter=i + 1,
                active=int(puppet.get_active_figure_index()),
                mesh=mesh.get_skeletal_mesh_asset().get_path_name() if mesh and mesh.get_skeletal_mesh_asset() else None,
                rel_loc=v(mesh.get_editor_property("relative_location")) if mesh else None,
                rel_rot=[round(float(mesh.get_editor_property("relative_rotation").pitch),1), round(float(mesh.get_editor_property("relative_rotation").yaw),1), round(float(mesh.get_editor_property("relative_rotation").roll),1)] if mesh else None,
                rel_scale=v(mesh.get_editor_property("relative_scale3d")) if mesh else None,
                world_center=v(mesh.get_component_location()) if mesh else None,
                anim=(mesh.get_anim_instance().get_animation_asset().get_path_name() if mesh and mesh.get_anim_instance() and mesh.get_anim_instance().get_animation_asset() else None)))
            c, e = puppet.get_actor_bounds(False)
            rows[-1]["actor_bounds_center"] = v(c)
            rows[-1]["actor_bounds_extent"] = v(e)
        puppet.apply_chapter_figure(0, True)
        S["figures"] = rows
    S["ok"] = True
except Exception:
    S["errors"].append(traceback.format_exc())
with open(AUDIT + "/cast-scene.json", "w", encoding="utf-8") as f:
    json.dump(S, f, ensure_ascii=False, indent=2, default=str)
print("SCENE_DONE", S.get("ok"), len(S.get("errors", [])))
unreal.SystemLibrary.quit_editor()
