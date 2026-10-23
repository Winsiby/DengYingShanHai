# -*- coding: utf-8 -*-
import json, traceback, unreal
AUDIT = "D:/灯影山海/Saved/Audit-2026-10-22-FourAct"
R = {"ok": False, "calls": [], "error": None}
try:
    unreal.EditorLoadingAndSavingUtils.load_map("/Game/DengYingShanHai/Maps/L_DY_Main")
    ACT = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    director = None; plaque = None
    for a in ACT.get_all_level_actors():
        if a.get_class().get_name().startswith("DYPuzzleDirector"):
            director = a
        if a.get_actor_label() == "ART_ZhuRiTitleGlyph":
            plaque = a
    comp = plaque.get_component_by_class(unreal.StaticMeshComponent)
    R["before"] = str(comp.get_materials()[0].get_path_name())
    for chapter in (0, 1, 2, 3, 1, 0):
        director.apply_chapter_title_plaque(chapter)
        got = str(comp.get_materials()[0].get_path_name())
        R["calls"].append(dict(chapter=chapter, material=got,
                               ok=("MI_DY_TitleGlyph_Act%d." % (chapter + 1)) in got))
    R["ok"] = all(c["ok"] for c in R["calls"])
except Exception:
    R["error"] = traceback.format_exc()
finally:
    open(AUDIT + "/title-swap-calls.json", "w", encoding="utf-8").write(json.dumps(R, ensure_ascii=False, indent=2))
    print("CALLS", R["ok"], len(R["calls"]))
    unreal.SystemLibrary.quit_editor()
