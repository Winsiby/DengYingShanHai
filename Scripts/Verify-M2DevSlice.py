"""Independently reload and verify the saved M2 Dev slice in UE 5.8."""

import unreal


MAP_PATH = "/Game/DengYingShanHai/Dev/M2/Maps/LV_M2PuzzleLab"
DEFINITION_PATH = "/Game/DengYingShanHai/Dev/M2/Data/DA_DY_P02_ChaseForm"
STAGE_PRESENTATION_PATH = "/Game/DengYingShanHai/Stage/BP_DYStagePresentation"
STAGE_ENVIRONMENT_PATH = "/Game/DengYingShanHai/Stage/BP_DYStageEnvironment"
M2_TAG = unreal.Name("DY_M2Generated")
failures = []


def check(condition, label):
    if condition:
        unreal.log(f"DY M2 Verify: PASS {label}")
        return True
    failures.append(label)
    unreal.log_error(f"DY M2 Verify: FAIL {label}")
    return False


def load(path):
    return unreal.load_asset(f"{path}.{path.rsplit('/', 1)[-1]}")


def verify_definition():
    definition = load(DEFINITION_PATH)
    if not check(definition is not None, "P02 definition loads"):
        return None
    check(str(definition.get_editor_property("puzzle_id")) == "P02_ChaseForm", "P02 id")
    check(
        str(definition.get_editor_property("required_puppet_pose_id"))
        == "P02_StrideReach",
        "P02 requires the authored reach pose",
    )
    check(
        abs(definition.get_editor_property("required_hold_seconds") - 1.25) < 0.0001,
        "P02 hold is 1.25 seconds",
    )
    light = definition.get_editor_property("light_position")
    puppet = definition.get_editor_property("puppet_position")
    check(bool(light.get_editor_property("enabled")), "light condition enabled")
    check(abs(light.get_editor_property("target") - 0.72) < 0.0001, "light target is 0.72")
    check(bool(puppet.get_editor_property("enabled")), "puppet condition enabled")
    check(abs(puppet.get_editor_property("target") - 0.80) < 0.0001, "puppet target is 0.80")
    return definition


def verify_map(definition):
    level_subsystem = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    if not check(level_subsystem.load_level(MAP_PATH), "M2 Dev map reloads from disk"):
        return
    actor_subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    generated = [
        actor
        for actor in actor_subsystem.get_all_level_actors()
        if M2_TAG in list(actor.get_editor_property("tags"))
    ]
    check(len(generated) == 6, f"exactly six M2 generated actors (found {len(generated)})")
    by_label = {actor.get_actor_label(): actor for actor in generated}
    for label in (
        "M2_LightRig_P02",
        "M2_Puppet_P02_Controlled",
        "M2_PuzzleDirector_P02",
        "M2_StagePresentation",
        "M2_StageEnvironment",
        "M2_PostProcess_ExposureLock",
    ):
        check(label in by_label, f"actor present: {label}")

    light = by_label.get("M2_LightRig_P02")
    puppet = by_label.get("M2_Puppet_P02_Controlled")
    director = by_label.get("M2_PuzzleDirector_P02")
    environment = by_label.get("M2_StageEnvironment")
    presentation = by_label.get("M2_StagePresentation")
    if director:
        check(director.get_editor_property("light_rig") == light, "Director explicitly references the light")
        check(director.get_editor_property("puppet_actor") == puppet, "Director explicitly references the puppet")
        check(
            director.get_editor_property("puzzle_definition") == definition,
            "Director explicitly references P02 definition",
        )
        check(
            abs(director.get_editor_property("evaluation_frequency_hz") - 15.0) < 0.0001,
            "Director uses accepted 15 Hz baseline",
        )
        check(
            not bool(director.get_editor_property("show_development_debug")),
            "Development debug remains opt-in",
        )
    if presentation:
        check(
            unreal.EditorAssetLibrary.load_blueprint_class(STAGE_PRESENTATION_PATH)
            is not None,
            "BP_DYStagePresentation class loads",
        )
        check(
            presentation.get_editor_property("puzzle_director") == director,
            "Presentation explicitly references the Director publisher",
        )
        check(
            presentation.get_editor_property("stage_environment") == environment,
            "Presentation explicitly references the Environment target",
        )
        check(
            presentation.get_editor_property("resolved_environment_state")
            == unreal.DYStageEnvironmentState.CHASE_AWAKENED,
            "P02 maps Resolve to ChaseAwakened",
        )
    if puppet:
        control_class = unreal.load_class(
            None, "/Script/DengYingShanHai.DYPuppetControlComponent"
        )
        control = puppet.get_component_by_class(control_class) if control_class else None
        check(control is not None, "P02 puppet owns the reusable control component")
        meshes = puppet.get_components_by_class(unreal.StaticMeshComponent)
        check(len(meshes) == 3, "P02 puppet keeps three real-time shadow-casting parts")
        check(
            all(mesh.get_editor_property("cast_shadow") for mesh in meshes),
            "all puppet placeholder parts cast UE shadows",
        )
    if environment:
        check(
            unreal.EditorAssetLibrary.load_blueprint_class(STAGE_ENVIRONMENT_PATH)
            is not None,
            "BP_DYStageEnvironment class loads",
        )
        accents = environment.get_components_by_class(unreal.PointLightComponent)
        check(len(accents) == 2, "Environment owns Sun and Chase accent components")
        check(
            all(abs(accent.get_editor_property("intensity")) < 0.0001 for accent in accents),
            "both environment accents are dormant in the saved map",
        )


def main():
    check(unreal.EditorAssetLibrary.does_asset_exist(MAP_PATH), "M2 map asset exists")
    check(unreal.EditorAssetLibrary.does_asset_exist(DEFINITION_PATH), "P02 definition asset exists")
    check(
        unreal.EditorAssetLibrary.does_asset_exist(STAGE_PRESENTATION_PATH),
        "BP_DYStagePresentation asset exists",
    )
    check(
        unreal.EditorAssetLibrary.does_asset_exist(STAGE_ENVIRONMENT_PATH),
        "BP_DYStageEnvironment asset exists",
    )
    definition = verify_definition()
    if definition:
        verify_map(definition)
    if failures:
        raise RuntimeError("DY M2 verification failed: " + "; ".join(failures))
    unreal.log("DY_M2_VERIFIED")


main()
