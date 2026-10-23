"""Create ONLY a Dev/M3 geometry lab; keep all accepted M2 assets untouched.

P02 definition, input, camera and light settings are inherited for operating the
fixture. This is NOT a P03 puzzle definition or a finale implementation.
"""
import unreal

SOURCE = "/Game/DengYingShanHai/Dev/M2/Maps/LV_M2PuzzleLab"
DESTINATION = "/Game/DengYingShanHai/Dev/M3/Maps/LV_M3GeometryProbe"


def require(value, message):
    if not value:
        raise RuntimeError(message)
    return value


def main():
    require(unreal.EditorAssetLibrary.does_asset_exist(SOURCE), "Accepted M2 map missing")
    # Refuse to overwrite an existing experiment rather than silently rebuild it.
    require(not unreal.EditorAssetLibrary.does_asset_exist(DESTINATION), "M3 lab already exists; verify it instead of overwriting")
    unreal.EditorAssetLibrary.make_directory("/Game/DengYingShanHai/Dev/M3/Maps")
    require(unreal.EditorAssetLibrary.duplicate_asset(SOURCE, DESTINATION), "Cannot duplicate accepted fixture")
    levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    actors_api = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    require(levels.load_level(DESTINATION), "Cannot load new M3 lab")
    actors = {a.get_actor_label(): a for a in actors_api.get_all_level_actors()}
    for label in ("M2_LightRig_P02", "M2_Puppet_P02_Controlled", "DEV_BackScreen"):
        require(label in actors, "Missing explicit fixture: " + label)
    probe_class = require(unreal.load_class(None, "/Script/DengYingShanHai.DYStaffProjectionProbe"), "Native geometry probe missing")
    probe = require(actors_api.spawn_actor_from_class(probe_class, unreal.Vector(915, -420, 650), unreal.Rotator(pitch=0, yaw=180, roll=0), False), "Cannot spawn probe")
    probe.set_actor_label("M3_StaffProjectionProbe_AB")
    probe.set_editor_property("tags", [unreal.Name("DY_M3GeometryOnly")])
    probe.set_editor_property("light", actors["M2_LightRig_P02"])
    probe.set_editor_property("puppet", actors["M2_Puppet_P02_Controlled"])
    probe.set_editor_property("screen_actor", actors["DEV_BackScreen"])
    for text in probe.get_components_by_class(unreal.TextRenderComponent):
        text.set_world_size(22.0 if text.get_name() == "Readout" else 35.0)
    probe.refresh_projection()
    require(levels.save_current_level(), "Cannot save new M3 lab")
    unreal.log("DY_M3_GEOMETRY_CREATED: " + DESTINATION)


main()
