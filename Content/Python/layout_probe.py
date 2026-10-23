# -*- coding: utf-8 -*-
"""Two orthographic layout views of the stage to choose a clear sightline."""
import json, os, time, traceback
import unreal
AUDIT = "D:/灯影山海/Saved/Audit-2026-10-22-FourAct"
S = dict(ok=False, errors=[], shots=[])
JOBS = [
    ("Layout-Top", (600.0, 0.0, 1400.0), (600.0, 0.0, 0.0), 2600.0),
    ("Layout-Side", (600.0, 2400.0, 300.0), (600.0, 0.0, 300.0), 2600.0),
    ("Layout-Front", (2600.0, 0.0, 300.0), (600.0, 0.0, 300.0), 2600.0),
]
try:
    unreal.EditorLoadingAndSavingUtils.load_map("/Game/DengYingShanHai/Maps/L_DY_Main")
    eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    cam = eas.spawn_actor_from_class(unreal.CameraActor, unreal.Vector(0.0, 0.0, 1400.0), unreal.Rotator(-90.0, 0.0, 0.0), False)
    cam.set_actor_label("TEMP_LayoutShot")
    cc = cam.get_component_by_class(unreal.CameraComponent)
    cc.set_editor_property("projection_mode", unreal.CameraProjectionMode.ORTHOGRAPHIC)
    cc.set_editor_property("aspect_ratio", 1.6)
    def finish(code):
        S["ok"] = code == 0
        with open(AUDIT + "/layout.json", "w", encoding="utf-8") as f:
            json.dump(S, f, ensure_ascii=False, indent=2, default=str)
        print("LAYOUT_DONE", S["ok"], json.dumps(S["shots"])); unreal.SystemLibrary.quit_editor()
    def tick(dt):
        try:
            now = time.monotonic()
            st = S.setdefault("stage", "aim"); S.setdefault("i", 0)
            if st == "aim":
                if S["i"] >= len(JOBS):
                    return finish(0)
                name, loc, tgt, width = JOBS[S["i"]]
                rot = unreal.MathLibrary.find_look_at_rotation(unreal.Vector(*loc), unreal.Vector(*tgt))
                cam.set_actor_location_and_rotation(unreal.Vector(*loc), rot, False, True)
                cc.set_editor_property("ortho_width", width)
                unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).set_level_viewport_camera_info(unreal.Vector(*loc), rot, "")
                S["stage"] = "settle"; S["mark"] = now; return
            if st == "settle" and now - S["mark"] > 3.5:
                name = JOBS[S["i"]][0]
                path = AUDIT + "/" + name + ".png"
                unreal.AutomationLibrary.take_high_res_screenshot(1600, 1000, path, camera=cam)
                S["shots"].append(dict(view=name, file=path)); S["stage"] = "poll"; S["mark"] = now; return
            if st == "poll":
                rec = S["shots"][-1]
                if os.path.isfile(rec["file"]) and os.path.getsize(rec["file"]) > 20000:
                    rec["bytes"] = os.path.getsize(rec["file"]); S["i"] += 1; S["stage"] = "aim"; S["mark"] = now; return
                if now - S["mark"] > 12:
                    rec["bytes"] = 0; S["i"] += 1; S["stage"] = "aim"; S["mark"] = now; return
        except Exception:
            S["errors"].append(traceback.format_exc()); finish(1)
    unreal.register_slate_post_tick_callback(tick)
except Exception:
    S["errors"].append(traceback.format_exc()); print("LAYOUT_FAIL", S["errors"][:1]); unreal.SystemLibrary.quit_editor()
