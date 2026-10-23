# -*- coding: utf-8 -*-
"""Import per-act title glyph textures and build the four plaque material instances."""
import json, os, traceback, unreal

EAL = unreal.EditorAssetLibrary
MEL = unreal.MaterialEditingLibrary
TOOLS = unreal.AssetToolsHelpers.get_asset_tools()
BASE = "/Game/DengYingShanHai/Stage/ArtMainline"
TEX = BASE + "/Textures"
MAT = BASE + "/Materials"
SRC = r"D:\灯影山海\Saved\Audit-2026-10-22-FourAct\TitleTextures"
R = {"ok": False, "textures": [], "instances": [], "checks": [], "error": None}


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
    tex = req(EAL.load_asset(dst), "Imported texture " + name)
    tex.set_editor_properties(dict(srgb=True, never_stream=True,
        compression_settings=unreal.TextureCompressionSettings.TC_DEFAULT,
        lod_group=unreal.TextureGroup.TEXTUREGROUP_WORLD))
    req(EAL.save_loaded_asset(tex, False), "Saved texture " + name)
    R["textures"].append(dict(path=dst, size=[tex.blueprint_get_size_x(), tex.blueprint_get_size_y()]))
    return tex


def master():
    path = MAT + "/M_DY_TitleGlyph_Master"
    if EAL.does_asset_exist(path):
        mat = EAL.load_asset(path)
        MEL.delete_all_material_expressions(mat)
    else:
        mat = req(TOOLS.create_asset("M_DY_TitleGlyph_Master", MAT, unreal.Material,
                                    unreal.MaterialFactoryNew()), "Created master material")
    mat.set_editor_properties(dict(blend_mode=unreal.BlendMode.BLEND_MASKED,
        shading_model=unreal.MaterialShadingModel.MSM_UNLIT,
        two_sided=True, material_domain=unreal.MaterialDomain.MD_SURFACE))
    tex = req(MEL.create_material_expression(mat, unreal.MaterialExpressionTextureSampleParameter2D, -600, 0),
              "TitleGlyph sampler")
    tex.set_editor_properties(dict(parameter_name="TitleGlyph",
        sampler_type=unreal.MaterialSamplerType.SAMPLERTYPE_COLOR))
    gain = req(MEL.create_material_expression(mat, unreal.MaterialExpressionConstant, -600, 260), "Gain")
    gain.set_editor_property("r", 60.0)
    mul = req(MEL.create_material_expression(mat, unreal.MaterialExpressionMultiply, -300, 60), "Multiply")
    req(MEL.connect_material_expressions(tex, "RGB", mul, "A"), "RGB into multiply")
    req(MEL.connect_material_expressions(gain, "", mul, "B"), "Gain into multiply")
    req(MEL.connect_material_property(mul, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR), "Emissive")
    req(MEL.connect_material_property(tex, "A", unreal.MaterialProperty.MP_OPACITY_MASK), "Opacity mask")
    req(not MEL.recompile_material(mat), "Master compiles")
    req(EAL.save_loaded_asset(mat, False), "Saved master")
    return mat


def instance(chapter, texture, parent):
    path = MAT + "/MI_DY_TitleGlyph_Act%d" % chapter
    if EAL.does_asset_exist(path):
        mi = EAL.load_asset(path)
        MEL.set_material_instance_parent(mi, parent)
    else:
        mi = req(TOOLS.create_asset("MI_DY_TitleGlyph_Act%d" % chapter, MAT,
                                    unreal.MaterialInstanceConstant,
                                    unreal.MaterialInstanceConstantFactoryNew()), "Created Act%d instance" % chapter)
        MEL.set_material_instance_parent(mi, parent)
    MEL.set_material_instance_texture_parameter_value(mi, "TitleGlyph", texture)
    readback = MEL.get_material_instance_texture_parameter_value(mi, "TitleGlyph")
    req(readback == texture, "Act%d texture readback" % chapter)
    MEL.update_material_instance(mi)
    req(EAL.save_loaded_asset(mi, False), "Saved Act%d instance" % chapter)
    R["instances"].append(dict(path=path, texture=texture.get_path_name()))
    return mi


try:
    imported = {n: import_tex("T_DY_TitleGlyph_Act%d" % n) for n in (2, 3, 4)}
    parent_material = master()
    original = req(EAL.load_asset(TEX + "/T_DY_ZhuRiTitle"), "Existing act 1 glyph texture")
    instance(1, original, parent_material)
    for n, tex in imported.items():
        instance(n, tex, parent_material)
    R["original_material"] = MAT + "/M_DY_TitleGlyph"
    R["ok"] = True
except Exception:
    R["error"] = traceback.format_exc()
finally:
    open(r"D:\灯影山海\Saved\Audit-2026-10-22-FourAct\title-build.json", "w", encoding="utf-8").write(
        json.dumps(R, ensure_ascii=False, indent=2))
    print("TITLE_BUILD", R["ok"], len(R["checks"]), R["error"][:300] if R["error"] else "")
    unreal.SystemLibrary.quit_editor()
