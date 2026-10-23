# -*- coding: utf-8 -*-
import unreal,json,traceback,os
ROOT='D:/灯影山海/Saved/Audit-2026-10-22-B2WallPolish'
BASE='/Game/DengYingShanHai/Maps/L_DY_Main'
CANDIDATE='/Game/DengYingShanHai/Dev/B2WallPolish_20261022/L_B2Wall_Candidate'
DEST='/Game/DengYingShanHai/Dev/B2WallPolish_20261022/Materials'
r={'ok':False,'walls':[],'hidden_frames':[]}
def vec(v):return [round(float(v.x),5),round(float(v.y),5),round(float(v.z),5)]
def state(a):
 rot=a.get_actor_rotation()
 cs=[]
 for c in a.get_components_by_class(unreal.StaticMeshComponent):
  cs.append({'mesh':c.get_editor_property('static_mesh').get_path_name(),'collision':str(c.get_collision_enabled()),'shadow':c.get_editor_property('cast_shadow')})
 return {'loc':vec(a.get_actor_location()),'rot':[rot.pitch,rot.yaw,rot.roll],'scale':vec(a.get_actor_scale3d()),'components':cs}
try:
 unreal.EditorLoadingAndSavingUtils.load_map(BASE)
 eas=unreal.get_editor_subsystem(unreal.EditorActorSubsystem);eal=unreal.EditorAssetLibrary;mel=unreal.MaterialEditingLibrary
 actors=eas.get_all_level_actors();by={a.get_actor_label():a for a in actors}
 before={a.get_actor_label():state(a) for a in actors}
 tools=unreal.AssetToolsHelpers.get_asset_tools()
 master=eal.load_asset(DEST+'/M_DY_WallBands')
 if master is None:
  master=tools.create_asset('M_DY_WallBands',DEST,unreal.Material,unreal.MaterialFactoryNew())
  master.set_editor_properties(dict(blend_mode=unreal.BlendMode.BLEND_OPAQUE,shading_model=unreal.MaterialShadingModel.MSM_DEFAULT_LIT,material_domain=unreal.MaterialDomain.MD_SURFACE,two_sided=False))
  def expr(cls,x,y,**props):
   n=mel.create_material_expression(master,cls,x,y)
   for k,v in props.items():n.set_editor_property(k,v)
   return n
  def connect(a,b,p):assert mel.connect_material_expressions(a,'',b,'' if p=='Input' else p), str(mel.get_material_expression_input_names(b))
  def color(name,value,y):return expr(unreal.MaterialExpressionVectorParameter,-500,y,parameter_name=name,default_value=unreal.LinearColor(*value,1))
  def scalar(name,value,y):return expr(unreal.MaterialExpressionScalarParameter,-950,y,parameter_name=name,default_value=value)
  pos=expr(unreal.MaterialExpressionWorldPosition,-1300,-50)
  z=expr(unreal.MaterialExpressionComponentMask,-1100,-50,b=True,r=False,g=False,a=False);connect(pos,z,'Input')
  masks=[]
  for idx,(name,height) in enumerate((('BaseHeightCm',150.0),('TopHeightCm',1740.0))):
   y=idx*220
   h=scalar(name,height,y+100)
   sub=expr(unreal.MaterialExpressionSubtract,-720,y);connect(z,sub,'A');connect(h,sub,'B')
   div=expr(unreal.MaterialExpressionDivide,-550,y,const_b=4.0);connect(sub,div,'A')
   sat=expr(unreal.MaterialExpressionSaturate,-380,y);connect(div,sat,'Input');masks.append(sat)
  stone=color('StoneColor',(0.145,0.158,0.165),-400)
  plaster=color('PlasterColor',(0.53,0.50,0.43),-250)
  timber=color('TopTimberColor',(0.06,0.037,0.026),500)
  low=expr(unreal.MaterialExpressionLinearInterpolate,-100,-180);connect(stone,low,'A');connect(plaster,low,'B');connect(masks[0],low,'Alpha')
  top=expr(unreal.MaterialExpressionLinearInterpolate,130,-100);connect(low,top,'A');connect(timber,top,'B');connect(masks[1],top,'Alpha')
  assert mel.connect_material_property(top,'',unreal.MaterialProperty.MP_BASE_COLOR)
  for value,prop,y in ((0.94,unreal.MaterialProperty.MP_ROUGHNESS,300),(0.0,unreal.MaterialProperty.MP_METALLIC,400),(0.15,unreal.MaterialProperty.MP_SPECULAR,500)):
   n=expr(unreal.MaterialExpressionConstant,100,y,r=value);assert mel.connect_material_property(n,'',prop)
  mel.recompile_material(master)
  assert eal.save_loaded_asset(master,False)
 def mi(name,base,top):
  m=eal.load_asset(DEST+'/'+name)
  if m is None:
   m=tools.create_asset(name,DEST,unreal.MaterialInstanceConstant,unreal.MaterialInstanceConstantFactoryNew())
   mel.set_material_instance_parent(m,master)
   mel.set_material_instance_scalar_parameter_value(m,'BaseHeightCm',base)
   mel.set_material_instance_scalar_parameter_value(m,'TopHeightCm',top)
   assert eal.save_loaded_asset(m,False)
  return m
 theater=mi('MI_DY_TheaterWallBands',150,1740)
 corridor=mi('MI_DY_CorridorWallBands',60,380)
 wall_labels=['DYTheater_Wall_L','DYTheater_Wall_R','DYTheater_RearWall_L','DYTheater_RearWall_R','DYTheater_RearWall_Head','DYTheater_FrontWall_L','DYTheater_FrontWall_R','DYTheater_FrontWall_Head','M05_EntryWall_Left','M05_EntryWall_Right']
 for label in wall_labels:
  a=by[label];c=a.get_component_by_class(unreal.StaticMeshComponent)
  assert c.get_editor_property('static_mesh').get_path_name()=='/Engine/BasicShapes/Cube.Cube'
  old=c.get_material(0).get_path_name()
  c.set_material(0,corridor if label.startswith('M05_') else theater)
  r['walls'].append({'label':label,'old':old,'new':c.get_material(0).get_path_name()})
 # Only legacy no-collision, non-shadowing M03 presentation modules; keep A1 cloth frame and A2 structure.
 for label,a in by.items():
  if not label.startswith('M03_Frame'):continue
  c=a.get_component_by_class(unreal.StaticMeshComponent)
  assert c.get_collision_enabled()==unreal.CollisionEnabled.NO_COLLISION
  assert c.get_editor_property('cast_shadow')==False
  a.set_actor_hidden_in_game(True)
  for comp in a.get_components_by_class(unreal.StaticMeshComponent):comp.set_visibility(False,False)
  r['hidden_frames'].append(label)
 assert len(r['hidden_frames'])==18
 assert {a.get_actor_label():state(a) for a in actors}==before,'Transform/collision/mesh/shadow altered'
 world=unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
 assert unreal.EditorLoadingAndSavingUtils.save_map(world,CANDIDATE),'Candidate save failed'
 unreal.EditorLoadingAndSavingUtils.load_map(CANDIDATE)
 loaded={a.get_actor_label():a for a in eas.get_all_level_actors()}
 assert len(loaded)==len(before)==1577
 assert {a.get_actor_label():state(a) for a in loaded.values()}==before
 assert loaded['DEV_BackScreen'].get_component_by_class(unreal.StaticMeshComponent).get_material(0).get_name()=='MI_DY_ScreenCloth'
 assert all(loaded[label].get_editor_property('hidden') for label in r['hidden_frames'])
 r['actor_count']=len(loaded);r['candidate']=CANDIDATE;r['ok']=True
except:r['error']=traceback.format_exc()
with open(ROOT+'/Walls-Frames-Candidate.json','w',encoding='utf8')as f:json.dump(r,f,indent=2,ensure_ascii=False)
unreal.SystemLibrary.quit_editor()
