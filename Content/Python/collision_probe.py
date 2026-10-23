import unreal, json
MAP = "/Game/DengYingShanHai/Maps/L_DY_Main"
unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).load_level(MAP)
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
actors = eas.get_all_level_actors()
print("PROBE actors", len(actors))
probe = [a for a in actors if "PlayerStart" in a.get_class().get_name()][:1]
probe += [a for a in actors if a.get_component_by_class(unreal.StaticMeshComponent) is not None][:5]
for a in probe:
    print("PROBE ACTOR", a.get_class().get_name(), a.get_actor_label())
    try:
        cs = a.get_components_by_class(unreal.StaticMeshComponent)
        print("  staticmesh comps", len(cs), [c.get_name() for c in cs][:5])
    except Exception as e:
        print("  ERR staticmesh", e)
    try:
        cs = a.get_components_by_class(unreal.PrimitiveComponent)
        print("  primitive comps", len(cs))
    except Exception as e:
        print("  ERR primitive", e)
    try:
        rc = a.get_editor_property("root_component")
        print("  root", rc.get_class().get_name(), rc.get_name())
        print("  root props sample:", [p for p in ("collision_enabled","collision_profile_name","bounds") if rc.get_editor_property(p) is not None])
    except Exception as e:
        print("  ERR root", e)
unreal.SystemLibrary.quit_editor()
