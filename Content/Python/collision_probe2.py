import unreal, json, collections
MAP = "/Game/DengYingShanHai/Maps/L_DY_Main"
unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).load_level(MAP)
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
actors = eas.get_all_level_actors()
cnt = collections.Counter(a.get_class().get_name() for a in actors)
print("CLS " + json.dumps(dict(cnt.most_common(40)), ensure_ascii=False))
sm = [a for a in actors if a.get_component_by_class(unreal.StaticMeshComponent) is not None][0]
c = sm.get_component_by_class(unreal.StaticMeshComponent)
print("CBLS " + json.dumps([n for n in dir(c) if "collision" in n.lower()], ensure_ascii=False))
print("CALL " + json.dumps([n for n in dir(c) if "bounds" in n.lower() or "profile" in n.lower()], ensure_ascii=False))
try:
    print("PROF " + str(c.get_collision_profile_name()))
except Exception as e:
    print("PROF_ERR " + str(e))
try:
    print("ENAB " + str(c.get_collision_enabled()))
except Exception as e:
    print("ENAB_ERR " + str(e))
try:
    print("BND " + str(c.bounds.origin) + " ext " + str(c.bounds.box_extent))
except Exception as e:
    print("BND_ERR " + str(e))
# all components of a mesh actor
allc = sm.get_components_by_class(unreal.ActorComponent)
print("ALLCOMP " + json.dumps([x.get_class().get_name()+":"+x.get_name() for x in allc], ensure_ascii=False))
unreal.SystemLibrary.quit_editor()
