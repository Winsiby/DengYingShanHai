# -*- coding: utf-8 -*-
import unreal, json, traceback
OUT = 'D:/灯影山海/Saved/Audit-2026-10-22-ArtPolish'
report = {'ok': False}
def vec(v): return [round(float(v.x),6), round(float(v.y),6), round(float(v.z),6)]
def prop(o,n):
    try:
        v=o.get_editor_property(n)
        return str(v) if not isinstance(v,(str,int,float,bool,type(None))) else v
    except Exception: return None
try:
    unreal.EditorLoadingAndSavingUtils.load_map('/Game/DengYingShanHai/Maps/L_DY_Main')
    actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
    report['actor_count']=len(actors)
    report['lamps']=[]; report['lights']=[]; report['critical']=[]
    report['api']={'shot':str(unreal.AutomationLibrary.take_high_res_screenshot.__doc__),
                   'import':str(unreal.FbxFactory.__doc__),
                   'save_map':str(unreal.EditorLoadingAndSavingUtils.save_map.__doc__)}
    for a in actors:
        label=a.get_actor_label()
        entry={'label':label,'class':a.get_class().get_name(),'location':vec(a.get_actor_location()),'scale':vec(a.get_actor_scale3d()),
               'rotation':str(a.get_actor_rotation()),'hidden':prop(a,'hidden')}
        if label.startswith(('DYExt30_GateLamp_','DYExt30_EaveLamp_','DYExt30_RoofLamp_')):
            entry['components']=[]
            for c in a.get_components_by_class(unreal.StaticMeshComponent):
                sm=c.get_editor_property('static_mesh')
                center,extent=a.get_actor_bounds(False)
                entry['bounds_center']=vec(center); entry['bounds_extent']=vec(extent)
                entry['components'].append({'name':c.get_name(),'mesh':sm.get_path_name() if sm else None,
                 'materials':[c.get_material(i).get_path_name() if c.get_material(i) else None for i in range(c.get_num_materials())],
                 'collision':str(c.get_collision_enabled()),'cast_shadow':prop(c,'cast_shadow'),'mobility':prop(c,'mobility')})
            report['lamps'].append(entry)
        lightcomponents=a.get_components_by_class(unreal.LightComponent)
        if lightcomponents:
            entry['components']=[]
            for c in lightcomponents:
                entry['components'].append({n:prop(c,n) for n in ('intensity','intensity_units','light_color','temperature','use_temperature','attenuation_radius','source_radius','specular_scale','use_inverse_squared_falloff','cast_shadows','mobility')})
            report['lights'].append(entry)
        if label in ('DEV_BackScreen','PlayerStart','DYLightRig','DY_PuzzleDirector') or a.get_class().get_name() in ('DYLightRigActor','DYPuzzleDirector') or label.startswith('BP_DYKuafuPuppet'):
            report['critical'].append(entry)
        if a.get_class().get_name()=='PostProcessVolume':
            settings=a.get_editor_property('settings')
            report['exposure']={n:prop(settings,n) for n in ('auto_exposure_method','auto_exposure_min_brightness','auto_exposure_max_brightness','auto_exposure_bias','override_auto_exposure_min_brightness','override_auto_exposure_max_brightness')}
    report['paper']={}
    for p in ('/Game/DengYingShanHai/Dev/WorldV2/Materials/MI_DY_LanternPaper','/Game/DengYingShanHai/Dev/FramePostAsset/Materials/MI_DY_FramePost_Wood','/Game/DengYingShanHai/Dev/KuafuAppearance/Materials/MI_DY_AgedBrass'):
        asset=unreal.EditorAssetLibrary.load_asset(p)
        report['paper'][p]={'exists':asset is not None,'parent':prop(asset,'parent') if asset else None}
        if asset and p.endswith('MI_DY_LanternPaper'):
            report['paper'][p]['Glow']=unreal.MaterialEditingLibrary.get_material_instance_scalar_parameter_value(asset,'Glow')
    report['ok']=True
except Exception: report['error']=traceback.format_exc()
with open(OUT+'/before-state.json','w',encoding='utf-8') as f: json.dump(report,f,ensure_ascii=False,indent=2)
unreal.SystemLibrary.quit_editor()
