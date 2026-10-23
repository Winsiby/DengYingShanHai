# -*- coding: utf-8 -*-
import json, os, time, traceback, unreal
AUDIT = "D:/灯影山海/Saved/Audit-2026-10-22-FourAct"
R = {"ok": False, "shots": [], "error": None, "plinth": {}}
S = {"stage": "setup", "i": 0,
     "items": [("Gate2-Outside", (-3000.0,-210.0,200.0), (-1500.0,-210.0,150.0), 60.0),
               ("Gate2-Door", (-2150.0,-210.0,160.0), (-1000.0,-210.0,140.0), 62.0),
               ("Gate2-Inside", (-1050.0,-210.0,160.0), (300.0,-160.0,140.0), 62.0)]}
def finish():
    open(AUDIT + "/gate-views2.json", "w", encoding="utf-8").write(json.dumps(R, ensure_ascii=False, indent=2))
    print("GATEVIEW2", R["ok"], len(R["shots"]), (R["error"] or "")[:200])
    unreal.SystemLibrary.quit_editor()
try:
    unreal.EditorLoadingAndSavingUtils.load_map("/Game/DengYingShanHai/Maps/L_DY_Main")
    ACT = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    for a in ACT.get_all_level_actors():
        if a.get_actor_label() == "ART_EXT_RearBase":
            c = a.get_component_by_class(unreal.StaticMeshComponent)
            mats = c.get_materials()
            R["plinth"] = {"materials": [m.get_path_name() if m else None for m in mats],
                           "loc": [round(float(a.get_actor_location().x),1), round(float(a.get_actor_location().y),1), round(float(a.get_actor_location().z),1)]}
    def tick(dt):
        try:
            now = time.monotonic()
            if S["stage"] == "setup":
                if S["i"] >= len(S["items"]):
                    R["ok"] = True; return finish()
                name, loc, tgt, fov = S["items"][S["i"]]
                S["name"] = name
                rot = unreal.MathLibrary.find_look_at_rotation(unreal.Vector(*loc), unreal.Vector(*tgt))
                cam = ACT.spawn_actor_from_class(unreal.CameraActor, unreal.Vector(*loc), rot, True)
                cam.set_actor_label("TEMP_GateCam%d" % S["i"])
                cc = cam.get_component_by_class(unreal.CameraComponent)
                cc.set_editor_property("field_of_view", fov)
                cc.set_editor_property("aspect_ratio", 1.6)
                S["cam"] = cam
                S["stage"] = "settle"; S["mark"] = now
                return
            if S["stage"] == "settle" and now - S["mark"] > 2.5:
                S["file"] = AUDIT + "/" + S["name"] + ".png"
                if os.path.isfile(S["file"]): os.remove(S["file"])
                unreal.AutomationLibrary.take_high_res_screenshot(1400, 875, S["file"], camera=S["cam"])
                S["stage"] = "poll"; S["mark"] = now
                return
            if S["stage"] == "poll":
                if os.path.isfile(S["file"]) and os.path.getsize(S["file"]) > 20000:
                    R["shots"].append(S["file"])
                    S["i"] += 1; S["stage"] = "setup"; return
                if now - S["mark"] > 25:
                    raise RuntimeError("timeout " + S["file"])
        except Exception:
            R["error"] = traceback.format_exc(); return finish()
    unreal.register_slate_post_tick_callback(tick)
except Exception:
    R["error"] = traceback.format_exc(); finish()
