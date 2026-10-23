# -*- coding: utf-8 -*-
import unreal,json,traceback,math,hashlib
ROOT='D:/灯影山海/Saved/Audit-2026-10-22-B2WallPolish'
SOURCE='D:/灯影山海/Assets/Sources/DengYingArt/B2-TreePolish-20261022'
MAP='/Game/DengYingShanHai/Dev/B2WallPolish_20261022/L_B2Wall_Candidate'
DEST='/Game/DengYingShanHai/Dev/B2WallPolish_20261022'
r={'ok':False,'crowns':[],'hidden_satellites':[],'grafts':[],'imports':[]}
def vec(v):return [round(float(v.x),5),round(float(v.y),5),round(float(v.z),5)]
def transform(a):
 rot=a.get_actor_rotation()
 return [vec(a.get_actor_location()),[rot.pitch,rot.yaw,rot.roll],vec(a.get_actor_scale3d())]
def component_state(a):
 c=a.get_component_by_class(unreal.StaticMeshComponent)
 return {'collision':str(c.get_collision_enabled()),'shadow':c.get_editor_property('cast_shadow')} if c else None
def sphere_data(mesh):
 body=mesh.get_editor_property('body_setup')
 agg=body.get_editor_property('agg_geom')
 spheres=list(agg.get_editor_property('sphere_elems'))
 return {'spheres':[{'center':vec(x.get_editor_property('center')),'radius':x.get_editor_property('radius')}for x in spheres],
 'boxes':len(agg.get_editor_property('box_elems')),'capsules':len(agg.get_editor_property('sphyl_elems')),
 'convex':len(agg.get_editor_property('convex_elems')),'trace':str(body.get_editor_property('collision_trace_flag'))}
try:
 manifest=json.load(open(SOURCE+'/SOURCE_MANIFEST.json',encoding='utf8'))
 pairs=manifest['placement_recommendations']['verified_main_crown_pairs']
 satellites=manifest['placement_recommendations']['hide_satellite_labels_exact']
 assert len(pairs)==46 and len(satellites)==282
 unreal.EditorLoadingAndSavingUtils.load_map(MAP)
 eas=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);eal=unreal.EditorAssetLibrary
 mel=unreal.MaterialEditingLibrary;tools=unreal.AssetToolsHelpers.get_asset_tools()
 actors=list(eas.get_all_level_actors());by={a.get_actor_label():a for a in actors}
 assert len(actors)==1577
 before={label:transform(a) for label,a in by.items()};before_components={label:component_state(a) for label,a in by.items()}
 sphere=eal.load_asset('/Engine/BasicShapes/Sphere')
 source_collision=sphere_data(sphere);r['original_collision']=source_collision
 assert len(source_collision['spheres'])==1 and source_collision['boxes']==source_collision['capsules']==source_collision['convex']==0,source_collision
 bark=eal.load_asset(DEST+'/Materials/MI_DY_BranchBark')
 if bark is None:
  bark=tools.create_asset('MI_DY_BranchBark',DEST+'/Materials',unreal.MaterialInstanceConstant,unreal.MaterialInstanceConstantFactoryNew())
  parent=eal.load_asset('/Game/DengYingShanHai/Dev/StageFrameM03/Materials/M_DY_M03_FrameConstantPBR')
  assert parent
  mel.set_material_instance_parent(bark,parent)
  mel.set_material_instance_vector_parameter_value(bark,'BaseColor',unreal.LinearColor(0.18,0.12,0.075,1))
  mel.set_material_instance_scalar_parameter_value(bark,'Roughness',0.92)
  mel.set_material_instance_scalar_parameter_value(bark,'Metallic',0.0)
  assert eal.save_loaded_asset(bark,False)
 meshes=[]
 expected=['0E35374028FC74FCC0C2C0CED6D322E9915B1E02A1E50971B8CC669F3EFDFAC7','1090424F62071EEA0181744456E9E0F9888597457455B25BB0E4273FA79C2D6F']
 world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
 unreal.SystemLibrary.execute_console_command(world,'Interchange.FeatureFlags.Import.OBJ 0')
 for i,item in enumerate(manifest['candidates']):
  path=item['obj'];assert hashlib.sha256(open(path,'rb').read()).hexdigest().upper()==expected[i]
  name='SM_DY_BranchCrown_'+('A' if i==0 else 'B')+'_Unit100'
  mesh=eal.load_asset(DEST+'/Meshes/'+name)
  if mesh is None:
   opt=unreal.FbxImportUI()
   opt.set_editor_properties(dict(mesh_type_to_import=unreal.FBXImportType.FBXIT_STATIC_MESH,import_as_skeletal=False,import_mesh=True,import_animations=False,import_materials=False,import_textures=False,automated_import_should_detect_type=False,override_full_name=True))
   opt.get_editor_property('static_mesh_import_data').set_editor_properties(dict(combine_meshes=True,auto_generate_collision=False,build_nanite=False,generate_lightmap_u_vs=False,convert_scene=False,convert_scene_unit=False,force_front_x_axis=False,import_uniform_scale=1.0,transform_vertex_to_absolute=True,bake_pivot_in_vertex=False,normal_import_method=unreal.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS))
   t=unreal.AssetImportTask();t.set_editor_properties(dict(filename=path,destination_path=DEST+'/Meshes',destination_name=name,factory=unreal.FbxFactory(),options=opt,automated=True,replace_existing=False,save=False))
   tools.import_asset_tasks([t]);mesh=eal.load_asset(DEST+'/Meshes/'+name)
  assert mesh
  bounds=mesh.get_bounds()
  assert all(abs(x)<0.02 for x in vec(bounds.origin))
  assert all(abs(x-50)<0.02 for x in vec(bounds.box_extent))
  mesh.set_material(0,bark)
  body=mesh.get_editor_property('body_setup');old_body=sphere.get_editor_property('body_setup')
  body.set_editor_property('agg_geom',old_body.get_editor_property('agg_geom'))
  body.set_editor_property('collision_trace_flag',old_body.get_editor_property('collision_trace_flag'))
  mesh.set_editor_property('generate_mesh_distance_field',False)
  assert sphere_data(mesh)==source_collision
  assert eal.save_loaded_asset(mesh,False)
  meshes.append(mesh);r['imports'].append({'asset':mesh.get_path_name(),'collision':sphere_data(mesh),'triangles':item['checks']['triangles']})
 cylinder=eal.load_asset('/Engine/BasicShapes/Cylinder')
 for i,pair in enumerate(pairs):
  label=pair['crown'];a=by[label];trunk=by[pair['trunk']]
  c=a.get_component_by_class(unreal.StaticMeshComponent)
  assert c.get_editor_property('static_mesh').get_path_name()=='/Engine/BasicShapes/Sphere.Sphere',label
  index=i%2;mesh=meshes[index]
  assert c.set_static_mesh(mesh)
  c.set_material(0,bark)
  tc=trunk.get_component_by_class(unreal.StaticMeshComponent);tc.set_material(0,bark)
  root_local=unreal.Vector(*manifest['candidates'][index]['root_base_center_cm'])
  root_world=unreal.MathLibrary.transform_location(a.get_actor_transform(),root_local)
  center,extent=trunk.get_actor_bounds(False)
  top=center.z+extent.z
  gap=root_world.z-top
  item={'label':label,'trunk':pair['trunk'],'asset':mesh.get_path_name(),'root_world':vec(root_world),'trunk_top':top,'gap_cm':gap}
  if gap>0.4:
   p0=unreal.Vector(center.x,center.y,top-4)
   p1=unreal.Vector(root_world.x,root_world.y,root_world.z+4)
   d=p1-p0;length=math.sqrt(d.x*d.x+d.y*d.y+d.z*d.z)
   radius=min(extent.x,extent.y,6.5*min(a.get_actor_scale3d().x,a.get_actor_scale3d().y))*0.92
   graft=eas.spawn_actor_from_class(unreal.StaticMeshActor,(p0+p1)*0.5)
   graft.set_actor_label('ART_Polish_B2_Graft_'+str(i).zfill(2))
   gc=graft.get_component_by_class(unreal.StaticMeshComponent);gc.set_static_mesh(cylinder);gc.set_material(0,bark);gc.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION);gc.set_mobility(unreal.ComponentMobility.STATIC);gc.set_cast_shadow(True)
   graft.set_actor_rotation(unreal.MathLibrary.make_rot_from_z(d),False);graft.set_actor_scale3d(unreal.Vector(radius/50,radius/50,length/100))
   r['grafts'].append({'label':graft.get_actor_label(),'crown':label,'start':vec(p0),'end':vec(p1),'length_cm':length,'radius_cm':radius,'collision':'NO_COLLISION'})
   item['gap_repaired']=True
  else:item['gap_repaired']='original overlap retained'
  r['crowns'].append(item)
 for label in satellites:
  a=by[label];c=a.get_component_by_class(unreal.StaticMeshComponent)
  assert c.get_editor_property('static_mesh').get_path_name()=='/Engine/BasicShapes/Sphere.Sphere'
  a.set_actor_hidden_in_game(True);c.set_visibility(False,False);r['hidden_satellites'].append(label)
 # Minimal seat joins the existing plaque (front x902) to the A1 top rail (x930).
 seat=eas.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(916,0,830))
 seat.set_actor_label('ART_Polish_PlaqueSeat')
 sc=seat.get_component_by_class(unreal.StaticMeshComponent);sc.set_static_mesh(eal.load_asset('/Engine/BasicShapes/Cube'));sc.set_material(0,eal.load_asset('/Game/DengYingShanHai/Dev/FramePostAsset/Materials/MI_DY_FramePost_Wood'));sc.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION);sc.set_cast_shadow(False);sc.set_mobility(unreal.ComponentMobility.STATIC)
 seat.set_actor_scale3d(unreal.Vector(0.34,3.9,0.12))
 assert all(transform(a)==before[label] for label,a in by.items())
 assert all(component_state(a)==before_components[label] for label,a in by.items()),'Existing collision flags or cast shadow changed'
 assert unreal.EditorLoadingAndSavingUtils.save_map(world,MAP)
 unreal.EditorLoadingAndSavingUtils.load_map(MAP)
 loaded={a.get_actor_label():a for a in eas.get_all_level_actors()}
 assert all(transform(loaded[label])==v for label,v in before.items())
 assert all(component_state(loaded[label])==v for label,v in before_components.items())
 for i,pair in enumerate(pairs):
  c=loaded[pair['crown']].get_component_by_class(unreal.StaticMeshComponent)
  assert sphere_data(c.get_editor_property('static_mesh'))==source_collision,'Saved collision mismatch'
  assert c.get_editor_property('static_mesh').get_name()==meshes[i%2].get_name()
 assert len(loaded)==1577+len(r['grafts'])+1
 r['actor_count']=len(loaded);r['existing_actor_transforms_preserved']=True;r['existing_collision_preserved']=True;r['ok']=True
except:r['error']=traceback.format_exc()
with open(ROOT+'/Trees-Candidate.json','w',encoding='utf8')as f:json.dump(r,f,indent=2,ensure_ascii=False)
unreal.SystemLibrary.quit_editor()
