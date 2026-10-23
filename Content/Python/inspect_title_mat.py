# -*- coding: utf-8 -*-
import json, traceback, unreal
EAL = unreal.EditorAssetLibrary
MEL = unreal.MaterialEditingLibrary
OUT = "D:/灯影山海/Saved/Audit-2026-10-22-FourAct/title-material.json"
out = {"error": None}
try:
    mat = EAL.load_asset("/Game/DengYingShanHai/Stage/ArtMainline/Materials/M_DY_TitleGlyph")
    out["class"] = mat.get_class().get_name()
    out["textures"] = {}
    for n in MEL.get_texture_parameter_names(mat):
        t = MEL.get_material_instance_texture_parameter_value(mat, n)
        out["textures"][str(n)] = t.get_path_name() if t else None
    out["scalars"] = {str(n): MEL.get_material_instance_scalar_parameter_value(mat, n)
                      for n in MEL.get_scalar_parameter_names(mat)}
    out["blend"] = str(mat.get_editor_property("blend_mode"))
    out["shading"] = str(mat.get_editor_property("shading_model"))
    out["twosided"] = bool(mat.get_editor_property("two_sided"))
    for n, p in out.get("textures", {}).items():
        if p:
            tex = EAL.load_asset(p.split(".")[0])
            if tex:
                out.setdefault("tex_info", {})[n] = dict(size=[tex.blueprint_get_size_x(), tex.blueprint_get_size_y()],
                    srgb=bool(tex.get_editor_property("srgb")), compression=str(tex.get_editor_property("compression_settings")))
except Exception:
    out["error"] = traceback.format_exc()
finally:
    open(OUT, "w", encoding="utf-8").write(json.dumps(out, ensure_ascii=False, indent=2))
    print("TITLE_MAT", json.dumps(out, ensure_ascii=False)[:900])
    unreal.SystemLibrary.quit_editor()
