# -*- coding: utf-8 -*-
"""Normalize cast figure transforms, dump component state, and re-shoot from further back."""
import json, os, time, traceback
import unreal
AUDIT = "D:/灯影山海/Saved/Audit-2026-10-22-FourAct"
CAST = "/Game/DengYingShanHai/Puppets/DA_DYPuppetCast"
EAL = unreal.EditorAssetLibrary
S = dict(ok=False, before=[], after=[], components=[], errors=[], shot=None)
def vec(v):
    return [round(float(v.x), 3), round(float(v.y), 3), round(float(v.z), 3)]
def eul(r):
    return [round(float(r.pitch), 3), round(float(r.yaw), 3), round(float(r.roll), 3)]
try:
    cast = unreal.load_asset(CAST)
    figs = cast.get_editor_property("figures")
    for f in figs:
        S["before"].append(dict(label=str(f.get_editor_property("label")),
            loc=vec(f.get_editor_property("mesh_relative_location")),
            rot=eul(f.get_editor_property("mesh_relative_rotation")),
            scale=vec(f.get_editor_property("mesh_relative_scale"))))
    # Kuafu keeps its authored 0.8 scale; give every chapter figure the same on-stage size.
    for f in figs:
        sc = f.get_editor_property("mesh_relative_scale")
        sc.x = 0.8; sc.y = 0.8; sc.z = 0.8
        f.set_editor_property("mesh_relative_scale", sc)
        L = f.get_editor_property("mesh_relative_location")
        L.x = 0.0; L.y = -42.44; L.z = -104.57
        f.set_editor_property("mesh_relative_location", L)
        R = f.get_editor_property("mesh_relative_rotation")
        R.pitch = 0.0; R.yaw = 180.0; R.roll = 0.0
        f.set_editor_property("mesh_relative_rotation", R)
    cast.set_editor_property("figures", figs)
    S["saved"] = bool(EAL.save_loaded_asset(cast, False))
    for f in figs:
        S["after"].append(dict(label=str(f.get_editor_property("label")),
            loc=vec(f.get_editor_property("mesh_relative_location")),
            scale=vec(f.get_editor_property("mesh_relative_scale"))))
    unreal.EditorLoadingAndSavingUtils.load_map("/Game/DengYingShanHai/Maps/L_DY_Main")
    eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    puppet = None
    for a in eas.get_all_level_actors():
        if "KuafuPuppet" in a.get_class().get_name():
            puppet = a
    puppet.call_method("ApplyChapterFigure", (1, True))
    S["active"] = puppet.call_method("GetActiveFigureIndex")
    for c in puppet.get_components_by_class(unreal.SkeletalMeshComponent):
        m = c.get_editor_property("skeletal_mesh_asset")
        S["components"].append(dict(name=c.get_name(), mesh=m.get_path_name() if m else None,
            visible=bool(c.is_visible()), cast_shadow=str(c.get_editor_property("cast_shadow")),
            scale=vec(c.get_editor_property("relative_scale3d")), loc=vec(c.get_editor_property("relative_location"))))
    center, extent = puppet.get_actor_bounds(False)
    S["actor_extent"] = vec(extent)
    loc = (300.0, -80.0, 320.0); tgt = (640.0, -80.0, 300.0)
    rot = unreal.MathLibrary.find_look_at_rotation(unreal.Vector(*loc), unreal.Vector(*tgt))
    cam = eas.spawn_actor_from_class(unreal.CameraActor, unreal.Vector(*loc), rot, False)
    cam.set_actor_label("TEMP_OpShot2")
    cc = cam.get_component_by_class(unreal.CameraComponent)
    cc.set_editor_property("field_of_view", 55.0)
    cc.set_editor_property("aspect_ratio", 1.6)
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).set_level_viewport_camera_info(unreal.Vector(*loc), rot, "")
    def finish(code):
        S["ok"] = code == 0
        with open(AUDIT + "/cast-normalize.json", "w", encoding="utf-8") as f:
            json.dump(S, f, ensure_ascii=False, indent=2, default=str)
        print("NORM_DONE", S["ok"], json.dumps(S["components"], ensure_ascii=False)); unreal.SystemLibrary.quit_editor()
    def tick(dt):
        try:
            now = time.monotonic()
            st = S.setdefault("stage", "settle")
            if st == "settle" and now - S.setdefault("mark", now) > 3.5:
                path = AUDIT + "/Op-Close3.png"
                unreal.AutomationLibrary.take_high_res_screenshot(1600, 1000, path, camera=cam)
                S["shot"] = path; S["stage"] = "poll"; S["mark"] = now; return
            if st == "poll":
                if os.path.isfile(S["shot"]) and os.path.getsize(S["shot"]) > 20000:
                    S["bytes"] = os.path.getsize(S["shot"]); return finish(0)
                if now - S["mark"] > 14:
                    return finish(0)
        except Exception:
            S["errors"].append(traceback.format_exc()); finish(1)
    unreal.register_slate_post_tick_callback(tick)
except Exception:
    S["errors"].append(traceback.format_exc())
    with open(AUDIT + "/cast-normalize.json", "w", encoding="utf-8") as f:
        json.dump(S, f, ensure_ascii=False, indent=2, default=str)
    print("NORM_FAIL", S["errors"][:1]); unreal.SystemLibrary.quit_editor()
