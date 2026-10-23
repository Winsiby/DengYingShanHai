"""Read-only cold-load checks for the M2-only prototype UI dependency chain."""
import unreal

UI = "/Game/DengYingShanHai/Dev/M2/UI"
MAP = "/Game/DengYingShanHai/Dev/M2/Maps/LV_M2PuzzleLab"

def require(value, message):
    if not value:
        raise RuntimeError(message)
    unreal.log("DY_UI_PASS " + message)
    return value

def main():
    levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    require(levels.load_level(MAP), "M2 exact map loaded")
    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    mode = world.get_world_settings().get_editor_property("default_game_mode")
    require(mode and mode.get_path_name() == UI + "/BP_DYM2UIGameMode.BP_DYM2UIGameMode_C", "M2 map explicitly selects UI prototype mode")
    mode_defaults = unreal.get_default_object(mode)
    require(mode_defaults.get_editor_property("default_pawn_class") == unreal.DYStageOperatorPawn.static_class(), "Pawn class unchanged")
    require(mode_defaults.get_editor_property("player_controller_class") == unreal.DYStagePlayerController.static_class(), "Controller class unchanged")
    hud = mode_defaults.get_editor_property("hud_class")
    require(hud.get_path_name() == UI + "/BP_DYInteractionHUD.BP_DYInteractionHUD_C", "Explicit prototype HUD class")
    widget_class = unreal.get_default_object(hud).get_editor_property("widget_class")
    require(widget_class and widget_class.get_path_name() == UI + "/WBP_DYInteractionHUD.WBP_DYInteractionHUD_C", "Explicit UMG view class")
    widget = unreal.get_default_object(widget_class)
    font = widget.get_editor_property("chinese_font")
    require(isinstance(font, unreal.Font), "Widget has serialized project UFont")
    require(font.get_path_name().startswith(UI + "/"), "Font isolated in prototype directory")
    require(font.get_editor_property("font_cache_type") == unreal.FontCacheType.RUNTIME, "Runtime font cache")
    face = unreal.load_asset(UI + "/FF_DYSourceHanSansSC")
    require(isinstance(face, unreal.FontFace), "Imported project FontFace exists")
    require(face.get_editor_property("loading_policy") == unreal.FontLoadingPolicy.INLINE, "Font payload inline, not system dependent")
    require(face.get_path_name() in font.get_editor_property("composite_font").export_text(), "UFont hard references imported face")
    require(str(widget.get_editor_property("act_title")) == "逐光成形", "P02 Chinese act title")
    require(widget.get_editor_property("body_font_size") == 22, "Prototype body size saved")
    require(widget.get_editor_property("tick_frequency") == unreal.WidgetTickFrequency.NEVER, "View does not Tick")
    require(not widget.get_editor_property("is_focusable"), "View cannot take keyboard focus")
    actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
    require(len(actors) == 25, "Saved actor count remains 25")
    fixtures = {"DEV_CameraWall": unreal.Vector(-100, -650, 170), "DEV_InnerCornerA": unreal.Vector(420, -750, 150), "DEV_InnerCornerB": unreal.Vector(690, -660, 150)}
    for label, location in fixtures.items():
        matches = [actor for actor in actors if actor.get_actor_label() == label]
        require(len(matches) == 1 and matches[0].get_actor_location() == location, "Accepted fixture unchanged: " + label)
    unreal.log("DY_M2_UI_VERIFIED")

if __name__ == "__main__":
    main()
