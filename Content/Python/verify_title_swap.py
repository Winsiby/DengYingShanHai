# -*- coding: utf-8 -*-
"""Call the shipped plaque swap for each chapter and record the resulting material and audience frame."""
import json, os, time, traceback, unreal

AUDIT = "D:/灯影山海/Saved/Audit-2026-10-22-FourAct"
R = {"ok": False, "steps": [], "error": None}
S = {"stage": "setup", "i": 0, "mark": 0.0, "items": [0, 1, 2, 3]}


def finish():
    R.pop("cam", None)
    R["map_saved"] = False
    open(AUDIT + "/title-swap-verify.json", "w", encoding="utf-8").write(json.dumps(R, ensure_ascii=False, indent=2))
    print("TITLE_SWAP", R["ok"], len(R["steps"]), (R["error"] or "")[:300])
    unreal.SystemLibrary.quit_editor()


try:
    unreal.EditorLoadingAndSavingUtils.load_map("/Game/DengYingShanHai/Maps/L_DY_Main")
    ACT = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    director = None
    plaque = None
    for a in ACT.get_all_level_actors():
        if a.get_class().get_name().startswith("DYPuzzleDirector"):
            director = a
        if a.get_actor_label() == "ART_ZhuRiTitleGlyph":
            plaque = a
    if director is None or plaque is None:
        raise RuntimeError("director or plaque missing")
    comp = plaque.get_component_by_class(unreal.StaticMeshComponent)
    R["before"] = str(comp.get_materials()[0].get_path_name())
    loc, tgt = (-980.0, -80.0, 250.0), (760.0, -80.0, 250.0)
    rot = unreal.MathLibrary.find_look_at_rotation(unreal.Vector(*loc), unreal.Vector(*tgt))
    cam = ACT.spawn_actor_from_class(unreal.CameraActor, unreal.Vector(*loc), rot, True)
    cam.set_actor_label("TEMP_TitleSwapCamera")
    cc = cam.get_component_by_class(unreal.CameraComponent)
    cc.set_editor_property("field_of_view", 62.0)
    cc.set_editor_property("aspect_ratio", 1.6)

    def tick(dt):
        try:
            now = time.monotonic()
            if S["stage"] == "setup":
                if S["i"] >= len(S["items"]):
                    R["ok"] = all(s["swapped"] for s in R["steps"])
                    return finish()
                chapter = S["items"][S["i"]]
                director.apply_chapter_title_plaque(chapter)
                got = str(comp.get_materials()[0].get_path_name())
                wanted = "MI_DY_TitleGlyph_Act%d" % (chapter + 1)
                R["steps"].append(dict(chapter=chapter, material=got, expected_contains=wanted,
                                       swapped=wanted in got))
                S["stage"] = "settle"; S["mark"] = now
                return
            if S["stage"] == "settle" and now - S["mark"] > 3.0:
                chapter = S["items"][S["i"]]
                S["file"] = AUDIT + "/TitleSwap-Act%d.png" % (chapter + 1)
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
