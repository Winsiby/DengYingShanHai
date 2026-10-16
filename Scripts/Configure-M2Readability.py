"""Idempotent, map-local readability fix for inherited Phase1 test fixtures.

Run after Create-M2DevSlice.py. Does not rebuild actors, input, definitions,
Blueprints, exposure or light settings. M1 remains an independent test map.
"""
import unreal

M2_MAP = "/Game/DengYingShanHai/Dev/M2/Maps/LV_M2PuzzleLab"
FIXTURES = {
    "DEV_CameraWall": unreal.Vector(-100.0, -650.0, 170.0),
    "DEV_InnerCornerA": unreal.Vector(420.0, -750.0, 150.0),
    "DEV_InnerCornerB": unreal.Vector(690.0, -660.0, 150.0),
}

def require(value, message):
    if not value:
        raise RuntimeError(message)
    return value

def main():
    levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    require(levels.load_level(M2_MAP), "Cannot load the explicit M2 Dev map")
    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    require(world.get_path_name() == M2_MAP + ".LV_M2PuzzleLab", "Unexpected world: refuse map writes")
    actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
    selected = {}
    for label in FIXTURES:
        matches = [actor for actor in actors if actor.get_actor_label() == label]
        require(len(matches) == 1, "Expected exactly one fixture: " + label)
        require(isinstance(matches[0], unreal.StaticMeshActor), "Unexpected fixture type: " + label)
        selected[label] = matches[0]
    # All preconditions above are checked before the first mutation.
    changed = False
    for label, location in FIXTURES.items():
        actor = selected[label]
        old = actor.get_actor_location()
        if old == location:
            unreal.log("DY_M2_READABILITY_NOOP " + label)
            continue
        actor.set_actor_location(location, False, False)
        changed = True
        unreal.log("DY_M2_READABILITY_MOVE " + label + " " + str(old) + " -> " + str(location))
    if changed:
        require(levels.save_current_level(), "Cannot save the explicit M2 Dev map")
    unreal.log("DY_M2_READABILITY_CONFIGURED: three fixture positions; no gameplay/light/camera changes")

if __name__ == "__main__":
    main()
