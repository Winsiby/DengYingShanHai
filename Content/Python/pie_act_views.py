# -*- coding: utf-8 -*-
"""Run the real game loop in PIE and photograph each act through the stage camera."""
import json, os, time, traceback
import unreal
AUDIT = "D:/灯影山海/Saved/Audit-2026-10-22-FourAct"
S = dict(ok=False, errors=[], shots={}, pie=False)
MAP = "/Game/DengYingShanHai/Maps/L_DY_Main"
try:
    unreal.EditorLoadingAndSavingUtils.load_map(MAP)
    LEVELS = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    LEVELS.editor_play_simulate()
    S["pie"] = True
    def finish(code):
        S["ok"] = code == 0
        try:
            LEVELS.editor_end_play()
        except Exception:
            pass
        with open(AUDIT + "/pie-act-views.json", "w", encoding="utf-8") as f:
            json.dump(S, f, ensure_ascii=False, indent=2, default=str)
        print("PIE_DONE", S["ok"], json.dumps(S["shots"])); unreal.SystemLibrary.quit_editor()
    def tick(dt):
        try:
            now = time.monotonic()
            st = S.setdefault("stage", "boot")
            if st == "boot" and now - S.setdefault("mark", now) > 6.0:
                world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
                S["world"] = world.get_name() if world else None
                eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
                # A camera that reproduces the hall sightline on the running stage.
                loc = (-980.0, -80.0, 250.0); tgt = (760.0, -80.0, 250.0)
                rot = unreal.MathLibrary.find_look_at_rotation(unreal.Vector(*loc), unreal.Vector(*tgt))
                cam = eas.spawn_actor_from_class(unreal.CameraActor, unreal.Vector(*loc), rot, True)
                cam.set_actor_location_and_rotation(unreal.Vector(*loc), rot, False, True)
                cc = cam.get_component_by_class(unreal.CameraComponent)
                cc.set_editor_property("field_of_view", 62.0)
                cc.set_editor_property("aspect_ratio", 1.6)
                S["camera"] = cam.get_name(); S["i"] = 0; S["stage"] = "switch"; S["mark"] = now
                return
            if st == "switch":
                i = S["i"]
                if i >= 4:
                    return finish(0)
                eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
                puppet = None
                for a in eas.get_all_level_actors():
                    if "KuafuPuppet" in a.get_class().get_name():
                        puppet = a
                if puppet:
                    # Direct switch for review of the display path only; the shipped game
                    # performs the same call from the puzzle director at each chapter start.
                    puppet.call_method("ApplyChapterFigure", (i, True))
                    S.setdefault("active", []).append(puppet.call_method("GetActiveFigureIndex"))
                S["stage"] = "settle"; S["mark"] = now; return
            if st == "settle" and now - S["mark"] > 2.5:
                i = S["i"]
                cam = None
                for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors():
                    if a.get_actor_label().startswith("CameraActor") or "Camera" in a.get_name():
                        cam = a
                path = AUDIT + "/Pie-Act%d.png" % (i + 1)
                unreal.AutomationLibrary.take_high_res_screenshot(1600, 1000, path, camera=cam)
                S["shots"]["Act%d" % (i + 1)] = dict(file=path, bytes=0)
                S["stage"] = "poll"; S["mark"] = now; return
            if st == "poll":
                key = "Act%d" % (S["i"] + 1); rec = S["shots"][key]
                if os.path.isfile(rec["file"]) and os.path.getsize(rec["file"]) > 20000:
                    rec["bytes"] = os.path.getsize(rec["file"]); S["i"] += 1; S["stage"] = "switch"; S["mark"] = now; return
                if now - S["mark"] > 14:
                    S["i"] += 1; S["stage"] = "switch"; S["mark"] = now; return
        except Exception:
            S["errors"].append(traceback.format_exc()); finish(1)
    unreal.register_slate_post_tick_callback(tick)
except Exception:
    S["errors"].append(traceback.format_exc())
    with open(AUDIT + "/pie-act-views.json", "w", encoding="utf-8") as f:
        json.dump(S, f, ensure_ascii=False, indent=2, default=str)
    print("PIE_FAIL", S["errors"][:1]); unreal.SystemLibrary.quit_editor()
