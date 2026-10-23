# -*- coding: utf-8 -*-
"""Persist the calibrated cast transform: loc from Kuafu, yaw 180 (concept orientation), scale 1.1."""
import json, unreal
EAL = unreal.EditorAssetLibrary
P = "/Game/DengYingShanHai/Puppets/DA_DYPuppetCast"
LOC = (0.0, -42.44, -104.57)
da = EAL.load_asset(P)
old = da.get_editor_property("figures")
arr = unreal.Array(unreal.DYPuppetFigureEntry)
rows = []
for i in range(len(old)):
    src = old[i]
    e = unreal.DYPuppetFigureEntry()
    e.set_editor_property("label", src.label)
    e.set_editor_property("skeletal_mesh", src.skeletal_mesh)
    e.set_editor_property("pose_animations", src.pose_animations)
    e.set_editor_property("hide_staff", src.hide_staff)
    e.set_editor_property("mesh_relative_location", unreal.Vector(*LOC))
    # unreal.Rotator(a, b, c) binds positional args as (roll, pitch, yaw).
    e.set_editor_property("mesh_relative_rotation", unreal.Rotator(0.0, 0.0, 180.0))
    k = 0.8 if i == 0 else 1.1
    e.set_editor_property("mesh_relative_scale", unreal.Vector(k, k, k))
    arr.append(e)
    rows.append(dict(i=i, label=str(src.label), scale=k, yaw=180.0))
da.set_editor_property("figures", arr)
saved = EAL.save_loaded_asset(da)
check = EAL.load_asset(P).get_editor_property("figures")
readback = []
for i in range(len(check)):
    f = check[i]
    r = f.mesh_relative_rotation
    readback.append(dict(label=str(f.label),
                         loc=[round(v, 2) for v in (f.mesh_relative_location.x, f.mesh_relative_location.y, f.mesh_relative_location.z)],
                         pitch=round(r.pitch, 2), yaw=round(r.yaw, 2), roll=round(r.roll, 2),
                         scale=round(f.mesh_relative_scale.x, 3), hide_staff=f.hide_staff))
out = dict(saved=saved, requested=rows, readback=readback,
           rotator_note="unreal.Rotator(a,b,c) positional order is roll,pitch,yaw")
open("D:/灯影山海/Saved/Audit-2026-10-22-FourAct/cast-transform-final.json", "w", encoding="utf-8").write(
    json.dumps(out, ensure_ascii=False, indent=2))
print("CAST_XF_FINAL", json.dumps(readback, ensure_ascii=False))
unreal.SystemLibrary.quit_editor()
