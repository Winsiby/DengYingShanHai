# -*- coding: utf-8 -*-
import json, unreal
OUT = "D:/灯影山海/Saved/Audit-2026-10-22-FourAct/entry-open-verify.json"
R = {"ok": False, "cards": [], "plinth": [], "walk_hits": [], "checks": [], "errors": []}
def chk(name, cond, detail=""):
    R["checks"].append({"name": name, "ok": bool(cond), "detail": detail})
    if not cond:
        R["errors"].append(name + " " + detail)
try:
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).load_level("/Game/DengYingShanHai/Maps/L_DY_Main")
    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    ACT = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    cards = []
    plinth = []
    for a in ACT.get_all_level_actors():
        lab = a.get_actor_label()
        if lab.startswith("ART_B1_Mountain"):
            comps = a.get_components_by_class(unreal.StaticMeshComponent)
            profs = [str(c.get_collision_profile_name()) for c in comps]
            en = [str(c.get_collision_enabled()) for c in comps]
            cards.append({"label": lab, "profiles": profs, "enabled": en})
            chk("card-nocollision:" + lab, all(p in ("NoCollision", "None") for p in profs), str(profs) + " / " + str(en))
        if lab in ("ART_EXT_RearBase", "ART_EXT_RearBase_R"):
            org, ext = a.get_actor_bounds(False)
            plinth.append({"label": lab, "loc": [round(float(org.x),1), round(float(org.y),1), round(float(org.z),1)],
                           "y_range": [round(float(org.y - ext.y),1), round(float(org.y + ext.y),1)],
                           "z_range": [round(float(org.z - ext.z),1), round(float(org.z + ext.z),1)]})
    R["cards"] = cards
    R["plinth"] = plinth
    chk("cards6", len(cards) == 6, str(len(cards)))
    chk("plinth2", len(plinth) == 2, str(len(plinth)))
    # door lane must be free of plinth between y=-540..120
    for p in plinth:
        chk("plinth-outside-door:" + p["label"], p["y_range"][1] <= -530 or p["y_range"][0] >= 110, str(p["y_range"]))
    def floor_z(x, y):
        h = unreal.SystemLibrary.line_trace_single(world, unreal.Vector(x, y, 600), unreal.Vector(x, y, -400),
            unreal.TraceTypeQuery.TRACE_TYPE_QUERY1, False, [], unreal.DrawDebugTrace.NONE, True)
        if h is None:
            return None
        return float(h.to_dict().get("impact_point").z)
    def step(x, y, fz):
        h = unreal.SystemLibrary.capsule_trace_single(world, unreal.Vector(x, y, fz + 90.0), unreal.Vector(x + 30.0, y, fz + 90.0),
            34.0, 88.0, unreal.TraceTypeQuery.TRACE_TYPE_QUERY1, False, [], unreal.DrawDebugTrace.NONE, True)
        if h is None:
            return None
        d = h.to_dict()
        if d.get("initial_overlap"):
            return None
        ip = d.get("impact_point")
        a = d.get("hit_actor")
        try:
            lab = a.get_actor_label()
        except Exception:
            lab = "?"
        return {"label": lab, "at": [round(float(ip.x),1), round(float(ip.y),1), round(float(ip.z),1)]}
    for x in range(-6900, 0, 30):
        fz = floor_z(x, -210)
        if fz is None:
            continue
        s = step(x, -210, fz)
        if s:
            R["walk_hits"].append(dict(s, x=x, floor=round(fz, 1)))
    names = sorted(set(h["label"] for h in R["walk_hits"]))
    R["walk_hit_names"] = names
    chk("walk-no-wall", all(n in ("DYTheater_ExtPath", "DYTheater_GateStep", "M05_EntryRearGuard") for n in names), str(names))
    R["ok"] = len(R["errors"]) == 0
except Exception:
    import traceback
    R["errors"].append(traceback.format_exc())
open(OUT, "w", encoding="utf-8").write(json.dumps(R, ensure_ascii=False, indent=2))
print("ENTRYOPEN " + json.dumps({"ok": R["ok"], "checks": len(R["checks"]), "errors": R["errors"][:2], "hits": R.get("walk_hit_names")}, ensure_ascii=False))
unreal.SystemLibrary.quit_editor()
