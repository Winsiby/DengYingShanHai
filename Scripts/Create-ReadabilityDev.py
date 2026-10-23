"""Exact seven-package authoring/verification. Passive hints only; no gameplay Python."""
import os, json, traceback, hashlib, unreal
ROOT='/Game/DengYingShanHai/Dev/Readability'
MAP=ROOT+'/Maps/LV_ReadabilityLab'
MODE=ROOT+'/Core/BP_DYReadabilityGameMode'
STAGE=ROOT+'/Stage/BP_DYReadabilityPresentation'
MAT=ROOT+'/Guides/M_DYReadabilityGuide'
INST=[ROOT+'/Guides/MI_DYReadability_P0%d'%i for i in (1,2,3)]
ALLOWED={MAP,MODE,STAGE,MAT,*INST}
SOURCE_MAP='/Game/DengYingShanHai/Dev/EntryLoop/Maps/LV_EntryLoopDev'
SOURCE_MODE='/Game/DengYingShanHai/Dev/EntryLoop/Core/BP_DYEntryLoopGameMode'
SOURCE_STAGE='/Game/DengYingShanHai/Dev/ThreeAct/Stage/BP_DYThreeActPresentation'
IDS=('P01_SunAwakening','P02_ChaseForm','P03_DevPlayableCandidate')
VARS=('GuideP01','GuideP02','GuideP03')
CAPTIONS=('操纵灯，用 A / D 将头部影子送入浅色缺口；影形渐合后保持。',
          '分别操纵灯与偶，让偶影进入浅色缺口；贴合后保持，沿用 E / A / D。',
          '协同灯与偶，使偶影进入缺口；保持后，杖尖落向地线短标并成林。')
OUT=os.environ['DY_READABILITY_OUT']; PHASE=os.environ['DY_READABILITY_PHASE']
R=dict(success=False,phase=PHASE,saved=[],runtime_python=False,assets=sorted(ALLOWED))
def req(v,w):
    if not v: raise RuntimeError(w)
    return v
def path(o): return o.get_path_name() if o else None
def filehash(f):
    with open(f,'rb') as s: return hashlib.sha256(s.read()).hexdigest().upper()
def protect():
    with open(os.path.join(unreal.Paths.project_saved_dir(),'Audit-2026-10-09-Readability/BEFORE.json'),encoding='utf-8-sig') as s: before=json.load(s)
    for row in before['OldAssets']:
        req(filehash(row['Path'])==row['SHA256'],'Original asset changed: '+row['Path'])
def saved(a):
    pkg=path(a).split('.')[0]
    req(pkg in ALLOWED,'Exact save allowlist')
    req(unreal.EditorAssetLibrary.save_loaded_asset(a,only_if_is_dirty=False),'Save only new asset '+pkg)
    R['saved'].append(pkg)
def copy(a,b):
    req(b in ALLOWED and not unreal.EditorAssetLibrary.does_asset_exist(b),'Refuse old/existing destination '+b)
    return req(unreal.EditorAssetLibrary.duplicate_asset(a,b),'Copy new package')
def vec(v): return [v.x,v.y,v.z]
def geometry(a):
    rr=a.get_actor_rotation()
    return dict(label=a.get_actor_label(),cls=path(a.get_class()),position=vec(a.get_actor_location()),rotation=[rr.pitch,rr.yaw,rr.roll],scale=vec(a.get_actor_scale3d()))
def load_map(m):
    req(unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).load_level(m),'Load exact map')
    w=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    req(path(w).split('.')[0]==m,'Exact loaded World')
    return w,unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
with open(os.path.join(unreal.Paths.project_dir(),'Scripts/Create-ThreeActDev.py'),encoding='utf-8-sig') as s:
    lib={'__name__':'readability_graph_helpers'}
    exec(s.read().split('\nprotected_before = None\n')[0],lib)
lib.update(OUT=OUT,REPORT=R,ROOT=ROOT,ALLOWED_SAVES=ALLOWED)
BEL=unreal.BlueprintEditorLibrary; BGE=unreal.BlueprintGraphEditor
call=lib['add_call']; connect=lib['connect']; literal=lib['literal']; compile_bp=lib['compile_bp']
MATH='/Script/Engine.KismetMathLibrary.'

def patch_stage(bp):
    main=BGE.get_graph_editor(BEL.find_event_graph(bp))
    for n in VARS:
        req(main.add_member_variable(n,BEL.get_object_reference_type(unreal.Actor)),'One explicit passive guide reference')
        BEL.set_blueprint_variable_instance_editable(bp,n,True)
    ed=BGE.create_and_edit_function_graph(bp,'ApplyReadabilityGuides'); ed.set_function_is_private()
    ident=ed.add_graph_input_parameter('PuzzleId',BEL.get_basic_type_by_name('name'))
    ex=[ed.find_graph_entry_pin()]
    # Idempotent, event-only visibility. Missing references are safely skipped.
    for n,pid in zip(VARS,IDS):
        get=req(ed.add_get_member_variable_node(n),'Guide get')
        valid=call(ed,'/Script/Engine.KismetSystemLibrary.IsValid',Object=get.find_output_pin(n))
        br=req(ed.add_branch_node(),'Guide validity gate')
        for previous in ex: connect(previous,br.find_execute_pin())
        connect(valid.find_result_pin(),br.find_input_pin('Condition'))
        hide=call(ed,MATH+'NotEqual_NameName',A=ident,B=pid)
        sethidden=call(ed,'/Script/Engine.Actor.SetActorHiddenInGame',bNewHidden=hide.find_result_pin())
        connect(get.find_output_pin(n),sethidden.find_self_pin()); connect(br.find_output_pin('then'),sethidden.find_execute_pin())
        ex=[br.find_output_pin('else'),sethidden.find_then_pin()]
    compile_bp(bp)
    main=BGE.get_graph_editor(BEL.find_event_graph(bp))
    for event,pid in (('ReceivePuzzleActivated','event'),('ReceivePuzzleResolved','None')):
        node=req(main.find_event_node(event),'Cold-proven Stage override '+event)
        output=node.find_then_pin(); links=output.list_connected_pins(); req(len(links)==1,'Exact original event successor')
        req(output.break_pin_links(),'Insert only event visibility hook')
        hint=call(main,'ApplyReadabilityGuides',PuzzleId=node.find_output_pin('PuzzleId') if pid=='event' else 'None')
        connect(output,hint.find_execute_pin()); connect(hint.find_then_pin(),links[0])
    guidance=lib['graph_editor'](bp,'ShowActGuidance')
    captions=lib['calls'](guidance,'ShowCaption'); req(len(captions)==4,'Three exact actions plus neutral caption')
    for node,old,new in zip(captions[:3],('引日启幕 · 先按 E 操纵灯，用 A / D 发现灯与影的关系','逐光成形 · 按 E 在灯与皮影之间切换，用 A / D 协同调整','杖落成林 · 综合调整灯与皮影，影形稳定后等待真实落杖成林'),CAPTIONS):
        req(lib['text_source'](node.find_input_pin('Text'))==old,'Exact saved action string')
        literal(node.find_input_pin('Text'),new)
    add_phase_gate(bp)
    compile_bp(bp)
    lib['inspect_complete_growth'](bp,patched=True)
    R['graphs']=lib['graph_inventory'](bp)

def material():
    tools=unreal.AssetToolsHelpers.get_asset_tools()
    m=req(tools.create_asset(MAT.rsplit('/',1)[1],MAT.rsplit('/',1)[0],unreal.Material,unreal.MaterialFactoryNew()),'New bounded mask material')
    m.set_editor_properties(dict(blend_mode=unreal.BlendMode.BLEND_MASKED,shading_model=unreal.MaterialShadingModel.MSM_UNLIT,two_sided=True,opacity_mask_clip_value=.3))
    mel=unreal.MaterialEditingLibrary; nodes=[]
    def node(cls,**props):
        n=mel.create_material_expression(m,cls,len(nodes)%8*220,len(nodes)//8*140); n.set_editor_properties(props); nodes.append(n); return n
    def con(a,b,slot): req(mel.connect_material_expressions(a,'',b,slot),'Material connection '+slot)
    def binary(cls,a,b):
        n=node(cls); con(a,n,'A'); con(b,n,'B'); return n
    def unary(cls,a):
        n=node(cls); con(a,n,''); return n
    def const(v): return node(unreal.MaterialExpressionConstant,r=v)
    def param(n,v): return node(unreal.MaterialExpressionScalarParameter,parameter_name=n,default_value=v)
    add=lambda a,b:binary(unreal.MaterialExpressionAdd,a,b)
    sub=lambda a,b:binary(unreal.MaterialExpressionSubtract,a,b)
    mul=lambda a,b:binary(unreal.MaterialExpressionMultiply,a,b)
    div=lambda a,b:binary(unreal.MaterialExpressionDivide,a,b)
    maximum=lambda a,b:binary(unreal.MaterialExpressionMax,a,b)
    ab=lambda a:unary(unreal.MaterialExpressionAbs,a)
    sat=lambda a:unary(unreal.MaterialExpressionSaturate,a)
    wp=node(unreal.MaterialExpressionWorldPosition)
    wy=node(unreal.MaterialExpressionComponentMask,r=False,g=True,b=False,a=False); con(wp,wy,'')
    wz=node(unreal.MaterialExpressionComponentMask,r=False,g=False,b=True,a=False); con(wp,wz,'')
    one=const(1); thick=param('LineWidth',3.5)
    def inside(d,w): return sub(one,sat(div(d,w)))
    u=sub(wy,param('SunY',0)); v=sub(wz,param('SunZ',310)); rad=param('SunRadius',56)
    dist=unary(unreal.MaterialExpressionSquareRoot,add(mul(u,u),mul(v,v)))
    arc=mul(inside(ab(sub(dist,rad)),thick),sat(div(add(v,const(6)),const(12))))
    u=ab(sub(wy,param('BodyY',0))); v=ab(sub(wz,param('BodyZ',270)))
    hw=param('BodyHalfWidth',60); hh=param('BodyHalfHeight',140)
    vertical=mul(inside(ab(sub(u,hw)),thick),sat(div(sub(hh,v),const(4))))
    vertical=mul(vertical,sat(div(sub(v,sub(hh,const(28))),const(4))))
    horizontal=mul(inside(ab(sub(v,hh)),thick),sat(div(sub(hw,u),const(4))))
    horizontal=mul(horizontal,sat(div(sub(u,sub(hw,const(28))),const(4))))
    bracket=mul(maximum(vertical,horizontal),param('BodyEnabled',0))
    u=ab(sub(wy,param('GroundY',0))); v=ab(sub(wz,param('GroundZ',70)))
    dash=mul(sat(div(sub(const(28),u),const(3))),inside(v,thick))
    tick=mul(inside(u,thick),sat(div(sub(const(12),v),const(3))))
    ground=mul(maximum(dash,tick),param('GroundEnabled',0))
    mask=maximum(maximum(arc,bracket),ground)
    color=node(unreal.MaterialExpressionVectorParameter,parameter_name='GuideInk',default_value=unreal.LinearColor(500,400,240,1))
    gi=node(unreal.MaterialExpressionGIReplace); con(color,gi,'')
    names=mel.get_material_expression_input_names(gi); req(len(names)==3,'Actual direct/static/dynamic inputs')
    zero=const(0)
    for name in names[1:]: con(zero,gi,name)
    req(mel.connect_material_property(gi,'',unreal.MaterialProperty.MP_EMISSIVE_COLOR),'Unlit authored ink')
    bsdf=node(unreal.MaterialExpressionSubstrateUnlitBSDF); con(gi,bsdf,'')
    req(mel.connect_material_property(bsdf,'',unreal.MaterialProperty.MP_FRONT_MATERIAL),'Explicit native Substrate unlit surface')
    req(mel.connect_material_property(mask,'',unreal.MaterialProperty.MP_OPACITY_MASK),'Bounded masked strokes')
    errors=mel.recompile_material(m); req(not errors,'Shader errors '+str(errors))
    R['material_node_count']=len(nodes); saved(m)
    return m

def create(probe,samples):
    for pkg in ALLOWED: req(not unreal.EditorAssetLibrary.does_asset_exist(pkg),'Refuse existing destination '+pkg)
    req(probe['success'] and not probe['saved'],'Cold source inspection required')
    # This exact scope is frozen on disk BEFORE the first package is created.
    contract=dict(assets=sorted(ALLOWED),count=7,source_probe_sha256=filehash(os.environ['DY_READABILITY_PROBE']),samples_sha256=filehash(os.environ['DY_READABILITY_SAMPLE']),old_assets_immutable=True,only_native_files=3)
    with open(os.path.join(os.path.dirname(OUT),'ASSET-CONTRACT.json'),'x',encoding='utf-8') as s: json.dump(contract,s,ensure_ascii=False,indent=2)
    bp=copy(SOURCE_STAGE,STAGE); patch_stage(bp); saved(bp)
    mode=copy(SOURCE_MODE,MODE); compile_bp(mode); saved(mode)
    m=material(); instances=[]; calibrations=[]
    for i,pkg in enumerate(INST):
        rows=samples[str(i)]['rows']; target=rows[1]; points=target['parts']['head']['bounds']+target['parts']['torso']['bounds']
        yy=[p['world'][1] for p in points]; zz=[p['world'][2] for p in points]
        # Open corners, not a full answer contour. Include the measured tolerance envelope.
        dy=max(abs(r['parts']['torso']['center']['world'][1]-target['parts']['torso']['center']['world'][1]) for r in rows[2:])
        head=target['parts']['head']; rr=max(abs(p['world'][1]-head['center']['world'][1]) for p in head['bounds'])+8
        vals=dict(SunY=head['center']['world'][1],SunZ=head['center']['world'][2],SunRadius=rr,BodyY=(max(yy)+min(yy))/2,BodyZ=(max(zz)-min(zz))/2+min(zz),BodyHalfWidth=(max(yy)-min(yy))/2+dy+8,BodyHalfHeight=(max(zz)-min(zz))/2+8,BodyEnabled=float(i>0),GroundEnabled=float(i==2),GroundY=target['A']['world'][1],GroundZ=70.,LineWidth=3.5)
        ins=req(unreal.AssetToolsHelpers.get_asset_tools().create_asset(pkg.rsplit('/',1)[1],pkg.rsplit('/',1)[0],unreal.MaterialInstanceConstant,unreal.MaterialInstanceConstantFactoryNew()),'Own material instance')
        unreal.MaterialEditingLibrary.set_material_instance_parent(ins,m)
        for n,v in vals.items():
            # Installed UE5.8.3 setter performs the write but always returns false
            # (MaterialEditingLibrary.cpp:1485-1493). Verify actual readback instead.
            unreal.MaterialEditingLibrary.set_material_instance_scalar_parameter_value(ins,n,v)
            req(abs(unreal.MaterialEditingLibrary.get_material_instance_scalar_parameter_value(ins,n)-v)<.0001,'Actual authored parameter readback '+n)
        unreal.MaterialEditingLibrary.update_material_instance(ins); saved(ins); instances.append(ins); calibrations.append(vals)
    copy(SOURCE_MAP,MAP)
    w,actors=load_map(MAP); api=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    old=req(next((a for a in actors if a.get_actor_label()=='ThreeAct_StagePresentation'),None),'Exact copied Stage')
    screen=old.get_editor_property('DevReceiver'); req(screen.get_world_rotation()==unreal.Rotator(0,0,0),'This analytic material requires the cold-proven unrotated screen')
    loc=screen.get_world_location(); sc=screen.get_world_scale(); req(abs(loc.x-950)<1e-8 and abs(sc.x-.5)<1e-8,'Cold face X925')
    bindings={n:old.get_editor_property(n) for n in ('puzzle_director','stage_environment','resolved_environment_state','enable_staff_contact_presentation','staff_projection_screen','narrative_ground_line','forest_presentation_actor','DevReceiver','DevGround')}
    ns=req(api.spawn_actor_from_class(bp.generated_class(),old.get_actor_location(),old.get_actor_rotation(),False),'New explicit Stage')
    ns.set_actor_label('Readability_StagePresentation'); ns.set_actor_scale3d(old.get_actor_scale3d()); ns.set_editor_properties(bindings)
    guides=[]
    for i,ins in enumerate(instances):
        a=req(api.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(923.5,0,350),unreal.Rotator(0,0,0),False),'Passive guide surface')
        a.set_actor_label('Readability_GuideP0%d'%(i+1)); a.set_actor_scale3d(unreal.Vector(.008,9,8)); a.set_actor_hidden_in_game(True)
        c=a.static_mesh_component; c.set_static_mesh(unreal.load_asset('/Engine/BasicShapes/Cube')); c.set_material(0,ins)
        c.set_collision_profile_name('NoCollision',False); c.set_editor_properties(dict(cast_shadow=False,receives_decals=False,can_ever_affect_navigation=False,affect_dynamic_indirect_lighting=False,affect_distance_field_lighting=False))
        ns.set_editor_property(VARS[i],a); guides.append(a)
    req(api.destroy_actor(old),'Replace only the copied Stage')
    w.get_world_settings().set_editor_property('default_game_mode',mode.generated_class())
    d=ns.get_puzzle_director(); req(not d.is_auto_start_on_begin_play() and d.get_evaluation_frequency_hz()==15,'Approved menu/Hz')
    R['calibrations']=calibrations; R['geometry']=[geometry(a) for a in api.get_all_level_actors()]
    req(unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level(),'Save only exact new map'); R['saved'].append(MAP)
    req(set(R['saved'])==ALLOWED and len(R['saved'])==7,'Only seven approved new packages')

def repair_collision(probe,samples):
    w,actors=load_map(MAP)
    st=req(next((a for a in actors if a.get_actor_label()=='Readability_StagePresentation'),None),'Exact new Stage')
    for n in VARS:
        a=req(st.get_editor_property(n),'Explicit guide'); c=a.static_mesh_component
        req(a.get_actor_label().startswith('Readability_Guide') and a.get_editor_property('hidden') and not c.get_editor_property('cast_shadow'),'Only new hidden passive guides')
        c.set_collision_profile_name('NoCollision',False)
        req(c.get_collision_enabled()==unreal.CollisionEnabled.NO_COLLISION,'Actual named profile is NoCollision')
    req(unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level(),'Save only new map collision profiles')
    R['saved'].append(MAP)

def add_phase_gate(bp):
    ed=lib['graph_editor'](bp,'ApplyReadabilityGuides')
    display=call(ed,'/Script/DengYingShanHai.DYStagePresentation.GetPlayerActDisplay')
    result=display.find_result_pin()
    actions=ed.list_available_nodes([result])
    candidates=[a for a in actions if 'break' in a.lower() and 'dyactsequencesnapshot' in ''.join(x for x in a.lower() if x.isalnum())]
    R['break_candidates']=candidates
    req(len(candidates)==1,'One reflected snapshot break action')
    broken=req(ed.create_node_from_name(candidates[0],unreal.Vector2D(0,0),[result]),'Official snapshot break node')
    if not broken.find_input_pin('DYActSequenceSnapshot').list_connected_pins(): connect(result,broken.find_input_pin('DYActSequenceSnapshot'))
    phase=req(broken.find_output_pin('Phase').is_valid(),'Actual passive Phase output')
    playing=call(ed,MATH+'EqualEqual_ByteByte',A=broken.find_output_pin('Phase'),B='1')
    notplaying=call(ed,MATH+'Not_PreBool',A=playing.find_result_pin())
    hidden=lib['calls'](ed,'SetActorHiddenInGame'); req(len(hidden)==3,'Exactly three visibility targets')
    for setter in hidden:
        pin=setter.find_input_pin('bNewHidden'); sources=pin.list_connected_pins(); req(len(sources)==1,'Original id gate')
        req(pin.break_pin_links(),'Add passive Phase gate only')
        gate=call(ed,MATH+'BooleanOR',A=sources[0],B=notplaying.find_result_pin()); connect(gate.find_result_pin(),pin)
    compile_bp(bp)

def repair_phase(probe,samples):
    bp=req(unreal.load_asset(STAGE),'Only new Stage'); add_phase_gate(bp); saved(bp)

def repair_visual(probe,samples):
    m=req(unreal.load_asset(MAT),'Only new guide material'); mel=unreal.MaterialEditingLibrary
    names=mel.get_scalar_parameter_names(m); req('SunY' in [str(n) for n in names],'Real guide parameters')
    # Official expression exporter is unnecessary: parameter identity is reflected.
    expressions=[o for o in unreal.ObjectIterator(unreal.MaterialExpressionVectorParameter) if o.get_outer()==m and str(o.get_editor_property('parameter_name'))=='GuideInk']
    req(len(expressions)==1,'One actual GuideInk expression'); color=expressions[0]
    color.set_editor_property('default_value',unreal.LinearColor(6,4.8,2.6,1))
    bsdf=req(mel.create_material_expression(m,unreal.MaterialExpressionSubstrateUnlitBSDF,1800,0),'Native unlit BSDF')
    req(mel.connect_material_expressions(color,'',bsdf,''),'Actual first input: EmissiveColor')
    req(mel.connect_material_property(bsdf,'',unreal.MaterialProperty.MP_FRONT_MATERIAL),'Actual front material root')
    req(not mel.recompile_material(m),'Native shader compilation'); saved(m)
    for i,pkg in enumerate(INST):
        ins=unreal.load_asset(pkg); head=samples[str(i)]['rows'][1]['parts']['head']
        values=dict(SunY=head['center']['world'][1],SunZ=head['center']['world'][2],SunRadius=max(abs(p['world'][1]-head['center']['world'][1]) for p in head['bounds'])+8)
        for n,v in values.items():
            mel.set_material_instance_scalar_parameter_value(ins,n,v)
            req(abs(mel.get_material_instance_scalar_parameter_value(ins,n)-v)<.0001,'Measured head projection readback')
        saved(ins)
    bp=unreal.load_asset(STAGE); ed=lib['graph_editor'](bp,'ShowActGuidance')
    captions=lib['calls'](ed,'ShowCaption'); req(len(captions)==4,'Three actual action lines')
    for n,text in zip(captions[:3],CAPTIONS): literal(n.find_input_pin('Text'),text)
    compile_bp(bp); saved(bp)

def tune_ink(probe,samples):
    # Screenshot review proved 6 cd/m2 was dark under the unchanged exposure.
    # Set an explicit per-instance value and validate actual readback.
    mel=unreal.MaterialEditingLibrary
    for pkg in INST:
        ins=req(unreal.load_asset(pkg),'Only new guide instance')
        ink=unreal.LinearColor(500,400,240,1)
        mel.set_material_instance_vector_parameter_value(ins,'GuideInk',ink)
        actual=mel.get_material_instance_vector_parameter_value(ins,'GuideInk')
        req(abs(actual.r-500)<.0001 and abs(actual.g-400)<.0001 and abs(actual.b-240)<.0001,'Actual per-instance ink readback')
        saved(ins)
    R['ink_cd_m2']=[500,400,240]

def suppress_hint_gi(probe,samples):
    m=unreal.load_asset(MAT); mel=unreal.MaterialEditingLibrary
    color=[o for o in unreal.ObjectIterator(unreal.MaterialExpressionVectorParameter) if o.get_outer()==m and str(o.get_editor_property('parameter_name'))=='GuideInk']
    bsdf=[o for o in unreal.ObjectIterator(unreal.MaterialExpressionSubstrateUnlitBSDF) if o.get_outer()==m]
    req(len(color)==len(bsdf)==1,'One actual guide color and root')
    gi=mel.create_material_expression(m,unreal.MaterialExpressionGIReplace,1600,0)
    zero=mel.create_material_expression(m,unreal.MaterialExpressionConstant,1400,100); zero.set_editor_property('r',0)
    names=mel.get_material_expression_input_names(gi); req(len(names)==3,'Actual direct/static/dynamic inputs')
    req(mel.connect_material_expressions(color[0],'',gi,''),'Direct appearance unchanged')
    for name in names[1:]: req(mel.connect_material_expressions(zero,'',gi,name),'Zero indirect input '+name)
    req(mel.connect_material_expressions(gi,'',bsdf[0],''),'Same unlit emission root')
    req(mel.connect_material_property(gi,'',unreal.MaterialProperty.MP_EMISSIVE_COLOR),'Same legacy compatibility root')
    req(not mel.recompile_material(m),'Compile hint-only GI isolation'); saved(m)
    _,actors=load_map(MAP); st=next(a for a in actors if a.get_actor_label()=='Readability_StagePresentation')
    for n in VARS:
        c=st.get_editor_property(n).static_mesh_component
        c.set_editor_properties(dict(affect_dynamic_indirect_lighting=False,affect_distance_field_lighting=False))
    req(unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level(),'Save only new hint component flags')
    R['saved'].append(MAP)

def verify(probe,samples):
    w,actors=load_map(MAP); stages=[a for a in actors if a.get_actor_label()=='Readability_StagePresentation']; req(len(stages)==1,'One cold Stage')
    st=stages[0]; req(path(st.get_class()).split('.')[0]==STAGE,'New saved Stage class')
    d=st.get_puzzle_director(); req(not d.is_auto_start_on_begin_play() and d.get_evaluation_frequency_hz()==15,'Cold no auto-start / 15Hz')
    mode=unreal.load_asset(MODE); req(w.get_world_settings().get_editor_property('default_game_mode')==mode.generated_class(),'Cold own mode')
    req(path(unreal.get_default_object(mode.generated_class()).get_editor_property('player_controller_class'))=='/Script/DengYingShanHai.DYDevEntryPlayerController','Cold native menu')
    for i,n in enumerate(VARS):
        a=req(st.get_editor_property(n),'Cold explicit guide'); c=a.static_mesh_component
        R.setdefault('guide_checks',[]).append(dict(name=n,hidden=a.get_editor_property('hidden'),shadow=c.get_editor_property('cast_shadow'),collision=str(c.get_collision_enabled()),profile=str(c.get_collision_profile_name()),indirect=c.get_editor_property('affect_dynamic_indirect_lighting'),distance_field=c.get_editor_property('affect_distance_field_lighting')))
        req(a in actors and a.get_actor_label()=='Readability_GuideP0%d'%(i+1),'Guide in this World')
        req(a.get_editor_property('hidden') and not c.get_editor_property('cast_shadow') and c.get_collision_enabled()==unreal.CollisionEnabled.NO_COLLISION,'Hidden / no collision / no shadow')
        req(not c.get_editor_property('affect_dynamic_indirect_lighting') and not c.get_editor_property('affect_distance_field_lighting'),'Hint excludes authored indirect/DF participation')
        req(path(c.get_material(0)).split('.')[0]==INST[i],'Cold correct per-act mask')
        req(unreal.get_default_object(st.get_class()).get_editor_property(n) is None,'No runtime references in CDO')
    original={r['label']:r for r in probe['actors']}
    current={a.get_actor_label():a for a in actors if not a.get_actor_label().startswith('Readability_')}
    req(set(current)==set(original)-{'ThreeAct_StagePresentation'},'No other actor added/removed')
    # Source inventory uses actual numeric transform strings; compare independently loaded source.
    copied=[geometry(a) for a in current.values()]
    _,sourceactors=load_map(SOURCE_MAP)
    src=[geometry(a) for a in sourceactors if a.get_actor_label()!='ThreeAct_StagePresentation']
    req(sorted(copied,key=lambda x:x['label'])==sorted(src,key=lambda x:x['label']),'Every other actor transform/class unchanged')
    bp=unreal.load_asset(STAGE); R['graphs']=lib['graph_inventory'](bp)
    req(all(not g['errors'] for g in R['graphs']),'Cold graph errors absent')
    req(sum(n['node_class']=='/Script/BlueprintGraph.K2Node_Timeline' for g in R['graphs'] for n in g['nodes'])==2,'Same original drop and growth Timelines')
    R['calibrations']=[{str(p.parameter_info.name):p.parameter_value for p in unreal.load_asset(ins).get_editor_property('scalar_parameter_values')} for ins in INST]
    m=unreal.load_asset(MAT)
    R['hint_material_nodes']=[o.get_class().get_name() for o in unreal.ObjectIterator(unreal.MaterialExpression) if o.get_outer()==m]
    req(R['hint_material_nodes'].count('MaterialExpressionSubstrateUnlitBSDF')==1 and R['hint_material_nodes'].count('MaterialExpressionGIReplace')==1,'One native unlit root and indirect replacement')
    R['guide_ink']=[str(unreal.MaterialEditingLibrary.get_material_instance_vector_parameter_value(unreal.load_asset(ins),'GuideInk')) for ins in INST]
    R['cold_read_only']=True

try:
    protect()
    with open(os.environ['DY_READABILITY_PROBE'],encoding='utf-8-sig') as s: probe=json.load(s)
    with open(os.environ['DY_READABILITY_SAMPLE'],encoding='utf-8-sig') as s: samples=json.load(s)
    {'create':create,'verify':verify,'repair_collision':repair_collision,'repair_phase':repair_phase,'repair_visual':repair_visual,'tune_ink':tune_ink,'suppress_hint_gi':suppress_hint_gi}[PHASE](probe,samples)
    protect(); R['success']=True
except Exception: R['error']=traceback.format_exc()
with open(OUT,'x',encoding='utf-8') as s: json.dump(R,s,ensure_ascii=False,indent=2)
unreal.log('READABILITY_AUTHOR '+json.dumps({k:R.get(k) for k in ('success','error','saved')},ensure_ascii=False))
