"""Cold-read actual references and geometry. No asset writes or simulated pose math."""
import unreal

MAP = "/Game/DengYingShanHai/Dev/M3/Maps/LV_M3GeometryProbe"


def check(value, message):
    if not value:
        raise RuntimeError("M3 geometry FAIL: " + message)
    unreal.log("M3 geometry PASS: " + message)


def main():
    check(unreal.EditorAssetLibrary.does_asset_exist(MAP), "separate Dev/M3 map exists")
    check(unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).load_level(MAP), "map cold-loads")
    actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
    check(len(actors) == 26, "accepted 25 actors plus exactly one probe")
    by_label = {a.get_actor_label(): a for a in actors}
    probe = by_label.get("M3_StaffProjectionProbe_AB")
    check(probe is not None, "probe exists")
    light = by_label["M2_LightRig_P02"]
    puppet = by_label["M2_Puppet_P02_Controlled"]
    receiver = by_label["DEV_BackScreen"]
    check(probe.get_editor_property("light") == light, "explicit light reference is local to duplicated map")
    check(probe.get_editor_property("puppet") == puppet, "explicit puppet reference is local to duplicated map")
    check(probe.get_editor_property("screen_actor") == receiver, "explicit receiver reference is local to duplicated map")
    # bCanEverTick is not reflected to Python. Native automation tests that flag;
    # cold-read only the separately observable enabled state, without claiming more.
    check(not probe.is_actor_tick_enabled(), "probe Tick is disabled in the saved fixture")
    check(by_label["M2_PuzzleDirector_P02"].get_editor_property("evaluation_frequency_hz") == 15.0, "inherited evaluation remains 15 Hz")
    definition = by_label["M2_PuzzleDirector_P02"].get_editor_property("puzzle_definition")
    check(str(definition.get_editor_property("puzzle_id")) == "P02_ChaseForm", "P02 sandbox definition retained; no invented P03 targets")
    probe.refresh_projection()
    capture = probe.get_last_capture()
    check(capture.has_geometry and capture.staff.is_valid, "actual Staff/emitter/receiver produce value evidence")
    check(capture.emitter_world != light.get_actor_location(), "reads emitter rather than actor pivot")
    check(abs(capture.end_a.world_position.x - 925.0) < 0.001, "uses near receiving surface X925, not cube centre X950")
    check(capture.end_a.status == unreal.DYStaffProjectionStatus.ON_SCREEN, "editor initial A is inside receiver")
    check(capture.end_b.status == unreal.DYStaffProjectionStatus.ON_SCREEN, "editor initial B is inside receiver")
    texts = probe.get_components_by_class(unreal.TextRenderComponent)
    check(len(texts) == 3 and all(not c.get_editor_property("cast_shadow") for c in texts), "debug text cannot cast gameplay shadows")
    rotation = probe.get_actor_rotation()
    check(abs(rotation.yaw - 180.0) < 0.01 and abs(rotation.roll) < 0.01, "readout faces backstage without an upside-down roll")
    check(all(c.get_editor_property("world_size") == (22.0 if c.get_name() == "Readout" else 35.0) for c in texts), "readout and A/B have explicit legible Dev sizes")
    unreal.log("M3_EDITOR_GEOMETRY (not runtime pose): emitter=%s staffA=%s shadowA=%s shadowB=%s" %
               (capture.emitter_world, capture.staff.end_a_world, capture.end_a.world_position, capture.end_b.world_position))
    unreal.log("DY_M3_GEOMETRY_VERIFIED")


main()
