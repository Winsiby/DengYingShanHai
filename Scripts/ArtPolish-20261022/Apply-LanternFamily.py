# -*- coding: utf-8 -*-
"""Replace only eight A5 decoration meshes. No gameplay, light, exposure or actor-transform edits."""
import unreal, json, traceback, math, hashlib, os
ROOT='D:/灯影山海/Saved/Audit-2026-10-22-ArtPolish'
MAP='/Game/DengYingShanHai/Maps/L_DY_Main'
ASSET='/Game/DengYingShanHai/Dev/ArtPolish_20261022/Meshes/SM_DY_LanternFamily_Unit100'
SOURCE='D:/灯影山海/Assets/Sources/DengYingArt/A5-LanternFamily-20261022/SM_DY_LanternFamily_Unit100_v01.obj'
EXPECTED_SOURCE='B16817CCC97C05036069AD4F0C4D6D0B6F5DE8AEABBAD89B2435A4E5182D44EE'
TARGETS=['DYExt30_GateLamp_0','DYExt30_GateLamp_1','DYExt30_EaveLamp_00','DYExt30_EaveLamp_02','DYExt30_EaveLamp_05','DYExt30_RoofLamp_00','DYExt30_RoofLamp_02','DYExt30_RoofLamp_06']
MATERIALS={'Paper':'/Game/DengYingShanHai/Dev/WorldV2/Materials/MI_DY_LanternPaper',
'Wood':'/Game/DengYingShanHai/Dev/FramePostAsset/Materials/MI_DY_FramePost_Wood',
'Brass':'/Game/DengYingShanHai/Dev/KuafuAppearance/Materials/MI_DY_AgedBrass'}
report={'ok':False,'targets':TARGETS,'source':SOURCE,'map':MAP,'changed':[]}
def vec(v):return [round(float(v.x),5),round(float(v.y),5),round(float(v.z),5)]
def transform(a):
    r=a.get_actor_rotation()
    return {'location':vec(a.get_actor_location()),'rotation':[round(r.pitch,5),round(r.yaw,5),round(r.roll,5)],'scale':vec(a.get_actor_scale3d())}
def light_state(actors):
    result={}
    for a in actors:
        cs=a.get_components_by_class(unreal.LightComponent)
        if not cs:continue
        values=[]
        for c in cs:
            data={}
            for p in ('intensity','intensity_units','attenuation_radius','temperature','use_temperature','source_radius','specular_scale','use_inverse_squared_falloff','cast_shadows','mobility'):
                try:
                    v=c.get_editor_property(p); data[p]=v if isinstance(v,(int,float,bool,str)) else str(v)
                except Exception:pass
            color=c.get_editor_property('light_color'); data['light_color']=[color.r,color.g,color.b,color.a]
            values.append(data)
        result[a.get_actor_label()]={'transform':transform(a),'components':values}
    return result
try:
    assert hashlib.sha256(open(SOURCE,'rb').read()).hexdigest().upper()==EXPECTED_SOURCE,'Unexpected source revision'
    unreal.EditorLoadingAndSavingUtils.load_map(MAP)
    eas=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    actors=list(eas.get_all_level_actors())
    selected={a.get_actor_label():a for a in actors if a.get_actor_label() in TARGETS}
    assert len(selected)==8,'Exactly eight existing decorations required'
    before_transforms={a.get_actor_label():transform(a) for a in actors}
    before_lights=light_state(actors)
    before_components={}
    for label,a in selected.items():
        c=a.get_component_by_class(unreal.StaticMeshComponent)
        center,extent=a.get_actor_bounds(False)
        before_components[label]={'transform':transform(a),'center':vec(center),'extent':vec(extent),'collision':str(c.get_collision_enabled()),'cast_shadow':c.get_editor_property('cast_shadow'),'mesh':c.get_editor_property('static_mesh').get_path_name(),'materials':[c.get_material(i).get_path_name() if c.get_material(i) else None for i in range(c.get_num_materials())]}
        assert before_components[label]['mesh']=='/Engine/BasicShapes/Sphere.Sphere','Unexpected existing mesh'
    with open(ROOT+'/A5-before-targets.json','w',encoding='utf-8') as f:json.dump(before_components,f,ensure_ascii=False,indent=2)
    world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    tools=unreal.AssetToolsHelpers.get_asset_tools(); eal=unreal.EditorAssetLibrary
    mesh=eal.load_asset(ASSET) if eal.does_asset_exist(ASSET) else None
    if mesh is None:
        unreal.SystemLibrary.execute_console_command(world,'Interchange.FeatureFlags.Import.OBJ 0')
        assert unreal.SystemLibrary.get_console_variable_int_value('Interchange.FeatureFlags.Import.OBJ')==0
        options=unreal.FbxImportUI()
        options.set_editor_properties(dict(mesh_type_to_import=unreal.FBXImportType.FBXIT_STATIC_MESH,import_as_skeletal=False,import_mesh=True,import_animations=False,import_materials=False,import_textures=False,automated_import_should_detect_type=False,override_full_name=True))
        options.get_editor_property('static_mesh_import_data').set_editor_properties(dict(combine_meshes=True,auto_generate_collision=False,build_nanite=False,generate_lightmap_u_vs=False,convert_scene=False,convert_scene_unit=False,force_front_x_axis=False,import_uniform_scale=1.0,transform_vertex_to_absolute=True,bake_pivot_in_vertex=False,normal_import_method=unreal.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS))
        task=unreal.AssetImportTask()
        task.set_editor_properties(dict(filename=SOURCE,destination_path=ASSET.rsplit('/',1)[0],destination_name=ASSET.rsplit('/',1)[1],factory=unreal.FbxFactory(),options=options,automated=True,replace_existing=False,save=False))
        tools.import_asset_tasks([task])
        report['imported_paths']=list(task.get_editor_property('imported_object_paths'))
        mesh=eal.load_asset(ASSET)
    assert mesh is not None,'Static mesh import failed'
    bounds=mesh.get_bounds()
    report['mesh_bounds']={'origin':vec(bounds.origin),'extent':vec(bounds.box_extent)}
    assert all(abs(v)<0.01 for v in vec(bounds.origin)),'Mesh pivot shifted'
    assert all(abs(v-50)<0.01 for v in vec(bounds.box_extent)),'Mesh import changed axes/scale'
    slots=list(mesh.get_editor_property('static_materials'))
    assert len(slots)==3,'Exactly three material slots required'
    report['slots']=[]
    assigned={}
    for i,slot in enumerate(slots):
        slot_name=str(slot.get_editor_property('imported_material_slot_name'))
        matching=[name for name in MATERIALS if name.lower() in slot_name.lower()]
        assert len(matching)==1,'Unknown imported material slot: '+slot_name
        name=matching[0]; mat=eal.load_asset(MATERIALS[name])
        assert mat is not None
        mesh.set_material(i,mat); assigned[i]=mat
        report['slots'].append({'index':i,'imported_name':slot_name,'material':MATERIALS[name]})
    mesh.set_editor_property('generate_mesh_distance_field',False)
    assert eal.save_loaded_asset(mesh,False),'Could not save new static mesh'
    for label,a in selected.items():
        c=a.get_component_by_class(unreal.StaticMeshComponent)
        assert c.set_static_mesh(mesh),'Mesh replacement rejected'
        for i,mat in assigned.items():c.set_material(i,mat)
        assert transform(a)==before_components[label]['transform']
        assert str(c.get_collision_enabled())==before_components[label]['collision']
        assert c.get_editor_property('cast_shadow')==before_components[label]['cast_shadow']
        center,extent=a.get_actor_bounds(False)
        assert all(abs(x-y)<0.02 for x,y in zip(vec(center),before_components[label]['center'])),'World bounds center changed'
        assert all(abs(x-y)<0.02 for x,y in zip(vec(extent),before_components[label]['extent'])),'World bounds envelope changed'
        report['changed'].append(label)
    assert len(eas.get_all_level_actors())==len(actors),'Actor count changed'
    assert {a.get_actor_label():transform(a) for a in eas.get_all_level_actors()}==before_transforms,'Actor transform changed'
    assert light_state(eas.get_all_level_actors())==before_lights,'Light parameters changed'
    assert unreal.EditorLoadingAndSavingUtils.save_map(world,MAP),'Map save failed'
    assert unreal.EditorLevelLibrary.save_current_level(),'Second map save failed'
    unreal.EditorLoadingAndSavingUtils.load_map(MAP)
    reloaded={a.get_actor_label():a for a in eas.get_all_level_actors()}
    for label in TARGETS:
        c=reloaded[label].get_component_by_class(unreal.StaticMeshComponent)
        assert c.get_editor_property('static_mesh').get_path_name().split('.')[0]==ASSET,'Map reload lost assignment'
        assert transform(reloaded[label])==before_components[label]['transform']
    report['actor_count']=len(actors); report['light_count']=len(before_lights)
    report['preserved']=['all actor transforms','actor count','all light transforms and parameters','target collision and cast shadow','target world bounds','shared material assets','gameplay data']
    report['ok']=True
except Exception:report['error']=traceback.format_exc()
with open(ROOT+'/A5-Apply.json','w',encoding='utf-8') as f:json.dump(report,f,ensure_ascii=False,indent=2)
unreal.SystemLibrary.quit_editor()
