# -*- coding: utf-8 -*-
import unreal,json,traceback
ROOT='D:/灯影山海/Saved/Audit-2026-10-22-ArtPolish'
MAP='/Game/DengYingShanHai/Maps/L_DY_Main'
report={'ok':False,'label':'DYExt16_FacadeLamp_R','reason':'Same-camera 2600/1300/650/0 cd A-B; reduce competing cold facade hotspot while retaining cool fill'}
try:
    unreal.EditorLoadingAndSavingUtils.load_map(MAP)
    eas=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    actors=eas.get_all_level_actors()
    light=next(a for a in actors if a.get_actor_label()==report['label'])
    c=light.get_component_by_class(unreal.PointLightComponent)
    assert c.get_editor_property('intensity')==2600.0
    assert c.get_editor_property('intensity_units')==unreal.LightUnits.CANDELAS
    report['before_cd']=2600.0; report['after_cd']=650.0
    report['location']=str(light.get_actor_location())
    report['preserved']=['transform','1100 cm attenuation radius','inverse squared falloff','light color RGB132/196/255','source radius','all other 56 lights','global manual exposure bias3.5','gameplay']
    assert c.get_editor_property('attenuation_radius')==1100.0
    c.set_intensity(650.0)
    world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    assert unreal.EditorLoadingAndSavingUtils.save_map(world,MAP)
    assert unreal.EditorLevelLibrary.save_current_level()
    unreal.EditorLoadingAndSavingUtils.load_map(MAP)
    light=next(a for a in eas.get_all_level_actors() if a.get_actor_label()==report['label'])
    assert light.get_component_by_class(unreal.PointLightComponent).get_editor_property('intensity')==650.0
    report['ok']=True
except Exception:report['error']=traceback.format_exc()
with open(ROOT+'/FacadeFill-Apply.json','w',encoding='utf-8') as f:json.dump(report,f,ensure_ascii=False,indent=2)
unreal.SystemLibrary.quit_editor()
