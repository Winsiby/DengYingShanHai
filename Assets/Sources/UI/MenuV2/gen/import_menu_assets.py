import unreal, os

src = r"D:\灯影山海\Assets\Sources\UI\MenuV2"
dst = "/Game/DengYingShanHai/UI/Menu"
files = [
    ("main-menu-reference.png", "T_MenuBackground"),
    ("PLQ_Normal.png", "T_PlqNormal"),
    ("PLQ_Hover.png", "T_PlqHover"),
    ("PLQ_Pressed.png", "T_PlqPressed"),
    ("PLQ_Disabled.png", "T_PlqDisabled"),
]
tasks = []
for fn, name in files:
    t = unreal.AssetImportTask()
    t.filename = os.path.join(src, fn)
    t.destination_path = dst
    t.destination_name = name
    t.automated = True
    t.replace_existing = True
    t.save = True
    tasks.append(t)

tools = unreal.AssetToolsHelpers.get_asset_tools()
tools.import_asset_tasks(tasks)

for fn, name in files:
    path = dst + "/" + name
    tex = unreal.EditorAssetLibrary.load_asset(path)
    if tex is None:
        unreal.log_error("MISSING " + path)
        continue
    tex.set_editor_property("mip_gen_settings", unreal.TextureMipGenSettings.TMGS_NO_MIPMAPS)
    tex.set_editor_property("srgb", True)
    tex.set_editor_property("compression_settings", unreal.TextureCompressionSettings.TC_EDITOR_ICON)
    tex.set_editor_property("never_stream", True)
    unreal.EditorAssetLibrary.save_loaded_asset(tex, False)
    unreal.log("OK " + path + " " + str(tex.blueprint_get_size_x()) + "x" + str(tex.blueprint_get_size_y()))
