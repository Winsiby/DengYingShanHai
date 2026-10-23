# -*- coding: utf-8 -*-
"""Switch the formal puppet to Jingwei and photograph both sides of the screen."""
import json, os, time, traceback
import unreal
AUDIT = "D:/灯影山海/Saved/Audit-2026-10-22-FourAct"
MAP = "/Game/DengYingShanHai/Maps/L_DY_Main"
S = dict(ok=False, errors=[], shots=[])
JOBS = [
    ("C2-Backstage", (250.0, -520.0, 300.0), (600.0, -80.0, 240.0), 50.0),
    ("C2-Audience", (1500.0, -150.0, 330.0), (600.0, -80.0, 240.0), 45.0),
]
try:
    unreal.EditorLoadingAndSavingUtils.load_map(MAP)
    eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    target = None
    for a in eas.get_all_level_actors():
        cls = a.get_class().get_name()
        if "KuafuPuppet" in cls or "Puppet" in cls:
            target = a
    if target is None:
        raise RuntimeError("no DYPuppetActor")
    cam = eas.spawn_actor_from_class(unreal.CameraActor, unreal.Vector(0.0, 0.0, 300.0), unreal.Rotator(0.0, 0.0, 0.0), False)
    cam.set_actor_label("TEMP_CastShot")
    cc = cam.get_component_by_class(unreal.CameraComponent)
    cc.set_editor_property("projection_mode", unreal.CameraProjectionMode.PERSPECTIVE)
    cc.set_editor_property("aspect_ratio", 1.6)
    def aim(loc, tgt, fov):
        rot = unreal.MathLibrary.find_look_at_rotation(unreal.Vector(*loc), unreal.Vector(*tgt))
        cam.set_actor_location_and_rotation(unreal.Vector(*loc), rot, False, True)
        cam.set_actor_rotation(rot, False)
        cc.set_editor_property("field_of_view", fov)
        unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).set_level_viewport_camera_info(unreal.Vector(*loc), rot, "")
    def finish(code):
        S["ok"] = code == 0
        with open(AUDIT + "/cast-jingwei.json", "w", encoding="utf-8") as f:
            json.dump(S, f, ensure_ascii=False, indent=2, default=str)
        print("CAST_DONE", S["ok"], json.dumps(S["shots"])); unreal.SystemLibrary.quit_editor()
    def tick(dt):
        try:
            now = time.monotonic()
            st = S.setdefault("stage", "switch")
            if st == "switch":
                target.call_method("ApplyChapterFigure", (1, True))
                time.sleep(0.1)
                S["active"] = target.call_method("GetActiveFigureIndex")
                S["stage"] = "aim"; S["i"] = 0; S["mark"] = now; return
            if st == "aim":
                if S["i"] >= len(JOBS):
                    S["stage"] = "restore"; return
                name, loc, tgt, fov = JOBS[S["i"]]
                aim(loc, tgt, fov); S["stage"] = "settle"; S["mark"] = now; return
            if st == "settle" and now - S["mark"] > 4:
                name = JOBS[S["i"]][0]
                path = AUDIT + "/Cast-" + name + ".png"
                unreal.AutomationLibrary.take_high_res_screenshot(1600, 1000, path, camera=cam)
                S["pending"] = path; S["stage"] = "poll"; S["mark"] = now
                S["shots"].append(dict(view=name, file=path)); return
            if st == "poll":
                ok = os.path.isfile(S["pending"]) and os.path.getsize(S["pending"]) > 20000
                if ok or now - S["mark"] > 12:
                    S["shots"][-1]["bytes"] = os.path.getsize(S["pending"]) if os.path.isfile(S["pending"]) else 0
                    S["i"] += 1; S["stage"] = "aim"; S["mark"] = now; return
            if st == "restore":
                target.call_method("ApplyChapterFigure", (0, True))
                S["restored"] = target.call_method("GetActiveFigureIndex")
                time.sleep(0.2); return finish(0)
        except Exception:
            S["errors"].append(traceback.format_exc()); finish(1)
    unreal.register_slate_post_tick_callback(tick)
except Exception:
    S["errors"].append(traceback.format_exc())
    with open(AUDIT + "/cast-jingwei.json", "w", encoding="utf-8") as f:
        json.dump(S, f, ensure_ascii=False, indent=2, default=str)
    print("CAST_FAIL", S["errors"][:1]); unreal.SystemLibrary.quit_editor()
