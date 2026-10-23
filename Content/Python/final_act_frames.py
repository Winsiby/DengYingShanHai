# -*- coding: utf-8 -*-
"""Render each act with the matching puppet AND plaque so the evidence frame is internally consistent."""
import json, os, time, traceback, unreal

AUDIT = "D:/灯影山海/Saved/Audit-2026-10-22-FourAct"
R = {"ok": False, "shots": [], "error": None}
S = {"stage": "setup", "i": 0, "items": [0, 1, 2, 3]}


def finish():
    R.pop("cam", None)
    open(AUDIT + "/final-acts.json", "w", encoding="utf-8").write(json.dumps(R, ensure_ascii=False, indent=2))
    print("FINAL_ACTS", R["ok"], len(R["shots"]), (R["error"] or "")[:200])
    unreal.SystemLibrary.quit_editor()


try:
    unreal.EditorLoadingAndSavingUtils.load_map("/Game/DengYingShanHai/Maps/L_DY_Main")
    ACT = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    director = None; puppet = None; plaque = None
    for a in ACT.get_all_level_actors():
        cls = a.get_class().get_name()
        if cls.startswith("DYPuzzleDirector"):
            director = a
        if "KuafuPuppet" in cls:
            puppet = a
        if a.get_actor_label() == "ART_ZhuRiTitleGlyph":
            plaque = a
    if not (director and puppet and plaque):
        raise RuntimeError("scene actors missing")
    loc, tgt = (-980.0, -80.0, 250.0), (760.0, -80.0, 250.0)
    rot = unreal.MathLibrary.find_look_at_rotation(unreal.Vector(*loc), unreal.Vector(*tgt))
    cam = ACT.spawn_actor_from_class(unreal.CameraActor, unreal.Vector(*loc), rot, True)
    cam.set_actor_label("TEMP_FinalActCamera")
    cc = cam.get_component_by_class(unreal.CameraComponent)
    cc.set_editor_property("field_of_view", 62.0)
    cc.set_editor_property("aspect_ratio", 1.6)
    comp = plaque.get_component_by_class(unreal.StaticMeshComponent)

    def tick(dt):
        try:
            now = time.monotonic()
            if S["stage"] == "setup":
                if S["i"] >= len(S["items"]):
                    R["ok"] = True
                    return finish()
                chapter = S["items"][S["i"]]
                puppet.call_method("ApplyChapterFigure", (chapter, True))
                director.apply_chapter_title_plaque(chapter)
                R["shots"].append(dict(chapter=chapter,
                    puppet_mesh=str(puppet.get_component_by_class(unreal.SkeletalMeshComponent).get_editor_property("skeletal_mesh").get_path_name()) if False else None,
                    plaque=str(comp.get_materials()[0].get_path_name())))
                S["stage"] = "settle"; S["mark"] = now
                return
            if S["stage"] == "settle" and now - S["mark"] > 3.0:
                chapter = S["items"][S["i"]]
                S["file"] = AUDIT + "/Final-Act%d.png" % (chapter + 1)
                unreal.AutomationLibrary.take_high_res_screenshot(1600, 1000, S["file"], camera=cam)
                S["stage"] = "poll"; S["mark"] = now
                return
            if S["stage"] == "poll":
                if os.path.isfile(S["file"]) and os.path.getsize(S["file"]) > 20000:
                    S["i"] += 1; S["stage"] = "setup"
                    return
                if now - S["mark"] > 20:
                    raise RuntimeError("timeout " + S["file"])
        except Exception:
            R["error"] = traceback.format_exc()
            return finish()

    unreal.register_slate_post_tick_callback(tick)
except Exception:
    R["error"] = traceback.format_exc()
    finish()
