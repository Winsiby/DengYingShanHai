# -*- coding: utf-8 -*-
import json, unreal
EAL = unreal.EditorAssetLibrary
da = EAL.load_asset("/Game/DengYingShanHai/Puppets/DA_DYPuppetCast")
rows = []
for i, f in enumerate(da.get_editor_property("figures")):
    s = f.get_editor_property("mesh_relative_scale"); l = f.get_editor_property("mesh_relative_location")
    rows.append(dict(i=i, label=str(f.get_editor_property("label")), scale=[round(s.x,3), round(s.y,3), round(s.z,3)],
                     loc=[round(l.x,2), round(l.y,2), round(l.z,2)]))
open("D:/灯影山海/Saved/Audit-2026-10-22-FourAct/cast-scale-final.json", "w", encoding="utf-8").write(json.dumps(rows, ensure_ascii=False, indent=2))
print("CAST", json.dumps(rows, ensure_ascii=False))
unreal.SystemLibrary.quit_editor()
