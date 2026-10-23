# -*- coding: utf-8 -*-
import unreal,json,traceback
OUT='D:/灯影山海/Saved/Audit-2026-10-22-B2WallPolish'
r={'ok':False,'actors':[],'materials':{}}
def vec(v):return [round(float(v.x),4),round(float(v.y),4),round(float(v.z),4)]
def prop(o,n):
 try:
  x=o.get_editor_property(n)
  return x if isinstance(x,(str,int,float,bool,type(None))) else str(x)
 except:return None
try:
 unreal.EditorLoadingAndSavingUtils.load_map('/Game/DengYingShanHai/Maps/L_DY_Main')
 actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
 r['actor_count']=len(actors)
 mats={}
 for a in actors:
  label=a.get_actor_label();rot=a.get_actor_rotation()
  e={'label':label,'name':a.get_name(),'class':a.get_class().get_name(),'location':vec(a.get_actor_location()),'scale':vec(a.get_actor_scale3d()),'rotation':[rot.pitch,rot.yaw,rot.roll],'hidden':prop(a,'hidden'),'components':[]}
  center,extent=a.get_actor_bounds(False);e['center']=vec(center);e['extent']=vec(extent)
  for c in a.get_components_by_class(unreal.StaticMeshComponent):
   sm=c.get_editor_property('static_mesh');ms=[c.get_material(i) for i in range(c.get_num_materials())]
   e['components'].append({'name':c.get_name(),'mesh':sm.get_path_name() if sm else None,'materials':[m.get_path_name() if m else None for m in ms],'collision':str(c.get_collision_enabled()),'cast_shadow':prop(c,'cast_shadow'),'visible':prop(c,'visible'),'hidden_in_game':prop(c,'hidden_in_game'),'mobility':prop(c,'mobility')})
   for m in ms:
    if m:mats[m.get_path_name()]=m
  r['actors'].append(e)
 for p,m in mats.items():
  d={'class':m.get_class().get_name(),'parent':prop(m,'parent')}
  if isinstance(m,unreal.MaterialInstanceConstant):
   d['scalar_parameters']={}
   for n in unreal.MaterialEditingLibrary.get_scalar_parameter_names(m):
    d['scalar_parameters'][str(n)]=unreal.MaterialEditingLibrary.get_material_instance_scalar_parameter_value(m,n)
   d['vector_parameters']={}
   for n in unreal.MaterialEditingLibrary.get_vector_parameter_names(m):
    c=unreal.MaterialEditingLibrary.get_material_instance_vector_parameter_value(m,n)
    d['vector_parameters'][str(n)]=[c.r,c.g,c.b,c.a]
  r['materials'][p]=d
 r['ok']=True
except:r['error']=traceback.format_exc()
with open(OUT+'/scene-before.json','w',encoding='utf8') as f:json.dump(r,f,indent=2,ensure_ascii=False)
unreal.SystemLibrary.quit_editor()
