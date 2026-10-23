# -*- coding: utf-8 -*-
import json, traceback, unreal
EAL = unreal.EditorAssetLibrary
OUT = "D:/灯影山海/Saved/Audit-2026-10-22-FourAct/title-pixels.json"
out = {"error": None}
try:
    tex = EAL.load_asset("/Game/DengYingShanHai/Stage/ArtMainline/Textures/T_DY_ZhuRiTitle")
    out["size"] = [tex.blueprint_get_size_x(), tex.blueprint_get_size_y()]
    w, h = out["size"]
    hits = 0; samples = []
    for y in range(h):
        for x in range(w):
            c = tex.blueprint_get_pixel(x, y)
            if c.r + c.g + c.b > 0.05:
                hits += 1
    out["nonzero"] = hits
    # Actor plane scale
    unreal.EditorLoadingAndSavingUtils.load_map("/Game/DengYingShanHai/Maps/L_DY_Main")
    ACT = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    for a in ACT.get_all_level_actors():
        if a.get_actor_label() == "ART_ZhuRiTitleGlyph":
            s = a.get_actor_scale3d(); r = a.get_actor_rotation()
            out["plane"] = dict(scale=[round(s.x,3), round(s.y,3), round(s.z,3)],
                                rot=[round(r.pitch,1), round(r.yaw,1), round(r.roll,1)])
except Exception:
    out["error"] = traceback.format_exc()
finally:
    open(OUT, "w", encoding="utf-8").write(json.dumps(out, ensure_ascii=False, indent=2))
    print("PIX", json.dumps(out, ensure_ascii=False)[:400])
    unreal.SystemLibrary.quit_editor()
