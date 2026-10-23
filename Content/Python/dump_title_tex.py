# -*- coding: utf-8 -*-
import json, traceback, unreal
EAL = unreal.EditorAssetLibrary
tex = EAL.load_asset("/Game/DengYingShanHai/Stage/ArtMainline/Textures/T_DY_ZhuRiTitle")
out = {"error": None}
try:
    out["size"] = [tex.blueprint_get_size_x(), tex.blueprint_get_size_y()]
    out["srgb"] = bool(tex.get_editor_property("srgb"))
    out["compression"] = str(tex.get_editor_property("compression_settings"))
    out["lod_group"] = str(tex.get_editor_property("lod_group"))
    out["never_stream"] = bool(tex.get_editor_property("never_stream"))
    # Export the actual pixels so new acts can match the same layout and palette.
    out["export"] = EAL.export_asset("/Game/DengYingShanHai/Stage/ArtMainline/Textures/T_DY_ZhuRiTitle",
        "D:/灯影山海/Saved/Audit-2026-10-22-FourAct/T_DY_ZhuRiTitle.png")
except Exception:
    out["error"] = traceback.format_exc()
finally:
    open("D:/灯影山海/Saved/Audit-2026-10-22-FourAct/title-tex.json", "w", encoding="utf-8").write(json.dumps(out, ensure_ascii=False, indent=2))
    print("TEX", json.dumps(out, ensure_ascii=False)[:500])
    unreal.SystemLibrary.quit_editor()
