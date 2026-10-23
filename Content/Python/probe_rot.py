# -*- coding: utf-8 -*-
import json, unreal
EAL = unreal.EditorAssetLibrary
r1 = unreal.Rotator(0.0, 180.0, 0.0)
info = dict(pos=(r1.pitch, r1.yaw, r1.roll))
da = EAL.load_asset("/Game/DengYingShanHai/Puppets/DA_DYPuppetCast")
f = da.get_editor_property("figures")[1]
rr = f.mesh_relative_rotation
info["stored"] = (rr.pitch, rr.yaw, rr.roll)
info["str"] = str(rr)
open("D:/灯影山海/Saved/Audit-2026-10-22-FourAct/rot-probe.json","w",encoding="utf-8").write(json.dumps(info,ensure_ascii=False,indent=2))
print("ROTPROBE", json.dumps(info, ensure_ascii=False))
unreal.SystemLibrary.quit_editor()
