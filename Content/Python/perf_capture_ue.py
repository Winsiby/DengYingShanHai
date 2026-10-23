# -*- coding: utf-8 -*-
"""Sample every performance clip ON THE CLOTH so the shipped animation assets are visually verified."""
import json, os, time, traceback, unreal

AUDIT = "D:/灯影山海/Saved/Audit-2026-10-23-Performance/UE"
DA = "/Game/DengYingShanHai/Puppets/DA_DYPuppetPerformance.DA_DYPuppetPerformance"
R = {"ok": False, "shots": [], "errors": []}
S = {"stage": "setup", "chapter": -1, "list": [], "i": 0}


def finish():
    try:
        os.makedirs(AUDIT, exist_ok=True)
        open(AUDIT + "/perf-ue-capture.json", "w", encoding="utf-8").write(json.dumps(R, ensure_ascii=False, indent=2))
    except Exception:
        pass
    print("PERF_CAPTURE", R["ok"], len(R["shots"]), len(R["errors"]), (R["errors"][:1] or [""])[0][:200])
    unreal.SystemLibrary.quit_editor()


try:
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
    cam.set_actor_label("TEMP_PerfCamera")
    cc = cam.get_component_by_class(unreal.CameraComponent)
    cc.set_editor_property("field_of_view", 62.0)
    cc.set_editor_property("aspect_ratio", 1.6)
    mesh = puppet.get_component_by_class(unreal.SkeletalMeshComponent)
    data = unreal.EditorAssetLibrary.load_asset(DA)
    if data is None:
        raise RuntimeError("DA missing")
    acts = data.get_editor_property("acts")
    R["acts"] = len(acts)
    work = []
    for ci in range(len(acts)):
        act = acts[ci]
        segs = act.get_editor_property("segments")
        for si in range(len(segs)):
            seg = segs[si]
            clip = seg.get_editor_property("animation")
            clip_path = clip if isinstance(clip, str) else clip.get_path_name()
            seconds = float(seg.get_editor_property("seconds"))
            work.append(dict(chapter=ci, seg=si, clip=clip_path, seconds=seconds))
    S["list"] = work

    def apply_chapter(chapter):
        puppet.call_method("ApplyChapterFigure", (chapter, True))
        director.apply_chapter_title_plaque(chapter)

    def apply_pose(clip_path, seconds, frac):
        seq = unreal.EditorAssetLibrary.load_asset(clip_path)
        if seq is None:
            raise RuntimeError("clip missing " + clip_path)
        try:
            mesh.set_editor_property("animation_mode", unreal.AnimationMode.ANIMATION_SINGLE_NODE)
        except Exception:
            pass
        mesh.set_animation(seq)
        try:
            mesh.set_play_rate(0.0)
        except Exception:
            pass
        length = seconds
        try:
            length = float(seq.get_editor_property("sequence_length"))
        except Exception:
            pass
        t = max(0.0, min(length - 0.01, length * frac))
        mesh.set_position(t, False)

    def tick(dt):
        try:
            now = time.monotonic()
            if S["stage"] in ("setup", "settle", "pose", "poll"):
                pass
            if S["stage"] == "setup":
                if S["i"] >= len(S["list"]):
                    R["ok"] = len(R["errors"]) == 0
                    return finish()
                item = S["list"][S["i"]]
                if item["chapter"] != S["chapter"]:
                    apply_chapter(item["chapter"])
                    S["chapter"] = item["chapter"]
                    S["stage"] = "settle"; S["mark"] = now
                    return
                S["stage"] = "pose"
                return
            if S["stage"] == "settle":
                if now - S["mark"] > 2.5:
                    S["stage"] = "pose"
                return
            if S["stage"] == "pose":
                item = S["list"][S["i"]]
                frac = S.setdefault("frames", {})
                idx = S.setdefault("fi", 0)
                fr = (0.25, 0.75)[idx % 2]
                apply_pose(item["clip"], item["seconds"], fr)
                S["file"] = "%s/Act%d-seg%d-f%d.png" % (AUDIT, item["chapter"] + 1, item["seg"] + 1, idx % 2)
                unreal.AutomationLibrary.take_high_res_screenshot(1280, 800, S["file"], camera=cam)
                S["stage"] = "poll"; S["mark"] = now
                return
            if S["stage"] == "poll":
                if os.path.isfile(S["file"]) and os.path.getsize(S["file"]) > 15000:
                    item = S["list"][S["i"]]
                    R["shots"].append(dict(chapter=item["chapter"] + 1, segment=item["seg"] + 1,
                                           clip=item["clip"], file=os.path.basename(S["file"])))
                    S["fi"] = S.get("fi", 0) + 1
                    if S["fi"] % 2 == 0:
                        S["i"] += 1
                    S["stage"] = "setup"
                    return
                if now - S["mark"] > 20:
                    R["errors"].append("timeout " + S["file"])
                    S["i"] += 1; S["stage"] = "setup"; return
        except Exception:
            R["errors"].append(traceback.format_exc())
            S["i"] += 1; S["stage"] = "setup"

    unreal.register_slate_post_tick_callback(tick)
except Exception:
    R["errors"].append(traceback.format_exc())
    finish()
