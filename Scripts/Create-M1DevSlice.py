"""Create the M1 "discover the rule" Dev vertical slice in Unreal Engine 5.8.

Run through UnrealEditor-Cmd with PythonScriptPlugin enabled. The script is
idempotent: it rebuilds the two Dev mapping contexts and replaces only actors
tagged DY_M1Generated. E/A/D/R and 15 Hz are accepted keyboard/mouse baselines;
the semantic actions remain device-remappable.
"""

import unreal


CORE_INPUT_DIR = "/Game/DengYingShanHai/Core/Input"
M1_INPUT_DIR = "/Game/DengYingShanHai/Dev/M1/Input"
M1_DATA_DIR = "/Game/DengYingShanHai/Dev/M1/Data"
STAGE_PRESENTATION_DIR = "/Game/DengYingShanHai/Stage"
STAGE_PRESENTATION_PATH = f"{STAGE_PRESENTATION_DIR}/BP_DYStagePresentation"
STAGE_ENVIRONMENT_PATH = f"{STAGE_PRESENTATION_DIR}/BP_DYStageEnvironment"
MAP_PATH = "/Game/DengYingShanHai/Dev/Interaction/LV_InteractionLab"
GENERATED_TAG = unreal.Name("DY_M1Generated")


def require(value, message):
    if not value:
        raise RuntimeError(message)
    return value


def factory_type(*candidate_names):
    for name in candidate_names:
        value = getattr(unreal, name, None)
        if value:
            return value
    raise RuntimeError("Missing factory type: " + ", ".join(candidate_names))


def load_or_create_asset(asset_name, package_path, asset_class, factory):
    object_path = f"{package_path}/{asset_name}.{asset_name}"
    existing = unreal.load_asset(object_path)
    if existing:
        unreal.log(f"DY M1: reusing {object_path}")
        return existing
    created = unreal.AssetToolsHelpers.get_asset_tools().create_asset(
        asset_name, package_path, asset_class, factory
    )
    return require(created, f"Failed to create {object_path}")


def save_asset(asset):
    require(
        unreal.EditorAssetLibrary.save_loaded_asset(asset, only_if_is_dirty=False),
        f"Failed to save {asset.get_path_name()}",
    )


def ensure_stage_presentation_blueprint_class():
    parent_class = require(
        unreal.load_class(None, "/Script/DengYingShanHai.DYStagePresentation"),
        "Cannot load ADYStagePresentation",
    )
    blueprint = unreal.load_asset(
        f"{STAGE_PRESENTATION_PATH}.BP_DYStagePresentation"
    )
    if not blueprint:
        unreal.EditorAssetLibrary.make_directory(STAGE_PRESENTATION_DIR)
        factory = unreal.BlueprintFactory()
        factory.set_editor_property("parent_class", parent_class)
        blueprint = require(
            unreal.AssetToolsHelpers.get_asset_tools().create_asset(
                "BP_DYStagePresentation",
                STAGE_PRESENTATION_DIR,
                None,
                factory,
            ),
            "Failed to create BP_DYStagePresentation",
        )
        save_asset(blueprint)
    return require(
        unreal.EditorAssetLibrary.load_blueprint_class(STAGE_PRESENTATION_PATH),
        "Cannot load BP_DYStagePresentation generated class",
    )


def ensure_stage_environment_blueprint_class():
    parent_class = require(
        unreal.load_class(None, "/Script/DengYingShanHai.DYStageEnvironment"),
        "Cannot load ADYStageEnvironment",
    )
    blueprint = unreal.load_asset(f"{STAGE_ENVIRONMENT_PATH}.BP_DYStageEnvironment")
    if not blueprint:
        unreal.EditorAssetLibrary.make_directory(STAGE_PRESENTATION_DIR)
        factory = unreal.BlueprintFactory()
        factory.set_editor_property("parent_class", parent_class)
        blueprint = require(
            unreal.AssetToolsHelpers.get_asset_tools().create_asset(
                "BP_DYStageEnvironment",
                STAGE_PRESENTATION_DIR,
                None,
                factory,
            ),
            "Failed to create BP_DYStageEnvironment",
        )
        save_asset(blueprint)
    return require(
        unreal.EditorAssetLibrary.load_blueprint_class(STAGE_ENVIRONMENT_PATH),
        "Cannot load BP_DYStageEnvironment generated class",
    )


def make_key(key_name):
    key = unreal.Key()
    key.set_editor_property("key_name", unreal.Name(key_name))
    return key


def find_mapping(mappings, action, key_name):
    for mapping in mappings:
        key = mapping.get_editor_property("key")
        if (
            mapping.get_editor_property("action") == action
            and str(key.get_editor_property("key_name")) == key_name
        ):
            return mapping
    raise RuntimeError(f"Missing mapping: {action.get_name()} on {key_name}")


def add_modifier(mapping, modifier):
    modifiers = list(mapping.get_editor_property("modifiers"))
    modifiers.append(modifier)
    mapping.set_editor_property("modifiers", modifiers)


def save_mapping_profile(context, mappings):
    profile = context.get_editor_property("default_key_mappings")
    profile.set_editor_property("mappings", mappings)
    context.set_editor_property("default_key_mappings", profile)
    save_asset(context)


def create_input_assets():
    action_factory_class = factory_type("InputAction_Factory", "InputActionFactory")
    context_factory_class = factory_type(
        "InputMappingContext_Factory", "InputMappingContextFactory"
    )

    move = require(
        unreal.load_asset(f"{CORE_INPUT_DIR}/IA_DY_Move.IA_DY_Move"),
        "Run Create-Phase1Assets.py first: IA_DY_Move is missing",
    )
    look = require(
        unreal.load_asset(f"{CORE_INPUT_DIR}/IA_DY_Look.IA_DY_Look"),
        "Run Create-Phase1Assets.py first: IA_DY_Look is missing",
    )
    reset = require(
        unreal.load_asset(
            f"{CORE_INPUT_DIR}/IA_DY_ResetOperator.IA_DY_ResetOperator"
        ),
        "Run Create-Phase1Assets.py first: IA_DY_ResetOperator is missing",
    )
    explore = require(
        unreal.load_asset(f"{CORE_INPUT_DIR}/IMC_DY_Explore.IMC_DY_Explore"),
        "Run Create-Phase1Assets.py first: IMC_DY_Explore is missing",
    )

    interact = load_or_create_asset(
        "IA_DY_Interact",
        M1_INPUT_DIR,
        unreal.InputAction,
        action_factory_class(),
    )
    manipulate = load_or_create_asset(
        "IA_DY_Manipulate",
        M1_INPUT_DIR,
        unreal.InputAction,
        action_factory_class(),
    )
    reset_controlled = load_or_create_asset(
        "IA_DY_ResetControlled",
        M1_INPUT_DIR,
        unreal.InputAction,
        action_factory_class(),
    )
    manipulate_context = load_or_create_asset(
        "IMC_DY_Manipulate",
        M1_INPUT_DIR,
        unreal.InputMappingContext,
        context_factory_class(),
    )

    interact.set_editor_property("value_type", unreal.InputActionValueType.BOOLEAN)
    manipulate.set_editor_property("value_type", unreal.InputActionValueType.AXIS1D)
    reset_controlled.set_editor_property(
        "value_type", unreal.InputActionValueType.BOOLEAN
    )

    # Explore is the only active context until control begins. E is duplicated
    # deliberately so the same semantic action exits Manipulate mode.
    explore.unmap_all()
    for action, key_name in (
        (move, "W"),
        (move, "S"),
        (move, "A"),
        (move, "D"),
        (look, "Mouse2D"),
        (reset, "R"),
        (interact, "E"),
    ):
        explore.map_key(action, make_key(key_name))

    explore_profile = explore.get_editor_property("default_key_mappings")
    explore_mappings = list(explore_profile.get_editor_property("mappings"))
    require(len(explore_mappings) == 7, "Explore context did not create 7 mappings")
    add_modifier(
        find_mapping(explore_mappings, move, "W"),
        unreal.InputModifierSwizzleAxis(outer=explore),
    )
    add_modifier(
        find_mapping(explore_mappings, move, "S"),
        unreal.InputModifierNegate(outer=explore),
    )
    add_modifier(
        find_mapping(explore_mappings, move, "S"),
        unreal.InputModifierSwizzleAxis(outer=explore),
    )
    add_modifier(
        find_mapping(explore_mappings, move, "A"),
        unreal.InputModifierNegate(outer=explore),
    )
    save_mapping_profile(explore, explore_mappings)

    manipulate_context.unmap_all()
    manipulate_context.map_key(interact, make_key("E"))
    manipulate_context.map_key(manipulate, make_key("A"))
    manipulate_context.map_key(manipulate, make_key("D"))
    manipulate_context.map_key(reset_controlled, make_key("R"))
    manipulate_profile = manipulate_context.get_editor_property(
        "default_key_mappings"
    )
    manipulate_mappings = list(
        manipulate_profile.get_editor_property("mappings")
    )
    require(
        len(manipulate_mappings) == 4,
        "Manipulate context did not create 4 mappings",
    )
    add_modifier(
        find_mapping(manipulate_mappings, manipulate, "A"),
        unreal.InputModifierNegate(outer=manipulate_context),
    )
    save_mapping_profile(manipulate_context, manipulate_mappings)

    for asset in (interact, manipulate, reset_controlled):
        save_asset(asset)
    unreal.log("DY M1: semantic input assets and Dev contexts saved")


def create_puzzle_definition():
    puzzle_class = require(
        unreal.load_class(None, "/Script/DengYingShanHai.DYPuzzleDefinition"),
        "Cannot load UDYPuzzleDefinition",
    )
    factory_class = factory_type("DataAssetFactory")
    factory = factory_class()
    factory.set_editor_property("data_asset_class", puzzle_class)
    definition = load_or_create_asset(
        "DA_DY_P01_SunAwakening", M1_DATA_DIR, puzzle_class, factory
    )
    definition.set_editor_property("puzzle_id", unreal.Name("P01_SunAwakening"))
    definition.set_editor_property("display_name", "逐日·辨光")
    definition.set_editor_property("required_hold_seconds", 1.25)
    definition.set_editor_property(
        "debug_notes",
        "M1 Dev parameter target. 15 Hz is accepted; tolerances remain tunable.",
    )
    target = definition.get_editor_property("light_position")
    target.set_editor_property("enabled", True)
    target.set_editor_property("target", 0.68)
    target.set_editor_property("enter_tolerance", 0.045)
    target.set_editor_property("exit_tolerance", 0.085)
    definition.set_editor_property("light_position", target)
    save_asset(definition)
    return definition


def mark_generated(actor, label):
    require(actor, f"Failed to spawn {label}")
    actor.set_actor_label(label)
    actor.set_editor_property("tags", [GENERATED_TAG])
    return actor


def try_set(target, property_name, value):
    try:
        target.set_editor_property(property_name, value)
        return True
    except Exception as error:
        unreal.log_warning(
            f"DY M1: optional property {property_name} unavailable: {error}"
        )
        return False


def configure_post_process(actor_subsystem):
    volume = mark_generated(
        actor_subsystem.spawn_actor_from_class(
            unreal.PostProcessVolume,
            unreal.Vector(0.0, 0.0, 250.0),
            unreal.Rotator(),
            False,
        ),
        "M1_PostProcess_ExposureLock",
    )
    volume.set_editor_property("unbound", True)
    volume.set_editor_property("priority", 50.0)
    settings = volume.get_editor_property("settings")
    manual_method = next(
        (
            getattr(unreal.AutoExposureMethod, member)
            for member in dir(unreal.AutoExposureMethod)
            if "MANUAL" in member.upper()
        ),
        None,
    )
    require(manual_method is not None, "Manual auto-exposure enum is unavailable")
    require(
        try_set(settings, "override_auto_exposure_method", True),
        "Cannot override auto exposure method",
    )
    require(
        try_set(settings, "auto_exposure_method", manual_method),
        "Cannot select manual exposure",
    )
    try_set(settings, "override_auto_exposure_bias", True)
    try_set(settings, "auto_exposure_bias", 3.5)
    try_set(
        settings,
        "override_auto_exposure_apply_physical_camera_exposure",
        True,
    )
    # Real-world light units require physical-camera exposure. Disabling this
    # makes the white Dev geometry clip even at moderate light intensities.
    try_set(settings, "auto_exposure_apply_physical_camera_exposure", True)
    volume.set_editor_property("settings", settings)
    return volume


def tune_existing_lab_lighting(actors):
    for actor in actors:
        label = actor.get_actor_label()
        if label == "DEV_DirectionalLight":
            component = actor.get_component_by_class(unreal.DirectionalLightComponent)
            if component:
                component.set_editor_property("intensity", 3.0)
        elif label == "DEV_SkyLight":
            component = actor.get_component_by_class(unreal.SkyLightComponent)
            if component:
                component.set_editor_property("intensity", 0.8)
        elif label == "DEV_PointLight":
            component = actor.get_component_by_class(unreal.PointLightComponent)
            if component:
                component.set_editor_property("intensity", 2500.0)
        elif label in ("DEV_Label_Title", "DEV_Label_Input"):
            # These labels were useful while bootstrapping Phase 1, but are not
            # player UI and can clip into the gameplay camera.
            actor.set_actor_hidden_in_game(True)
        elif isinstance(actor, unreal.PlayerStart):
            # At BeginPlay the lamp moves to its authored initial rail value
            # (Y=-210). Aligning the Dev spawn makes the first focus test clear.
            actor.set_actor_location(unreal.Vector(-900.0, -210.0, 120.0), False, False)


def create_m1_map_slice(definition):
    level_subsystem = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    actor_subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    require(level_subsystem.load_level(MAP_PATH), f"Failed to load {MAP_PATH}")

    actors = list(actor_subsystem.get_all_level_actors())
    for actor in actors:
        if GENERATED_TAG in list(actor.get_editor_property("tags")):
            actor_subsystem.destroy_actor(actor)

    actors = list(actor_subsystem.get_all_level_actors())
    tune_existing_lab_lighting(actors)

    light_class = require(
        unreal.load_class(None, "/Script/DengYingShanHai.DYLightRigActor"),
        "Cannot load ADYLightRigActor",
    )
    puppet_class = require(
        unreal.load_class(None, "/Script/DengYingShanHai.DYPuppetActor"),
        "Cannot load ADYPuppetActor",
    )
    director_class = require(
        unreal.load_class(None, "/Script/DengYingShanHai.DYPuzzleDirector"),
        "Cannot load ADYPuzzleDirector",
    )
    environment_class = ensure_stage_environment_blueprint_class()
    presentation_class = ensure_stage_presentation_blueprint_class()

    light = mark_generated(
        actor_subsystem.spawn_actor_from_class(
            light_class,
            unreal.Vector(-460.0, 0.0, 310.0),
            unreal.Rotator(),
            False,
        ),
        "M1_LightRig_P01",
    )
    puppet = mark_generated(
        actor_subsystem.spawn_actor_from_class(
            puppet_class,
            unreal.Vector(600.0, 0.0, 210.0),
            unreal.Rotator(),
            False,
        ),
        "M1_Puppet_P01_Fixed",
    )
    director = mark_generated(
        actor_subsystem.spawn_actor_from_class(
            director_class,
            unreal.Vector(0.0, 0.0, 0.0),
            unreal.Rotator(),
            False,
        ),
        "M1_PuzzleDirector_P01",
    )
    environment = mark_generated(
        actor_subsystem.spawn_actor_from_class(
            environment_class,
            unreal.Vector(820.0, 0.0, 420.0),
            unreal.Rotator(),
            False,
        ),
        "M1_StageEnvironment",
    )
    presentation = mark_generated(
        actor_subsystem.spawn_actor_from_class(
            presentation_class,
            unreal.Vector(0.0, 0.0, 0.0),
            unreal.Rotator(),
            False,
        ),
        "M1_StagePresentation",
    )
    director.set_editor_property("light_rig", light)
    director.set_editor_property("puppet_actor", puppet)
    director.set_editor_property("puzzle_definition", definition)
    director.set_editor_property("evaluation_frequency_hz", 15.0)
    director.set_editor_property("show_development_debug", False)
    presentation.set_editor_property("puzzle_director", director)
    presentation.set_editor_property("stage_environment", environment)
    presentation.set_editor_property(
        "resolved_environment_state",
        unreal.DYStageEnvironmentState.SUN_AWAKENED,
    )

    configure_post_process(actor_subsystem)

    require(level_subsystem.save_current_level(), f"Failed to save {MAP_PATH}")
    unreal.log(
        f"DY M1: map slice saved with {light.get_name()}, {puppet.get_name()}, {director.get_name()}, {presentation.get_name()}, and {environment.get_name()}"
    )


def main():
    unreal.log("DY M1: Dev vertical-slice generation started")
    create_input_assets()
    definition = create_puzzle_definition()
    create_m1_map_slice(definition)
    unreal.log("DY_M1_DEV_SLICE_CREATED")


main()
