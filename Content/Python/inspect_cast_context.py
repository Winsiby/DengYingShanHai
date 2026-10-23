# -*- coding: utf-8 -*-
import unreal, json, os, traceback
OUT = r'D:/灯影山海/Saved/Audit-2026-10-22-FourAct'
R = {}
try:
    os.makedirs(OUT, exist_ok=True)
    unreal.EditorLoadingAndSavingUtils.load_map('/Game/DengYingShanHai/Maps/L_DY_Main')
    actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
    def v(x): return [round(float(x.x),2), round(float(x.y),2), round(float(x.z),2)]
    def r(x): return [round(float(x.pitch),2), round(float(x.yaw),2), round(float(x.roll),2)]
    puppet = next(a for a in actors if a.get_class().get_name() == 'BP_DYKuafuPuppet_Fitted_C')
    rows = []
    for c in puppet.get_components_by_class(unreal.SceneComponent):
        rows.append(dict(name=c.get_name(), cls=c.get_class().get_name(),
                         rel_loc=v(c.get_editor_property('relative_location')),
                         rel_rot=r(c.get_editor_property('relative_rotation')),
                         rel_scale=v(c.get_editor_property('relative_scale3d')),
                         vis=c.is_visible()))
    R['components'] = rows
    ar = unreal.AssetRegistryHelpers.get_asset_registry()
    R['kuafu_anims'] = sorted(str(x.asset_name) for x in ar.get_assets_by_path('/Game/DengYingShanHai/Dev/KuafuAppearance', True)
                              if 'AnimSequence' in str(x.asset_class_path.asset_name))
    R['cast_class'] = hasattr(unreal, 'DYPuppetCastData')
    R['entry_struct'] = hasattr(unreal, 'DYPuppetFigureEntry')
    R['ok'] = True
except Exception:
    R['error'] = traceback.format_exc()
finally:
    with open(OUT + '/cast-context.json', 'w', encoding='utf-8') as f:
        json.dump(R, f, ensure_ascii=False, indent=2)
    print('CAST_CONTEXT_DONE', R.get('ok'))
    unreal.SystemLibrary.quit_editor()
