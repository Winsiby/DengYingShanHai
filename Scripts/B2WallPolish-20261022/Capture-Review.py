# -*- coding: utf-8 -*-
import unreal,os,time,json,traceback
ROOT='D:/灯影山海/Saved/Audit-2026-10-22-B2WallPolish'
phase=os.environ.get('DY_POLISH_PHASE','Candidate')
map_path='/Game/DengYingShanHai/Maps/L_DY_Main' if phase in ('Before','Final') else '/Game/DengYingShanHai/Dev/B2WallPolish_20261022/L_B2Wall_Candidate'
jobs=[('Gate',(-2700,-210,420),(-1800,-210,760)),('Entry',(-4600,-210,160),(-1800,-210,520)),('Hall',(-1200,-210,280),(950,0,424)),('HallNear',(-500,-210,220),(950,0,424)),('Audience',(2000,0,550),(925,0,460)),('ExteriorAngle',(-3700,500,500),(-1800,-210,700))]
if phase=='Before':jobs=jobs[3:]
s={'ok':False,'phase':phase,'map':map_path,'index':-1,'stage':'setup','mark':time.monotonic(),'shots':[]}
try:
 unreal.EditorLoadingAndSavingUtils.load_map(map_path)
 eas=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
 cam=eas.spawn_actor_from_class(unreal.CameraActor,unreal.Vector())
 cam.set_actor_label('TEMP_B2Wall_ReviewCamera')
 cc=cam.get_component_by_class(unreal.CameraComponent);cc.set_editor_property('field_of_view',70.0);cc.set_editor_property('aspect_ratio',1.6)
 def finish():
  with open(ROOT+'/'+phase+'-capture.json','w',encoding='utf8')as f:json.dump(s,f,indent=2,ensure_ascii=False,default=str)
  unreal.SystemLibrary.quit_editor()
 def tick(dt):
  try:
   now=time.monotonic()
   if now-s['mark']>90:raise RuntimeError('capture timeout')
   if s['stage']=='setup':
    s['index']+=1
    if s['index']>=len(jobs):s['ok']=True;s['stage']='done';finish();return
    name,pos,target=jobs[s['index']]
    cam.set_actor_location(unreal.Vector(*pos),False,False)
    cam.set_actor_rotation(unreal.MathLibrary.find_look_at_rotation(unreal.Vector(*pos),unreal.Vector(*target)),False)
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).set_level_viewport_camera_info(cam.get_actor_location(),cam.get_actor_rotation(),'')
    s['stage']='settle';s['mark']=now
   elif s['stage']=='settle' and now-s['mark']>=10:
    name,pos,target=jobs[s['index']];s['target']=ROOT+'/'+phase+'-'+name+'.png'
    unreal.AutomationLibrary.take_high_res_screenshot(1920,1200,s['target'],camera=cam,comparison_notes='Same camera, no scene cutaway or light/exposure override; technical art comparison')
    s['stage']='save';s['mark']=now
   elif s['stage']=='save' and os.path.isfile(s['target']) and os.path.getsize(s['target'])>10000 and now-s['mark']>3:
    name,pos,target=jobs[s['index']];s['shots'].append({'file':s['target'],'camera':pos,'target':target,'fov':70})
    s['stage']='setup';s['mark']=now
  except:s['error']=traceback.format_exc();s['stage']='failed';finish()
 unreal.register_slate_post_tick_callback(tick)
except:s['error']=traceback.format_exc();finish()
