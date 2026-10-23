import unreal,json,sys,traceback,os
BASE='/Game/DengYingShanHai/Dev/ThreePuppets_20261022'
OUT='D:/灯影山海/Saved/Audit-2026-10-22-ThreePuppets'
fix=os.environ.get('DY_THREEPUPPETS_FIX')=='1'
r={'ok':False,'fix_mode':fix,'materials':[],'textures':[],'actors':[],'poses':[]}
try:
 usage=unreal.MaterialUsage.MATUSAGE_SKELETAL_MESH;M=unreal.MaterialEditingLibrary;A=unreal.EditorAssetLibrary
 for path in A.list_assets(BASE+'/Materials',True,False):
  m=A.load_asset(path)
  if m.get_name().endswith('_Screen'):continue
  if fix:
   if isinstance(m,unreal.Material):M.set_base_material_usage(m,usage,True);M.recompile_material(m)
   elif isinstance(m,unreal.MaterialInstanceConstant):M.set_material_usage_override(m,usage,True,True);M.update_material_instance(m)
   assert A.save_loaded_asset(m,False)
  assert M.has_material_usage(m,usage),path
  r['materials'].append({'path':path,'skeletal_usage':True})
 for path in A.list_assets(BASE+'/Textures',True,False):
  if path.endswith(('BaseColor','ClosedBaseColor')):
   tex=A.load_asset(path);assert tex.get_editor_property('never_stream');r['textures'].append({'path':path,'never_stream':True})
 unreal.EditorLoadingAndSavingUtils.load_map(BASE+'/L_ThreePuppetsReview')
 aa={a.get_actor_label():a for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()}
 for ident,count in [('Jingwei',17),('Xingtian',14),('Zhulong',8)]:
  c=aa['DYThreePuppets_'+ident].get_component_by_class(unreal.SkeletalMeshComponent)
  assert c.get_num_bones()==count
  assert c.get_editor_property('animation_data').get_editor_property('anim_to_play').get_name()=='A_DY_'+ident+'_Rest'
  r['actors'].append({'id':ident,'bones':count,'persisted_pose':'Rest'})
  names={'Jingwei':['Rest','Flight','Reach'],'Xingtian':['Rest','Guard','Reach'],'Zhulong':['Rest','Day','Night','Reach']}[ident]
  bone={'Jingwei':'WingL_Upper','Xingtian':'Arm_L_Upper','Zhulong':'Eyelid'}[ident]
  for pose in names:
   anim=A.load_asset(BASE+'/Animations/A_DY_'+ident+'_'+pose);assert isinstance(anim,unreal.AnimSequence)
   assert abs(anim.get_play_length()-1)<.01
   c.set_animation(anim);c.set_position(.5,False);c.override_animation_data(anim,False,False,.5,1)
   assert c.get_anim_instance().get_animation_asset()==anim
   tr=c.get_socket_transform(bone)
   row={'id':ident,'pose':pose,'evaluated_bone':bone,'rotation':[tr.rotation.x,tr.rotation.y,tr.rotation.z,tr.rotation.w],'scale':[tr.scale3d.x,tr.scale3d.y,tr.scale3d.z],'duration':anim.get_play_length()}
   r['poses'].append(row)
   if ident=='Zhulong':assert abs(tr.scale3d.x-(1 if pose=='Night' else .0001))<.001
  if ident!='Zhulong':
   rest=r['poses'][-3];second=r['poses'][-2]
   assert sum(abs(a-b)for a,b in zip(rest['rotation'],second['rotation']))>.01
 assert len(r['poses'])==10 and len(r['textures'])==4
 r['ok']=True;r['formal_integration']=False;r['human_art_acceptance']=False
except:r['error']=traceback.format_exc()
with open(OUT+('/UE-FinalAssetFix.json' if fix else '/UE-ColdReload-Final.json'),'w',encoding='utf8')as f:json.dump(r,f,ensure_ascii=False,indent=2)
assert r['ok'],r.get('error')