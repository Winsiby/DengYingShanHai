# -*- coding: utf-8 -*-
"""Align every chapter figure to the Kuafu baseline and the screen centre, then save the cast."""
import json, traceback
import unreal
AUDIT = "D:/灯影山海/Saved/Audit-2026-10-22-FourAct"
CAST = "/Game/DengYingShanHai/Puppets/DA_DYPuppetCast"
EAL = unreal.EditorAssetLibrary
S = dict(ok=False, measured=[], offsets=[], errors=[])
def box(comp):
    o, e = comp.get_local_bounds()
    m = comp.get_component_to_world()
    world = unreal.MathLibrary.transform_location(m, o)
    scale = float(comp.get_editor_property("relative_scale3d").z)
    actor = comp.get_owner().get_actor_scale3d().z
    ez = float(e.z) * scale * actor
    return dict(origin=[round(float(world.x), 2), round(float(world.y), 2), round(float(world.z), 2)],
                extent=[round(float(e.x), 2), round(float(e.y), 2), round(float(e.z), 2)],
                min_z=round(float(world.z - ez), 2), max_z=round(float(world.z + ez), 2))
try:
    unreal.EditorLoadingAndSavingUtils.load_map("/Game/DengYingShanHai/Maps/L_DY_Main")
    eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    puppet = None
    for a in eas.get_all_level_actors():
        if "KuafuPuppet" in a.get_class().get_name():
            puppet = a
    baseline = None
    for i in range(4):
        puppet.call_method("ApplyChapterFigure", (i, True))
        comp = None
        for c in puppet.get_components_by_class(unreal.SkeletalMeshComponent):
            if c.is_visible():
                comp = c
        data = box(comp)
        data["index"] = i
        data["component"] = comp.get_name()
        S["measured"].append(data)
        if i == 0:
            baseline = (data["min_z"], data["origin"][1])
    cast = unreal.load_asset(CAST)
    figs = cast.get_editor_property("figures")
    for i, f in enumerate(figs):
        m = S["measured"][i]
        dy = round(baseline[1] - m["origin"][1], 2)
        dz = round(baseline[0] - m["min_z"], 2)
        L = f.get_editor_property("mesh_relative_location")
        base = S["measured"][0]
        L.y = round(L.y + dy, 3)
        L.z = round(L.z + dz, 3)
        f.set_editor_property("mesh_relative_location", L)
        S["offsets"].append(dict(index=i, dy=dy, dz=dz, loc=[round(float(L.x), 2), round(float(L.y), 2), round(float(L.z), 2)]))
    cast.set_editor_property("figures", figs)
    S["saved"] = bool(EAL.save_loaded_asset(cast, False))
    # Re-measure after the adjustment.
    S["after"] = []
    for i in range(4):
        puppet.call_method("ApplyChapterFigure", (i, True))
        comp = [c for c in puppet.get_components_by_class(unreal.SkeletalMeshComponent) if c.is_visible()][0]
        d = box(comp); d["index"] = i; S["after"].append(d)
    puppet.call_method("ApplyChapterFigure", (0, True))
    S["ok"] = True
except Exception:
    S["errors"].append(traceback.format_exc())
with open(AUDIT + "/cast-align.json", "w", encoding="utf-8") as f:
    json.dump(S, f, ensure_ascii=False, indent=2, default=str)
print("ALIGN", json.dumps(S["offsets"]), json.dumps(S.get("after")))
unreal.SystemLibrary.quit_editor()
