"""Five new floor-only assets; preserve the existing scene except floor slot zero."""
import os, json, traceback, hashlib, unreal
ROOT = unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir())
AUDIT = os.path.join(unreal.Paths.project_saved_dir(), 'Audit-2026-10-11-WoodFloor')
MAP = '/Game/DengYingShanHai/Dev/EnvironmentStates/Maps/LV_EnvironmentStatesLab'
BASE = '/Game/DengYingShanHai/Dev/WoodFloor/'
MAT = BASE+'Materials/M_DY_WoodFloor_Master'
MI = BASE+'Materials/MI_DY_WoodFloor_Dev'
SPECS = [
 ('T_DY_WoodFloor_BaseColor','old_wooden_floor_02_diff_2k.png',True,'TC_DEFAULT','SAMPLERTYPE_COLOR','BaseColor','D60C5E6193A08536F9D51FF70A2CAD79BC16AB216D6F28F18C61A6BDBA619029'),
 ('T_DY_WoodFloor_NormalDX','old_wooden_floor_02_nor_dx_2k.png',False,'TC_NORMALMAP','SAMPLERTYPE_NORMAL','NormalDX','E6534B04F22ED2154C431ACD63C4D841D6DE69236494CBFDF58FA6FAC0ACA1D2'),
 ('T_DY_WoodFloor_ARM','old_wooden_floor_02_arm_2k.png',False,'TC_MASKS','SAMPLERTYPE_MASKS','ARM','CCCFC53F964CC55754A9FC78F6300F3CDFB0829990D113AEFCF40FD5398E512C')]
ASSETS = sorted([MAT, MI]+[BASE+'Textures/'+s[0] for s in SPECS])
OUT = os.environ['DY_READABILITY_OUT']; PHASE = os.environ['DY_READABILITY_PHASE']
R = dict(success=False,phase=PHASE,saved=[],checks=[],assets=ASSETS,map=MAP)
MEL = unreal.MaterialEditingLibrary

def req(v, m):
    if not v: raise RuntimeError(m)
    R['checks'].append(m)
    return v
def path(v): return v.get_path_name() if v else None
def xyz(v): return [v.x,v.y,v.z]
def sha(f):
    with open(f,'rb') as stream: return hashlib.sha256(stream.read()).hexdigest().upper()
def enum_name(v): return str(v).split('.')[-1] if not hasattr(v,'name') else v.name
def protect():
    with open(os.path.join(AUDIT,'BEFORE.json'),encoding='utf-8-sig') as stream: before=json.load(stream)
    for row in before['Files']:
        if row['Relative'] not in before['Approved']:
            req(sha(os.path.join(ROOT,row['Relative']))==row['SHA256'],'Protected '+row['Relative'])
    with open(os.path.join(AUDIT,'RAW-SOURCES.json'),encoding='utf-8-sig') as stream: raw=json.load(stream)
    for row in raw: req(sha(os.path.join(ROOT,row['Relative']))==row['SHA256'],'Raw source '+row['Relative'])
def save(a):
    pkg=path(a).split('.')[0]; req(pkg in ASSETS,'Exact five-package save allowlist')
    req(unreal.EditorAssetLibrary.save_loaded_asset(a,only_if_is_dirty=False),'Save new '+pkg)
    R['saved'].append(pkg)
def scene():
    # Reuse the audited read-only scene contract; never execute its old authoring phase.
    with open(os.path.join(ROOT,'Scripts/Create-EnvironmentStates.py'),encoding='utf-8-sig') as stream:
        lib={'__name__':'wood_floor_scene_contract'}
        exec(stream.read().split('\ntry:\n')[0],lib)
    world, actors, stage, contract=lib['contract']()
    for actor in actors:
        meshes=actor.get_components_by_class(unreal.StaticMeshComponent)
        contract[actor.get_actor_label()]['static_meshes']=[dict(
            name=c.get_name(),mesh=path(c.get_editor_property('static_mesh')),
            materials=[path(c.get_material(i)) for i in range(c.get_num_materials())],
            collision_profile=str(c.get_collision_profile_name()),collision_enabled=enum_name(c.get_collision_enabled()),
            cast_shadow=c.get_editor_property('cast_shadow')) for c in meshes]
    floor=req(next((a for a in actors if a.get_actor_label()=='DEV_Floor'),None),'Exact existing floor label')
    component=req(floor.get_component_by_class(unreal.StaticMeshComponent),'Existing floor component')
    origin,extent=floor.get_actor_bounds(False)
    return world,actors,stage,contract,floor,component,dict(origin=xyz(origin),extent=xyz(extent))
def comparable(contract):
    # Exclude exactly slot zero, not other materials or any other component fields.
    c=json.loads(json.dumps(contract))
    req(len(c['DEV_Floor']['static_meshes'])==1,'One existing floor mesh')
    req(len(c['DEV_Floor']['static_meshes'][0]['materials'])==1,'One existing floor material slot')
    c['DEV_Floor']['static_meshes'][0]['materials'][0]='<OnlyApprovedSlot0>'
    return c
def probe():
    world,actors,stage,contract,floor,component,bounds=scene()
    req(stage.is_five_state_environment_enabled(),'Accepted five-state Dev remains enabled')
    req(component.get_editor_property('static_mesh').get_path_name()=='/Engine/BasicShapes/Cube.Cube','Actual existing engine cube')
    req(bounds['extent']==[1200.0,900.0,50.0],'Actual unchanged 24 m by 18 m floor')
    temp=unreal.Material()
    node=req(MEL.create_material_expression(temp,unreal.MaterialExpressionSubstrateSlabBSDF),'Transient API probe, no asset or save')
    R.update(scene_contract=contract,floor_bounds=bounds,floor_component=path(component),
       api=dict(slab_inputs=list(MEL.get_material_expression_input_names(node)),
                normal_sampler=enum_name(unreal.MaterialSamplerType.SAMPLERTYPE_NORMAL),
                texture_size_method=hasattr(unreal.Texture2D,'blueprint_get_size_x'),
                material_front_property=enum_name(unreal.MaterialProperty.MP_FRONT_MATERIAL)))
    req(R['api']['texture_size_method'],'Actual reflected texture size API')
    req(all(not unreal.EditorAssetLibrary.does_asset_exist(p) for p in ASSETS),'Five destinations absent before authoring')
def create(probe_data):
    req(probe_data['success'] and probe_data['phase']=='probe' and not probe_data['saved'],'Frozen read-only probe')
    world,actors,stage,before,floor,component,bounds=scene()
    req(before==probe_data['scene_contract'],'Source unchanged since probe')
    req(all(not unreal.EditorAssetLibrary.does_asset_exist(p) for p in ASSETS),'Never overwrite existing assets')
    textures=[]; tools=unreal.AssetToolsHelpers.get_asset_tools()
    for name,filename,srgb,compression,sampler,param,source_sha in SPECS:
        source=os.path.join(ROOT,'Assets/Sources/PolyHaven/old_wooden_floor_02',filename)
        req(sha(source)==source_sha,'Exact official raw texture hash')
        task=unreal.AssetImportTask(); task.set_editor_properties(dict(filename=source,destination_path=BASE+'Textures',destination_name=name,automated=True,replace_existing=False,save=False))
        tools.import_asset_tasks([task])
        imported=list(task.get_editor_property('imported_object_paths'))
        req(imported==[BASE+'Textures/'+name+'.'+name],'Exact imported texture object')
        tex=req(unreal.load_asset(imported[0]),'New texture exists')
        tex.set_editor_properties(dict(srgb=srgb,compression_settings=getattr(unreal.TextureCompressionSettings,compression)))
        save(tex);textures.append(tex)
    m=req(tools.create_asset(MAT.rsplit('/',1)[1],MAT.rsplit('/',1)[0],unreal.Material,unreal.MaterialFactoryNew()),'New floor-only material')
    m.set_editor_properties(dict(blend_mode=unreal.BlendMode.BLEND_OPAQUE,shading_model=unreal.MaterialShadingModel.MSM_DEFAULT_LIT,two_sided=False,tangent_space_normal=True))
    nodes=[]
    def node(cls,**properties):
        obj=req(MEL.create_material_expression(m,cls,len(nodes)%6*220,len(nodes)//6*200),'Material node '+cls.__name__)
        obj.set_editor_properties(properties);nodes.append(obj);return obj
    def connect(a,b,slot,output=''):
        req(MEL.connect_material_expressions(a,output,b,slot),'Actual graph link '+slot)
    uv=node(unreal.MaterialExpressionTextureCoordinate,coordinate_index=0)
    u=node(unreal.MaterialExpressionScalarParameter,parameter_name='TilingU',default_value=12.)
    v=node(unreal.MaterialExpressionScalarParameter,parameter_name='TilingV',default_value=9.)
    xy=node(unreal.MaterialExpressionAppendVector);connect(u,xy,'A');connect(v,xy,'B')
    scaled=node(unreal.MaterialExpressionMultiply);connect(uv,scaled,'A');connect(xy,scaled,'B')
    samples=[]
    for tex,spec in zip(textures,SPECS):
        sample=node(unreal.MaterialExpressionTextureSampleParameter2D,parameter_name=spec[5],texture=tex,sampler_type=getattr(unreal.MaterialSamplerType,spec[4]))
        connect(scaled,sample,'UVs');samples.append(sample)
    req(unreal.SystemLibrary.get_console_variable_int_value('r.Substrate')==0,'Keep actual existing standard PBR renderer')
    for sample,output,prop in [(samples[0],'RGB',unreal.MaterialProperty.MP_BASE_COLOR),
        (samples[1],'RGB',unreal.MaterialProperty.MP_NORMAL),(samples[2],'G',unreal.MaterialProperty.MP_ROUGHNESS)]:
        req(MEL.connect_material_property(sample,output,prop),'Actual standard PBR property '+enum_name(prop))
    metal=node(unreal.MaterialExpressionConstant,r=0.);specular=node(unreal.MaterialExpressionConstant,r=.5)
    req(MEL.connect_material_property(metal,'',unreal.MaterialProperty.MP_METALLIC),'Nonmetal wood')
    req(MEL.connect_material_property(specular,'',unreal.MaterialProperty.MP_SPECULAR),'Default dielectric F0 .04')
    req(MEL.connect_material_property(samples[2],'R',unreal.MaterialProperty.MP_AMBIENT_OCCLUSION),'ARM AO output')
    errors=list(MEL.recompile_material(m));req(not errors,'Material compiles without shader errors: '+str(errors))
    save(m)
    ins=req(tools.create_asset(MI.rsplit('/',1)[1],MI.rsplit('/',1)[0],unreal.MaterialInstanceConstant,unreal.MaterialInstanceConstantFactoryNew()),'Floor constant instance')
    MEL.set_material_instance_parent(ins,m)
    for param,val in [('TilingU',12.),('TilingV',9.)]:
        MEL.set_material_instance_scalar_parameter_value(ins,param,val)
        req(MEL.get_material_instance_scalar_parameter_value(ins,param)==val,'Verify setter actual readback '+param)
    MEL.update_material_instance(ins);save(ins)
    component.set_material(0,ins)
    req(comparable(scene()[3])==comparable(before),'Only floor material slot changes in full scene contract')
    req(unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level(),'Save only existing approved Dev map')
    R['saved'].append(MAP)
def repair():
    # Correct only this new material after actual RenderInspect proved r.Substrate=0.
    req(unreal.SystemLibrary.get_console_variable_int_value('r.Substrate')==0,'Actual existing renderer is standard PBR')
    m=req(unreal.load_asset(MAT),'Only own new master may be repaired')
    slab=req(MEL.get_material_property_input_node(m,unreal.MaterialProperty.MP_FRONT_MATERIAL),'Exact initial unused Slab root')
    req(slab.get_class().get_name()=='MaterialExpressionSubstrateSlabBSDF','Expected initial Slab class')
    inputs=list(MEL.get_inputs_for_material_expression(m,slab));names=list(MEL.get_material_expression_input_names(slab))
    nodes={''.join(c for c in n if c.isalnum()).lower():i for n,i in zip(names,inputs)}
    for key,output,prop,param in [('diffusealbedo','RGB',unreal.MaterialProperty.MP_BASE_COLOR,'BaseColor'),
        ('normal','RGB',unreal.MaterialProperty.MP_NORMAL,'NormalDX'),('roughness','G',unreal.MaterialProperty.MP_ROUGHNESS,'ARM')]:
        sample=req(nodes[key],'Original own texture node '+key)
        req(str(sample.get_editor_property('parameter_name'))==param,'Exact authored texture parameter')
        req(MEL.connect_material_property(sample,output,prop),'Repair only inactive PBR output '+key)
    MEL.delete_material_expression(m,slab)
    if nodes['f0']:MEL.delete_material_expression(m,nodes['f0'])
    for name,val,prop in [('Metallic',0.,unreal.MaterialProperty.MP_METALLIC),('Specular',.5,unreal.MaterialProperty.MP_SPECULAR)]:
        node=req(MEL.create_material_expression(m,unreal.MaterialExpressionConstant),'One explicit '+name)
        node.set_editor_property('r',val);req(MEL.connect_material_property(node,'',prop),'Standard '+name)
    req(not list(MEL.recompile_material(m)),'Repaired standard PBR compiles');save(m)
def verify(probe_data):
    world,actors,stage,contract,floor,component,bounds=scene()
    req(comparable(contract)==comparable(probe_data['scene_contract']),'Frozen scene unchanged except exact floor slot zero')
    ins=req(unreal.load_asset(MI),'Actual floor instance');m=req(unreal.load_asset(MAT),'Actual parent material')
    req(component.get_material(0)==ins,'Floor actual slot zero points to own instance')
    req(ins.get_editor_property('parent')==m,'Actual instance parent')
    req(unreal.SystemLibrary.get_console_variable_int_value('r.Substrate')==0,'Actual standard PBR baseline remains unchanged')
    req(MEL.get_material_property_input_node(m,unreal.MaterialProperty.MP_FRONT_MATERIAL) is None,'No unused Substrate root')
    graph_inputs={}
    for prop,param,output,spec in [(unreal.MaterialProperty.MP_BASE_COLOR,'BaseColor','RGB',SPECS[0]),
        (unreal.MaterialProperty.MP_NORMAL,'NormalDX','RGB',SPECS[1]),
        (unreal.MaterialProperty.MP_ROUGHNESS,'ARM','G',SPECS[2]),
        (unreal.MaterialProperty.MP_AMBIENT_OCCLUSION,'ARM','R',SPECS[2])]:
        node=req(MEL.get_material_property_input_node(m,prop),'Actual active PBR root '+enum_name(prop))
        actual_output=MEL.get_material_property_input_node_output_name(m,prop)
        req(str(node.get_editor_property('parameter_name'))==param and actual_output==output,'Actual PBR channel '+param+'/'+output)
        req(path(node.get_editor_property('texture'))==BASE+'Textures/'+spec[0]+'.'+spec[0],'Exact active root texture')
        req(enum_name(node.get_editor_property('sampler_type'))==spec[4],'Actual sample interpretation')
        graph_inputs[enum_name(prop)]=dict(node=path(node),output=actual_output,texture=path(node.get_editor_property('texture')))
    for prop,expected in [(unreal.MaterialProperty.MP_METALLIC,0.),(unreal.MaterialProperty.MP_SPECULAR,.5)]:
        constant=req(MEL.get_material_property_input_node(m,prop),'Explicit dielectric property')
        req(constant.get_class().get_name()=='MaterialExpressionConstant' and constant.get_editor_property('r')==expected,'Actual nonmetal dielectric value')
    for spec in SPECS:
        tex=req(unreal.load_asset(BASE+'Textures/'+spec[0]),'Cold texture load')
        dimensions=[tex.blueprint_get_size_x(),tex.blueprint_get_size_y()]
        req(dimensions==[2048,2048],'Actual texture dimensions 2048 square')
        req(tex.get_editor_property('srgb')==spec[2] and enum_name(tex.get_editor_property('compression_settings'))==spec[3],'Actual color/compression '+spec[0])
        req(MEL.get_material_instance_texture_parameter_value(ins,spec[5])==tex,'Actual instance inherited texture '+spec[5])
        R.setdefault('textures',[]).append(dict(package=BASE+'Textures/'+spec[0],dimensions=dimensions,srgb=tex.get_editor_property('srgb'),compression=enum_name(tex.get_editor_property('compression_settings')),source_sha256=spec[6]))
    errors=list(MEL.recompile_material(m));req(not errors,'Cold compile without shader errors: '+str(errors))
    actual=dict(root_bsdf='StandardPBR',substrate_enabled=False,standard_pbr_verified=True,opaque=m.get_editor_property('blend_mode')==unreal.BlendMode.BLEND_OPAQUE,
        two_sided=m.get_editor_property('two_sided'),normal_tangent_space=m.get_editor_property('tangent_space_normal'),
        tiling_u=MEL.get_material_instance_scalar_parameter_value(ins,'TilingU'),tiling_v=MEL.get_material_instance_scalar_parameter_value(ins,'TilingV'),
        instance_parent=path(ins.get_editor_property('parent')),floor_slot0=path(component.get_material(0)))
    req(actual['opaque'] and not actual['two_sided'] and actual['normal_tangent_space'],'Opaque single-sided tangent-space material')
    req(actual['tiling_u']==12. and actual['tiling_v']==9.,'Measured floor sample tiling')
    R.update(source_contract_preserved=True,floor_material_only=True,shader_errors=errors,materials=actual,graph_inputs=graph_inputs,scene_contract=contract,floor_bounds=bounds,actor_count=len(actors),
        render_settings=dict(substrate_cvar=unreal.SystemLibrary.get_console_variable_int_value('r.Substrate'),
        use_material_attributes=m.get_editor_property('use_material_attributes'),
        front_material_root=path(MEL.get_material_property_input_node(m,unreal.MaterialProperty.MP_FRONT_MATERIAL)),
        legacy_base_color_root=path(MEL.get_material_property_input_node(m,unreal.MaterialProperty.MP_BASE_COLOR)),
        legacy_normal_root=path(MEL.get_material_property_input_node(m,unreal.MaterialProperty.MP_NORMAL)),
        legacy_roughness_root=path(MEL.get_material_property_input_node(m,unreal.MaterialProperty.MP_ROUGHNESS)),
        ambient_occlusion_root=path(MEL.get_material_property_input_node(m,unreal.MaterialProperty.MP_AMBIENT_OCCLUSION))))
try:
    req(PHASE in ('probe','create','repair','verify'),'Exact bounded phase');protect()
    req(unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).load_level(MAP),'Load only current Dev map')
    if PHASE=='probe': probe()
    else:
        with open(os.environ['DY_READABILITY_PROBE'],encoding='utf-8-sig') as stream: probe_data=json.load(stream)
        if PHASE=='create':create(probe_data)
        if PHASE=='repair':repair()
        verify(probe_data)
    protect();R['success']=True
except Exception:
    R['error']=traceback.format_exc();unreal.log_error(R['error'])
finally:
    with open(OUT,'x',encoding='utf-8') as stream:json.dump(R,stream,ensure_ascii=False,indent=2)
