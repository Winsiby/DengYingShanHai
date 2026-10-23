import unreal, json
report = {"changed": [], "sweep": [], "saved": False}
try:
    MAP = "/Game/DengYingShanHai/Maps/L_DY_Main"
    les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    les.load_level(MAP)
    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)

    # 1) disable collision on backdrop mountain cards
    for a in eas.get_all_level_actors():
        lab = a.get_actor_label()
        if not lab.startswith("ART_B1_Mountain"):
            continue
        for c in a.get_components_by_class(unreal.StaticMeshComponent):
            before = str(c.get_collision_profile_name())
            c.set_collision_profile_name("NoCollision")
            c.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
            report["changed"].append({"label": lab, "before": before, "after": str(c.get_collision_profile_name())})

    # 2) re-sweep the approach lanes with a pawn-size capsule
    def cap(x, y, z, fx, fy, fz):
        h = unreal.SystemLibrary.capsule_trace_single(world, unreal.Vector(x,y,z), unreal.Vector(x+fx,y+fy,z+fz),
            34.0, 88.0, unreal.TraceTypeQuery.TRACE_TYPE_QUERY1, False, [], unreal.DrawDebugTrace.NONE, True)
        if h is None: return None
        d = h.to_dict()
        if d.get("initial_overlap"): return {"overlap": True}
        a = d.get("hit_actor")
        ip = d.get("impact_point")
        try: lab = a.get_actor_label()
        except Exception: lab = str(a)
        return {"label": lab, "at": [round(float(ip.x),1), round(float(ip.y),1), round(float(ip.z),1)]}
    for y in (-310, -210, -110):
        first = None
        for x in range(-6900, -100, 50):
            h = cap(x, y, 150, 50, 0, 0)
            if h and not h.get("overlap"):
                first = dict(h, from_x=x); break
        report["sweep"].append({"lane_y": y, "first": first})

    report["saved"] = bool(les.save_current_level())
    print("FIX " + json.dumps(report, ensure_ascii=False))
except Exception as e:
    print("FIX_ERR " + str(e))
finally:
    unreal.SystemLibrary.quit_editor()
