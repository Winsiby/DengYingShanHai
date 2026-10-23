"""Independently verify the saved M1 Dev vertical slice in UE 5.8."""

import unreal


MAP_PATH = "/Game/DengYingShanHai/Dev/Interaction/LV_InteractionLab"
CORE_INPUT_DIR = "/Game/DengYingShanHai/Core/Input"
M1_INPUT_DIR = "/Game/DengYingShanHai/Dev/M1/Input"
DEFINITION_PATH = "/Game/DengYingShanHai/Dev/M1/Data/DA_DY_P01_SunAwakening"
STAGE_PRESENTATION_PATH = "/Game/DengYingShanHai/Stage/BP_DYStagePresentation"
STAGE_ENVIRONMENT_PATH = "/Game/DengYingShanHai/Stage/BP_DYStageEnvironment"
GENERATED_TAG = unreal.Name("DY_M1Generated")
EXPECTED_GENERATED_ACTORS = 6
failures = []


def check(condition, label):
    if condition:
        unreal.log(f"DY M1 Verify: PASS {label}")
        return True
    failures.append(label)
    unreal.log_error(f"DY M1 Verify: FAIL {label}")
    return False


def load(path):
    return unreal.load_asset(f"{path}.{path.rsplit('/', 1)[-1]}")


def mappings(context):
    return list(
        context.get_editor_property("default_key_mappings").get_editor_property(
            "mappings"
        )
    )


def find_mapping(mapping_list, action, key_name):
    for mapping in mapping_list:
        key = mapping.get_editor_property("key")
        if (
            mapping.get_editor_property("action") == action
            and str(key.get_editor_property("key_name")) == key_name
        ):
            return mapping
    return None


def verify_packages_and_input():
    for path in (
        MAP_PATH,
        f"{M1_INPUT_DIR}/IA_DY_Interact",
        f"{M1_INPUT_DIR}/IA_DY_Manipulate",
        f"{M1_INPUT_DIR}/IA_DY_ResetControlled",
        f"{M1_INPUT_DIR}/IMC_DY_Manipulate",
        DEFINITION_PATH,
    ):
        check(unreal.EditorAssetLibrary.does_asset_exist(path), f"asset exists: {path}")

    interact = load(f"{M1_INPUT_DIR}/IA_DY_Interact")
    manipulate = load(f"{M1_INPUT_DIR}/IA_DY_Manipulate")
    reset_controlled = load(f"{M1_INPUT_DIR}/IA_DY_ResetControlled")
    explore = load(f"{CORE_INPUT_DIR}/IMC_DY_Explore")
    manipulate_context = load(f"{M1_INPUT_DIR}/IMC_DY_Manipulate")
    if not check(
        all((interact, manipulate, reset_controlled, explore, manipulate_context)),
        "all M1 input assets load",
    ):
        return

    check(
        interact.get_editor_property("value_type")
        == unreal.InputActionValueType.BOOLEAN,
        "Interact is Boolean",
    )
    check(
        manipulate.get_editor_property("value_type")
        == unreal.InputActionValueType.AXIS1D,
        "Manipulate is Axis1D",
    )
    check(
        reset_controlled.get_editor_property("value_type")
        == unreal.InputActionValueType.BOOLEAN,
        "ResetControlled is Boolean",
    )

    explore_mappings = mappings(explore)
    control_mappings = mappings(manipulate_context)
    check(len(explore_mappings) == 7, "Explore has exactly 7 current Dev mappings")
    check(len(control_mappings) == 4, "Manipulate has exactly 4 Dev mappings")
    check(
        find_mapping(explore_mappings, interact, "E") is not None,
        "Explore E enters control",
    )
    check(
        find_mapping(control_mappings, interact, "E") is not None,
        "Manipulate E exits control",
    )
    left = find_mapping(control_mappings, manipulate, "A")
    right = find_mapping(control_mappings, manipulate, "D")
    reset = find_mapping(control_mappings, reset_controlled, "R")
    check(left is not None, "Manipulate A maps to semantic axis")
    check(right is not None, "Manipulate D maps to semantic axis")
    check(reset is not None, "Manipulate R maps to contextual reset")
    if left:
        modifiers = list(left.get_editor_property("modifiers"))
        check(
            len(modifiers) == 1
            and isinstance(modifiers[0], unreal.InputModifierNegate),
            "Manipulate A has exactly one Negate modifier",
        )
    if right:
        check(
            len(list(right.get_editor_property("modifiers"))) == 0,
            "Manipulate D has no modifier",
        )
    if reset:
        check(
            len(list(reset.get_editor_property("modifiers"))) == 0,
            "Manipulate R has no modifier",
        )


def verify_definition():
    definition = load(DEFINITION_PATH)
    if not check(definition is not None, "P01 definition loads"):
        return
    check(str(definition.get_editor_property("puzzle_id")) == "P01_SunAwakening", "P01 id")
    check(
        abs(definition.get_editor_property("required_hold_seconds") - 1.25) < 0.0001,
        "P01 hold requirement is 1.25 s",
    )
    target = definition.get_editor_property("light_position")
    check(bool(target.get_editor_property("enabled")), "light parameter enabled")
    check(abs(target.get_editor_property("target") - 0.68) < 0.0001, "target is 0.68")
    check(
        abs(target.get_editor_property("enter_tolerance") - 0.045) < 0.0001,
        "enter tolerance is 0.045",
    )
    check(
        abs(target.get_editor_property("exit_tolerance") - 0.085) < 0.0001,
        "exit tolerance is 0.085",
    )


def verify_map_and_wiring():
    level_subsystem = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    if not check(level_subsystem.load_level(MAP_PATH), "M1 Dev map loads"):
        return
    actor_subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    actors = list(actor_subsystem.get_all_level_actors())
    all_by_label = {actor.get_actor_label(): actor for actor in actors}
    generated = [
        actor
        for actor in actors
        if GENERATED_TAG in list(actor.get_editor_property("tags"))
    ]
    check(
        len(generated) == EXPECTED_GENERATED_ACTORS,
        f"M1 generated actor count is {EXPECTED_GENERATED_ACTORS} (found {len(generated)})",
    )

    by_label = {actor.get_actor_label(): actor for actor in generated}
    for label in (
        "M1_LightRig_P01",
        "M1_Puppet_P01_Fixed",
        "M1_PuzzleDirector_P01",
        "M1_StagePresentation",
        "M1_StageEnvironment",
        "M1_PostProcess_ExposureLock",
    ):
        check(label in by_label, f"actor present: {label}")

    light = by_label.get("M1_LightRig_P01")
    director = by_label.get("M1_PuzzleDirector_P01")
    puppet = by_label.get("M1_Puppet_P01_Fixed")
    environment = by_label.get("M1_StageEnvironment")
    presentation = by_label.get("M1_StagePresentation")
    definition = load(DEFINITION_PATH)
    if light:
        spot = light.get_component_by_class(unreal.SpotLightComponent)
        check(spot is not None, "LightRig owns SpotLightComponent")
        if spot:
            check(
                spot.get_editor_property("mobility") == unreal.ComponentMobility.MOVABLE,
                "Spot Light is Movable",
            )
            check(bool(spot.get_editor_property("cast_shadows")), "Spot Light casts shadows")
            check(
                abs(spot.get_editor_property("intensity") - 30000.0) < 0.1,
                "Spot Light has readable fixed-exposure intensity",
            )
    if puppet:
        mesh_components = puppet.get_components_by_class(unreal.StaticMeshComponent)
        check(len(mesh_components) == 3, "P01 puppet has three placeholder mesh parts")
        check(
            all(component.get_editor_property("cast_shadow") for component in mesh_components),
            "all P01 puppet parts cast real UE shadows",
        )
    if director:
        check(
            director.get_editor_property("light_rig") == light,
            "Director has explicit LightRig reference",
        )
        check(
            director.get_editor_property("puppet_actor") == puppet,
            "Director has explicit fixed Puppet reference",
        )
        check(
            director.get_editor_property("puzzle_definition") == definition,
            "Director has explicit definition reference",
        )
        check(
            abs(director.get_editor_property("evaluation_frequency_hz") - 15.0)
            < 0.0001,
            "Director uses accepted 15 Hz baseline",
        )
        check(
            not bool(director.get_editor_property("show_development_debug")),
            "Development debug is opt-in",
        )
    if presentation:
        presentation_class = unreal.EditorAssetLibrary.load_blueprint_class(
            STAGE_PRESENTATION_PATH
        )
        check(presentation_class is not None, "BP_DYStagePresentation class loads")
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
            == unreal.DYStageEnvironmentState.SUN_AWAKENED,
            "P01 maps Resolve to SunAwakened",
        )
    volume = by_label.get("M1_PostProcess_ExposureLock")
    if volume:
        check(bool(volume.get_editor_property("unbound")), "exposure volume is unbound")
        settings = volume.get_editor_property("settings")
        method = settings.get_editor_property("auto_exposure_method")
        check("MANUAL" in str(method).upper(), "exposure method is manual")
        check(
            abs(settings.get_editor_property("auto_exposure_bias") - 3.5) < 0.0001,
            "manual exposure bias is readable and fixed",
        )
        check(
            bool(settings.get_editor_property("auto_exposure_apply_physical_camera_exposure")),
            "manual exposure uses physical-camera exposure for real-world light units",
        )
    check("M1_Label_Controls" not in by_label, "no world-space debug text clips into the player view")
    directional = all_by_label.get("DEV_DirectionalLight")
    skylight = all_by_label.get("DEV_SkyLight")
    point_light = all_by_label.get("DEV_PointLight")
    if directional:
        component = directional.get_component_by_class(unreal.DirectionalLightComponent)
        check(
            component is not None
            and abs(component.get_editor_property("intensity") - 3.0) < 0.0001,
            "Dev directional fill is readable",
        )
    if skylight:
        component = skylight.get_component_by_class(unreal.SkyLightComponent)
        check(
            component is not None
            and abs(component.get_editor_property("intensity") - 0.8) < 0.0001,
            "Dev skylight fill is readable",
        )
    if point_light:
        component = point_light.get_component_by_class(unreal.PointLightComponent)
        check(
            component is not None
            and abs(component.get_editor_property("intensity") - 2500.0) < 0.1,
            "Dev backstage fill is readable",
        )
    for legacy_label in ("DEV_Label_Title", "DEV_Label_Input"):
        actor = all_by_label.get(legacy_label)
        if actor:
            check(
                bool(actor.get_editor_property("hidden")),
                f"legacy world-space label hidden in game: {legacy_label}",
            )
    if environment:
        check(
            unreal.EditorAssetLibrary.load_blueprint_class(STAGE_ENVIRONMENT_PATH)
            is not None,
            "BP_DYStageEnvironment class loads",
        )
        accents = environment.get_components_by_class(unreal.PointLightComponent)
        check(len(accents) == 2, "StageEnvironment owns both semantic point-light accents")
        if accents:
            check(
                all(
                    accent.get_editor_property("mobility")
                    == unreal.ComponentMobility.MOVABLE
                    for accent in accents
                ),
                "environment accents are Movable",
            )
            check(
                all(abs(accent.get_editor_property("intensity")) < 0.0001 for accent in accents),
                "saved Dormant accent intensities are zero",
            )


def verify_class_wiring():
    pawn_class = unreal.load_class(None, "/Script/DengYingShanHai.DYStageOperatorPawn")
    controller_class = unreal.load_class(
        None, "/Script/DengYingShanHai.DYStagePlayerController"
    )
    check(pawn_class is not None, "operator pawn class loads")
    check(controller_class is not None, "stage controller class loads")
    if pawn_class:
        pawn_cdo = unreal.get_default_object(pawn_class)
        interaction_class = unreal.load_class(
            None, "/Script/DengYingShanHai.DYInteractionComponent"
        )
        interaction = (
            pawn_cdo.get_component_by_class(interaction_class)
            if interaction_class
            else None
        )
        check(interaction is not None, "operator pawn owns InteractionComponent")


def main():
    unreal.log("DY M1 Verify: verification started")
    verify_packages_and_input()
    verify_definition()
    verify_map_and_wiring()
    verify_class_wiring()
    if failures:
        raise RuntimeError(f"DY M1 verification FAILED: {failures}")
    unreal.log("DY_M1_VERIFIED")


main()
