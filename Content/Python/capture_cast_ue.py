# -*- coding: utf-8 -*-
"""Four-chapter appearance evidence. Cameras spawn with an explicit aim so a Static
CameraActor cannot silently ignore the rotation. The map is never saved."""
import json, os, time, traceback
import unreal

AUDIT = "D:/灯影山海/Saved/Audit-2026-10-22-FourAct"
S = dict(shots=[], errors=[], log=[])


def dump():
    with open(AUDIT + "/cast-evidence.json", "w", encoding="utf-8") as f:
        json.dump(S, f, ensure_ascii=False, indent=2, default=str)


def make_cam(eas, label, loc, target, fov):
    rot = unreal.MathLibrary.find_look_at_rotation(unreal.Vector(*loc), unreal.Vector(*target))
    cam = eas.spawn_actor_from_class(unreal.CameraActor, unreal.Vector(*loc), rot, False)
    cam.set_actor_label(label)
    root = cam.get_editor_property("root_component")
    if root:
        root.set_mobility(unreal.ComponentMobility.MOVABLE)
    cam.set_actor_location_and_rotation(unreal.Vector(*loc), rot, False, True)
    cc = cam.get_component_by_class(unreal.CameraComponent)
    cc.set_editor_property("field_of_view", float(fov))
    cc.set_editor_property("aspect_ratio", 1.6)
    actual = cam.get_actor_rotation()
    S["log"].append("%s loc=%s yaw=%.1f" % (label, [round(v, 1) for v in (loc[0], loc[1], loc[2])], float(actual.yaw)))
    return cam


try:
    unreal.EditorLoadingAndSavingUtils.load_map("/Game/DengYingShanHai/Maps/L_DY_Main")
    eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    puppet = next((a for a in eas.get_all_level_actors() if "Puppet_P02" in a.get_actor_label() and hasattr(a, "apply_chapter_figure")), None)
    if puppet is None:
        raise RuntimeError("puppet missing")
    aud = make_cam(eas, "TEMP_Audience", (1700.0, 0.0, 430.0), (925.0, 0.0, 430.0), 62.0)
    back = make_cam(eas, "TEMP_Backstage", (250.0, 0.0, 380.0), (600.0, -80.0, 230.0), 50.0)
    plan = [(i, v) for v in ("Audience", "Backstage") for i in range(4)]
    def finish():
        if puppet:
            puppet.apply_chapter_figure(0, True)
        dump()
        print("EVIDENCE_DONE", sum(1 for s in S["shots"] if s.get("bytes", 0) > 20000), S["errors"][:1])
        unreal.SystemLibrary.quit_editor()
    def tick(dt):
        try:
            now = time.monotonic()
            if "stage" not in S:
                S["stage"] = "settle"; S["mark"] = now; S["i"] = 0; return
            if S["stage"] == "settle" and now - S["mark"] > 4.0:
                chapter, view = plan[S["i"]]
                puppet.apply_chapter_figure(chapter, True)
                path = "%s/Ev-C%d-%s.png" % (AUDIT, chapter + 1, view)
                unreal.AutomationLibrary.take_high_res_screenshot(1920, 1200, path, camera=(aud if view == "Audience" else back))
                S["shots"].append(dict(chapter=chapter + 1, view=view, file=path,
                                       active=int(puppet.get_active_figure_index()), bytes=0))
                S["stage"] = "wait"; S["mark"] = now; dump(); return
            if S["stage"] == "wait" and now - S["mark"] > 2.2:
                cur = S["shots"][-1]
                cur["bytes"] = os.path.getsize(cur["file"]) if os.path.isfile(cur["file"]) else 0
                S["i"] += 1
                if S["i"] >= len(plan):
                    return finish()
                S["stage"] = "settle"; S["mark"] = now
        except Exception:
            S["errors"].append(traceback.format_exc()); dump(); finish()
    unreal.register_slate_post_tick_callback(tick)
except Exception:
    S["errors"].append(traceback.format_exc()); dump(); print("EVIDENCE_FAIL", S["errors"][:1]); unreal.SystemLibrary.quit_editor()
