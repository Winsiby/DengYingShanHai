# -*- coding: utf-8 -*-
"""Import puppet assets into production content and author the four-chapter cast."""
import hashlib, json, os, traceback
import unreal

SOURCE = "D:/灯影山海/Assets/Sources/DengYingArt/ThreePuppets-20261022/Run4"
BASE = "/Game/DengYingShanHai/Puppets"
AUDIT = "D:/灯影山海/Saved/Audit-2026-10-22-FourAct"
CAST = BASE + "/DA_DYPuppetCast"
BRASS = "/Game/DengYingShanHai/Dev/KuafuAppearance/Materials/MI_DY_AgedBrass"
KUAFU_MESH = "/Game/DengYingShanHai/Dev/KuafuAppearance/Puppet/SK_DY_Kuafu_M01_LeftGrip_v04.SK_DY_Kuafu_M01_LeftGrip_v04"
CHARACTERS = (("Jingwei", ("Rest", "Flight", "Reach")),
              ("Xingtian", ("Rest", "Guard", "Reach")),
              ("Zhulong", ("Rest", "Day", "Night", "Reach")))
EAL = unreal.EditorAssetLibrary
MEL = unreal.MaterialEditingLibrary
TOOLS = unreal.AssetToolsHelpers.get_asset_tools()
R = dict(ok=False, imported=[], materials={}, checks=[], errors=[])


def require(v, m):
    if not v:
        raise RuntimeError(m)
    R["checks"].append(m)
    return v


def pkg(a):
    return a.get_path_name().split(".")[0]


def save(a):
    require(EAL.save_loaded_asset(a, only_if_is_dirty=False), "Saved " + pkg(a))


def create(path, cls, factory):
    if EAL.does_asset_exist(path):
        return require(EAL.load_asset(path), "Loaded " + path)
    return require(TOOLS.create_asset(path.rsplit("/", 1)[1], path.rsplit("/", 1)[0], cls, factory), "Created " + path)


def import_file(filename, dest, options=None):
    require(os.path.isfile(filename), "Source exists " + filename)
    task = unreal.AssetImportTask()
    props = dict(filename=filename, destination_path=dest.rsplit("/", 1)[0], destination_name=dest.rsplit("/", 1)[1],
                 automated=True, replace_existing=True, replace_existing_settings=True, save=False)
    if options is not None:
        props.update(factory=unreal.FbxFactory(), options=options)
    task.set_editor_properties(props)
    TOOLS.import_asset_tasks([task])
    paths = list(task.get_editor_property("imported_object_paths"))
    require(paths, "Importer returned objects " + filename)
    asset = EAL.load_asset(dest)
    if asset is None:
        cands = [EAL.load_asset(p) for p in paths]
        cands = [a for a in cands if a and (isinstance(a, unreal.AnimSequence) if options and not options.get_editor_property("import_mesh") else isinstance(a, unreal.SkeletalMesh))]
        require(len(cands) == 1, "Single imported asset when the name changed")
        EAL.rename_asset(pk, dest) if False else EAL.rename_asset(cands[0].get_path_name().split(".")[0], dest)
        asset = EAL.load_asset(dest)
    require(asset, "Loaded imported " + dest)
    R["imported"].append(dict(source=filename, path=pkg(asset), sha256=hashlib.sha256(open(filename, "rb").read()).hexdigest()))
    return asset


def texture(character, kind):
    name = "T_DY_" + character + "_" + kind
    asset = import_file(SOURCE + "/" + character + "/" + name + ".png", BASE + "/Textures/" + name)
    require(isinstance(asset, unreal.Texture2D), "Texture2D " + name)
    comp = (unreal.TextureCompressionSettings.TC_NORMALMAP if kind == "NormalDX"
            else unreal.TextureCompressionSettings.TC_MASKS if kind == "ORM"
            else unreal.TextureCompressionSettings.TC_DEFAULT)
    asset.set_editor_properties(dict(srgb=kind in ("BaseColor", "ClosedBaseColor"), compression_settings=comp))
    if kind in ("BaseColor", "ClosedBaseColor"):
        asset.set_editor_property("never_stream", True)
        asset.set_editor_property("lod_group", unreal.TextureGroup.TEXTUREGROUP_CHARACTER)
    save(asset)
    return asset


def node(material, cls, x, y, **props):
    v = require(MEL.create_material_expression(material, cls, x, y), "Graph node " + cls.__name__)
    if props:
        v.set_editor_properties(props)
    return v


def link(expr, out, prop):
    require(MEL.connect_material_property(expr, out, prop), "Connected " + str(prop))


def skin_parent(first):
    m = create(BASE + "/Materials/M_DY_PuppetSkin", unreal.Material, unreal.MaterialFactoryNew())
    MEL.delete_all_material_expressions(m)
    m.set_editor_properties(dict(material_domain=unreal.MaterialDomain.MD_SURFACE, blend_mode=unreal.BlendMode.BLEND_OPAQUE,
                                 shading_model=unreal.MaterialShadingModel.MSM_DEFAULT_LIT, two_sided=False, tangent_space_normal=True))
    samples = {}
    for i, kind in enumerate(("BaseColor", "NormalDX", "ORM")):
        st = (unreal.MaterialSamplerType.SAMPLERTYPE_NORMAL if kind == "NormalDX"
              else unreal.MaterialSamplerType.SAMPLERTYPE_MASKS if kind == "ORM"
              else unreal.MaterialSamplerType.SAMPLERTYPE_COLOR)
        samples[kind] = node(m, unreal.MaterialExpressionTextureSampleParameter2D, -450, i * 220, parameter_name=kind, texture=first[kind], sampler_type=st)
    for kind, ch, prop in (("BaseColor", "RGB", unreal.MaterialProperty.MP_BASE_COLOR),
                           ("NormalDX", "RGB", unreal.MaterialProperty.MP_NORMAL),
                           ("ORM", "R", unreal.MaterialProperty.MP_AMBIENT_OCCLUSION),
                           ("ORM", "G", unreal.MaterialProperty.MP_ROUGHNESS),
                           ("ORM", "B", unreal.MaterialProperty.MP_METALLIC)):
        link(samples[kind], ch, prop)
    require(not MEL.recompile_material(m), "Puppet skin parent compiles")
    MEL.set_base_material_usage(m, unreal.MaterialUsage.MATUSAGE_SKELETAL_MESH, True)
    save(m)
    return m


def solid(path, color, rough, usage=True):
    m = create(path, unreal.Material, unreal.MaterialFactoryNew())
    MEL.delete_all_material_expressions(m)
    m.set_editor_properties(dict(material_domain=unreal.MaterialDomain.MD_SURFACE, blend_mode=unreal.BlendMode.BLEND_OPAQUE,
                                 shading_model=unreal.MaterialShadingModel.MSM_DEFAULT_LIT, two_sided=False))
    c = node(m, unreal.MaterialExpressionConstant3Vector, -250, 0, constant=unreal.LinearColor(color[0], color[1], color[2], 1.0))
    rr = node(m, unreal.MaterialExpressionConstant, -250, 160, r=rough)
    mm = node(m, unreal.MaterialExpressionConstant, -250, 300, r=0.0)
    link(c, "", unreal.MaterialProperty.MP_BASE_COLOR)
    link(rr, "", unreal.MaterialProperty.MP_ROUGHNESS)
    link(mm, "", unreal.MaterialProperty.MP_METALLIC)
    require(not MEL.recompile_material(m), "Solid material compiles " + path)
    if usage:
        MEL.set_base_material_usage(m, unreal.MaterialUsage.MATUSAGE_SKELETAL_MESH, True)
    save(m)
    return m


def instance(path, parent, textures=None):
    mi = create(path, unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
    MEL.set_material_instance_parent(mi, parent)
    for name, asset in (textures or {}).items():
        MEL.set_material_instance_texture_parameter_value(mi, name, asset)
        require(MEL.get_material_instance_texture_parameter_value(mi, name) == asset, "Readback " + path + "/" + name)
    MEL.set_material_usage_override(mi, unreal.MaterialUsage.MATUSAGE_SKELETAL_MESH, True, True)
    MEL.update_material_instance(mi)
    save(mi)
    return mi


def fbx_options(anim=False, skeleton=None, name=""):
    o = unreal.FbxImportUI()
    o.set_editor_properties(dict(mesh_type_to_import=(unreal.FBXImportType.FBXIT_ANIMATION if anim else unreal.FBXImportType.FBXIT_SKELETAL_MESH),
                                 import_as_skeletal=True, import_mesh=not anim, import_animations=anim,
                                 import_materials=False, import_textures=False, create_physics_asset=False,
                                 automated_import_should_detect_type=False, override_full_name=True))
    if skeleton:
        o.set_editor_property("skeleton", skeleton)
    if anim:
        o.set_editor_property("override_animation_name", name)
        d = o.get_editor_property("anim_sequence_import_data")
        d.set_editor_properties(dict(convert_scene=True, convert_scene_unit=True, import_uniform_scale=1.0,
                                     import_bone_tracks=True, use_default_sample_rate=True,
                                     animation_length=unreal.FBXAnimationLengthImportType.FBXALIT_EXPORTED_TIME))
    else:
        d = o.get_editor_property("skeletal_mesh_import_data")
        d.set_editor_properties(dict(convert_scene=True, convert_scene_unit=True, import_uniform_scale=1.0,
                                     normal_import_method=unreal.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS,
                                     import_morph_targets=False, import_meshes_in_bone_hierarchy=True))
    return o


def assign(mesh, materials):
    slots = list(mesh.get_editor_property("materials"))
    require(len(slots) == len(materials), "Slot count " + str(len(slots)))
    seen = set()
    for slot in slots:
        text = (str(slot.get_editor_property("imported_material_slot_name")) + " " + str(slot.get_editor_property("material_slot_name"))).lower()
        if "eyelidskin" in text:
            name = "EyelidSkin"
        else:
            name = [n for n in ("Skin", "CutEdge", "Brass") if n.lower() in text]
            require(len(name) == 1, "Known slot " + text)
            name = name[0]
        require(name in materials, "Material present for slot " + name)
        slot.set_editor_property("material_interface", materials[name])
        seen.add(name)
    require(seen == set(materials), "All slots assigned")
    mesh.set_editor_property("materials", slots)
    save(mesh)
    return sorted(seen)


def entry(label, mesh_path, anims, hide_staff, loc, rot, scale):
    e = unreal.DYPuppetFigureEntry()
    e.set_editor_property("label", label)
    e.set_editor_property("skeletal_mesh", require(unreal.load_asset(mesh_path), "Cast mesh " + mesh_path))
    e.set_editor_property("pose_animations", {unreal.Name(k): require(unreal.load_asset(v), "Cast anim " + v) for k, v in anims.items()})
    e.set_editor_property("hide_staff", hide_staff)
    e.set_editor_property("mesh_relative_location", unreal.Vector(*loc))
    e.set_editor_property("mesh_relative_rotation", unreal.Rotator(*rot))
    e.set_editor_property("mesh_relative_scale", unreal.Vector(*scale))
    return e


try:
    os.makedirs(AUDIT, exist_ok=True)
    prev = unreal.SystemLibrary.get_console_variable_int_value("Interchange.FeatureFlags.Import.FBX")
    unreal.SystemLibrary.execute_console_command(unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world(), "Interchange.FeatureFlags.Import.FBX 0", None)
    brass = require(EAL.load_asset(BRASS), "Existing brass material")
    edge = solid(BASE + "/Materials/M_DY_PuppetCutEdge", (0.05, 0.016, 0.006), 0.88)
    tex = {c: {k: texture(c, k) for k in (("BaseColor", "NormalDX", "ORM", "ClosedBaseColor") if c == "Zhulong" else ("BaseColor", "NormalDX", "ORM"))} for c, _ in CHARACTERS}
    skin = skin_parent(tex["Jingwei"])
    meshes, anims = {}, {}
    for c, poses in CHARACTERS:
        mpath = BASE + "/Meshes/SK_DY_" + c
        mesh = import_file(SOURCE + "/" + c + "/SK_DY_" + c + ".fbx", mpath, fbx_options())
        require(isinstance(mesh, unreal.SkeletalMesh), "SkeletalMesh " + c)
        require(mesh.get_editor_property("physics_asset") is None, "No physics asset " + c)
        skel = require(mesh.get_editor_property("skeleton"), "Skeleton " + c)
        save(skel)
        mats = {"Skin": instance(BASE + "/Materials/MI_DY_" + c + "_Skin", skin, tex[c]),
                "CutEdge": instance(BASE + "/Materials/MI_DY_" + c + "_CutEdge", edge),
                "Brass": instance(BASE + "/Materials/MI_DY_" + c + "_Brass", brass)}
        if c == "Zhulong":
            mats["EyelidSkin"] = instance(BASE + "/Materials/MI_DY_Zhulong_EyelidSkin", skin, tex[c])
        R["materials"][c] = assign(mesh, mats)
        meshes[c] = mesh
        anims[c] = {}
        for p in poses:
            name = "A_DY_" + c + "_" + p
            a = import_file(SOURCE + "/" + c + "/" + name + ".fbx", BASE + "/Animations/" + name, fbx_options(True, skel, name))
            require(isinstance(a, unreal.AnimSequence), "AnimSequence " + name)
            require(a.get_editor_property("skeleton") == skel, "Anim skeleton " + name)
            save(a)
            anims[c][name] = a
        save(mesh)
    # Four-chapter cast. Kuafu keeps its shipped transform so chapter one looks unchanged.
    XF = dict(loc=(0.0, -42.44, -104.57), rot=(0.0, 0.0, 180.0), scale=(0.8, 0.8, 0.8), cast_scale=(1.1, 1.1, 1.1))
    figures = [entry("夸父", KUAFU_MESH, {}, False, XF["loc"], XF["rot"], XF["scale"])]
    def anim_path(c, p):
        return pkg(anims[c]["A_DY_" + c + "_" + p])
    figures.append(entry("精卫", pkg(meshes["Jingwei"]),
                         {"None": anim_path("Jingwei", "Rest"), "P02_StrideBack": anim_path("Jingwei", "Rest"),
                          "P02_StrideMid": anim_path("Jingwei", "Flight"), "P02_StrideReach": anim_path("Jingwei", "Reach")},
                         True, XF["loc"], XF["rot"], XF["cast_scale"]))
    figures.append(entry("刑天", pkg(meshes["Xingtian"]),
                         {"None": anim_path("Xingtian", "Rest"), "P02_StrideBack": anim_path("Xingtian", "Rest"),
                          "P02_StrideMid": anim_path("Xingtian", "Guard"), "P02_StrideReach": anim_path("Xingtian", "Reach")},
                         True, XF["loc"], XF["rot"], XF["cast_scale"]))
    figures.append(entry("烛龙", pkg(meshes["Zhulong"]),
                         {"None": anim_path("Zhulong", "Night"), "P02_StrideBack": anim_path("Zhulong", "Night"),
                          "P02_StrideMid": anim_path("Zhulong", "Day"), "P02_StrideReach": anim_path("Zhulong", "Day")},
                         True, XF["loc"], XF["rot"], XF["cast_scale"]))
    factory = unreal.DataAssetFactory()
    factory.set_editor_property("data_asset_class", unreal.DYPuppetCastData)
    da = create(CAST, unreal.DYPuppetCastData, factory)
    da.set_editor_property("figures", figures)
    save(da)
    R["cast"] = dict(path=pkg(da), figures=[f.get_editor_property("label") for f in da.get_editor_property("figures")])
    require(len(da.get_editor_property("figures")) == 4, "Cast holds four chapters")
    unreal.SystemLibrary.execute_console_command(unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world(), "Interchange.FeatureFlags.Import.FBX " + str(prev), None)
    R["ok"] = True
except Exception:
    R["errors"].append(traceback.format_exc())
finally:
    os.makedirs(AUDIT, exist_ok=True)
    with open(AUDIT + "/cast-import.json", "w", encoding="utf-8") as f:
        json.dump(R, f, ensure_ascii=False, indent=2)
    print("CAST_IMPORT_DONE", R.get("ok"), len(R.get("checks", [])), R.get("errors"))
    unreal.SystemLibrary.quit_editor()
