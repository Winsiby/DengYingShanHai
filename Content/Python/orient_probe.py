# -*- coding: utf-8 -*-
"""Isolate asset orientation: two fresh actors, identity and yaw 90, one ortho frame."""
import json, os, time, traceback
import unreal
AUDIT = "D:/灯影山海/Saved/Audit-2026-10-22-FourAct"
S = dict(errors=[], bytes=0)
try:
    unreal.EditorLoadingAndSavingUtils.load_map("/Game/DengYingShanHai/Maps/L_DY_Main")
    eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    mesh_asset = unreal.load_asset("/Game/DengYingShanHai/Puppets/Meshes/SK_DY_Jingwei")
    anim = unreal.load_asset("/Game/DengYingShanHai/Puppets/Animations/A_DY_Jingwei_Rest")
    for y, yaw in ((-420.0, 0.0), (-860.0, 90.0)):
        a = eas.spawn_actor_from_class(unreal.SkeletalMeshActor, unreal.Vector(600.0, y, 210.0), unreal.Rotator(0.0, yaw, 0.0), False)
        a.set_actor_label("TEMP_Orient_%d" % int(yaw))
        c = a.get_component_by_class(unreal.SkeletalMeshComponent)
        c.set_skeletal_mesh_asset(mesh_asset)
        c.set_mobility(unreal.ComponentMobility.MOVABLE)
        c.set_animation(anim)
        c.set_position(0.0, False)
        c.play(False)
        c.set_editor_property("cast_shadow", True)
    loc = (1500.0, -640.0, 230.0); target = (600.0, -640.0, 230.0)
    rot = unreal.MathLibrary.find_look_at_rotation(unreal.Vector(*loc), unreal.Vector(*target))
    cam = eas.spawn_actor_from_class(unreal.CameraActor, unreal.Vector(*loc), rot, False)
    cam.set_actor_location_and_rotation(unreal.Vector(*loc), rot, False, True)
    cc = cam.get_component_by_class(unreal.CameraComponent)
    cc.set_editor_property("projection_mode", unreal.CameraProjectionMode.ORTHOGRAPHIC)
    cc.set_editor_property("ortho_width", 900.0)
    cc.set_editor_property("aspect_ratio", 1.6)
    def finish():
        with open(AUDIT + "/orientation.json", "w", encoding="utf-8") as f:
            json.dump(S, f, ensure_ascii=False, indent=2, default=str)
        print("ORIENT_DONE", S["bytes"], S["errors"][:1]); unreal.SystemLibrary.quit_editor()
    def tick(dt):
        try:
            now = time.monotonic()
            if "stage" not in S:
                S.update(stage="settle", mark=now); return
            if S["stage"] == "settle" and now - S["mark"] > 4:
                path = AUDIT + "/Orient-Jingwei.png"
                unreal.AutomationLibrary.take_high_res_screenshot(1600, 1000, path, camera=cam)
                S["file"] = path; S["stage"] = "wait"; S["mark"] = now; return
            if S["stage"] == "wait" and now - S["mark"] > 2.5:
                S["bytes"] = os.path.getsize(S["file"]) if os.path.isfile(S["file"]) else 0
                return finish()
        except Exception:
            S["errors"].append(traceback.format_exc()); finish()
    unreal.register_slate_post_tick_callback(tick)
except Exception:
    S["errors"].append(traceback.format_exc())
    with open(AUDIT + "/orientation.json", "w", encoding="utf-8") as f:
        json.dump(S, f, ensure_ascii=False, indent=2, default=str)
    print("ORIENT_FAIL", S["errors"][:1]); unreal.SystemLibrary.quit_editor()
