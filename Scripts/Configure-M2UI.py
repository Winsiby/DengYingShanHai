"""Whitelisted M2-only UMG prototype setup. Never regenerates gameplay actors.

Font import uses the engine's FontFileImportFactory and its documented
BatchCreateFontAsset=YES; no guessed composite-font Python structs or graphs.
Native UMG prototype supplies layout; Widget Blueprint defaults supply style.
"""
import unreal

UI_DIR = "/Game/DengYingShanHai/Dev/M2/UI"
MAP = "/Game/DengYingShanHai/Dev/M2/Maps/LV_M2PuzzleLab"
SOURCE = "C:/UEProjects/DengYingShanHai/Saved/Audit-2026-10-03-M2UI/FontSource/SourceHanSansSC-Regular.otf"

def require(value, message):
    if not value:
        raise RuntimeError(message)
    return value

def save(asset):
    require(asset.get_path_name().startswith(UI_DIR + "/"), "Refuse asset save outside UI whitelist")
    require(unreal.EditorAssetLibrary.save_loaded_asset(asset, only_if_is_dirty=True), "Save failed: " + asset.get_path_name())

def blueprint(name, parent, widget=False):
    path = UI_DIR + "/" + name
    existing = unreal.load_asset(path)
    if existing:
        require(isinstance(existing, unreal.WidgetBlueprint if widget else unreal.Blueprint), "Unexpected existing asset type: " + path)
        return existing
    factory = unreal.WidgetBlueprintFactory() if widget else unreal.BlueprintFactory()
    factory.set_editor_property("parent_class", parent)
    result = unreal.AssetToolsHelpers.get_asset_tools().create_asset(name, UI_DIR, unreal.WidgetBlueprint if widget else unreal.Blueprint, factory)
    return require(result, "Create failed: " + path)

def defaults(bp):
    unreal.BlueprintEditorLibrary.compile_blueprint(bp)
    return unreal.get_default_object(require(bp.generated_class(), "Blueprint class missing"))

def assign(obj, key, value):
    if obj.get_editor_property(key) != value:
        obj.set_editor_property(key, value)

def main():
    # Resolve all required APIs/classes and exact map before any writes.
    require(getattr(unreal, "FontFileImportFactory", None), "FontFileImportFactory unavailable")
    require(getattr(unreal, "BatchCreateFontAsset", None), "BatchCreateFontAsset unavailable")
    require(getattr(unreal, "DYInteractionHUDWidget", None), "Native UMG class unavailable")
    levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    require(levels.load_level(MAP), "M2 map load failed")
    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    require(world.get_path_name() == MAP + ".LV_M2PuzzleLab", "Refuse unexpected map")
    settings = world.get_world_settings()
    old_mode = settings.get_editor_property("default_game_mode")
    require(old_mode == unreal.DYStageGameMode.static_class() or (old_mode and old_mode.get_path_name() == UI_DIR + "/BP_DYM2UIGameMode.BP_DYM2UIGameMode_C"), "Unexpected current GameMode; refuse overwrite")

    face_path = UI_DIR + "/FF_DYSourceHanSansSC"
    face = unreal.load_asset(face_path)
    if not face:
        factory = unreal.FontFileImportFactory()
        factory.set_editor_property("batch_create_font_asset", unreal.BatchCreateFontAsset.YES)
        task = unreal.AssetImportTask()
        task.set_editor_property("filename", SOURCE)
        task.set_editor_property("destination_path", UI_DIR)
        task.set_editor_property("destination_name", "FF_DYSourceHanSansSC")
        task.set_editor_property("automated", True)
        task.set_editor_property("save", True)
        task.set_editor_property("factory", factory)
        unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
        unreal.log("DY_UI_IMPORTED " + str(task.get_editor_property("imported_object_paths")))
        face = unreal.load_asset(face_path)
    require(isinstance(face, unreal.FontFace), "Imported FontFace missing")
    # Inline embeds original font data in cooked asset; no OS font dependencies.
    assign(face, "loading_policy", unreal.FontLoadingPolicy.INLINE)
    save(face)
    fonts = [unreal.load_asset(path) for path in unreal.EditorAssetLibrary.list_assets(UI_DIR, recursive=False, include_folder=False)]
    fonts = [asset for asset in fonts if isinstance(asset, unreal.Font)]
    require(len(fonts) == 1, "Expected one factory-created UFont in prototype folder")
    font = fonts[0]
    require(font.get_editor_property("font_cache_type") == unreal.FontCacheType.RUNTIME, "Font must be runtime cached")
    require(face.get_path_name() in font.get_editor_property("composite_font").export_text(), "Font has no explicit imported face reference")
    save(font)

    widget_bp = blueprint("WBP_DYInteractionHUD", unreal.DYInteractionHUDWidget, widget=True)
    widget_defaults = defaults(widget_bp)
    assign(widget_defaults, "chinese_font", font)
    assign(widget_defaults, "act_title", unreal.Text("逐光成形"))
    assign(widget_defaults, "body_font_size", 22)
    assign(widget_defaults, "tick_frequency", unreal.WidgetTickFrequency.NEVER)
    save(widget_bp)

    hud_bp = blueprint("BP_DYInteractionHUD", unreal.DYInteractionHUD)
    assign(defaults(hud_bp), "widget_class", widget_bp.generated_class())
    save(hud_bp)
    mode_bp = blueprint("BP_DYM2UIGameMode", unreal.DYStageGameMode)
    assign(defaults(mode_bp), "hud_class", hud_bp.generated_class())
    save(mode_bp)
    if old_mode != mode_bp.generated_class():
        settings.set_editor_property("default_game_mode", mode_bp.generated_class())
        require(levels.save_current_level(), "M2 GameMode override save failed")
    unreal.log("DY_M2_UI_CONFIGURED Font=" + font.get_path_name() + " Face=" + face.get_path_name())

if __name__ == "__main__":
    main()
