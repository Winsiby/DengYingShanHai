import unreal, json
out = []
try:
    MAP = "/Game/DengYingShanHai/Maps/L_DY_Main"
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).load_level(MAP)
    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    def cap(x, y, z, fx, fy, fz):
        h = unreal.SystemLibrary.capsule_trace_single(world, unreal.Vector(x,y,z), unreal.Vector(x+fx,y+fy,z+fz),
            34.0, 88.0, unreal.TraceTypeQuery.TRACE_TYPE_QUERY1, False, [], unreal.DrawDebugTrace.NONE, True)
        if h is None: return None
        d = h.to_dict()
        if d.get("initial_overlap"): return {"overlap": True}
        a = d.get("hit_actor")
        lab = None
        try: lab = a.get_actor_label()
        except Exception: lab = str(a)
        ip = d.get("impact_point")
        return {"label": lab, "at": [round(float(ip.x),1), round(float(ip.y),1), round(float(ip.z),1)]}
    for y in (-510,-410,-310,-210,-110,-10,90):
        first = None
        for x in range(-6900, -100, 50):
            h = cap(x, y, 150, 50, 0, 0)
            if h and not h.get("overlap"):
                first = dict(h, from_x=x); break
        out.append({"y": y, "first": first})
    first = None
    for x in range(-200, 1600, 50):
        h = cap(x, -210, 150, 50, 0, 0)
        if h and not h.get("overlap"):
            first = dict(h, from_x=x); break
    out.append({"y": -210, "theater": first})
    print("SWEEP " + json.dumps(out, ensure_ascii=False))
except Exception as e:
    print("SWEEP_ERR " + str(e))
finally:
    unreal.SystemLibrary.quit_editor()
