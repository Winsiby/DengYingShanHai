# -*- coding: utf-8 -*-
"""Import three articulated puppets into one isolated Dev review level.

Run only in a disposable UE editor process. This script never loads the formal map,
changes project settings, or imports physics/collision. FBX options are from the
installed UE 5.8.3 headers and the project's existing ArtPolish importer.
"""
import glob
import hashlib
import json
import os
import traceback
import unreal

SOURCE = "D:/灯影山海/Assets/Sources/DengYingArt/ThreePuppets-20261022/Run2"
BASE = "/Game/DengYingShanHai/Dev/ThreePuppets_20261022"
MAP = BASE + "/L_ThreePuppetsReview"
AUDIT = "D:/灯影山海/Saved/Audit-2026-10-22-ThreePuppets"
BRASS = "/Game/DengYingShanHai/Dev/KuafuAppearance/Materials/MI_DY_AgedBrass"
CHARACTERS = (
    ("Jingwei", ("Rest", "Flight", "Reach"), -360.0),
    ("Xingtian", ("Rest", "Guard", "Reach"), 0.0),
    ("Zhulong", ("Rest", "Day", "Night", "Reach"), 360.0),
)
GEOMETRY = {"Jingwei": (17, 160.0), "Xingtian": (14, 180.0), "Zhulong": (8, 200.0)}
EAL = unreal.EditorAssetLibrary
MEL = unreal.MaterialEditingLibrary
TOOLS = unreal.AssetToolsHelpers.get_asset_tools()
R = dict(ok=False, scope=BASE, map=MAP, source=SOURCE, saved=[], imported=[],
         characters={}, checks=[], warnings=[], scene={})
PREVIOUS_FBX = None
WORLD = None


def require(value, message):
    if not value:
        raise RuntimeError(message)
    R["checks"].append(message)
    return value


def package(asset):
    return asset.get_path_name().split(".")[0]


def path(asset):
    return asset.get_path_name() if asset else None


def vector(value):
    return [round(float(value.x), 5), round(float(value.y), 5), round(float(value.z), 5)]


def own_package(value):
    require(value.startswith(BASE + "/"), "Destination inside exact Dev namespace: " + value)
    return value


def save(asset):
    value = own_package(package(asset))
    require(EAL.save_loaded_asset(asset, only_if_is_dirty=False), "Saved " + value)
    if value not in R["saved"]:
        R["saved"].append(value)


def create(value, asset_class, factory):
    own_package(value)
    if EAL.does_asset_exist(value):
        asset = require(EAL.load_asset(value), "Loaded own existing " + value)
        require(isinstance(asset, asset_class), "Existing own asset has expected type: " + value)
        return asset
    return require(TOOLS.create_asset(value.rsplit("/", 1)[1], value.rsplit("/", 1)[0],
                                     asset_class, factory), "Created " + value)


def import_file(filename, destination, options=None):
    require(os.path.isfile(filename), "Source exists: " + filename)
    own_package(destination)
    task = unreal.AssetImportTask()
    properties = dict(filename=filename, destination_path=destination.rsplit("/", 1)[0],
                      destination_name=destination.rsplit("/", 1)[1], automated=True,
                      replace_existing=True, replace_existing_settings=True, save=False)
    if options is not None:
        properties.update(factory=unreal.FbxFactory(), options=options)
    task.set_editor_properties(properties)
    TOOLS.import_asset_tasks([task])
    imported = list(task.get_editor_property("imported_object_paths"))
    require(imported, "Importer returned objects: " + filename)
    require(all(p.split(".")[0].startswith(BASE + "/") for p in imported),
            "All imported packages stay in the Dev namespace")
    R["imported"].append(dict(source=filename, paths=imported,
                              sha256=hashlib.sha256(open(filename, "rb").read()).hexdigest()))
    asset = EAL.load_asset(destination)
    if asset is None:
        candidates = [EAL.load_asset(p) for p in imported]
        expected_type = unreal.AnimSequence if options and not options.get_editor_property("import_mesh") else None
        candidates = [a for a in candidates if a and (expected_type is None or isinstance(a, expected_type))]
        require(len(candidates) == 1, "Exactly one animation when importer changed its name")
        actual = candidates[0]
        require(EAL.rename_asset(package(actual), destination), "Normalize imported asset name")
        asset = EAL.load_asset(destination)
    require(asset, "Actual imported asset: " + destination)
    return asset


def fbx_options(animation=False, skeleton=None, name=""):
    options = unreal.FbxImportUI()
    options.set_editor_properties(dict(
        mesh_type_to_import=(unreal.FBXImportType.FBXIT_ANIMATION if animation
                             else unreal.FBXImportType.FBXIT_SKELETAL_MESH),
        import_as_skeletal=True, import_mesh=not animation, import_animations=animation,
        import_materials=False, import_textures=False, create_physics_asset=False,
        automated_import_should_detect_type=False, override_full_name=True))
    if skeleton:
        options.set_editor_property("skeleton", skeleton)
    if animation:
        options.set_editor_property("override_animation_name", name)
        data = options.get_editor_property("anim_sequence_import_data")
        data.set_editor_properties(dict(convert_scene=True, convert_scene_unit=True,
            force_front_x_axis=False, import_uniform_scale=1.0, import_bone_tracks=True,
            import_custom_attribute=False, import_meshes_in_bone_hierarchy=False,
            use_default_sample_rate=True,
            animation_length=unreal.FBXAnimationLengthImportType.FBXALIT_EXPORTED_TIME))
    else:
        data = options.get_editor_property("skeletal_mesh_import_data")
        data.set_editor_properties(dict(convert_scene=True, convert_scene_unit=True,
            force_front_x_axis=False, import_uniform_scale=1.0,
            normal_import_method=unreal.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS,
            update_skeleton_reference_pose=False, use_t0_as_ref_pose=False,
            import_morph_targets=False, import_meshes_in_bone_hierarchy=True))
    return options


def texture(character, kind):
    name = "T_DY_" + character + "_" + kind
    asset = import_file(SOURCE + "/" + character + "/" + name + ".png", BASE + "/Textures/" + name)
    require(isinstance(asset, unreal.Texture2D), "Imported Texture2D " + name)
    compression = (unreal.TextureCompressionSettings.TC_NORMALMAP if kind == "NormalDX"
                   else unreal.TextureCompressionSettings.TC_MASKS if kind == "ORM"
                   else unreal.TextureCompressionSettings.TC_DEFAULT)
    asset.set_editor_properties(dict(srgb=kind in ("BaseColor", "ClosedBaseColor"), compression_settings=compression))
    if kind in ('BaseColor','ClosedBaseColor'):asset.set_editor_property('never_stream',True)
    save(asset)
    return asset


def node(material, cls, x, y, **properties):
    value = require(MEL.create_material_expression(material, cls, x, y),
                    "Created graph node " + cls.__name__)
    if properties:
        value.set_editor_properties(properties)
    return value


def link_root(expression, output, prop):
    require(MEL.connect_material_property(expression, output, prop), "Connected " + str(prop))


def compile_and_save(material):
    if material.get_name().endswith(('Skin','CutEdge')):MEL.set_base_material_usage(material,unreal.MaterialUsage.MATUSAGE_SKELETAL_MESH,True)
    errors = MEL.recompile_material(material)
    require(not errors, "Material compiles: " + package(material))
    save(material)


def parent_materials(first_textures):
    skin_path = BASE + "/Materials/M_DY_ThreePuppets_Skin"
    skin = create(skin_path, unreal.Material, unreal.MaterialFactoryNew())
    MEL.delete_all_material_expressions(skin)
    skin.set_editor_properties(dict(material_domain=unreal.MaterialDomain.MD_SURFACE,
        blend_mode=unreal.BlendMode.BLEND_OPAQUE,
        shading_model=unreal.MaterialShadingModel.MSM_DEFAULT_LIT,
        two_sided=False, tangent_space_normal=True, use_material_attributes=False))
    samples = {}
    for index, kind in enumerate(("BaseColor", "NormalDX", "ORM")):
        sampler = (unreal.MaterialSamplerType.SAMPLERTYPE_NORMAL if kind == "NormalDX"
                   else unreal.MaterialSamplerType.SAMPLERTYPE_MASKS if kind == "ORM"
                   else unreal.MaterialSamplerType.SAMPLERTYPE_COLOR)
        samples[kind] = node(skin, unreal.MaterialExpressionTextureSampleParameter2D, -450, index*220,
                            parameter_name=kind, texture=first_textures[kind], sampler_type=sampler)
    for kind, channel, prop in (
        ("BaseColor", "RGB", unreal.MaterialProperty.MP_BASE_COLOR),
        ("NormalDX", "RGB", unreal.MaterialProperty.MP_NORMAL),
        ("ORM", "R", unreal.MaterialProperty.MP_AMBIENT_OCCLUSION),
        ("ORM", "G", unreal.MaterialProperty.MP_ROUGHNESS),
        ("ORM", "B", unreal.MaterialProperty.MP_METALLIC)):
        link_root(samples[kind], channel, prop)
    compile_and_save(skin)
    edge = solid_material(BASE + "/Materials/M_DY_ThreePuppets_CutEdge",
                          (0.045, 0.014, 0.005), 0.9)
    screen = solid_material(BASE + "/Materials/M_DY_ThreePuppets_Screen",
                            (0.55, 0.49, 0.39), 0.95)
    return skin, edge, screen


def solid_material(value, color, roughness):
    material = create(value, unreal.Material, unreal.MaterialFactoryNew())
    MEL.delete_all_material_expressions(material)
    material.set_editor_properties(dict(material_domain=unreal.MaterialDomain.MD_SURFACE,
        blend_mode=unreal.BlendMode.BLEND_OPAQUE,
        shading_model=unreal.MaterialShadingModel.MSM_DEFAULT_LIT, two_sided=False))
    color_node = node(material, unreal.MaterialExpressionConstant3Vector, -250, 0,
                      constant=unreal.LinearColor(color[0], color[1], color[2], 1.0))
    rough_node = node(material, unreal.MaterialExpressionConstant, -250, 160, r=roughness)
    metal_node = node(material, unreal.MaterialExpressionConstant, -250, 300, r=0.0)
    link_root(color_node, "", unreal.MaterialProperty.MP_BASE_COLOR)
    link_root(rough_node, "", unreal.MaterialProperty.MP_ROUGHNESS)
    link_root(metal_node, "", unreal.MaterialProperty.MP_METALLIC)
    compile_and_save(material)
    return material


def instance(value, parent, textures=None):
    material = create(value, unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
    MEL.set_material_instance_parent(material, parent)
    MEL.set_material_usage_override(material,unreal.MaterialUsage.MATUSAGE_SKELETAL_MESH,True,True)
    for name, asset in (textures or {}).items():
        MEL.set_material_instance_texture_parameter_value(material, name, asset)
        require(MEL.get_material_instance_texture_parameter_value(material, name) == asset,
                "Readback texture parameter " + value + "/" + name)
    MEL.update_material_instance(material)
    save(material)
    return material


def assign_materials(mesh, materials):
    slots = list(mesh.get_editor_property('materials'))
    require(len(slots) == len(materials), "Exact role-specific material slot count")
    rows = []
    seen = set()
    for index, slot in enumerate(slots):
        imported_name = str(slot.get_editor_property("imported_material_slot_name"))
        visible_name = str(slot.get_editor_property("material_slot_name"))
        text = (imported_name + " " + visible_name).lower()
        if "eyelidskin" in text:
            require("EyelidSkin" in materials, "Only Zhulong has an EyelidSkin slot")
            name = "EyelidSkin"
        else:
            matching = [name for name in ("Skin", "CutEdge", "Brass") if name.lower() in text]
            require(len(matching) == 1, "Known source material slot: " + imported_name)
            name = matching[0]
        seen.add(name)
        slot.set_editor_property("material_interface", materials[name])
        rows.append(dict(index=index, imported_name=imported_name, slot_name=visible_name,
                         material=path(materials[name])))
    require(seen == set(materials), "All expected material slots assigned")
    mesh.set_editor_property('materials', slots)
    save(mesh)
    return rows


def spawn(actor_class, label, location):
    actor = require(ACTORS.spawn_actor_from_class(actor_class, unreal.Vector(*location), unreal.Rotator(), False),
                    "Spawned " + label)
    actor.set_actor_label("DYThreePuppets_" + label)
    return actor


def scene(meshes, animations, screen_material):
    cube = require(EAL.load_asset("/Engine/BasicShapes/Cube"), "Engine cube for independent screens")
    R["scene"]["characters"] = {}
    for character, poses, y in CHARACTERS:
        actor = spawn(unreal.SkeletalMeshActor, character, (0.0, y, 0.0))
        component = require(actor.get_component_by_class(unreal.SkeletalMeshComponent), "Skeletal mesh component")
        saved_mesh = require(EAL.load_asset(package(meshes[character])), "Read saved mesh asset " + character)
        component.set_skeletal_mesh_asset(saved_mesh)
        expected_bones, expected_height = GEOMETRY[character]
        actual_bones = int(component.get_num_bones())
        bone_names = [str(component.get_bone_name(i)) for i in range(actual_bones)]
        require(actual_bones == expected_bones, "Exact imported bone count " + character)
        imported_bounds = saved_mesh.get_imported_bounds()
        mesh_height = float(imported_bounds.box_extent.z) * 2.0
        require(abs(mesh_height - expected_height) <= 1.0, "Imported mesh height within 1 cm: " + character)
        R["characters"][character]["mesh_bounds"] = dict(
            source="USkeletalMesh.get_imported_bounds", origin=vector(imported_bounds.origin),
            extent=vector(imported_bounds.box_extent), height_cm=mesh_height, expected_height_cm=expected_height)
        R["characters"][character]["bone_count"] = actual_bones
        R["characters"][character]["bone_names"] = bone_names
        if character == "Zhulong":
            require("Eyelid" in bone_names, "Real Eyelid bone imported")
            R["characters"][character]["eyelid_bone_index"] = bone_names.index("Eyelid")
        component.set_mobility(unreal.ComponentMobility.MOVABLE)
        component.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
        component.set_cast_shadow(True)
        component.set_editor_property("cast_dynamic_shadow", True)
        component.override_animation_data(animations[character]["Rest"], False, False, 0.0, 1.0)
        center, extent = actor.get_actor_bounds(False)
        require(extent.z > 10 and max(extent.y, extent.x) > 10, "Nonempty puppet world bounds " + character)
        require(extent.z < 350 and max(extent.y, extent.x) < 650, "Puppet cm scale bounded " + character)
        R["characters"][character]["bounds"] = dict(origin=vector(center), extent=vector(extent))
        R["scene"]["characters"][character] = dict(actor=path(actor), label=actor.get_actor_label(),
            location=vector(actor.get_actor_location()), animation="Rest", component=path(component))

        screen = spawn(unreal.StaticMeshActor, character + "_Screen", (-65.0, y, 100.0))
        screen.set_actor_scale3d(unreal.Vector(0.02, 4.0, 3.2))
        screen_component = screen.get_component_by_class(unreal.StaticMeshComponent)
        screen_component.set_static_mesh(cube)
        screen_component.set_material(0, screen_material)
        screen_component.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
        screen_component.set_cast_shadow(False)

        lamp = spawn(unreal.PointLight, character + "_ProjectionLight", (400.0, y, 200.0))
        lamp.set_actor_rotation(unreal.Rotator(0.0, 180.0, 0.0), False)
        light = lamp.get_component_by_class(unreal.PointLightComponent)
        light.set_mobility(unreal.ComponentMobility.MOVABLE)
        light.set_editor_properties(dict(intensity_units=unreal.LightUnits.CANDELAS,
            intensity=1600.0, attenuation_radius=540.0, source_radius=0.3,
            use_inverse_squared_falloff=True, cast_shadows=True))
        light.set_light_color(unreal.LinearColor(1.0, 0.91, 0.78, 1.0))
    post = spawn(unreal.PostProcessVolume, "ManualExposure", (0.0, 0.0, 140.0))
    post.set_editor_properties(dict(unbound=True, priority=100.0))
    settings = post.get_editor_property("settings")
    manual = require(next((getattr(unreal.AutoExposureMethod, n) for n in dir(unreal.AutoExposureMethod)
                           if "MANUAL" in n.upper()), None), "Manual exposure enum available")
    settings.set_editor_properties(dict(override_auto_exposure_method=True, auto_exposure_method=manual,
        override_auto_exposure_bias=True, auto_exposure_bias=4.0,
        override_auto_exposure_apply_physical_camera_exposure=True,
        auto_exposure_apply_physical_camera_exposure=True,
        override_camera_iso=True, camera_iso=400.0,
        override_camera_shutter_speed=True, camera_shutter_speed=60.0,
        override_depth_of_field_fstop=True, depth_of_field_fstop=4.0))
    post.set_editor_property("settings", settings)
    R["scene"]["lighting"] = dict(type="Movable PointLight", units="candela", intensity=1600,
        distance_to_mesh_cm=400, source_radius_cm=0.3, attenuation_radius_cm=540,
        exposure=dict(method="Manual", iso=400, shutter_reciprocal_s=60, fstop=4, compensation_stops=4),
        note="Independent review baseline; visually verify exposure and silhouette before art acceptance.")
    require(unreal.EditorLoadingAndSavingUtils.save_map(WORLD, MAP), "Saved own review level")
    R["map_saved"] = True


try:
    os.makedirs(AUDIT, exist_ok=True)
    for character, poses, y in CHARACTERS:
        directory = SOURCE + "/" + character
        expected = [directory + "/SK_DY_" + character + ".fbx"]
        expected += [directory + "/A_DY_" + character + "_" + pose + ".fbx" for pose in poses]
        expected += [directory + "/T_DY_" + character + "_" + kind + ".png"
                     for kind in ("BaseColor", "NormalDX", "ORM")]
        if character == "Zhulong":
            expected.append(directory + "/T_DY_Zhulong_ClosedBaseColor.png")
        require(all(os.path.isfile(p) for p in expected), "Complete exported source set " + character)
    brass = require(EAL.load_asset(BRASS), "Existing unchanged brass source material")
    require(unreal.SystemLibrary.get_console_variable_int_value("r.Substrate") == 0,
            "Project uses legacy DefaultLit material path")
    LEVELS = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    ACTORS = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    if EAL.does_asset_exist(MAP):
        require(LEVELS.load_level(MAP), "Loaded only own review level")
    else:
        require(LEVELS.new_level(MAP, False), "Created empty independent review level")
    WORLD = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    for actor in list(ACTORS.get_all_level_actors()):
        if actor.get_actor_label().startswith("DYThreePuppets_"):
            require(ACTORS.destroy_actor(actor), "Replace own previous review actor")
    PREVIOUS_FBX = unreal.SystemLibrary.get_console_variable_int_value("Interchange.FeatureFlags.Import.FBX")
    unreal.SystemLibrary.execute_console_command(WORLD, "Interchange.FeatureFlags.Import.FBX 0", None)
    require(unreal.SystemLibrary.get_console_variable_int_value("Interchange.FeatureFlags.Import.FBX") == 0,
            "Legacy FBX importer active only for this process")
    textures = {character: {kind: texture(character, kind) for kind in ("BaseColor", "NormalDX", "ORM")}
                for character, poses, y in CHARACTERS}
    textures["Zhulong"]["ClosedBaseColor"] = texture("Zhulong", "ClosedBaseColor")
    skin, edge, screen_material = parent_materials(textures["Jingwei"])
    meshes, animations = {}, {}
    for character, poses, y in CHARACTERS:
        mesh_path = BASE + "/Meshes/SK_DY_" + character
        mesh = import_file(SOURCE + "/" + character + "/SK_DY_" + character + ".fbx",
                           mesh_path, fbx_options())
        require(isinstance(mesh, unreal.SkeletalMesh), "Actual SkeletalMesh " + character)
        require(mesh.get_editor_property("physics_asset") is None, "No physics asset generated")
        skeleton = require(mesh.get_editor_property('skeleton'), "Imported skeleton " + character)
        require(package(skeleton).startswith(BASE + "/"), "Skeleton inside own Dev namespace")
        save(skeleton)
        materials = {
            "Skin": instance(BASE + "/Materials/MI_DY_" + character + "_Skin", skin,
                             {kind: textures[character][kind] for kind in ("BaseColor", "NormalDX", "ORM")}),
            "CutEdge": instance(BASE + "/Materials/MI_DY_" + character + "_CutEdge", edge),
            "Brass": instance(BASE + "/Materials/MI_DY_" + character + "_Brass", brass)}
        if character == "Zhulong":
            eyelid_textures = {kind: textures[character][kind] for kind in ("NormalDX", "ORM")}
            eyelid_textures["BaseColor"] = textures[character]["ClosedBaseColor"]
            materials["EyelidSkin"] = instance(BASE + "/Materials/MI_DY_Zhulong_EyelidSkin", skin, eyelid_textures)
        slots = assign_materials(mesh, materials)
        meshes[character] = mesh
        animations[character] = {}
        row = dict(mesh=path(mesh), skeleton=path(skeleton), slots=slots,
                   textures={k:path(v) for k,v in textures[character].items()}, animations={})
        R["characters"][character] = row
        for pose in poses:
            name = "A_DY_" + character + "_" + pose
            animation = import_file(SOURCE + "/" + character + "/" + name + ".fbx",
                                    BASE + "/Animations/" + name, fbx_options(True, skeleton, name))
            require(isinstance(animation, unreal.AnimSequence), "Actual AnimSequence " + name)
            require(animation.get_editor_property("skeleton") == skeleton, "Animation uses its own skeleton " + name)
            duration = float(animation.get_play_length())
            require(duration > 0.0, "Nonzero animation duration " + name)
            save(animation)
            animations[character][pose] = animation
            row["animations"][pose] = dict(path=path(animation), duration_seconds=duration)
    scene(meshes, animations, screen_material)
    R["counts"] = dict(meshes=len(meshes), textures=sum(len(x) for x in textures.values()),
                       animations=sum(len(x) for x in animations.values()))
    require(R["counts"] == dict(meshes=3, textures=10, animations=10), "Complete model and animation counts")
    R["ok"] = True
except Exception:
    R["error"] = traceback.format_exc()
    unreal.log_error(R["error"])
finally:
    if PREVIOUS_FBX is not None and WORLD is not None:
        try:
            unreal.SystemLibrary.execute_console_command(
                WORLD, "Interchange.FeatureFlags.Import.FBX " + str(PREVIOUS_FBX), None)
            R["fbx_flag_restored"] = (
                unreal.SystemLibrary.get_console_variable_int_value("Interchange.FeatureFlags.Import.FBX")
                == PREVIOUS_FBX)
        except Exception:
            R["fbx_restore_error"] = traceback.format_exc()
            R["ok"] = False
    os.makedirs(AUDIT, exist_ok=True)
    with open(AUDIT + "/UE-Import.json", "w", encoding="utf-8") as stream:
        json.dump(R, stream, ensure_ascii=False, indent=2)
    if R["ok"]:
        unreal.log("THREE_PUPPETS_IMPORT_OK " + MAP)
    unreal.SystemLibrary.quit_editor()


