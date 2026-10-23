# -*- coding: utf-8 -*-
import unreal, os, time, json, traceback
ROOT='D:/灯影山海/Saved/Audit-2026-10-22-ArtPolish'
phase=os.environ.get('DY_ART_PHASE','Before')
jobs=[
 ('Gate',(-2700,-210,420),(-1800,-210,760)),
 ('Entry',(-4600,-210,160),(-1800,-210,520)),
 ('Hall',(-1200,-210,280),(950,0,424)),
]
if phase=='Tune': jobs=[('Entry-ColdFillHalf',(-4600,-210,160),(-1800,-210,520)),('Entry-ColdFillQuarter',(-4600,-210,160),(-1800,-210,520))]
if phase=='Before': jobs.append(('Gate-ColdFillOff',(-2700,-210,420),(-1800,-210,760)))
elif phase=='After': jobs.append(('Entry-ColdFillOff',(-4600,-210,160),(-1800,-210,520)))
state={'index':-1,'stage':'setup','mark':time.monotonic(),'shots':[],'ok':False}
try:
    unreal.EditorLoadingAndSavingUtils.load_map('/Game/DengYingShanHai/Maps/L_DY_Main')
    eas=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    camera=eas.spawn_actor_from_class(unreal.CameraActor,unreal.Vector(0,0,0))
    camera.set_actor_label('TEMP_ArtPolish_ReviewCamera')
    cc=camera.get_component_by_class(unreal.CameraComponent)
    cc.set_editor_property('field_of_view',70.0)
    cc.set_editor_property('aspect_ratio',1.6)
    cold=next(a for a in eas.get_all_level_actors() if a.get_actor_label()=='DYExt16_FacadeLamp_R')
    cold_component=cold.get_component_by_class(unreal.PointLightComponent)
    cold_original=cold_component.get_editor_property('intensity')
    def finish():
        cold_component.set_intensity(cold_original)
        state['ok']=len(state['shots'])==len(jobs)
        with open(ROOT+'/'+phase+'-capture.json','w',encoding='utf-8') as f: json.dump(state,f,ensure_ascii=False,indent=2,default=str)
        unreal.SystemLibrary.quit_editor()
    def tick(dt):
        try:
            now=time.monotonic()
            if now-state['mark']>90: raise RuntimeError('Capture stage timed out: '+str(state))
            if state['stage']=='setup':
                state['index']+=1
                if state['index']>=len(jobs):
                    state['stage']='finished'; finish(); return
                name,pos,target=jobs[state['index']]
                cold_component.set_intensity(cold_original*(0.5 if name.endswith('ColdFillHalf') else 0.25 if name.endswith('ColdFillQuarter') else 0.0 if name.endswith('ColdFillOff') else 1.0))
                camera.set_actor_location(unreal.Vector(*pos),False,False)
                camera.set_actor_rotation(unreal.MathLibrary.find_look_at_rotation(unreal.Vector(*pos),unreal.Vector(*target)),False)
                unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).set_level_viewport_camera_info(camera.get_actor_location(),camera.get_actor_rotation(),'')
                state['stage']='settle'; state['mark']=now
            elif state['stage']=='settle' and now-state['mark']>=10:
                name=jobs[state['index']][0]
                path=ROOT+'/'+phase+'-'+name+'.png'
                state['target']=path
                unreal.AutomationLibrary.take_high_res_screenshot(1920,1200,path,camera=camera,comparison_notes='Technical fixed-camera editor comparison; not human playtest')
                state['stage']='save'; state['mark']=now
            elif state['stage']=='save' and os.path.isfile(state['target']) and os.path.getsize(state['target'])>10000 and now-state['mark']>3:
                state['shots'].append({'path':state['target'],'camera':jobs[state['index']][1],'target':jobs[state['index']][2],'fov':70})
                state['stage']='setup'; state['mark']=now
        except Exception:
            state['error']=traceback.format_exc()
            state['stage']='finished'; finish()
    unreal.register_slate_post_tick_callback(tick)
except Exception:
    state['error']=traceback.format_exc()
    with open(ROOT+'/'+phase+'-capture.json','w',encoding='utf-8') as f: json.dump(state,f,ensure_ascii=False,indent=2,default=str)
    unreal.SystemLibrary.quit_editor()
