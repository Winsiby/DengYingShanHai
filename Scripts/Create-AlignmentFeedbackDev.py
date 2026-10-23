"""One independent Dev map. Only saved changes: light speed and passive UI opt-in."""
import os,json,hashlib,traceback,unreal
SOURCE='/Game/DengYingShanHai/Dev/Readability/Maps/LV_ReadabilityLab'
MAP='/Game/DengYingShanHai/Dev/AlignmentFeedback/Maps/LV_AlignmentFeedbackLab'
OUT=os.environ['DY_READABILITY_OUT']; PHASE=os.environ['DY_READABILITY_PHASE']
R=dict(success=False,phase=PHASE,saved=[],map=MAP)
def req(v,m):
    if not v: raise RuntimeError(m)
    return v
def protect():
    with open(os.path.join(unreal.Paths.project_saved_dir(),'Audit-2026-10-10-AlignmentFeedback/BEFORE.json'),encoding='utf-8-sig') as f: baseline=json.load(f)
    for row in baseline['Files']:
        if not row['Relative'].startswith(('Content\\','Config\\')): continue
        p=os.path.join(unreal.Paths.project_dir(),row['Relative'])
        with open(p,'rb') as f: actual=hashlib.sha256(f.read()).hexdigest().upper()
        req(actual==row['SHA256'],'Protected original changed '+p)
def load(m):
    req(unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).load_level(m),'Load exact map')
    world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    req(world.get_path_name().split('.')[0]==m,'Exact world identity')
    actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
    bylabel={a.get_actor_label():a for a in actors}
    light=req(bylabel.get('M2_LightRig_P02'),'Saved light'); puppet=req(bylabel.get('M2_Puppet_P02_Controlled'),'Saved puppet'); stage=req(bylabel.get('Readability_StagePresentation'),'Saved presentation')
    return world,actors,light.get_editor_property('light_control'),puppet.get_editor_property('puppet_control'),stage
def geometry(actors):
    def xyz(v): return [v.x,v.y,v.z]
    def rotation(v): return [v.pitch,v.yaw,v.roll]
    return {a.get_actor_label():dict(cls=a.get_class().get_path_name(),position=xyz(a.get_actor_location()),rotation=rotation(a.get_actor_rotation()),scale=xyz(a.get_actor_scale3d())) for a in actors}
try:
    protect()
    w,actors,light,puppet,stage=load(SOURCE)
    speed=light.get_editor_property('normalized_units_per_second')
    puppet_speed=puppet.get_editor_property('normalized_units_per_second')
    source_geometry=geometry(actors)
    req(speed>0,'Actual source speed positive')
    req(not stage.get_editor_property('enable_player_alignment_feedback'),'Original map remains default-off')
    R.update(source_light_speed=speed,new_light_speed=speed*.75,puppet_speed=puppet_speed,actor_count=len(actors))
    if PHASE=='create':
        req(not unreal.EditorAssetLibrary.does_asset_exist(MAP),'Preserve existing destination')
        req(unreal.EditorAssetLibrary.duplicate_asset(SOURCE,MAP),'Duplicate only new map')
    else: req(PHASE in ('verify','inspect'),'Explicit phase')
    w,actors,light,puppet,stage=load(MAP)
    R['geometry_source']=source_geometry
    R['geometry_new']=geometry(actors)
    if PHASE=='inspect':
        protect();R['success']=True
        with open(OUT,'w',encoding='utf-8') as f:json.dump(R,f,ensure_ascii=False,indent=2)
        raise SystemExit
    req(geometry(actors)==source_geometry,'All actor transforms/classes preserved')
    if PHASE=='create':
        light.set_editor_property('normalized_units_per_second',speed*.75)
        stage.set_editor_property('enable_player_alignment_feedback',True)
        req(unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level(),'Save only new map')
        R['saved'].append(MAP)
    req(abs(light.get_editor_property('normalized_units_per_second')-speed*.75)<1.e-8,'Actual 75 percent saved speed')
    req(puppet.get_editor_property('normalized_units_per_second')==puppet_speed,'Puppet speed unchanged')
    req(stage.get_editor_property('enable_player_alignment_feedback'),'Only new instance opts in')
    req(not unreal.get_default_object(stage.get_class()).get_editor_property('enable_player_alignment_feedback'),'Shared Stage CDO default-off')
    req(stage.get_puzzle_director() and stage.get_puzzle_director().get_world()==w,'Copied Director is in new world, not source world')
    req(stage.get_stage_environment() and stage.get_stage_environment().get_world()==w,'Copied environment is in new world')
    req(stage.get_forest_presentation_actor() and stage.get_forest_presentation_actor().get_world()==w,'Copied forest is in new world')
    for name in ('GuideP01','GuideP02','GuideP03'):
        guide=stage.get_editor_property(name)
        req(guide and guide.get_world()==w,'Copied explicit guide is in new world')
    R['protected_old_packages']=True
    protect();R['success']=True
except Exception:R['error']=traceback.format_exc();unreal.log_error(R['error'])
finally:
    with open(OUT,'w',encoding='utf-8') as f:json.dump(R,f,ensure_ascii=False,indent=2)
    unreal.log(json.dumps(R,ensure_ascii=False))
