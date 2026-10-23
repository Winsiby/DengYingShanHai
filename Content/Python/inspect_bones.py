# -*- coding: utf-8 -*-
import json, traceback
import unreal
AUDIT = "D:/灯影山海/Saved/Audit-2026-10-22-FourAct"
S = dict(ok=False, errors=[], rows=[])
AL = unreal.AnimationLibrary
def e(x): return [round(float(x.x),2), round(float(x.y),2), round(float(x.z),2)]
try:
    unreal.EditorLoadingAndSavingUtils.load_map("/Game/DengYingShanHai/Maps/L_DY_Main")
    eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    puppet = next(a for a in eas.get_all_level_actors() if "Puppet_P02" in a.get_actor_label())
    mesh = puppet.get_components_by_class(unreal.SkeletalMeshComponent)[0]
    for i in range(4):
        puppet.apply_chapter_figure(i, True)
        comp = mesh
        names = ["Root", "Head", "WingL_Tip", "WingR_Tip", "Tail", "Hip", "BodyUpper", "Eyelid"]
        row = dict(chapter=i + 1, asset=mesh.get_skeletal_mesh_asset().get_name(), bones={})
        for n in names:
            try:
                xf = AL.get_bone_pose(comp, n, unreal.Name("Default"), False)
                row["bones"][n] = e(xf.translation)
            except Exception:
                pass
        S["rows"].append(row)
    puppet.apply_chapter_figure(0, True)
    S["ok"] = True
except Exception:
    S["errors"].append(traceback.format_exc())
with open(AUDIT + "/bones.json", "w", encoding="utf-8") as f:
    json.dump(S, f, ensure_ascii=False, indent=2, default=str)
print("BONES_DONE", S["ok"], S["errors"][:1])
unreal.SystemLibrary.quit_editor()
