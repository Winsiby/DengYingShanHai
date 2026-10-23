# -*- coding: utf-8 -*-
import json, traceback, unreal
OUT = "D:/灯影山海/Saved/Audit-2026-10-22-FourAct/text-actors.json"
out = {"actors": [], "error": None}
try:
    unreal.EditorLoadingAndSavingUtils.load_map("/Game/DengYingShanHai/Maps/L_DY_Main")
    ACT = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    for a in ACT.get_all_level_actors():
        cls = a.get_class().get_name()
        if "Text" in cls or "TextRender" in cls:
            loc = a.get_actor_location()
            row = dict(label=a.get_actor_label(), cls=cls,
                       loc=[round(loc.x,1), round(loc.y,1), round(loc.z,1)])
            try:
                c = a.get_component_by_class(unreal.TextRenderComponent)
                if c:
                    row["text"] = str(c.get_editor_property("text"))
                    row["size"] = float(c.get_editor_property("world_size"))
                    row["font"] = str(c.get_editor_property("font").get_path_name()) if c.get_editor_property("font") else None
                    row["color"] = str(c.get_editor_property("text_render_color"))
                    row["h_align"] = str(c.get_editor_property("horizontal_alignment"))
            except Exception as e:
                row["err"] = str(e)
            out["actors"].append(row)
except Exception:
    out["error"] = traceback.format_exc()
finally:
    open(OUT, "w", encoding="utf-8").write(json.dumps(out, ensure_ascii=False, indent=2))
    print("TEXTACTORS", len(out["actors"]))
    unreal.SystemLibrary.quit_editor()
