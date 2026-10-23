import unreal, json
R = {"walk": [], "blockers": {}}
try:
    MAP = "/Game/DengYingShanHai/Maps/L_DY_Main"
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).load_level(MAP)
    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()

    def floor_z(x, y):
        h = unreal.SystemLibrary.line_trace_single(world, unreal.Vector(x,y,600), unreal.Vector(x,y,-400),
            unreal.TraceTypeQuery.TRACE_TYPE_QUERY1, False, [], unreal.DrawDebugTrace.NONE, True)
        if h is None: return None
        d = h.to_dict()
        ip = d.get("impact_point")
        return float(ip.z)

    def walk(x, y, fz):
        h = unreal.SystemLibrary.capsule_trace_single(world, unreal.Vector(x,y,fz+90.0), unreal.Vector(x+30.0,y,fz+90.0),
            34.0, 88.0, unreal.TraceTypeQuery.TRACE_TYPE_QUERY1, False, [], unreal.DrawDebugTrace.NONE, True)
        if h is None: return None
        d = h.to_dict()
        if d.get("initial_overlap"): return {"overlap": True}
        a = d.get("hit_actor"); ip = d.get("impact_point")
        try: lab = a.get_actor_label()
        except Exception: lab = str(a)
        return {"label": lab, "at": [round(float(ip.x),1), round(float(ip.y),1), round(float(ip.z),1)]}

    blocks = []
    for x in range(-6900, 0, 30):
        fz = floor_z(x, -210)
        if fz is None:
            R["walk"].append({"x": x, "floor": None}); continue
        w = walk(x, -210, fz)
        if w and not w.get("overlap"):
            blocks.append(dict(w, x=x, floor=round(fz,1)))
    # group consecutive
    for b in blocks:
        R["blockers"].setdefault(b["label"], []).append(b["x"])
    R["walk"] = blocks[:80]
    print("WALK " + json.dumps({"n": len(blocks), "by": {k: [min(v), max(v), len(v)] for k, v in R["blockers"].items()}}, ensure_ascii=False))
except Exception as e:
    print("WALK_ERR " + str(e))
finally:
    unreal.SystemLibrary.quit_editor()
