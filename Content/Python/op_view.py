# -*- coding: utf-8 -*-
"""Operator-side views of the swapped puppet and its screen shadow."""
import json, os, time, traceback
import unreal
AUDIT = "D:/灯影山海/Saved/Audit-2026-10-22-FourAct"
S = dict(ok=False, errors=[], shots={}, active=None, restored=None)
JOBS = [
    ("Op-Close", (380.0, -80.0, 250.0), (650.0, -80.0, 250.0), 65.0),
    ("Op-Wide", (330.0, -300.0, 320.0), (700.0, -40.0, 300.0), 80.0),
]
try:
    unreal.EditorLoadingAndSavingUtils.load_map("/Game/DengYingShanHai/Maps/L_DY_Main")
    eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    target = None
    for a in eas.get_all_level_actors():
        if "KuafuPuppet" in a.get_class().get_name():
            target = a
    if target is None:
        raise RuntimeError("puppet not found")
    cam = eas.spawn_actor_from_class(unreal.CameraActor, unreal.Vector(0.0, 0.0, 300.0), unreal.Rotator(0.0, 0.0, 0.0), False)
    cam.set_actor_label("TEMP_OpShot")
    cc = cam.get_component_by_class(unreal.CameraComponent)
    cc.set_editor_property("projection_mode", unreal.CameraProjectionMode.PERSPECTIVE)
    cc.set_editor_property("aspect_ratio", 1.6)
    def finish(code):
        S["ok"] = code == 0
        with open(AUDIT + "/op-view.json", "w", encoding="utf-8") as f:
            json.dump(S, f, ensure_ascii=False, indent=2, default=str)
        print("OP_DONE", S["ok"], json.dumps(S["shots"])); unreal.SystemLibrary.quit_editor()
    def tick(dt):
        try:
            now = time.monotonic()
            st = S.setdefault("stage", "switch"); i = S.setdefault("i", 0)
            if st == "switch":
                target.call_method("ApplyChapterFigure", (1, True))
                S["active"] = target.call_method("GetActiveFigureIndex")
                S["stage"] = "aim"; S["mark"] = now; return
            if st == "aim":
                if i >= len(JOBS):
                    target.call_method("ApplyChapterFigure", (0, True))
                    S["restored"] = target.call_method("GetActiveFigureIndex")
                    return finish(0)
                name, loc, tgt, fov = JOBS[i]
                rot = unreal.MathLibrary.find_look_at_rotation(unreal.Vector(*loc), unreal.Vector(*tgt))
                cam.set_actor_location_and_rotation(unreal.Vector(*loc), rot, False, True)
                cc.set_editor_property("field_of_view", fov)
                unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).set_level_viewport_camera_info(unreal.Vector(*loc), rot, "")
                S["stage"] = "settle"; S["mark"] = now; return
            if st == "settle" and now - S["mark"] > 3.5:
                name = JOBS[i][0]
                unreal.AutomationLibrary.take_high_res_screenshot(1600, 1000, AUDIT + "/" + name + ".png", camera=cam)
                S["shots"][name] = dict(file=AUDIT + "/" + name + ".png", bytes=0)
                S["stage"] = "poll"; S["mark"] = now; return
            if st == "poll":
                name = JOBS[i][0]; rec = S["shots"][name]
                f = rec["file"]
                if os.path.isfile(f) and os.path.getsize(f) > 20000:
                    rec["bytes"] = os.path.getsize(f); S["i"] = i + 1; S["stage"] = "aim"; S["mark"] = now; return
                if now - S["mark"] > 12:
                    S["i"] = i + 1; S["stage"] = "aim"; S["mark"] = now; return
        except Exception:
            S["errors"].append(traceback.format_exc()); finish(1)
    unreal.register_slate_post_tick_callback(tick)
except Exception:
    S["errors"].append(traceback.format_exc()); print("OP_FAIL", S["errors"][:1]); unreal.SystemLibrary.quit_editor()
