# -*- coding: utf-8 -*-
"""Cold verification of the Run4 production cast: transforms, poses, eyelid, textures, material usage."""
import unreal, json, traceback
BASE = '/Game/DengYingShanHai/Puppets'
OUT = 'D:/灯影山海/Saved/Audit-2026-10-22-FourAct'
R = {'ok': False, 'checks': [], 'errors': [], 'figures': [], 'poses': [], 'textures': [], 'materials': []}

def check(cond, label):
    R['checks'].append({'label': label, 'ok': bool(cond)})
    if not cond:
        raise AssertionError(label)

try:
    A = unreal.EditorAssetLibrary
    M = unreal.MaterialEditingLibrary
    Al = unreal.AnimationLibrary
    da = A.load_asset(BASE + '/DA_DYPuppetCast')
    check(isinstance(da, unreal.DYPuppetCastData), 'cast asset is DYPuppetCastData')
    figs = da.get_editor_property('figures')
    check(len(figs) == 4, 'cast holds four chapters')
    for i in range(len(figs)):
        f = figs[i]
        loc = f.mesh_relative_location
        rot = f.mesh_relative_rotation
        scl = f.mesh_relative_scale
        row = dict(label=str(f.label), mesh=f.skeletal_mesh.get_path_name() if f.skeletal_mesh else None,
                   loc=[round(v, 2) for v in (loc.x, loc.y, loc.z)],
                   rot=[round(v, 2) for v in (rot.pitch, rot.yaw, rot.roll)],
                   scale=round(scl.x, 3), hide_staff=f.hide_staff,
                   poses=sorted(str(k) for k in dict(f.pose_animations).keys()))
        check(row['label'] in ('夸父', '精卫', '刑天', '烛龙'), 'entry label %d' % i)
        check(row['loc'] == [0.0, -42.44, -104.57], 'entry %d location' % i)
        check(row['rot'] == [0.0, 180.0, 0.0], 'entry %d yaw 180' % i)
        check(abs(row['scale'] - (0.8 if i == 0 else 1.1)) < 0.001, 'entry %d scale' % i)
        if i == 0:
            check(f.hide_staff is False and not row['poses'], 'kuafu keeps blueprint staff, no baked clips')
        else:
            check(f.hide_staff is True and len(row['poses']) == 4, 'cast entry %d has four pose clips' % i)
        R['figures'].append(row)

    # Every baked clip must evaluate, and each character's key bone must move between poses.
    anims = {'Jingwei': ('WingL_Upper', ['Rest', 'Flight', 'Reach']),
             'Xingtian': ('Arm_L_Upper', ['Rest', 'Guard', 'Reach']),
             'Zhulong': ('Eyelid', ['Rest', 'Day', 'Night', 'Reach'])}
    for ident, (bone, poses) in anims.items():
        seen = []
        for pose in poses:
            anim = A.load_asset(BASE + '/Animations/A_DY_' + ident + '_' + pose)
            check(isinstance(anim, unreal.AnimSequence), 'anim %s %s' % (ident, pose))
            check(abs(anim.get_play_length() - 1.0) < 0.01, 'anim %s %s is 1s' % (ident, pose))
            tr = Al.get_bone_pose_for_frame(anim, bone, 0, False)
            row = dict(id=ident, pose=pose, bone=bone,
                       rot=[round(v, 4) for v in (tr.rotation.x, tr.rotation.y, tr.rotation.z, tr.rotation.w)],
                       scale=round(tr.scale3d.x, 4))
            seen.append(row)
            R['poses'].append(row)
        if ident != 'Zhulong':
            check(len({tuple(r['rot']) for r in seen}) == len(seen), '%s poses differ on %s' % (ident, bone))
        else:
            night = [r for r in seen if r['pose'] == 'Night'][0]
            day = [r for r in seen if r['pose'] == 'Day'][0]
            check(abs(night['scale'] - 1.0) < 0.001, 'zhulong night keeps eyelid open')
            check(abs(day['scale'] - 0.0001) < 0.001, 'zhulong day closes eyelid')

    # Textures imported for the 4K pass stay resident and stream-free.
    for p in A.list_assets(BASE + '/Textures', True, False):
        if p.endswith(('BaseColor', 'ClosedBaseColor')):
            t = A.load_asset(p)
            check(t.get_editor_property('never_stream'), 'texture resident ' + p)
            R['textures'].append({'path': p, 'width': t.blueprint_get_size_x(), 'never_stream': True})

    # Every material or instance used by the cast keeps skeletal mesh usage.
    usage = unreal.MaterialUsage.MATUSAGE_SKELETAL_MESH
    for p in A.list_assets(BASE + '/Materials', True, False):
        m = A.load_asset(p)
        if isinstance(m, unreal.MaterialInstanceConstant):
            has = M.has_material_usage(m, usage)
            check(has, 'skeletal usage ' + p)
            R['materials'].append({'instance': p, 'skeletal_usage': bool(has)})
    R['ok'] = all(c['ok'] for c in R['checks'])
except Exception:
    R['errors'].append(traceback.format_exc())
    R['ok'] = False
finally:
    with open(OUT + '/run4-verify.json', 'w', encoding='utf-8') as f:
        json.dump(R, f, ensure_ascii=False, indent=2, default=str)
    print('RUN4_VERIFY', R['ok'], len(R['checks']), len(R['errors']), (R['errors'][0][-300:] if R['errors'] else ''))
    unreal.SystemLibrary.quit_editor()
