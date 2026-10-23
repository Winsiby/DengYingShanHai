"""Verify the phase-one technical base in UE 5.8.

Independent of Create-Phase1Assets.py: this script loads the saved packages
from disk and checks map content, input bindings, and C++ class wiring.
Run only through UnrealEditor with PythonScriptPlugin enabled.
Success is confirmed by the DY_PHASE1_VERIFIED log sentinel.
"""

import unreal


MAP_PATH = "/Game/DengYingShanHai/Dev/Interaction/LV_InteractionLab"
INPUT_DIR = "/Game/DengYingShanHai/Core/Input"
M1_INPUT_DIR = "/Game/DengYingShanHai/Dev/M1/Input"
GENERATED_TAG = unreal.Name("DY_Phase1Generated")
EXPECTED_GENERATED_ACTORS = 19

failures = []


def check(condition, label):
    if condition:
        unreal.log(f"DY Verify: PASS {label}")
        return True
    failures.append(label)
    unreal.log_error(f"DY Verify: FAIL {label}")
    return False


def verify_packages():
    for path in (
        MAP_PATH,
        f"{INPUT_DIR}/IA_DY_Move",
        f"{INPUT_DIR}/IA_DY_Look",
        f"{INPUT_DIR}/IA_DY_ResetOperator",
        f"{INPUT_DIR}/IMC_DY_Explore",
        f"{M1_INPUT_DIR}/IA_DY_Interact",
    ):
        check(
            unreal.EditorAssetLibrary.does_asset_exist(path),
            f"asset package exists: {path}",
        )


def verify_map():
    level_subsystem = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    if not check(level_subsystem.load_level(MAP_PATH), f"map loads: {MAP_PATH}"):
        return

    actor_subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    actors = list(actor_subsystem.get_all_level_actors())
    generated = [
        actor
        for actor in actors
        if GENERATED_TAG in list(actor.get_editor_property("tags"))
    ]
    check(
        len(generated) == EXPECTED_GENERATED_ACTORS,
        f"generated actor count == {EXPECTED_GENERATED_ACTORS} (found {len(generated)})",
    )
    check(
        any(isinstance(actor, unreal.PlayerStart) for actor in actors),
        "PlayerStart present",
    )
    check(
        any(isinstance(actor, unreal.DirectionalLight) for actor in actors),
        "DirectionalLight present",
    )
    check(
        any(isinstance(actor, unreal.SkyLight) for actor in actors),
        "SkyLight present",
    )

    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    world_settings = check(world and world.get_world_settings(), "WorldSettings available")
    if not world_settings:
        return
    settings = world.get_world_settings()
    check(
        abs(settings.get_editor_property("kill_z") - (-900.0)) < 0.01,
        "kill_z == -900 (FellOutOfWorld reset testable)",
    )
    game_mode = settings.get_editor_property("default_game_mode")
    expected_game_mode = unreal.load_class(None, "/Script/DengYingShanHai.DYStageGameMode")
    check(
        game_mode == expected_game_mode,
        "WorldSettings default GameMode == ADYStageGameMode",
    )


def verify_input_assets():
    move = unreal.load_asset(f"{INPUT_DIR}/IA_DY_Move.IA_DY_Move")
    look = unreal.load_asset(f"{INPUT_DIR}/IA_DY_Look.IA_DY_Look")
    reset = unreal.load_asset(f"{INPUT_DIR}/IA_DY_ResetOperator.IA_DY_ResetOperator")
    interact = unreal.load_asset(f"{M1_INPUT_DIR}/IA_DY_Interact.IA_DY_Interact")
    context = unreal.load_asset(f"{INPUT_DIR}/IMC_DY_Explore.IMC_DY_Explore")
    if not check(all((move, look, reset, interact, context)), "input assets load"):
        return

    axis2d = unreal.InputActionValueType.AXIS2D
    boolean = unreal.InputActionValueType.BOOLEAN
    check(move.get_editor_property("value_type") == axis2d, "IA_DY_Move is Axis2D")
    check(look.get_editor_property("value_type") == axis2d, "IA_DY_Look is Axis2D")
    check(reset.get_editor_property("value_type") == boolean, "IA_DY_ResetOperator is Boolean")
    check(interact.get_editor_property("value_type") == boolean, "IA_DY_Interact is Boolean")

    mappings = list(
        context.get_editor_property("default_key_mappings").get_editor_property("mappings")
    )
    check(len(mappings) == 7, f"IMC_DY_Explore has 7 current Dev mappings (found {len(mappings)})")

    def find_mapping(action, key_name):
        for mapping in mappings:
            key = mapping.get_editor_property("key")
            if (
                mapping.get_editor_property("action") == action
                and str(key.get_editor_property("key_name")) == key_name
            ):
                return mapping
        return None

    expected = (
        (move, "W", (unreal.InputModifierSwizzleAxis,)),
        (move, "S", (unreal.InputModifierNegate, unreal.InputModifierSwizzleAxis)),
        (move, "A", (unreal.InputModifierNegate,)),
        (move, "D", ()),
        (look, "Mouse2D", ()),
        (reset, "R", ()),
        (interact, "E", ()),
    )
    for action, key_name, modifier_types in expected:
        mapping = find_mapping(action, key_name)
        if not check(mapping is not None, f"{key_name} maps to {action.get_name()}"):
            continue
        modifiers = list(mapping.get_editor_property("modifiers"))
        actual_types = tuple(type(modifier) for modifier in modifiers)
        check(
            actual_types == modifier_types,
            f"{key_name} modifiers == {[modifier.__name__ for modifier in modifier_types]}",
        )

    for key_name, modifier_index in (("W", 0), ("S", 1)):
        mapping = find_mapping(move, key_name)
        if mapping:
            modifiers = list(mapping.get_editor_property("modifiers"))
            swizzle = (
                modifiers[modifier_index]
                if len(modifiers) > modifier_index
                and isinstance(
                    modifiers[modifier_index], unreal.InputModifierSwizzleAxis
                )
                else None
            )
            if swizzle:
                check(
                    swizzle.get_editor_property("order")
                    == unreal.InputAxisSwizzle.YXZ,
                    f"{key_name} swizzle order == YXZ (forward on Move.Y)",
                )
            else:
                check(
                    False,
                    f"{key_name} has swizzle modifier at index {modifier_index}",
                )


def verify_class_wiring():
    game_mode_class = unreal.load_class(None, "/Script/DengYingShanHai.DYStageGameMode")
    if not check(game_mode_class is not None, "ADYStageGameMode loads (module bound)"):
        return
    # UClass::GetDefaultObject is not a UFUNCTION, so reflection cannot see it.
    # The PythonScriptPlugin exposes it as the free function below.
    game_mode_cdo = unreal.get_default_object(game_mode_class)
    if not check(
        game_mode_cdo is not None and not isinstance(game_mode_cdo, unreal.Class),
        "GameMode CDO obtained (instance, not Class)",
    ):
        return

    pawn_class = game_mode_cdo.get_editor_property("default_pawn_class")
    controller_class = game_mode_cdo.get_editor_property("player_controller_class")
    check(
        pawn_class is not None and pawn_class.get_name() == "DYStageOperatorPawn",
        "GameMode DefaultPawnClass == ADYStageOperatorPawn",
    )
    check(
        controller_class is not None and controller_class.get_name() == "DYStagePlayerController",
        "GameMode PlayerControllerClass == ADYStagePlayerController",
    )
    if not pawn_class:
        return

    pawn_cdo = unreal.get_default_object(pawn_class)
    boom = pawn_cdo.get_component_by_class(unreal.SpringArmComponent)
    camera = pawn_cdo.get_component_by_class(unreal.CameraComponent)
    check(boom is not None, "operator pawn has SpringArm (sole base camera rig)")
    check(camera is not None, "operator pawn has follow Camera")
    if boom:
        check(
            abs(boom.get_editor_property("target_arm_length") - 360.0) < 0.01,
            "spring arm length == 360",
        )
        check(
            bool(boom.get_editor_property("use_pawn_control_rotation")),
            "spring arm uses pawn control rotation (look intent)",
        )
        check(
            bool(boom.get_editor_property("do_collision_test")),
            "spring arm camera collision enabled",
        )
        check(
            abs(boom.get_editor_property("probe_size") - 12.0) < 0.01,
            "spring arm probe size == 12",
        )
        check(
            not bool(boom.get_editor_property("enable_camera_lag")),
            "spring arm position lag disabled",
        )
        check(
            not bool(boom.get_editor_property("enable_camera_rotation_lag")),
            "spring arm rotation lag disabled",
        )
    if camera:
        check(
            abs(camera.get_editor_property("field_of_view") - 70.0) < 0.01,
            "camera FOV == 70",
        )
        check(
            not bool(camera.get_editor_property("use_pawn_control_rotation")),
            "follow camera does not rotate independently from pawn control",
        )
        if boom:
            check(
                camera.get_attach_parent() == boom,
                "follow camera attached to spring arm",
            )
            check(
                str(camera.get_attach_socket_name()) == "SpringEndpoint",
                "follow camera attached at spring-arm endpoint",
            )


def main():
    unreal.log("DY Verify: phase-one verification started")
    verify_packages()
    verify_map()
    verify_input_assets()
    verify_class_wiring()
    if failures:
        raise RuntimeError(f"DY Phase1 verification FAILED: {failures}")
    unreal.log("DY_PHASE1_VERIFIED")


main()
