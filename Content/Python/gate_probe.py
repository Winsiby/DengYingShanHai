import unreal, json
out = {"actors": [], "profile": []}
try:
    MAP = "/Game/DengYingShanHai/Maps/L_DY_Main"
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).load_level(MAP)
    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    for a in eas.get_all_level_actors():
        lab = a.get_actor_label()
        if not any(k in lab for k in ("RearBase", "RearWall", "Gate", "Door", "ExtBase", "Facade")):
            continue
        org, ext = a.get_actor_bounds(False)
        info = {"label": lab, "loc": [round(float(a.get_actor_location().x),1), round(float(a.get_actor_location().y),1), round(float(a.get_actor_location().z),1)],
                "ext": [round(float(ext.x),1), round(float(ext.y),1), round(float(ext.z),1)], "comps": []}
        for c in a.get_components_by_class(unreal.StaticMeshComponent):
            m = c.get_editor_property("static_mesh")
            info["comps"].append({"prof": str(c.get_collision_profile_name()),
                                  "mesh": m.get_path_name() if m else None})
        out["actors"].append(info)
    # vertical profile through the doorway plane x=-1846..-1800 at y=-210
    for z in range(20, 460, 40):
        h = unreal.SystemLibrary.capsule_trace_single(world, unreal.Vector(-1950,-210,z), unreal.Vector(-1750,-210,z),
            34.0, 40.0, unreal.TraceTypeQuery.TRACE_TYPE_QUERY1, False, [], unreal.DrawDebugTrace.NONE, True)
        if h is None:
            out["profile"].append({"z": z, "hit": None})
        else:
            d = h.to_dict()
            a = d.get("hit_actor")
            out["profile"].append({"z": z, "hit": (a.get_actor_label() if a else None), "overlap": bool(d.get("initial_overlap"))})
    print("GATE " + json.dumps(out, ensure_ascii=False))
except Exception as e:
    print("GATE_ERR " + str(e))
finally:
    unreal.SystemLibrary.quit_editor()
