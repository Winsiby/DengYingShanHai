# -*- coding: utf-8 -*-
import json, os, time, traceback
import unreal
AUDIT = "D:/灯影山海/Saved/Audit-2026-10-22-FourAct"
S = dict(shots=[], errors=[])
def dump():
    with open(AUDIT + "/ortho.json", "w", encoding="utf-8") as f:
        json.dump(S, f, ensure_ascii=False, indent=2, default=str)
try:
    unreal.EditorLoadingAndSavingUtils.load_map("/Game/DengYingShanHai/Maps/L_DY_Main")
    eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    puppet = next(a for a in eas.get_all_level_actors() if "Puppet_P02" in a.get_actor_label())
    def cam(label, loc, target, width):
        rot = unreal.MathLibrary.find_look_at_rotation(unreal.Vector(*loc), unreal.Vector(*target))
        c = eas.spawn_actor_from_class(unreal.CameraActor, unreal.Vector(*loc), rot, False)
        c.set_actor_label(label)
        c.set_actor_location_and_rotation(unreal.Vector(*loc), rot, False, True)
        cc = c.get_component_by_class(unreal.CameraComponent)
        cc.set_editor_property("projection_mode", unreal.CameraProjectionMode.ORTHOGRAPHIC)
        cc.set_editor_property("ortho_width", float(width))
        cc.set_editor_property("aspect_ratio", 1.6)
        return c
    front = cam("TEMP_OrthoFront", (1400.0, -110.0, 230.0), (600.0, -110.0, 230.0), 420.0)
    side = cam("TEMP_OrthoSide", (600.0, 800.0, 230.0), (600.0, -80.0, 230.0), 420.0)
    plan = [(1, "Front", front), (1, "Side", side), (2, "Front", front), (2, "Side", side), (3, "Front", front), (4, "Front", front)]
    def finish():
        puppet.apply_chapter_figure(0, True); dump()
        print("ORTHO_DONE", len([s for s in S["shots"] if s.get("bytes")]), S["errors"][:1]); unreal.SystemLibrary.quit_editor()
    def tick(dt):
        try:
            now = time.monotonic()
            if "stage" not in S:
                S.update(stage="settle", mark=now, i=0); return
            if S["stage"] == "settle" and now - S["mark"] > 3.0:
                ch, view, c = plan[S["i"]]
                puppet.apply_chapter_figure(ch, True)
                path = "%s/Ortho-C%d-%s.png" % (AUDIT, ch + 1, view)
                unreal.AutomationLibrary.take_high_res_screenshot(1600, 1000, path, camera=c)
                S["shots"].append(dict(chapter=ch + 1, view=view, file=path, bytes=0))
                S["stage"] = "wait"; S["mark"] = now; dump(); return
            if S["stage"] == "wait" and now - S["mark"] > 1.8:
                cur = S["shots"][-1]
                cur["bytes"] = os.path.getsize(cur["file"]) if os.path.isfile(cur["file"]) else 0
                S["i"] += 1
                if S["i"] >= len(plan):
                    return finish()
                S["stage"] = "settle"; S["mark"] = now
        except Exception:
            S["errors"].append(traceback.format_exc()); dump(); finish()
    unreal.register_slate_post_tick_callback(tick)
except Exception:
    S["errors"].append(traceback.format_exc()); dump(); print("ORTHO_FAIL", S["errors"][:1]); unreal.SystemLibrary.quit_editor()
