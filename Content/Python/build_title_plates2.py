# -*- coding: utf-8 -*-
"""Rebuild the plaque master with a Gain parameter, refresh the four act instances, then render the audience view."""
import json, os, time, traceback, unreal

EAL = unreal.EditorAssetLibrary
MEL = unreal.MaterialEditingLibrary
TOOLS = unreal.AssetToolsHelpers.get_asset_tools()
BASE = "/Game/DengYingShanHai/Stage/ArtMainline"
TEX = BASE + "/Textures"
MAT = BASE + "/Materials"
MASTER = MAT + "/M_DY_TitleGlyph_Master"
SRC = r"D:\灯影山海\Saved\Audit-2026-10-22-FourAct\TitleTextures"
AUDIT = "D:/灯影山海/Saved/Audit-2026-10-22-FourAct"
GAINS = {1: 60.0, 2: 50.0, 3: 50.0, 4: 50.0}
R = {"ok": False, "checks": [], "error": None, "instances": [], "shots": []}


def req(v, msg):
    if not v:
        raise RuntimeError(msg)
    R["checks"].append(msg)
    return v


def import_tex(name):
    dst = TEX + "/" + name
    task = unreal.AssetImportTask()
    task.set_editor_properties(dict(filename=SRC + "\\" + name + ".png", destination_path=TEX,
        destination_name=name, automated=True, replace_existing=True, save=False))
    TOOLS.import_asset_tasks([task])
    tex = req(EAL.load_asset(dst), "Imported " + name)
    tex.set_editor_properties(dict(srgb=True, never_stream=True,
        compression_settings=unreal.TextureCompressionSettings.TC_DEFAULT,
        lod_group=unreal.TextureGroup.TEXTUREGROUP_WORLD))
    req(EAL.save_loaded_asset(tex, False), "Saved " + name)
    return tex


def master():
    mat = EAL.load_asset(MASTER) if EAL.does_asset_exist(MASTER) else req(
        TOOLS.create_asset("M_DY_TitleGlyph_Master", MAT, unreal.Material, unreal.MaterialFactoryNew()), "master")
    MEL.delete_all_material_expressions(mat)
    mat.set_editor_properties(dict(blend_mode=unreal.BlendMode.BLEND_MASKED,
        shading_model=unreal.MaterialShadingModel.MSM_UNLIT, two_sided=True,
        material_domain=unreal.MaterialDomain.MD_SURFACE))
    tex = req(MEL.create_material_expression(mat, unreal.MaterialExpressionTextureSampleParameter2D, -600, 0), "sampler")
    tex.set_editor_properties(dict(parameter_name="TitleGlyph", sampler_type=unreal.MaterialSamplerType.SAMPLERTYPE_COLOR))
    gain = req(MEL.create_material_expression(mat, unreal.MaterialExpressionScalarParameter, -600, 260), "gain")
    gain.set_editor_properties(dict(parameter_name="Gain", default_value=60.0))
    mul = req(MEL.create_material_expression(mat, unreal.MaterialExpressionMultiply, -300, 60), "mul")
    req(MEL.connect_material_expressions(tex, "RGB", mul, "A"), "rgb->mul")
    req(MEL.connect_material_expressions(gain, "", mul, "B"), "gain->mul")
    req(MEL.connect_material_property(mul, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR), "emissive")
    req(MEL.connect_material_property(tex, "A", unreal.MaterialProperty.MP_OPACITY_MASK), "mask")
    req(not MEL.recompile_material(mat), "master compiles")
    req(EAL.save_loaded_asset(mat, False), "master saved")
    return mat


def instance(chapter, texture, parent):
    path = MAT + "/MI_DY_TitleGlyph_Act%d" % chapter
    mi = EAL.load_asset(path) if EAL.does_asset_exist(path) else req(
        TOOLS.create_asset("MI_DY_TitleGlyph_Act%d" % chapter, MAT, unreal.MaterialInstanceConstant,
                           unreal.MaterialInstanceConstantFactoryNew()), "mi %d" % chapter)
    MEL.set_material_instance_parent(mi, parent)
    MEL.set_material_instance_texture_parameter_value(mi, "TitleGlyph", texture)
    MEL.set_material_instance_scalar_parameter_value(mi, "Gain", GAINS[chapter])
    req(MEL.get_material_instance_texture_parameter_value(mi, "TitleGlyph") == texture, "mi tex %d" % chapter)
    req(abs(MEL.get_material_instance_scalar_parameter_value(mi, "Gain") - GAINS[chapter]) < 0.01, "mi gain %d" % chapter)
    MEL.update_material_instance(mi)
    req(EAL.save_loaded_asset(mi, False), "mi saved %d" % chapter)
    R["instances"].append(dict(path=path, gain=GAINS[chapter]))
    return mi


def finish():
    try:
        if R.get("plaque"):
            R["plaque"].get_component_by_class(unreal.StaticMeshComponent).set_material(
                0, EAL.load_asset(MAT + "/M_DY_TitleGlyph"))
            R["restored"] = True
    except Exception:
        R["restore_error"] = traceback.format_exc()
    R.pop("plaque", None)
    R.pop("cam", None)
    R["map_saved"] = False
    open(AUDIT + "/title-build3.json", "w", encoding="utf-8").write(json.dumps(R, ensure_ascii=False, indent=2))
    print("TITLE_BUILD2", R["ok"], len(R["checks"]), (R["error"] or "")[:200])
    unreal.SystemLibrary.quit_editor()


try:
    textures = {n: import_tex("T_DY_TitleGlyph_Act%d" % n) for n in (2, 3, 4)}
    parent = master()
    original = req(EAL.load_asset(TEX + "/T_DY_ZhuRiTitle"), "act1 texture")
    instance(1, original, parent)
    for n, t in textures.items():
        instance(n, t, parent)
    unreal.EditorLoadingAndSavingUtils.load_map("/Game/DengYingShanHai/Maps/L_DY_Main")
    ACT = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    plaque = None
    for a in ACT.get_all_level_actors():
        if a.get_actor_label() == "ART_ZhuRiTitleGlyph":
            plaque = a
    req(plaque, "plaque actor")
    R["plaque"] = plaque
    comp = plaque.get_component_by_class(unreal.StaticMeshComponent)
    loc, tgt = (-980.0, -80.0, 250.0), (760.0, -80.0, 250.0)
    rot = unreal.MathLibrary.find_look_at_rotation(unreal.Vector(*loc), unreal.Vector(*tgt))
    cam = ACT.spawn_actor_from_class(unreal.CameraActor, unreal.Vector(*loc), rot, True)
    cam.set_actor_label("TEMP_TitleGainCamera")
    cc = cam.get_component_by_class(unreal.CameraComponent)
    cc.set_editor_property("field_of_view", 62.0)
    cc.set_editor_property("aspect_ratio", 1.6)
    S = {"stage": "setup", "i": 0, "mark": 0.0, "items": [(1, "Title3-Act1"), (2, "Title3-Act2"),
                                                           (3, "Title3-Act3"), (4, "Title3-Act4")]}

    def tick(dt):
        try:
            now = time.monotonic()
            if S["stage"] == "setup":
                if S["i"] >= len(S["items"]):
                    R["ok"] = True
                    return finish()
                act, tag = S["items"][S["i"]]
                comp.set_material(0, EAL.load_asset(MAT + "/MI_DY_TitleGlyph_Act%d" % act))
                S["stage"] = "settle"; S["mark"] = now
                return
            if S["stage"] == "settle" and now - S["mark"] > 3.0:
                act, tag = S["items"][S["i"]]
                S["file"] = AUDIT + "/" + tag + ".png"
                unreal.AutomationLibrary.take_high_res_screenshot(1600, 1000, S["file"], camera=cam)
                S["stage"] = "poll"; S["mark"] = now
                return
            if S["stage"] == "poll":
                if os.path.isfile(S["file"]) and os.path.getsize(S["file"]) > 20000:
                    act, tag = S["items"][S["i"]]
                    R["shots"].append(dict(act=act, file=S["file"],
                        material=str(comp.get_materials()[0].get_path_name())))
                    S["i"] += 1; S["stage"] = "setup"
                    return
                if now - S["mark"] > 20:
                    raise RuntimeError("timeout " + S["file"])
        except Exception:
            R["error"] = traceback.format_exc()
            return finish()

    unreal.register_slate_post_tick_callback(tick)
except Exception:
    R["error"] = traceback.format_exc()
    finish()
