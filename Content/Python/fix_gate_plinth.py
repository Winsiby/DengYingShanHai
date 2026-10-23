import unreal, json
R = {"ok": False, "split": None, "sweep": [], "error": None, "saved": False}
try:
    MAP = "/Game/DengYingShanHai/Maps/L_DY_Main"
    les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    les.load_level(MAP)
    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    base = None
    for a in eas.get_all_level_actors():
        if a.get_actor_label() == "ART_EXT_RearBase":
            base = a
    if base is None:
        raise RuntimeError("ART_EXT_RearBase missing")
    comp = base.get_component_by_class(unreal.StaticMeshComponent)
    mesh = comp.get_editor_property("static_mesh")
    mats = [comp.get_material(i) for i in range(comp.get_num_materials())]

    # left segment: y -1230..-540
    base.set_actor_location(unreal.Vector(-1828.0, -885.0, 65.0), False, False)
    base.set_actor_scale3d(unreal.Vector(0.36, 6.9, 1.3))

    # right segment: y 120..1230
    right = eas.spawn_actor_from_class(unreal.StaticMeshActor, unreal.Vector(-1828.0, 675.0, 65.0), unreal.Rotator(0.0, 0.0, 0.0), True)
    right.set_actor_label("ART_EXT_RearBase_R")
    rc = right.get_component_by_class(unreal.StaticMeshComponent)
    rc.set_editor_property("static_mesh", mesh)
    rc.set_editor_property("mobility", unreal.ComponentMobility.STATIC)
    for i, m in enumerate(mats):
        if m: rc.set_material(i, m)
    right.set_actor_scale3d(unreal.Vector(0.36, 11.1, 1.3))
    R["split"] = {"mesh": mesh.get_path_name() if mesh else None,
                  "materials": [m.get_path_name() if m else None for m in mats],
                  "left": {"label": base.get_actor_label(), "loc": str(base.get_actor_location()), "scale": str(base.get_actor_scale3d())},
                  "right": {"label": right.get_actor_label(), "loc": str(right.get_actor_location()), "scale": str(right.get_actor_scale3d())}}

    def cap(x, y, z, fx, fy, fz):
        h = unreal.SystemLibrary.capsule_trace_single(world, unreal.Vector(x,y,z), unreal.Vector(x+fx,y+fy,z+fz),
            34.0, 88.0, unreal.TraceTypeQuery.TRACE_TYPE_QUERY1, False, [], unreal.DrawDebugTrace.NONE, True)
        if h is None: return None
        d = h.to_dict()
        if d.get("initial_overlap"): return {"overlap": True}
        a = d.get("hit_actor"); ip = d.get("impact_point")
        try: lab = a.get_actor_label()
        except Exception: lab = str(a)
        return {"label": lab, "at": [round(float(ip.x),1), round(float(ip.y),1), round(float(ip.z),1)]}

    first = None
    for x in range(-2000, 400, 50):
        h = cap(x, -210, 150, 50, 0, 0)
        if h and not h.get("overlap"):
            first = dict(h, from_x=x); break
    R["sweep"].append({"lane": "door->auditorium", "first": first})
    for y in (-400, -210, 0, 60):
        f = None
        for x in range(-2000, -1500, 50):
            h = cap(x, y, 150, 50, 0, 0)
            if h and not h.get("overlap"):
                f = dict(h, from_x=x); break
        R["sweep"].append({"lane_y": y, "first": f})
    R["saved"] = bool(les.save_current_level())
    R["ok"] = True
    print("SPLIT " + json.dumps(R, ensure_ascii=False))
except Exception as e:
    R["error"] = str(e)
    print("SPLIT_ERR " + json.dumps(R, ensure_ascii=False))
finally:
    unreal.SystemLibrary.quit_editor()
