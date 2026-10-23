"""Create the phase-one Enhanced Input assets and Dev interaction lab in UE 5.8.

Run only through UnrealEditor with PythonScriptPlugin enabled. The script is
idempotent for assets it owns: it rebuilds the mapping list and replaces only
actors tagged DY_Phase1Generated.
"""

import unreal


INPUT_DIR = "/Game/DengYingShanHai/Core/Input"
MAP_PATH = "/Game/DengYingShanHai/Dev/Interaction/LV_InteractionLab"
GENERATED_TAG = unreal.Name("DY_Phase1Generated")


def require(value, message):
    if not value:
        raise RuntimeError(message)
    return value


def factory_type(*candidate_names):
    for name in candidate_names:
        value = getattr(unreal, name, None)
        if value:
            return value
    raise RuntimeError(
        "None of the Unreal Python factory types are available: "
        + ", ".join(candidate_names)
    )


def load_or_create_asset(asset_name, package_path, asset_class, factory_class):
    object_path = f"{package_path}/{asset_name}.{asset_name}"
    existing = unreal.load_asset(object_path)
    if existing:
        unreal.log(f"DY Phase1: reusing {object_path}")
        return existing

    asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
    created = asset_tools.create_asset(
        asset_name,
        package_path,
        asset_class,
        factory_class(),
    )
    return require(created, f"Failed to create {object_path}")


def save_asset(asset):
    require(
        unreal.EditorAssetLibrary.save_loaded_asset(asset, only_if_is_dirty=False),
        f"Failed to save {asset.get_path_name()}",
    )


def add_modifier(mapping, modifier):
    modifiers = list(mapping.get_editor_property("modifiers"))
    modifiers.append(modifier)
    mapping.set_editor_property("modifiers", modifiers)


def find_mapping(mappings, action, key_name):
    for mapping in mappings:
        key = mapping.get_editor_property("key")
        if (
            mapping.get_editor_property("action") == action
            and str(key.get_editor_property("key_name")) == key_name
        ):
            return mapping
    raise RuntimeError(f"Missing mapping: {action.get_name()} on {key_name}")


def make_key(key_name):
    # FKey is a reflected struct in UE 5.8.  Its Python wrapper no longer
    # accepts the key name as a positional constructor argument.
    key = unreal.Key()
    key.set_editor_property("key_name", unreal.Name(key_name))
    return key


def create_input_assets():
    # The reflected C++ types contain an underscore before Factory. UE Python
    # preserves it in current 5.8 builds; the alternate name keeps the script
    # usable if a later build normalizes it.
    action_factory = factory_type("InputAction_Factory", "InputActionFactory")
    context_factory = factory_type(
        "InputMappingContext_Factory", "InputMappingContextFactory"
    )

    move = load_or_create_asset("IA_DY_Move", INPUT_DIR, unreal.InputAction, action_factory)
    look = load_or_create_asset("IA_DY_Look", INPUT_DIR, unreal.InputAction, action_factory)
    reset = load_or_create_asset("IA_DY_ResetOperator", INPUT_DIR, unreal.InputAction, action_factory)
    context = load_or_create_asset(
        "IMC_DY_Explore", INPUT_DIR, unreal.InputMappingContext, context_factory
    )

    move.set_editor_property("value_type", unreal.InputActionValueType.AXIS2D)
    look.set_editor_property("value_type", unreal.InputActionValueType.AXIS2D)
    reset.set_editor_property("value_type", unreal.InputActionValueType.BOOLEAN)

    # Development-only physical bindings. They are intentionally replaceable
    # without changing the semantic Input Actions or gameplay code.
    context.unmap_all()

    context.map_key(move, make_key("W"))
    context.map_key(move, make_key("S"))
    context.map_key(move, make_key("A"))
    context.map_key(move, make_key("D"))
    context.map_key(look, make_key("Mouse2D"))
    context.map_key(reset, make_key("R"))

    # FEnhancedActionKeyMapping is exposed to Python as a value struct.  The
    # object returned by map_key() is therefore not a durable reference to the
    # array entry.  Modify the copied entries and assign the complete array
    # back to the profile so the modifiers are serialized into the asset.
    default_key_mappings = context.get_editor_property("default_key_mappings")
    mappings = list(default_key_mappings.get_editor_property("mappings"))
    require(len(mappings) == 6, f"Expected 6 Dev mappings, found {len(mappings)}")

    add_modifier(find_mapping(mappings, move, "W"), unreal.InputModifierSwizzleAxis(outer=context))
    add_modifier(find_mapping(mappings, move, "S"), unreal.InputModifierNegate(outer=context))
    add_modifier(find_mapping(mappings, move, "S"), unreal.InputModifierSwizzleAxis(outer=context))
    add_modifier(find_mapping(mappings, move, "A"), unreal.InputModifierNegate(outer=context))

    default_key_mappings.set_editor_property("mappings", mappings)
    context.set_editor_property("default_key_mappings", default_key_mappings)

    for asset in (move, look, reset, context):
        save_asset(asset)

    saved_mappings = list(context.get_editor_property("default_key_mappings").get_editor_property("mappings"))
    require(len(saved_mappings) == 6, f"Expected 6 Dev mappings, found {len(saved_mappings)}")
    require(len(find_mapping(saved_mappings, move, "W").get_editor_property("modifiers")) == 1, "W modifier did not persist")
    require(len(find_mapping(saved_mappings, move, "S").get_editor_property("modifiers")) == 2, "S modifiers did not persist")
    require(len(find_mapping(saved_mappings, move, "A").get_editor_property("modifiers")) == 1, "A modifier did not persist")
    unreal.log("DY Phase1: input assets created and saved")


def mark_generated(actor, label):
    require(actor, f"Failed to spawn actor '{label}'")
    actor.set_actor_label(label)
    actor.set_editor_property("tags", [GENERATED_TAG])
    return actor


def spawn_static_mesh(actor_subsystem, mesh, material, label, location, scale, rotation=None):
    actor = mark_generated(
        actor_subsystem.spawn_actor_from_class(
            unreal.StaticMeshActor,
            location,
            rotation or unreal.Rotator(),
            False,
        ),
        label,
    )
    component = require(
        actor.get_component_by_class(unreal.StaticMeshComponent),
        f"{label} has no StaticMeshComponent",
    )
    component.set_static_mesh(mesh)
    if material:
        component.set_material(0, material)
    actor.set_actor_scale3d(scale)
    return actor


def spawn_text(actor_subsystem, label, text, location, rotation):
    actor = mark_generated(
        actor_subsystem.spawn_actor_from_class(
            unreal.TextRenderActor, location, rotation, False
        ),
        label,
    )
    component = require(
        actor.get_component_by_class(unreal.TextRenderComponent),
        f"{label} has no TextRenderComponent",
    )
    component.set_editor_property("text", text)
    component.set_editor_property("world_size", 32.0)
    # Epic's reflected enum name has changed across engine branches (and was
    # historically misspelled), and the reflected member spelling varies too
    # (EHTA_CENTER vs CENTER). Alignment is cosmetic, so probe the reflected
    # members instead of depending on one exact spelling.
    alignment_enum = getattr(unreal, "HorizontalTextAligment", None)
    if alignment_enum is None:
        alignment_enum = getattr(unreal, "HorizTextAligment", None)
    center_value = None
    if alignment_enum is not None:
        center_value = next(
            (
                getattr(alignment_enum, name)
                for name in dir(alignment_enum)
                if "CENTER" in name.upper()
            ),
            None,
        )
    if center_value is not None:
        component.set_editor_property("horizontal_alignment", center_value)
    return actor


def create_dev_map():
    level_subsystem = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    actor_subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    editor_subsystem = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)

    if unreal.EditorAssetLibrary.does_asset_exist(MAP_PATH):
        require(level_subsystem.load_level(MAP_PATH), f"Failed to load {MAP_PATH}")
    else:
        require(level_subsystem.new_level(MAP_PATH, False), f"Failed to create {MAP_PATH}")

    for actor in list(actor_subsystem.get_all_level_actors()):
        if GENERATED_TAG in list(actor.get_editor_property("tags")):
            actor_subsystem.destroy_actor(actor)

    cube = require(unreal.load_asset("/Engine/BasicShapes/Cube.Cube"), "Missing Engine cube")
    material = unreal.load_asset(
        "/Engine/BasicShapes/BasicShapeMaterial_Inst.BasicShapeMaterial_Inst"
    )

    # Main platform: its open outer edges make the FellOutOfWorld reset testable.
    spawn_static_mesh(
        actor_subsystem,
        cube,
        material,
        "DEV_Floor",
        unreal.Vector(0.0, 0.0, -50.0),
        unreal.Vector(24.0, 18.0, 1.0),
    )

    # Camera collision and spatial-readability fixtures.
    spawn_static_mesh(actor_subsystem, cube, material, "DEV_BackScreen", unreal.Vector(950.0, 0.0, 350.0), unreal.Vector(0.5, 9.0, 8.0))
    spawn_static_mesh(actor_subsystem, cube, material, "DEV_LeftBoundary", unreal.Vector(0.0, -875.0, 200.0), unreal.Vector(24.0, 0.5, 4.0))
    spawn_static_mesh(actor_subsystem, cube, material, "DEV_RightBoundary", unreal.Vector(0.0, 875.0, 200.0), unreal.Vector(24.0, 0.5, 4.0))
    spawn_static_mesh(actor_subsystem, cube, material, "DEV_CameraWall", unreal.Vector(-100.0, 0.0, 170.0), unreal.Vector(0.45, 3.0, 3.4))
    spawn_static_mesh(actor_subsystem, cube, material, "DEV_InnerCornerA", unreal.Vector(420.0, -520.0, 150.0), unreal.Vector(3.0, 0.35, 3.0))
    spawn_static_mesh(actor_subsystem, cube, material, "DEV_InnerCornerB", unreal.Vector(690.0, -250.0, 150.0), unreal.Vector(0.35, 3.0, 3.0))
    spawn_static_mesh(actor_subsystem, cube, material, "DEV_LowCeiling", unreal.Vector(420.0, 500.0, 285.0), unreal.Vector(3.0, 2.2, 0.3))
    spawn_static_mesh(actor_subsystem, cube, material, "DEV_LowCeilingPostA", unreal.Vector(170.0, 300.0, 125.0), unreal.Vector(0.3, 0.3, 2.5))
    spawn_static_mesh(actor_subsystem, cube, material, "DEV_LowCeilingPostB", unreal.Vector(670.0, 300.0, 125.0), unreal.Vector(0.3, 0.3, 2.5))

    # A small stepped fixture checks movement braking and scale without adding gameplay.
    for index, (x, z) in enumerate(((220.0, 12.5), (310.0, 25.0), (400.0, 37.5))):
        spawn_static_mesh(
            actor_subsystem,
            cube,
            material,
            f"DEV_Step_{index + 1}",
            unreal.Vector(x, 650.0, z),
            unreal.Vector(0.9, 1.5, (index + 1) * 0.25),
        )

    player_start = mark_generated(
        actor_subsystem.spawn_actor_from_class(
            unreal.PlayerStart,
            unreal.Vector(-900.0, 0.0, 120.0),
            unreal.Rotator(0.0, 0.0, 0.0),
            False,
        ),
        "DEV_PlayerStart",
    )
    player_start.set_actor_rotation(unreal.Rotator(0.0, 0.0, 0.0), False)

    directional = mark_generated(
        actor_subsystem.spawn_actor_from_class(
            unreal.DirectionalLight,
            unreal.Vector(0.0, 0.0, 800.0),
            unreal.Rotator(-45.0, -35.0, 0.0),
            False,
        ),
        "DEV_DirectionalLight",
    )
    directional_component = directional.get_component_by_class(unreal.DirectionalLightComponent)
    directional_component.set_editor_property("intensity", 3.0)

    skylight = mark_generated(
        actor_subsystem.spawn_actor_from_class(
            unreal.SkyLight, unreal.Vector(0.0, 0.0, 500.0), unreal.Rotator(), False
        ),
        "DEV_SkyLight",
    )
    skylight_component = skylight.get_component_by_class(unreal.SkyLightComponent)
    skylight_component.set_editor_property("intensity", 0.8)

    point_light = mark_generated(
        actor_subsystem.spawn_actor_from_class(
            unreal.PointLight,
            unreal.Vector(-650.0, 0.0, 450.0),
            unreal.Rotator(),
            False,
        ),
        "DEV_PointLight",
    )
    point_component = point_light.get_component_by_class(unreal.PointLightComponent)
    point_component.set_editor_property("intensity", 2500.0)
    point_component.set_editor_property("attenuation_radius", 1800.0)

    spawn_text(
        actor_subsystem,
        "DEV_Label_Title",
        "DY PHASE 1 - INTERACTION LAB",
        unreal.Vector(-850.0, -520.0, 260.0),
        unreal.Rotator(0.0, 90.0, 0.0),
    )
    spawn_text(
        actor_subsystem,
        "DEV_Label_Input",
        "DEV ONLY: WASD MOVE | MOUSE LOOK | R RESET",
        unreal.Vector(-850.0, -520.0, 210.0),
        unreal.Rotator(0.0, 90.0, 0.0),
    )

    world = require(editor_subsystem.get_editor_world(), "No editor world after map creation")
    world_settings = require(world.get_world_settings(), "No WorldSettings")
    world_settings.set_editor_property("kill_z", -900.0)
    game_mode_class = require(
        unreal.load_class(None, "/Script/DengYingShanHai.DYStageGameMode"),
        "Cannot load ADYStageGameMode class",
    )
    world_settings.set_editor_property("default_game_mode", game_mode_class)

    require(level_subsystem.save_current_level(), f"Failed to save {MAP_PATH}")
    unreal.log("DY Phase1: Dev interaction map created and saved")


def main():
    unreal.log("DY Phase1: asset generation started")
    create_input_assets()
    create_dev_map()
    unreal.log("DY_PHASE1_ASSETS_CREATED")


main()
