# -*- coding: utf-8 -*-
"""Persist a larger in-stage display scale for the three new puppets."""
import json, unreal
EAL = unreal.EditorAssetLibrary
P = "/Game/DengYingShanHai/Puppets/DA_DYPuppetCast"
da = EAL.load_asset(P)
old = da.get_editor_property("figures")
rows = []
new_arr = unreal.Array(unreal.DYPuppetFigureEntry)
for i in range(len(old)):
    src = old[i]
    e = unreal.DYPuppetFigureEntry()
    e.set_editor_property("label", src.label)
    e.set_editor_property("skeletal_mesh", src.skeletal_mesh)
    e.set_editor_property("pose_animations", src.pose_animations)
    e.set_editor_property("hide_staff", src.hide_staff)
    e.set_editor_property("mesh_relative_location", src.mesh_relative_location)
    e.set_editor_property("mesh_relative_rotation", src.mesh_relative_rotation)
    k = 0.8 if i == 0 else 1.1
    e.set_editor_property("mesh_relative_scale", unreal.Vector(k, k, k))
    new_arr.append(e)
    rows.append(dict(i=i, label=str(src.label), scale=k))
da.set_editor_property("figures", new_arr)
saved = EAL.save_loaded_asset(da)
unreal.EditorAssetLibrary.make_directory("/Game/DengYingShanHai/Puppets")
check = EAL.load_asset(P).get_editor_property("figures")
readback = [round(float(check[i].mesh_relative_scale.x), 3) for i in range(len(check))]
out = dict(saved=saved, requested=rows, readback=readback)
open("D:/灯影山海/Saved/Audit-2026-10-22-FourAct/cast-scale-final.json", "w", encoding="utf-8").write(json.dumps(out, ensure_ascii=False, indent=2))
print("SETSCALE", json.dumps(out, ensure_ascii=False))
unreal.SystemLibrary.quit_editor()
