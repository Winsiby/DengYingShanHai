"""One independent Dev map with one passive beam; old 34-actor contract frozen."""
import hashlib
import json
import os
import traceback
import unreal

ROOT=os.path.realpath(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir()))
AUDIT=os.path.join(ROOT,'Saved','Audit-2026-10-12-FrameBeamPlacementDev')
SOURCE='/Game/DengYingShanHai/Dev/FramePostPlacement/Maps/LV_FramePostPlacementLab'
MAP='/Game/DengYingShanHai/Dev/FrameBeamPlacement/Maps/LV_FrameBeamPlacementLab'
LABEL='DEV_FrameBeam_RightJoint'
SM='/Game/DengYingShanHai/Dev/FrameBeamAsset/Meshes/SM_DY_FrameBeam_Source'
WOOD='/Game/DengYingShanHai/Dev/FramePostAsset/Materials/MI_DY_FramePost_Wood'
OUT=os.environ['DY_BEAM_DEV_OUT'];PHASE=os.environ['DY_BEAM_DEV_PHASE']
R=dict(success=False,phase=PHASE,saved=[],checks=[],map=MAP,source=SOURCE,
       visual_acceptance=False,formal_scale=False,physical_blocking=False,joinery_or_load_accepted=False)
def req(value,message):
    if not value: raise RuntimeError(message)
    R['checks'].append(message)
    return value
def read(path):
    with open(path,encoding='utf-8-sig') as f: return json.load(f)
def sha(path):
    path=os.path.abspath(path)
    req(os.path.normcase(path)!=os.path.normcase(os.path.join(ROOT,'Docs','LICENSES.md')),'Restricted register excluded before read')
    h=hashlib.sha256()
    with open(path,'rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''): h.update(chunk)
    return h.hexdigest().upper()
def protect():
    before=read(os.path.join(AUDIT,'BEFORE.json'))
    published=read(os.path.join(AUDIT,'CPP-PUBLISHED.json'))
    req(published['Status']=='PASS-TWO-CPP-PUBLICATION-ONLY' and len(published['Files'])==2,'Actual two-CPP publication')
    overrides={row['Relative']:row['PublishedSHA256'] for row in published['Files']}
    for row in before['Files']:
        req(sha(os.path.join(ROOT,row['Relative']))==overrides.get(row['Relative'],row['SHA256']),'Frozen '+row['Relative'])
    for row in before['OldRaw']+before['IsolatedSources']:
        req(sha(os.path.join(ROOT,row['Relative']))==row['SHA256'],'Frozen source '+row['Relative'])
def load_reader():
    path=os.path.join(ROOT,'Scripts','Create-FramePostPlacementDev.py')
    with open(path,encoding='utf-8-sig') as f: code=f.read()
    req(code.count('\ntry:\n')==1,'Exact reviewed parent main boundary')
    parent={'__name__':'beam_parent_contract_readonly'}
    exec(code.split('\ntry:\n')[0],parent)
    parent['READER']=parent['load_reader']()
    return parent
def normalize(value,package): return P['normalize'](value,package)
def scene():
    current=P['scene']()
    P['dependencies'](current[0],current[1],current[2])
    R['inherited_contract_checks']=len(P['R']['checks'])
    return current
def path(obj): return P['path'](obj)
def xyz(value): return P['xyz'](value)
def oldpost(current):
    actors=[a for a in current[1] if a.get_actor_label()=='DEV_FramePost_Right']
    req(len(actors)==1,'Exactly one unchanged original right post')
    actual=P['post_observation'](actors[0])
    old=read(os.path.join(ROOT,'Saved','Audit-2026-10-12-FramePostPlacementDev','verify-Run1','Result.json'))['post']
    package=path(current[0]).split('.')[0]
    req(normalize(actual,package)==normalize(old,SOURCE),'Original post full observed contract unchanged')
    return actual
def baseline(probe,extra):
    req(probe['success'] and probe['phase']=='probe' and probe['saved']==[] and probe['actor_count']==34,'Actual immutable new source probe')
    current=scene()
    package=MAP if extra is not None else SOURCE
    req(path(current[0])==package+'.'+package.rsplit('/',1)[1],'Exact current world package')
    expected=set(probe['scene_contract'])|({LABEL} if extra else set())
    req(set(current[3])==expected,'Old34 plus optional one beam; pawn/flow contract keys retained')
    original={key:value for key,value in current[3].items() if key!=LABEL}
    req(normalize(original,package)==probe['normalized_contract'],'Original34 transform/components/lights/flow/audio/forest unchanged')
    req(len(current[1])==(35 if extra else 34),'Exact native actor inventory')
    oldpost(current)
    return current
def beam_observation(actor):
    c=req(actor.get_component_by_class(unreal.StaticMeshComponent),'Actual beam native mesh component')
    origin,extent=actor.get_actor_bounds(False)
    result=dict(label=actor.get_actor_label(),object_path=path(actor),class_path=path(actor.get_class()),component_path=path(c),
        actor_collision_enabled=actor.get_actor_enable_collision(),location=xyz(actor.get_actor_location()),scale=xyz(actor.get_actor_scale3d()),
        rotation=[actor.get_actor_rotation().pitch,actor.get_actor_rotation().yaw,actor.get_actor_rotation().roll],
        bounds=dict(origin=xyz(origin),extent=xyz(extent),min=xyz(origin-extent),max=xyz(origin+extent)),
        mesh=path(c.get_editor_property('static_mesh')),materials=[path(c.get_material(i)) for i in range(c.get_num_materials())],
        mobility=P['enum'](c.get_editor_property('mobility')),collision_enabled=P['enum'](c.get_collision_enabled()),
        stored_collision_enabled=P['enum'](c.get_editor_property('body_instance').get_editor_property('collision_enabled')),
        object_type=P['enum'](c.get_collision_object_type()),collision_profile=str(c.get_collision_profile_name()),
        use_default_collision=c.get_editor_property('use_default_collision'),overlap=c.get_editor_property('generate_overlap_events'),
        actor_tick_enabled=actor.is_actor_tick_enabled(),component_tick_enabled=c.is_component_tick_enabled(),
        tags=[str(v) for v in actor.get_editor_property('tags')],controllable=unreal.SystemLibrary.does_implement_interface(actor,unreal.DYControllable))
    result.update({name:c.get_editor_property(name) for name in ('cast_shadow','cast_hidden_shadow','affect_dynamic_indirect_lighting','affect_distance_field_lighting')})
    channels={v.value:v for name in dir(unreal.CollisionChannel) for v in [getattr(unreal.CollisionChannel,name)] if isinstance(v,unreal.CollisionChannel) and 0<=v.value<8}
    req(set(channels)==set(range(8)),'Actual eight public channels')
    result['public_collision_responses']={v.name:P['enum'](c.get_collision_response_to_channel(v)) for _,v in sorted(channels.items())}
    dto=read(os.path.join(AUDIT,'PLACEMENT.json'))
    req(actor.get_class()==unreal.StaticMeshActor.static_class() and c.get_owner()==actor and len(actor.get_components_by_class(unreal.StaticMeshComponent))==1,'Exact native passive ownership')
    req(all(abs(a-b)<1e-6 for a,b in zip(result['location'],dto['LocationCm'])) and all(abs(v-dto['UniformScale'])<1e-7 for v in result['scale']) and all(abs(a-b)<1e-6 for a,b in zip(result['rotation'],dto['RotationDegrees'])),'Exact frozen equal-scale beam transform')
    req(result['mesh']==SM+'.'+SM.rsplit('/',1)[1] and result['materials']==[WOOD+'.'+WOOD.rsplit('/',1)[1]],'Only old beam mesh and one frozen wood MI')
    req(result['mobility']=='STATIC' and result['actor_collision_enabled'] and result['collision_enabled']==result['stored_collision_enabled']=='NO_COLLISION' and result['object_type']=='ECC_WORLD_STATIC' and result['collision_profile']=='Custom' and result['use_default_collision'] is False and result['overlap'] is False,'Actual collision profile/body/channel contract')
    req(all(v=='ECR_IGNORE' for v in result['public_collision_responses'].values()),'Actual eight responses Ignore')
    req(all(result[name] is False for name in ('cast_shadow','cast_hidden_shadow','affect_dynamic_indirect_lighting','affect_distance_field_lighting','actor_tick_enabled','component_tick_enabled','controllable')) and result['tags']==[],'No gameplay/Tick/shadow flags, without all-path render claims')
    req(all(abs(a-b)<.001 for a,b in zip(result['bounds']['min'],dto['ExpectedBoundsMinCm'])) and all(abs(a-b)<.001 for a,b in zip(result['bounds']['max'],dto['ExpectedBoundsMaxCm'])),'Actual native world bounds agree with numerical candidate')
    req(result['bounds']['min'][2]>770,'Beam remains above frozen core protection top')
    return result
def probe():
    current=scene()
    req(path(current[0])==SOURCE+'.'+SOURCE.rsplit('/',1)[1] and len(current[1])==34 and LABEL not in current[3],'Exact unchanged single-post source')
    req(not unreal.EditorAssetLibrary.does_asset_exist(MAP) and not os.path.exists(os.path.join(ROOT,'Content',MAP[6:]+'.umap')),'Only absent new Dev destination')
    R['post']=oldpost(current)
    mesh=req(unreal.load_asset(SM),'Actual frozen accepted beam mesh')
    info=P['bounds'](mesh)
    req(abs(info['size'][0]-2630.546630859375)<.001 and len(mesh.get_editor_property('static_materials'))==1,'Original unscaled one-slot beam preserved')
    R.update(actor_count=34,scene_contract=current[3],normalized_contract=normalize(current[3],SOURCE),mesh_bounds=info,assets_saved=[],map_saved=False,storage_probe=P['storage'](current[0]))
def author(probe):
    current=baseline(probe,None)
    P['storage'](current[0]);current=None
    req(not unreal.EditorAssetLibrary.does_asset_exist(MAP),'Refuse existing destination')
    req(LEVELS.new_level_from_template(MAP,SOURCE),'Native template copy to own new map only')
    R['saved'].append(MAP)
    current=baseline(probe,False)
    dto=read(os.path.join(AUDIT,'PLACEMENT.json'))
    req(dto['Schema']=='FrameBeamPlacementDev.v1' and dto['Map']==MAP and dto['SourceMap']==SOURCE,'Frozen exact DTO identity')
    actor=req(unreal.get_editor_subsystem(unreal.EditorActorSubsystem).spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(*dto['LocationCm']),unreal.Rotator(pitch=0.0,yaw=90.0,roll=0.0),False),'Spawn only one beam')
    actor.set_actor_label(LABEL);actor.set_editor_property('tags',[]);actor.set_actor_enable_collision(True);actor.set_actor_tick_enabled(False)
    c=actor.get_component_by_class(unreal.StaticMeshComponent)
    req(c.set_static_mesh(unreal.load_asset(SM)),'Only reference existing mesh')
    c.set_material(0,unreal.load_asset(WOOD));actor.set_actor_scale3d(unreal.Vector(*([dto['UniformScale']]*3)))
    c.set_mobility(unreal.ComponentMobility.STATIC);c.set_collision_profile_name('NoCollision');c.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
    c.set_collision_response_to_all_channels(unreal.CollisionResponseType.ECR_IGNORE);c.set_editor_property('generate_overlap_events',False)
    c.set_editor_properties(dict(cast_shadow=False,cast_hidden_shadow=False,affect_dynamic_indirect_lighting=False,affect_distance_field_lighting=False))
    c.set_component_tick_enabled(False)
    current=baseline(probe,True)
    R.update(beam=beam_observation(actor),post=oldpost(current),actor_count=35,scene_contract=current[3],storage_probe=P['storage'](current[0]))
    protect();req(LEVELS.save_current_level(),'Save only own new Dev level after contract gates')
    R.update(save_operations=2,assets_saved=[],map_saved=True,map_creation_api='LevelEditorSubsystem.new_level_from_template')
def verify(probe):
    baseline(probe,None)
    req(LEVELS.load_level(MAP),'Cold load actual own new map')
    current=baseline(probe,True)
    actors=[a for a in current[1] if a.get_actor_label()==LABEL];req(len(actors)==1,'Exactly one real saved beam')
    R.update(beam=beam_observation(actors[0]),post=oldpost(current),actor_count=35,scene_contract=current[3],assets_saved=[],map_saved=False,storage_probe=P['storage'](current[0]))
try:
    req(PHASE in ('probe','create','verify'),'Bounded phases only')
    req(os.path.commonpath([os.path.abspath(OUT),os.path.abspath(AUDIT)])==os.path.abspath(AUDIT),'Result only in own audit')
    protect();P=load_reader();LEVELS=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    req(LEVELS.load_level(SOURCE),'Load exact old source readonly')
    if PHASE=='probe': probe()
    else:
        data=read(os.path.join(AUDIT,'probe-Run1','Result.json'))
        if PHASE=='create': author(data)
        else: verify(data)
    protect();R['success']=True
except Exception:
    R['error']=traceback.format_exc();unreal.log_error(R['error'])
finally:
    with open(OUT,'x',encoding='utf-8') as f: json.dump(R,f,ensure_ascii=False,indent=2)
