# -*- coding: utf-8 -*-
import unreal,time,os,json,traceback
ROOT='D:/灯影山海/Saved/Audit-2026-10-22-ThreePuppets';BASE='/Game/DengYingShanHai/Dev/ThreePuppets_20261022'
s={'ok':False,'i':-1,'stage':'setup','mark':time.monotonic(),'shots':[],'note':'Actual mesh and its separate offset shadow in the same perspective view; scene/light adjustments temporary, not saved.'}
try:
 unreal.EditorLoadingAndSavingUtils.load_map(BASE+'/L_ThreePuppetsReview');eas=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);aa={a.get_actor_label():a for a in eas.get_all_level_actors()}
 chars={k:aa['DYThreePuppets_'+k] for k in ('Jingwei','Xingtian','Zhulong')};cam=eas.spawn_actor_from_class(unreal.CameraActor,unreal.Vector());cc=cam.get_component_by_class(unreal.CameraComponent);cc.set_editor_properties(dict(field_of_view=48.0,aspect_ratio=4/3))
 post=aa['DYThreePuppets_ManualExposure'];settings=post.get_editor_property('settings');settings.set_editor_property('auto_exposure_bias',5.0);post.set_editor_property('settings',settings)
 jobs=[('Jingwei','Rest'),('Jingwei','Flight'),('Jingwei','Reach'),('Xingtian','Rest'),('Xingtian','Guard'),('Xingtian','Reach'),('Zhulong','Rest'),('Zhulong','Day'),('Zhulong','Night'),('Zhulong','Reach'),('Zhulong','DayEye'),('Zhulong','NightEye')]
 def finish():
  s['ok']=len(s['shots'])==len(jobs) and 'error' not in s
  with open(ROOT+'/UE-Projection.json','w',encoding='utf8')as f:json.dump({key:value for key,value in s.items() if key!='active_component'},f,ensure_ascii=False,indent=2)
  unreal.SystemLibrary.quit_editor()
 def tick(dt):
  try:
   now=time.monotonic()
   if now-s['mark']>75:raise RuntimeError('timeout '+s['stage'])
   if s['stage']=='setup':
    s['i']+=1
    if s['i']>=len(jobs):s['stage']='done';finish();return
    k,pose=jobs[s['i']];a=chars[k];center,ext=a.get_actor_bounds(False);y=center.y
    for name,actor in chars.items():
     comp=actor.get_component_by_class(unreal.SkeletalMeshComponent);comp.set_cast_hidden_shadow(False);comp.set_visibility(name==k);comp.set_cast_shadow(name==k)
     screen=aa['DYThreePuppets_'+name+'_Screen'];screen.get_component_by_class(unreal.StaticMeshComponent).set_visibility(name==k)
     light=aa['DYThreePuppets_'+name+'_ProjectionLight'];light.get_component_by_class(unreal.PointLightComponent).set_visibility(name==k)
    c=a.get_component_by_class(unreal.SkeletalMeshComponent);is_eye=pose.endswith('Eye');actual_pose=pose[:-3] if is_eye else pose;anim=unreal.EditorAssetLibrary.load_asset(BASE+'/Animations/A_DY_'+k+'_'+actual_pose);c.set_animation(anim);c.set_position(.5,False);c.override_animation_data(anim,False,False,.5,1);c.set_update_animation_in_editor(True);assert c.get_anim_instance().get_animation_asset()==anim
    screen=aa['DYThreePuppets_'+k+'_Screen'];screen.set_actor_location(unreal.Vector(-200,y-150,80),False,False);screen.set_actor_scale3d(unreal.Vector(.02,9.0,4.2))
    la=aa['DYThreePuppets_'+k+'_ProjectionLight'];la.set_actor_location(unreal.Vector(500,y+600,220),False,False);l=la.get_component_by_class(unreal.PointLightComponent);l.set_intensity(6000);l.set_attenuation_radius(1400)
    pos=unreal.Vector(800,y-120,110);target=unreal.Vector(-80,y-120,110);cc.set_editor_property('field_of_view',48.0)
    if is_eye:
     head=c.get_socket_location('Head');pos=unreal.Vector(220,head.y+20,head.z+20);target=unreal.Vector(0,head.y+20,head.z+20);cc.set_editor_property('field_of_view',20.0)
    cam.set_actor_location(pos,False,False);cam.set_actor_rotation(unreal.MathLibrary.find_look_at_rotation(pos,target),False);unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).set_level_viewport_camera_info(cam.get_actor_location(),cam.get_actor_rotation(),'')
    s['active_component']=c;s['current']={'id':k,'pose':pose,'actual_animation':anim.get_path_name(),'evaluated_pose':[{'bone':str(c.get_bone_name(i)),'world':str(c.get_socket_transform(c.get_bone_name(i)))} for i in range(c.get_num_bones())],'file':ROOT+'/UE-Projection-'+k+'-'+pose+'.png','light_cm':[500,y+600,220],'light_cd':6000,'camera_cm':[800,y-120,110]};s['stage']='settle';s['mark']=now
   elif s['stage']=='settle' and now-s['mark']>6:
    unreal.AutomationLibrary.take_high_res_screenshot(1800,1200,s['current']['file'],camera=cam);s['stage']='save';s['mark']=now
   elif s['stage']=='save' and now-s['mark']>2 and os.path.isfile(s['current']['file']):
    s['shots'].append(s['current']);s['stage']='setup';s['mark']=now
  except:s['error']=traceback.format_exc();s['stage']='done';finish()
 unreal.register_slate_post_tick_callback(tick)
except:
 s['error']=traceback.format_exc()
 with open(ROOT+'/UE-Projection.json','w',encoding='utf8')as f:json.dump({key:value for key,value in s.items() if key!='active_component'},f,ensure_ascii=False,indent=2)
 unreal.SystemLibrary.quit_editor()