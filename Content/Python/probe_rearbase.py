import json, unreal
R=[]
try:
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).load_level("/Game/DengYingShanHai/Maps/L_DY_Main")
    ACT = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    for a in ACT.get_all_level_actors():
        lab=a.get_actor_label()
        if "RearBase" in lab or "Plinth" in lab:
            org, ext = a.get_actor_bounds(False)
            sc = a.get_actor_scale3d()
            R.append({"label":lab,"class":a.get_class().get_name(),
                      "loc":[round(float(org.x),1),round(float(org.y),1),round(float(org.z),1)],
                      "ext":[round(float(ext.x),1),round(float(ext.y),1),round(float(ext.z),1)],
                      "scale":[round(float(sc.x),2),round(float(sc.y),2),round(float(sc.z),2)]})
    print("REARBASE " + json.dumps(R, ensure_ascii=False))
except Exception as e:
    print("REARBASE_ERR " + str(e))
finally:
    unreal.SystemLibrary.quit_editor()
