# -*- coding: utf-8 -*-
import json, unreal
EAL = unreal.EditorAssetLibrary
da = EAL.load_asset("/Game/DengYingShanHai/Puppets/DA_DYPuppetCast")
figs = da.get_editor_property("figures")
f = figs[1]
props = [p for p in dir(f) if not p.startswith("_")]
open("D:/灯影山海/Saved/Audit-2026-10-22-FourAct/entry-props.json","w",encoding="utf-8").write(json.dumps(props, indent=1))
print(json.dumps(props))
unreal.SystemLibrary.quit_editor()
