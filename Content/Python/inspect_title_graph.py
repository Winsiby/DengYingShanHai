# -*- coding: utf-8 -*-
import json, traceback, unreal
EAL = unreal.EditorAssetLibrary
MEL = unreal.MaterialEditingLibrary
OUT = "D:/灯影山海/Saved/Audit-2026-10-22-FourAct/title-graph.json"
out = {"nodes": [], "error": None}
try:
    mat = EAL.load_asset("/Game/DengYingShanHai/Stage/ArtMainline/Materials/M_DY_TitleGlyph")
    for e in MEL.get_material_expressions(mat):
        row = dict(cls=e.get_class().get_name(), name=e.get_name())
        for prop in ("texture", "const_a", "const_b", "constant", "parameter_name", "text"):
            try:
                v = e.get_editor_property(prop)
                if v is not None:
                    row[prop] = v.get_path_name() if hasattr(v, "get_path_name") else str(v)
            except Exception:
                pass
        out["nodes"].append(row)
except Exception:
    out["error"] = traceback.format_exc()
finally:
    open(OUT, "w", encoding="utf-8").write(json.dumps(out, ensure_ascii=False, indent=2))
    print("GRAPH", len(out["nodes"]))
    unreal.SystemLibrary.quit_editor()
