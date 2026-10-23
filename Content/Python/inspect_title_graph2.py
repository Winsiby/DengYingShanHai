# -*- coding: utf-8 -*-
import json, traceback, unreal
EAL = unreal.EditorAssetLibrary
MEL = unreal.MaterialEditingLibrary
out = {"nodes": [], "error": None}
try:
    mat = EAL.load_asset("/Game/DengYingShanHai/Stage/ArtMainline/Materials/M_DY_TitleGlyph")
    for e in MEL.get_material_expressions(mat):
        row = dict(cls=e.get_class().get_name(), name=e.get_name())
        for prop in ("r", "g", "b", "a", "const_a", "const_b", "const_r", "const_g", "const_b2"):
            try:
                row[prop] = float(e.get_editor_property(prop))
            except Exception:
                pass
        try:
            inputs = []
            for idx, nm in enumerate(("A", "B", "RGB")):
                try:
                    src = MEL.get_input_node(e, 0) if idx == 0 else None
                except Exception:
                    src = None
                inputs.append(src.get_name() if src else None)
            row["inputs_resolved"] = inputs
        except Exception:
            pass
        out["nodes"].append(row)
except Exception:
    out["error"] = traceback.format_exc()
finally:
    open("D:/灯影山海/Saved/Audit-2026-10-22-FourAct/title-graph2.json", "w", encoding="utf-8").write(json.dumps(out, ensure_ascii=False, indent=2))
    print("G2", json.dumps(out["nodes"])[:600])
    unreal.SystemLibrary.quit_editor()
