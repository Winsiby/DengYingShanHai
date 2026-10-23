# -*- coding: utf-8 -*-
import json, time, traceback
import unreal
AUDIT = "D:/灯影山海/Saved/Audit-2026-10-22-FourAct"
S = dict(ok=False, stage="setup", shots=[], errors=[], log=[])


def dump():
    with open(AUDIT + "/diag2.json", "w", encoding="utf-8") as f:
        json.dump(S, f, ensure_ascii=False, indent=2, default=str)


try:
    unreal.EditorLoadingAndSavingUtils.load_map("/Game/DengYingShanHai/Maps/L_DY_Main")
    eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    puppet = next((a for a in eas.get_all_level_actors() if "Puppet_P02" in a.get_actor_label()), None)
    S["log"].append("puppet=" + str(puppet is not None))
    def cam(label, loc, target, fov=None, ortho=None):
        c = eas.spawn_actor_from_class(unreal.CameraActor, unreal.Vector(*loc)); c.set_actor_label(label)
        cc = c.get_component_by_class(unreal.CameraComponent); cc.set_editor_property("aspect_ratio", 1.6)
        if ortho:
            cc.set_editor_property("projection_mode", unreal.CameraProjectionMode.ORTHOGRAPHIC)
            cc.set_editor_property("ortho_width", float(ortho))
        else:
            cc.set_editor_property("field_of_view", float(fov))
        c.set_actor_rotation(unreal.MathLibrary.find_look_at_rotation(unreal.Vector(*loc), unreal.Vector(*target)), False)
        return c
    elev = cam("TEMP_Elev", (2600.0, 0.0, 430.0), (600.0, 0.0, 430.0), None, 1900.0)
    aud = cam("TEMP_Aud", (1700.0, 0.0, 430.0), (925.0, 0.0, 430.0), 62.0)
    back = cam("TEMP_Back", (-120.0, 0.0, 380.0), (600.0, -80.0, 230.0), 50.0)
    plan = [("A-Elevation", elev), ("B-Audience", aud), ("C-Backstage", back)]
    def finish():
        S["ok"] = all(x.get("done") for x in S["shots"]) and not S["errors"]
        dump(); print("DIAG2_DONE", S["ok"], len(S["shots"]), S["errors"][:1]); unreal.SystemLibrary.quit_editor()
    def tick(dt):
        try:
            now = time.monotonic()
            if S["stage"] == "setup":
                S["stage"] = "settle"; S["mark"] = now; S["i"] = 0; return
            if S["stage"] == "settle" and now - S["mark"] > 4:
                name, c = plan[S["i"]]
                path = AUDIT + "/Diag2-%s.png" % name
                ok = unreal.AutomationLibrary.take_high_res_screenshot(1600, 1000, path, camera=c)
                S["shots"].append(dict(view=name, file=path, call=bool(ok)))
                S["log"].append("shot %s -> %s" % (name, bool(ok)))
                S["stage"] = "next"; S["mark"] = now; dump(); return
            if S["stage"] == "next" and now - S["mark"] > 2.5:
                import os
                prev = S["shots"][-1]
                prev["bytes"] = os.path.getsize(prev["file"]) if os.path.isfile(prev["file"]) else 0
                prev["done"] = prev["bytes"] > 20000
                S["i"] += 1
                if S["i"] >= len(plan):
                    if puppet: puppet.apply_chapter_figure(0, True)
                    return finish()
                S["stage"] = "settle"; S["mark"] = now
        except Exception:
            S["errors"].append(traceback.format_exc()); dump(); finish()
    unreal.register_slate_post_tick_callback(tick)
except Exception:
    S["errors"].append(traceback.format_exc()); dump(); print("DIAG2_FAIL", S["errors"][:1]); unreal.SystemLibrary.quit_editor()
