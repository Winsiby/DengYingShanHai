# -*- coding: utf-8 -*-
"""Compare yaw 0 vs 180 for the three new chapter figures at the audience camera."""
import json, os, time, traceback, unreal

AUDIT = "D:/灯影山海/Saved/Audit-2026-10-22-FourAct"
R = {"ok": False, "shots": [], "error": None}
ITEMS = [(180, 1), (180, 2), (180, 3), (0, 1), (0, 2), (0, 3)]
S = {"stage": "setup", "i": 0, "mark": 0.0, "file": None}

def set_yaw(yaw):
    da = unreal.EditorAssetLibrary.load_asset("/Game/DengYingShanHai/Puppets/DA_DYPuppetCast")
    old = da.get_editor_property("figures")
    arr = unreal.Array(unreal.DYPuppetFigureEntry)
    for i in range(len(old)):
        src = old[i]
        e = unreal.DYPuppetFigureEntry()
        e.set_editor_property("label", src.label)
        e.set_editor_property("skeletal_mesh", src.skeletal_mesh)
        e.set_editor_property("pose_animations", src.pose_animations)
        e.set_editor_property("hide_staff", src.hide_staff)
        e.set_editor_property("mesh_relative_location", src.mesh_relative_location)
        e.set_editor_property("mesh_relative_rotation", unreal.Rotator(0.0, 0.0, 0.0 if i == 0 else yaw))
        e.set_editor_property("mesh_relative_scale", src.mesh_relative_scale)
        arr.append(e)
    da.set_editor_property("figures", arr)
    return [round(da.get_editor_property("figures")[i].mesh_relative_rotation.yaw, 1) for i in range(4)]

def finish():
    open(AUDIT + "/yaw-compare.json", "w", encoding="utf-8").write(json.dumps(R, ensure_ascii=False, indent=2))
    print("YAWCOMPARE", R["ok"], len(R["shots"]), (R["error"] or "")[:200])
    unreal.SystemLibrary.quit_editor()

try:
    for f in ("Final-Y0-Act2.png", "Final-Y0-Act3.png", "Final-Y0-Act4.png",
              "Final-Y180-Act2.png", "Final-Y180-Act3.png", "Final-Y180-Act4.png"):
        if os.path.isfile(AUDIT + "/" + f):
            os.remove(AUDIT + "/" + f)
    unreal.EditorLoadingAndSavingUtils.load_map("/Game/DengYingShanHai/Maps/L_DY_Main")
    ACT = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    director = None; puppet = None
    for a in ACT.get_all_level_actors():
        cls = a.get_class().get_name()
        if cls.startswith("DYPuzzleDirector"):
            director = a
        if "KuafuPuppet" in cls:
            puppet = a
    if not (director and puppet):
        raise RuntimeError("scene actors missing")
    loc, tgt = (-980.0, -80.0, 250.0), (760.0, -80.0, 250.0)
    rot = unreal.MathLibrary.find_look_at_rotation(unreal.Vector(*loc), unreal.Vector(*tgt))
    cam = ACT.spawn_actor_from_class(unreal.CameraActor, unreal.Vector(*loc), rot, True)
    cam.set_actor_label("TEMP_YawCamera")
    cc = cam.get_component_by_class(unreal.CameraComponent)
    cc.set_editor_property("field_of_view", 62.0)
    cc.set_editor_property("aspect_ratio", 1.6)
    R["camera"] = dict(loc=[loc[0], loc[1], loc[2]], fov=62.0)

    def tick(dt):
        try:
            now = time.monotonic()
            if S["stage"] == "setup":
                if S["i"] >= len(ITEMS):
                    R["ok"] = True
                    return finish()
                yaw, chapter = ITEMS[S["i"]]
                if S["i"] == 0 or ITEMS[S["i"] - 1][0] != yaw:
                    R.setdefault("yaw_readback", {})[str(yaw)] = set_yaw(yaw)
                puppet.call_method("ApplyChapterFigure", (chapter, True))
                director.apply_chapter_title_plaque(chapter)
                S["stage"] = "settle"; S["mark"] = now
                return
            if S["stage"] == "settle" and now - S["mark"] > 3.0:
                yaw, chapter = ITEMS[S["i"]]
                S["file"] = AUDIT + "/Final-Y%d-Act%d.png" % (yaw, chapter + 1)
                unreal.AutomationLibrary.take_high_res_screenshot(1600, 1000, S["file"], camera=cam)
                S["stage"] = "poll"; S["mark"] = now
                return
            if S["stage"] == "poll":
                if os.path.isfile(S["file"]) and os.path.getsize(S["file"]) > 20000:
                    R["shots"].append(dict(file=os.path.basename(S["file"]), bytes=os.path.getsize(S["file"])))
                    S["i"] += 1; S["stage"] = "setup"
                    return
                if now - S["mark"] > 25:
                    raise RuntimeError("timeout " + S["file"])
        except Exception:
            R["error"] = traceback.format_exc()
            return finish()

    unreal.register_slate_post_tick_callback(tick)
except Exception:
    R["error"] = traceback.format_exc()
    finish()
