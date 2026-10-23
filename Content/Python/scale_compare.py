# -*- coding: utf-8 -*-
"""Compare 0.8 vs 1.1 in-stage scale for chapters 2-4 and keep the better one."""
import json, os, time, traceback
import unreal
AUDIT = "D:/灯影山海/Saved/Audit-2026-10-22-FourAct"
CAST = "/Game/DengYingShanHai/Puppets/DA_DYPuppetCast"
S = dict(ok=False, errors=[], shots={}, kept=None)
try:
    unreal.EditorLoadingAndSavingUtils.load_map("/Game/DengYingShanHai/Maps/L_DY_Main")
    EAL = unreal.EditorAssetLibrary
    da = EAL.load_asset(CAST)
    ACTORS = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    puppet = None
    for a in ACTORS.get_all_level_actors():
        if "KuafuPuppet" in a.get_class().get_name():
            puppet = a
    loc, tgt = (-980.0, -80.0, 250.0), (760.0, -80.0, 250.0)
    rot = unreal.MathLibrary.find_look_at_rotation(unreal.Vector(*loc), unreal.Vector(*tgt))
    cam = ACTORS.spawn_actor_from_class(unreal.CameraActor, unreal.Vector(*loc), rot, True)
    cc = cam.get_component_by_class(unreal.CameraComponent)
    cc.set_editor_property("field_of_view", 62.0); cc.set_editor_property("aspect_ratio", 1.6)
    def finish(code):
        S["ok"] = code == 0
        with open(AUDIT + "/scale-compare.json", "w", encoding="utf-8") as h:
            json.dump(S, h, ensure_ascii=False, indent=2, default=str)
        print("SCALE_DONE", S["ok"], json.dumps(S["shots"]))
        unreal.SystemLibrary.quit_editor()
    def tick(dt):
        try:
            now = time.monotonic(); st = S.get("stage", "start")
            if st == "start":
                S.update(stage="act", i=1, mark=now); return
            if st == "act":
                i = S["i"]
                if i > 3: return finish(0)
                S["active"] = puppet.call_method("ApplyChapterFigure", (i, True))
                S.update(stage="shot_small", mark=now); return
            if st == "shot_small" and now - S["mark"] > 2.0:
                S["path"] = "%s/Scale-Small-Act%d.png" % (AUDIT, S["i"] + 1)
                unreal.AutomationLibrary.take_high_res_screenshot(1600, 1000, S["path"], camera=cam)
                S.update(stage="poll_small", mark=now); return
            if st == "poll_small":
                if os.path.isfile(S["path"]) and os.path.getsize(S["path"]) > 20000:
                    S["shots"]["small_%d" % S["i"]] = os.path.getsize(S["path"])
                    S.update(stage="grow", mark=now); return
                if now - S["mark"] > 15:
                    S.update(stage="grow", mark=now); return
            if st == "grow":
                figures = da.get_editor_property("figures")
                f = figures[S["i"]]
                f.set_editor_property("mesh_relative_scale", unreal.Vector(1.1, 1.1, 1.1))
                figures[S["i"]] = f
                da.set_editor_property("figures", figures)
                EAL.save_loaded_asset(da)
                puppet.call_method("ApplyChapterFigure", (S["i"], True))
                S.update(stage="shot_big", mark=now); return
            if st == "shot_big" and now - S["mark"] > 2.0:
                S["path"] = "%s/Scale-Big-Act%d.png" % (AUDIT, S["i"] + 1)
                unreal.AutomationLibrary.take_high_res_screenshot(1600, 1000, S["path"], camera=cam)
                S.update(stage="poll_big", mark=now); return
            if st == "poll_big":
                if os.path.isfile(S["path"]) and os.path.getsize(S["path"]) > 20000:
                    S["shots"]["big_%d" % S["i"]] = os.path.getsize(S["path"])
                    S.update(stage="act", i=S["i"] + 1, mark=now); return
                if now - S["mark"] > 15:
                    S.update(stage="act", i=S["i"] + 1, mark=now); return
        except Exception:
            S["errors"].append(traceback.format_exc()); finish(1)
    unreal.register_slate_post_tick_callback(tick)
except Exception:
    S["errors"].append(traceback.format_exc())
    with open(AUDIT + "/scale-compare.json", "w", encoding="utf-8") as h:
        json.dump(S, h, ensure_ascii=False, indent=2, default=str)
    print("SCALE_FAIL", S["errors"][:1]); unreal.SystemLibrary.quit_editor()
