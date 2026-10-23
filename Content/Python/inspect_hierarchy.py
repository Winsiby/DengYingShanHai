# -*- coding: utf-8 -*-
import json, traceback
import unreal
AUDIT = "D:/灯影山海/Saved/Audit-2026-10-22-FourAct"
S = dict(ok=False, errors=[], comps=[], cams=[])
M = unreal.MathLibrary
def e(x): return [round(float(x.x),2), round(float(x.y),2), round(float(x.z),2)]
def rt(x): return [round(float(x.pitch),2), round(float(x.yaw),2), round(float(x.roll),2)]
try:
    unreal.EditorLoadingAndSavingUtils.load_map("/Game/DengYingShanHai/Maps/L_DY_Main")
    eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    actors = eas.get_all_level_actors()
    puppet = next(a for a in actors if "Puppet_P02" in a.get_actor_label())
    actor_xf = unreal.Transform(unreal.Vector(600.0, -80.0, 210.0), unreal.Rotator(0, 0, 0), unreal.Vector(1, 1, 1))
    chain = {}
    for c in puppet.get_components_by_class(unreal.SceneComponent):
        chain[c.get_name()] = c
    rows = []
    for name, c in chain.items():
        rel = unreal.Transform(c.get_editor_property("relative_location"), c.get_editor_property("relative_rotation"),
                               c.get_editor_property("relative_scale3d"))
        xf = rel
        p = c.get_attach_parent()
        depth = 0
        while p is not None and depth < 12:
            xf = M.compose_transforms(unreal.Transform(p.get_editor_property("relative_location"), p.get_editor_property("relative_rotation"), p.get_editor_property("relative_scale3d")), xf)
            p = p.get_attach_parent(); depth += 1
        xf = M.compose_transforms(actor_xf, xf)
        rows.append(dict(name=name, cls=c.get_class().get_name(), visible=bool(c.is_visible()),
                         parent=c.get_attach_parent().get_name() if c.get_attach_parent() else None,
                         rel_loc=e(c.get_editor_property("relative_location")), rel_rot=rt(c.get_editor_property("relative_rotation")),
                         rel_scale=e(c.get_editor_property("relative_scale3d")),
                         world_loc=e(xf.translation), world_rot=str(xf.rotation), world_scale=e(xf.scale3d)))
    S["comps"] = rows
    for a in actors:
        if "Camera" in a.get_class().get_name() or "Camera" in a.get_actor_label():
            S["cams"].append(dict(label=a.get_actor_label(), cls=a.get_class().get_name(), loc=e(a.get_actor_location()), rot=rt(a.get_actor_rotation())))
    S["ok"] = True
except Exception:
    S["errors"].append(traceback.format_exc())
with open(AUDIT + "/hierarchy.json", "w", encoding="utf-8") as f:
    json.dump(S, f, ensure_ascii=False, indent=2, default=str)
print("HIER_DONE", S["ok"], len(S["comps"]), S["errors"][:1])
unreal.SystemLibrary.quit_editor()
