# -*- coding: utf-8 -*-
"""Preview each act's plaque material in the shipped theatre. Restores the authored material and never saves the map."""
import json, os, time, traceback, unreal

AUDIT = "D:/灯影山海/Saved/Audit-2026-10-22-FourAct"
MAT = "/Game/DengYingShanHai/Stage/ArtMainline/Materials"
ORIGINAL = MAT + "/M_DY_TitleGlyph"
EAL = unreal.EditorAssetLibrary
S = {"ok": False, "stage": "setup", "index": 0, "shots": [], "error": None,
     "jobs": [(1, "Audience"), (1, "Plate"), (2, "Audience"), (2, "Plate"),
              (3, "Audience"), (3, "Plate"), (4, "Audience"), (4, "Plate")]}
VIEWS = {"Audience": ((-980.0, -80.0, 250.0), (760.0, -80.0, 250.0), 62.0),
         "Plate": ((700.0, 0.0, 880.0), (895.0, 0.0, 880.0), 40.0)}


def finish():
    try:
        if S.get("plaque"):
            S["plaque"].get_component_by_class(unreal.StaticMeshComponent).set_material(0,
                EAL.load_asset(ORIGINAL))
            S["restored"] = True
    except Exception:
        S["restore_error"] = traceback.format_exc()
    S["map_saved"] = False
    open(AUDIT + "/title-preview.json", "w", encoding="utf-8").write(json.dumps(S, ensure_ascii=False, indent=2))
    print("TITLE_PREVIEW", S["ok"], len(S["shots"]), S["error"][:200] if S["error"] else "")
    unreal.SystemLibrary.quit_editor()


try:
    unreal.EditorLoadingAndSavingUtils.load_map("/Game/DengYingShanHai/Maps/L_DY_Main")
    ACT = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    for a in ACT.get_all_level_actors():
        if a.get_actor_label() == "ART_ZhuRiTitleGlyph":
            S["plaque"] = a
    if not S.get("plaque"):
        raise RuntimeError("plaque missing")
    S["component"] = S["plaque"].get_component_by_class(unreal.StaticMeshComponent)
    S["original_material"] = S["component"].get_materials()[0].get_path_name()
    loc, tgt, fov = VIEWS["Audience"]
    rot = unreal.MathLibrary.find_look_at_rotation(unreal.Vector(*loc), unreal.Vector(*tgt))
    cam = ACT.spawn_actor_from_class(unreal.CameraActor, unreal.Vector(*loc), rot, True)
    cam.set_actor_label("TEMP_TitlePreviewCamera")
    cc = cam.get_component_by_class(unreal.CameraComponent)
    cc.set_editor_property("field_of_view", fov)
    cc.set_editor_property("aspect_ratio", 1.6)
    S["camera"] = cam

    def tick(dt):
        try:
            now = time.monotonic()
            if S["stage"] == "setup":
                if S["index"] >= len(S["jobs"]):
                    S["ok"] = True
                    return finish()
                act, view = S["jobs"][S["index"]]
                mat = EAL.load_asset(MAT + "/MI_DY_TitleGlyph_Act%d" % act)
                S["component"].set_material(0, mat)
                loc, tgt, fov = VIEWS[view]
                rot = unreal.MathLibrary.find_look_at_rotation(unreal.Vector(*loc), unreal.Vector(*tgt))
                cam.set_actor_location_and_rotation(unreal.Vector(*loc), rot, False, False)
                cc.set_editor_property("field_of_view", fov)
                S["stage"] = "settle"
                S["mark"] = now
                return
            if S["stage"] == "settle" and now - S["mark"] > 3.0:
                act, view = S["jobs"][S["index"]]
                S["target"] = AUDIT + "/Title-Act%d-%s.png" % (act, view)
                unreal.AutomationLibrary.take_high_res_screenshot(1600, 1000, S["target"], camera=cam)
                S["stage"] = "poll"
                S["mark"] = now
                return
            if S["stage"] == "poll":
                if os.path.isfile(S["target"]) and os.path.getsize(S["target"]) > 20000:
                    act, view = S["jobs"][S["index"]]
                    S["shots"].append(dict(act=act, view=view, file=S["target"],
                        material=str(S["component"].get_materials()[0].get_path_name())))
                    S["index"] += 1
                    S["stage"] = "setup"
                    return
                if now - S["mark"] > 15:
                    raise RuntimeError("screenshot timeout " + S["target"])
        except Exception:
            S["error"] = traceback.format_exc()
            return finish()

    unreal.register_slate_post_tick_callback(tick)
except Exception:
    S["error"] = traceback.format_exc()
    finish()
