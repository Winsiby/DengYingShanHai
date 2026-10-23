"""Create the M2 "coordinated control" Dev slice in a separate UE 5.8 map.

The script duplicates the proven M1 lab shell, replaces only generated actors,
and reuses the existing semantic input assets. It never modifies the M1 map.
"""

import unreal


SOURCE_MAP = "/Game/DengYingShanHai/Dev/Interaction/LV_InteractionLab"
M2_MAP_DIR = "/Game/DengYingShanHai/Dev/M2/Maps"
M2_MAP = f"{M2_MAP_DIR}/LV_M2PuzzleLab"
M2_DATA_DIR = "/Game/DengYingShanHai/Dev/M2/Data"
STAGE_PRESENTATION_DIR = "/Game/DengYingShanHai/Stage"
STAGE_PRESENTATION_PATH = f"{STAGE_PRESENTATION_DIR}/BP_DYStagePresentation"
STAGE_ENVIRONMENT_PATH = f"{STAGE_PRESENTATION_DIR}/BP_DYStageEnvironment"
M1_TAG = unreal.Name("DY_M1Generated")
M2_TAG = unreal.Name("DY_M2Generated")


def require(value, message):
    if not value:
        raise RuntimeError(message)
    return value


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


def create_definition():
    puzzle_class = require(
        unreal.load_class(None, "/Script/DengYingShanHai.DYPuzzleDefinition"),
        "Cannot load UDYPuzzleDefinition",
    )
    object_path = f"{M2_DATA_DIR}/DA_DY_P02_ChaseForm.DA_DY_P02_ChaseForm"
    definition = unreal.load_asset(object_path)
    if not definition:
        factory = unreal.DataAssetFactory()
        factory.set_editor_property("data_asset_class", puzzle_class)
        definition = require(
            unreal.AssetToolsHelpers.get_asset_tools().create_asset(
                "DA_DY_P02_ChaseForm", M2_DATA_DIR, puzzle_class, factory
            ),
            f"Failed to create {object_path}",
        )

    definition.set_editor_property("puzzle_id", unreal.Name("P02_ChaseForm"))
    definition.set_editor_property("display_name", "逐光成形")
    definition.set_editor_property("required_puppet_pose_id", unreal.Name("P02_StrideReach"))
    definition.set_editor_property("required_hold_seconds", 1.25)
    definition.set_editor_property(
        "debug_notes",
        "M2 Dev coordinated-control target. 15 Hz and E/A/D/R are accepted baselines.",
    )

    light_target = definition.get_editor_property("light_position")
    light_target.set_editor_property("enabled", True)
    light_target.set_editor_property("target", 0.72)
    light_target.set_editor_property("enter_tolerance", 0.05)
    light_target.set_editor_property("exit_tolerance", 0.09)
    definition.set_editor_property("light_position", light_target)

    puppet_target = definition.get_editor_property("puppet_position")
    puppet_target.set_editor_property("enabled", True)
    puppet_target.set_editor_property("target", 0.80)
    puppet_target.set_editor_property("enter_tolerance", 0.05)
    puppet_target.set_editor_property("exit_tolerance", 0.09)
    definition.set_editor_property("puppet_position", puppet_target)
    save_asset(definition)
    return definition


def ensure_m2_map():
    require(
        unreal.EditorAssetLibrary.does_asset_exist(SOURCE_MAP),
        "Run Create-M1DevSlice.py first: source M1 map is missing",
    )
    unreal.EditorAssetLibrary.make_directory(M2_MAP_DIR)
    if not unreal.EditorAssetLibrary.does_asset_exist(M2_MAP):
        require(
            unreal.EditorAssetLibrary.duplicate_asset(SOURCE_MAP, M2_MAP),
            "Failed to duplicate the M1 lab shell for M2",
        )


def mark_generated(actor, label):
    require(actor, f"Failed to spawn {label}")
    actor.set_actor_label(label)
    actor.set_editor_property("tags", [M2_TAG])
    return actor


def rebuild_generated_actors(definition):
    level_subsystem = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    actor_subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    require(level_subsystem.load_level(M2_MAP), f"Failed to load {M2_MAP}")

    exposure = None
    for actor in list(actor_subsystem.get_all_level_actors()):
        tags = list(actor.get_editor_property("tags"))
        label = actor.get_actor_label()
        if label in ("M1_PostProcess_ExposureLock", "M2_PostProcess_ExposureLock"):
            exposure = actor
            actor.set_actor_label("M2_PostProcess_ExposureLock")
            actor.set_editor_property("tags", [M2_TAG])
        elif M1_TAG in tags or M2_TAG in tags:
            actor_subsystem.destroy_actor(actor)

    require(exposure is not None, "Duplicated lab is missing the proven exposure volume")

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
            light_class, unreal.Vector(-460.0, -20.0, 310.0), unreal.Rotator(), False
        ),
        "M2_LightRig_P02",
    )
    puppet = mark_generated(
        actor_subsystem.spawn_actor_from_class(
            puppet_class, unreal.Vector(600.0, -80.0, 210.0), unreal.Rotator(), False
        ),
        "M2_Puppet_P02_Controlled",
    )
    director = mark_generated(
        actor_subsystem.spawn_actor_from_class(
            director_class, unreal.Vector(), unreal.Rotator(), False
        ),
        "M2_PuzzleDirector_P02",
    )
    environment = mark_generated(
        actor_subsystem.spawn_actor_from_class(
            environment_class, unreal.Vector(820.0, 0.0, 420.0), unreal.Rotator(), False
        ),
        "M2_StageEnvironment",
    )
    presentation = mark_generated(
        actor_subsystem.spawn_actor_from_class(
            presentation_class, unreal.Vector(), unreal.Rotator(), False
        ),
        "M2_StagePresentation",
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
        unreal.DYStageEnvironmentState.CHASE_AWAKENED,
    )

    require(level_subsystem.save_current_level(), f"Failed to save {M2_MAP}")


def main():
    unreal.log("DY M2: coordinated-control Dev slice generation started")
    definition = create_definition()
    ensure_m2_map()
    rebuild_generated_actors(definition)
    unreal.log("DY_M2_DEV_SLICE_CREATED")


main()
