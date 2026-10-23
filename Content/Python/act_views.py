# -*- coding: utf-8 -*-
"""Photograph all four chapter puppets from the audience side of the formal stage."""
import json, os, time, traceback
import unreal
AUDIT = "D:/灯影山海/Saved/Audit-2026-10-22-FourAct"
S = dict(ok=False, errors=[], shots={}, active=[])
CAM = (-980.0, -80.0, 250.0)
TGT = (760.0, -80.0, 250.0)
try:
    unreal.EditorLoadingAndSavingUtils.load_map("/Game/DengYingShanHai/Maps/L_DY_Main")
    eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    puppet = None
    for a in eas.get_all_level_actors():
        if "KuafuPuppet" in a.get_class().get_name():
            puppet = a
    rot = unreal.MathLibrary.find_look_at_rotation(unreal.Vector(*CAM), unreal.Vector(*TGT))
    cam = eas.spawn_actor_from_class(unreal.CameraActor, unreal.Vector(*CAM), rot, False)
    cam.set_actor_label("TEMP_ActShot")
    cam.set_actor_location_and_rotation(unreal.Vector(*CAM), rot, False, True)
    cc = cam.get_component_by_class(unreal.CameraComponent)
    cc.set_editor_property("field_of_view", 62.0)
    cc.set_editor_property("aspect_ratio", 1.6)
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).set_level_viewport_camera_info(unreal.Vector(*CAM), rot, "")
    def finish(code):
        S["ok"] = code == 0
        with open(AUDIT + "/act-views.json", "w", encoding="utf-8") as f:
            json.dump(S, f, ensure_ascii=False, indent=2, default=str)
        print("ACT_DONE", S["ok"], json.dumps(S["shots"])); unreal.SystemLibrary.quit_editor()
    def tick(dt):
        try:
            now = time.monotonic()
            st = S.setdefault("stage", "switch"); i = S.setdefault("i", 0)
            if st == "switch":
                if i >= 4:
                    puppet.call_method("ApplyChapterFigure", (0, True))
                    S["restored"] = puppet.call_method("GetActiveFigureIndex")
                    return finish(0)
                puppet.call_method("ApplyChapterFigure", (i, True))
                S["active"].append(puppet.call_method("GetActiveFigureIndex"))
                S["stage"] = "settle"; S["mark"] = now; return
            if st == "settle" and now - S["mark"] > 3.0:
                name = "Act%d" % (i + 1)
                path = AUDIT + "/" + name + "-Audience.png"
                unreal.AutomationLibrary.take_high_res_screenshot(1600, 1000, path, camera=cam)
                S["shots"][name] = dict(file=path, bytes=0)
                S["stage"] = "poll"; S["mark"] = now; return
            if st == "poll":
                name = "Act%d" % (i + 1); rec = S["shots"][name]
                if os.path.isfile(rec["file"]) and os.path.getsize(rec["file"]) > 20000:
                    rec["bytes"] = os.path.getsize(rec["file"]); S["i"] = i + 1; S["stage"] = "switch"; S["mark"] = now; return
                if now - S["mark"] > 14:
                    S["i"] = i + 1; S["stage"] = "switch"; S["mark"] = now; return
        except Exception:
            S["errors"].append(traceback.format_exc()); finish(1)
    unreal.register_slate_post_tick_callback(tick)
except Exception:
    S["errors"].append(traceback.format_exc()); print("ACT_FAIL", S["errors"][:1]); unreal.SystemLibrary.quit_editor()
