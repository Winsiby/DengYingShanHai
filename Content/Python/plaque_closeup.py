# -*- coding: utf-8 -*-
import json, os, time, traceback, unreal
AUDIT = "D:/灯影山海/Saved/Audit-2026-10-22-FourAct"
S = {"ok": False, "error": None}
try:
    unreal.EditorLoadingAndSavingUtils.load_map("/Game/DengYingShanHai/Maps/L_DY_Main")
    ACT = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    loc, tgt = (700.0, 0.0, 880.0), (895.0, 0.0, 880.0)
    rot = unreal.MathLibrary.find_look_at_rotation(unreal.Vector(*loc), unreal.Vector(*tgt))
    cam = ACT.spawn_actor_from_class(unreal.CameraActor, unreal.Vector(*loc), rot, True)
    cc = cam.get_component_by_class(unreal.CameraComponent)
    cc.set_editor_property("field_of_view", 40.0); cc.set_editor_property("aspect_ratio", 1.6)
    S["path"] = AUDIT + "/Plaque-Closeup.png"
    def tick(dt):
        try:
            now = time.monotonic(); st = S.get("stage")
            if st is None:
                S["stage"] = "wait"; S["mark"] = now; return
            if st == "wait" and now - S["mark"] > 3:
                unreal.AutomationLibrary.take_high_res_screenshot(1600, 1000, S["path"], camera=cam)
                S["stage"] = "poll"; S["mark"] = now; return
            if st == "poll":
                if os.path.isfile(S["path"]) and os.path.getsize(S["path"]) > 20000:
                    S["ok"] = True; raise SystemExit
                if now - S["mark"] > 12:
                    raise SystemExit
        except SystemExit:
            open(AUDIT + "/plaque-closeup.json", "w", encoding="utf-8").write(json.dumps(S, ensure_ascii=False, indent=2))
            print("CLOSEUP", S)
            unreal.SystemLibrary.quit_editor()
        except Exception:
            S["error"] = traceback.format_exc()
            open(AUDIT + "/plaque-closeup.json", "w", encoding="utf-8").write(json.dumps(S, ensure_ascii=False, indent=2))
            print("CLOSEUP_FAIL", S["error"][:300]); unreal.SystemLibrary.quit_editor()
    unreal.register_slate_post_tick_callback(tick)
except Exception:
    S["error"] = traceback.format_exc()
    open(AUDIT + "/plaque-closeup.json", "w", encoding="utf-8").write(json.dumps(S, ensure_ascii=False, indent=2))
    print("FAIL", S["error"][:300]); unreal.SystemLibrary.quit_editor()
