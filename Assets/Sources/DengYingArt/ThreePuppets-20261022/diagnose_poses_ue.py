import unreal,json,traceback
BASE='/Game/DengYingShanHai/Dev/ThreePuppets_20261022'
report={'ok':False,'rows':[]}
try:
 for k,bone in [('Jingwei','WingUpper_L'),('Xingtian','UpperArm_L'),('Zhulong','Eyelid')]:
  for pose in {'Jingwei':['Rest','Flight'],'Xingtian':['Rest','Guard'],'Zhulong':['Day','Night']}[k]:
   anim=unreal.EditorAssetLibrary.load_asset(BASE+'/Animations/A_DY_'+k+'_'+pose)
   row={'id':k,'pose':pose,'animation':anim.get_path_name()}
   try:row['bone_pose']=str(unreal.AnimationLibrary.get_bone_pose_for_time(anim,bone,.5,False))
   except:row['pose_error']=traceback.format_exc()
   report['rows'].append(row)
 report['ok']=True
except:report['error']=traceback.format_exc()
with open('D:/灯影山海/Saved/Audit-2026-10-22-ThreePuppets/UE-Pose-Diagnostic.json','w',encoding='utf8')as f:json.dump(report,f,ensure_ascii=False,indent=2)