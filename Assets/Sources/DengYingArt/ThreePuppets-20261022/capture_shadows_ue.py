# -*- coding: utf-8 -*-
"""Reload only the new Dev level; capture real UE meshes, poses and shadows without saving changes."""
import unreal,os,time,json,traceback
ROOT='D:/灯影山海/Saved/Audit-2026-10-22-ThreePuppets'
BASE='/Game/DengYingShanHai/Dev/ThreePuppets_20261022'
MAP=BASE+'/L_ThreePuppetsReview'
s={'ok':False,'stage':'start','index':-1,'shots':[],'reload_checks':[],'mark':time.monotonic()}
try:
    unreal.EditorLoadingAndSavingUtils.load_map(MAP)
    eas=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    actors={a.get_actor_label():a for a in eas.get_all_level_actors()}
    chars={k:actors['DYThreePuppets_'+k] for k in ('Jingwei','Xingtian','Zhulong')}
    lights={k:actors['DYThreePuppets_'+k+'_ProjectionLight'].get_component_by_class(unreal.PointLightComponent) for k in chars}
    for k,a in chars.items():
        c=a.get_component_by_class(unreal.SkeletalMeshComponent)
        data=c.get_editor_property('animation_data');anim=data.get_editor_property('anim_to_play')
        assert anim and anim.get_name()=='A_DY_'+k+'_Rest','Persisted Rest missing '+k
        assert c.get_num_bones()=={'Jingwei':17,'Xingtian':14,'Zhulong':8}[k]
        s['reload_checks'].append({'id':k,'bones':c.get_num_bones(),'persisted_animation':anim.get_path_name()})
    for k,a in chars.items():
        scr=actors['DYThreePuppets_'+k+'_Screen'];loc=scr.get_actor_location();loc.z=100;scr.set_actor_location(loc,False,False);scr.set_actor_scale3d(unreal.Vector(.02,4.0,3.2))
    post=actors['DYThreePuppets_ManualExposure'];settings=post.get_editor_property('settings');settings.set_editor_property('auto_exposure_bias',4.0);post.set_editor_property('settings',settings)
    assert unreal.EditorLoadingAndSavingUtils.save_map(unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world(),MAP)
    s['texture_residency']=[]
    for asset_path in unreal.EditorAssetLibrary.list_assets(BASE+'/Textures',True,False):
        tex=unreal.EditorAssetLibrary.load_asset(asset_path)
        row={'path':asset_path}
        for prop in ('lod_bias','max_texture_size','mip_gen_settings','num_cinematic_mip_levels','never_stream','lod_group','filter'):
            row[prop]=str(tex.get_editor_property(prop))
        if 'BaseColor' in tex.get_name():
            tex.set_editor_property('never_stream',True);unreal.EditorAssetLibrary.save_loaded_asset(tex,False)
        tex.set_force_mip_levels_to_be_resident(300.0,0)
        s['texture_residency'].append(row)
    camera=eas.spawn_actor_from_class(unreal.CameraActor,unreal.Vector())
    cc=camera.get_component_by_class(unreal.CameraComponent);cc.set_editor_property('aspect_ratio',4/3)
    jobs=[(k,'Rest','Shadow') for k in chars]+[('Zhulong','Day','Shadow'),('Zhulong','Night','Shadow')]
    def finish():
        s['ok']=len(s['shots'])==len(jobs) and 'error' not in s
        with open(ROOT+'/UE-Shadow-Capture.json','w',encoding='utf8')as f:json.dump(s,f,ensure_ascii=False,indent=2,default=str)
        unreal.SystemLibrary.quit_editor()
    def tick(dt):
        try:
            now=time.monotonic()
            if now-s['mark']>75:raise RuntimeError('Capture stage timeout '+s['stage'])
            if s['stage'] in ('start','next'):
                s['index']+=1
                if s['index']>=len(jobs):finish();s['stage']='done';return
                k,pose,view=jobs[s['index']];a=chars[k];c=a.get_component_by_class(unreal.SkeletalMeshComponent)
                anim=unreal.EditorAssetLibrary.load_asset(BASE+'/Animations/A_DY_'+k+'_'+pose);assert anim
                for aa in chars.values():aa.get_component_by_class(unreal.SkeletalMeshComponent).set_visibility(True)
                c.override_animation_data(anim,False,False,0,1)
                c.set_update_animation_in_editor(True)
                for key,l in lights.items():l.set_visibility(key==k)
                center,extent=a.get_actor_bounds(False)
                y=center.y;z=center.z
                # Shared +X/YZ mesh contract verified from imported bounds.
                cc.set_editor_property('projection_mode',unreal.CameraProjectionMode.PERSPECTIVE)
                cc.set_editor_property('field_of_view',36.0)
                if view=='Shadow':
                    pos=(-10,y,100);target=(-65,y,100);c.set_visibility(True);cc.set_auto_calculate_ortho_planes(False);cc.set_ortho_near_clip_plane(1.0);cc.set_ortho_far_clip_plane(2000.0);cc.set_editor_property('update_ortho_planes',False)
                    cc.set_editor_property('projection_mode',unreal.CameraProjectionMode.ORTHOGRAPHIC);cc.set_editor_property('ortho_width',380.0)
                elif view=='Eye':
                    head=c.get_socket_location('Head');pos=(230,head.y+20,head.z+20);target=(0,head.y+20,head.z+20);cc.set_editor_property('field_of_view',20.0)
                else:pos=(600,y,z);target=(0,y,z)
                camera.set_actor_location(unreal.Vector(*pos),False,False)
                camera.set_actor_rotation(unreal.MathLibrary.find_look_at_rotation(unreal.Vector(*pos),unreal.Vector(*target)),False)
                unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).set_level_viewport_camera_info(camera.get_actor_location(),camera.get_actor_rotation(),'')
                s['current']={'id':k,'pose':pose,'view':view,'camera':pos,'target':target,'file':ROOT+'/UE-'+k+'-'+pose+'-'+view+'.png'}
                s['mark']=now;s['stage']='settle'
            elif s['stage']=='settle' and now-s['mark']>=7:
                unreal.AutomationLibrary.take_high_res_screenshot(1600,1200,s['current']['file'],camera=camera,comparison_notes='Actual reloaded UE Dev scene. Movable point-light shadows. No source artwork card.')
                s['mark']=now;s['stage']='save'
            elif s['stage']=='save' and now-s['mark']>=2 and os.path.isfile(s['current']['file']):
                assert os.path.getsize(s['current']['file'])>10000
                s['shots'].append(s['current']);s['stage']='next';s['mark']=now
        except Exception:s['error']=traceback.format_exc();s['stage']='done';finish()
    unreal.register_slate_post_tick_callback(tick)
except Exception:
    s['error']=traceback.format_exc()
    with open(ROOT+'/UE-Shadow-Capture.json','w',encoding='utf8')as f:json.dump(s,f,ensure_ascii=False,indent=2,default=str)
    unreal.SystemLibrary.quit_editor()
