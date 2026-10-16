"""Copy the accepted single-stage Dev scene; change ONE new Presentation opt-in only."""
import os,json,traceback,hashlib,unreal
SOURCE='/Game/DengYingShanHai/Dev/AlignmentFeedback/Maps/LV_AlignmentFeedbackLab'
MAP='/Game/DengYingShanHai/Dev/EnvironmentStates/Maps/LV_EnvironmentStatesLab'
AUDIT=os.path.join(unreal.Paths.project_saved_dir(),'Audit-2026-10-11-EnvironmentStates')
ROOT=unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir())
OUT=os.environ['DY_READABILITY_OUT'];PHASE=os.environ['DY_READABILITY_PHASE']
R=dict(success=False,phase=PHASE,saved=[],checks=[])
def req(v,m):
    if not v:raise RuntimeError(m)
    R['checks'].append(m)
    return v
def protect():
    with open(os.path.join(AUDIT,'BEFORE.json'),encoding='utf-8-sig') as f:b=json.load(f)
    approved=set(b['Approved'])
    extension=os.path.join(AUDIT,'SCOPE_EXTENSION.json')
    if os.path.isfile(extension):
        with open(extension,encoding='utf-8-sig') as f:approved.update(json.load(f)['AdditionalApproved'])
    for r in b['Files']:
        if r['Relative'] not in approved:
            with open(os.path.join(ROOT,r['Relative']),'rb') as f:actual=hashlib.sha256(f.read()).hexdigest().upper()
            req(actual==r['SHA256'],'Protected '+r['Relative'])
def xyz(v):return [v.x,v.y,v.z]
def contract():
    actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
    stage=req(next((a for a in actors if a.get_actor_label()=='Readability_StagePresentation'),None),'Explicit existing Stage')
    result={}
    for a in actors:
        t=a.get_actor_transform();q=t.rotation
        result[a.get_actor_label()]=dict(location=xyz(t.translation),scale=xyz(t.scale3d),rotation=[q.x,q.y,q.z,q.w],class_path=a.get_class().get_path_name())
    world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    settings=world.get_world_settings();gm=settings.get_editor_property('default_game_mode')
    pawn=unreal.get_default_object(unreal.get_default_object(gm).get_editor_property('default_pawn_class'))
    foot=pawn.get_editor_property('FootstepAudio');arm=pawn.get_camera_boom()
    result['_pawn']=dict(speed=pawn.get_editor_property('character_movement').get_editor_property('max_walk_speed'),arm=arm.get_editor_property('target_arm_length'),socket=xyz(arm.get_editor_property('socket_offset')),target=xyz(arm.get_editor_property('target_offset')),collision=arm.get_editor_property('do_collision_test'),fov=pawn.get_follow_camera().get_editor_property('field_of_view'),stride=foot.get_editor_property('StepDistanceCentimeters'),enabled=foot.get_editor_property('bEnableDevelopmentFootsteps'),left=foot.get_editor_property('LeftSound').get_path_name(),right=foot.get_editor_property('RightSound').get_path_name(),inputs=[pawn.get_editor_property(p).get_path_name() for p in ('MoveActionAsset','LookActionAsset','ResetActionAsset','InteractActionAsset','ManipulateActionAsset','ResetControlledActionAsset')])
    d=stage.get_puzzle_director()
    result['_flow']=dict(gm=gm.get_path_name(),controller=unreal.get_default_object(gm).get_editor_property('player_controller_class').get_path_name(),hz=d.get_evaluation_frequency_hz(),transition=stage.get_editor_property('DevActTransitionSeconds'),auto=d.is_auto_start_on_begin_play(),sequence=d.is_act_sequence_enabled(),entries=str(d.get_editor_property('ActSequence')))
    return world,actors,stage,result
try:
    req(PHASE in ('create','verify'),'Exact phase')
    protect()
    levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    req(levels.load_level(SOURCE),'Load immutable source map')
    old_world,old_actors,old_stage,old_contract=contract()
    req(not old_stage.is_five_state_environment_enabled(),'Source map remains opt-off')
    req(not unreal.get_default_object(unreal.DYStagePresentation).is_five_state_environment_enabled(),'Native CDO remains opt-off')
    if PHASE=='create':
        req(not unreal.EditorAssetLibrary.does_asset_exist(MAP),'Refuse existing destination')
        copied=req(unreal.EditorAssetLibrary.duplicate_asset(SOURCE,MAP),'Copy only independent Dev map')
        req(levels.load_level(MAP),'Load copied map')
        world,actors,stage,new_contract=contract()
        req(new_contract==old_contract,'All existing actor transforms/classes, speed, input, camera, stride and flow identical')
        stage.set_editor_property('bEnableFiveStateDevEnvironment',True)
        req(levels.save_current_level(),'Save only copied map');R['saved'].append(MAP)
    else:req(levels.load_level(MAP),'Cold load saved new map')
    world,actors,stage,new_contract=contract()
    req(new_contract==old_contract,'Exact frozen source scene contract')
    req(stage.is_five_state_environment_enabled(),'Only new map opts into five states')
    env=stage.get_stage_environment();director=stage.get_puzzle_director();forest=stage.get_forest_presentation_actor()
    req(env and director and forest,'Explicit dependencies remain present')
    req(all(a.get_world()==world and a in actors for a in (env,director,forest)),'Dependencies remapped into this new same world')
    audio=req(next((a for a in actors if a.get_actor_label()=='AudioDev_Presentation'),None),'Existing stage audio')
    req(audio.get_editor_property('StagePresentation')==stage,'Audio references copied Stage')
    req(director.get_evaluation_frequency_hz()==15 and new_contract['_pawn']['speed']==360 and new_contract['_pawn']['stride']==150,'Frozen 15 Hz, speed, stride')
    req(not director.is_auto_start_on_begin_play() and director.is_act_sequence_enabled(),'Manual three-act start preserved')
    for name in ('SunAwakenedAccent','ChaseAwakenedAccent'):
        light=env.get_editor_property(name)
        req(not light.get_editor_property('cast_shadows'),'Existing environment accents do not cast new shadows')
    protect()
    R.update(success=True,actor_count=len(actors),new_contract=new_contract,map=MAP,source=SOURCE,formal_art=False,source_map_changed=False)
except Exception:
    R['error']=traceback.format_exc();unreal.log_error(R['error'])
finally:
    with open(OUT,'x',encoding='utf-8') as f:json.dump(R,f,ensure_ascii=False,indent=2)
