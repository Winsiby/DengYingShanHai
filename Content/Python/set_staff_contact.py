import unreal, json, os
out={"actors":[]}
try:
    les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    les.load_level("/Game/DengYingShanHai/Maps/L_DY_Main")
    eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    for a in eas.get_all_level_actors():
        cls = a.get_class().get_name()
        if "Presentation" not in cls:
            continue
        e={"label":a.get_actor_label(),"class":cls}
        for prop in ["b_enable_staff_contact_presentation","bEnableStaffContactPresentation"]:
            try:
                old=a.get_editor_property(prop)
                e["read_"+prop]=bool(old)
            except Exception as ex:
                e["readerr_"+prop]=str(ex)[:120]
            try:
                a.set_editor_property(prop, True)
                e["set_ok_"+prop]=True
            except Exception as ex:
                e["seterr_"+prop]=str(ex)[:120]
        try:
            e["after"]=bool(a.get_editor_property("b_enable_staff_contact_presentation"))
        except Exception as ex:
            e["aftererr"]=str(ex)[:120]
        out["actors"].append(e)
    out["saved"]=les.save_current_level()
    out["ok"]=True
except Exception as e:
    out["ok"]=False; out["error"]=repr(e)
with open(r"D:/灯影山海/Saved/Audit-2026-10-23-Performance/staff-contact-enable.json","w",encoding="utf-8") as f:
    json.dump(out,f,ensure_ascii=False,indent=1)
print("ENABLE_PROBE " + json.dumps(out,ensure_ascii=False)[:1200])
