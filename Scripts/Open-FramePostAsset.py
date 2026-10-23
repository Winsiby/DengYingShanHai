"""Open the admitted Dev mesh in UE's native asset viewer; never save or edit."""
import hashlib
import json
import os
import traceback
import unreal

ROOT = os.path.realpath(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir()))
AUDIT = os.path.join(ROOT, 'Saved', 'Audit-2026-10-12-FramePostAsset')
OUT = os.environ['DY_POST_REVIEW_OUT']
R = dict(success=False, map_saved=False, assets_saved=[], game_started=False,
         scale_changed=False, visual_quality_accepted=False)

def sha(filename):
    value = hashlib.sha256()
    with open(filename, 'rb') as stream:
        for block in iter(lambda: stream.read(1048576), b''):
            value.update(block)
    return value.hexdigest().upper()

try:
    assert os.path.commonpath([os.path.abspath(OUT),AUDIT]) == AUDIT
    with open(os.path.join(AUDIT,'OWN-ASSETS.json'), encoding='utf-8-sig') as stream:
        rows = json.load(stream)
    expected = {
        'Content\\DengYingShanHai\\Dev\\FramePostAsset\\Meshes\\SM_DY_FramePost_Source.uasset',
        'Content\\DengYingShanHai\\Dev\\FramePostAsset\\Materials\\M_DY_FramePost_Master.uasset',
        'Content\\DengYingShanHai\\Dev\\FramePostAsset\\Materials\\MI_DY_FramePost_Wood.uasset',
        'Content\\DengYingShanHai\\Dev\\FramePostAsset\\Materials\\MI_DY_FramePost_Base.uasset',
        'Content\\DengYingShanHai\\Dev\\FramePostAsset\\Textures\\T_DY_FramePost_BaseColor.uasset',
        'Content\\DengYingShanHai\\Dev\\FramePostAsset\\Textures\\T_DY_FramePost_NormalDX.uasset',
        'Content\\DengYingShanHai\\Dev\\FramePostAsset\\Textures\\T_DY_FramePost_ARM.uasset',
    }
    assert len(rows) == 7 and {row['Relative'] for row in rows} == expected
    for row in rows:
        target = os.path.abspath(os.path.join(ROOT,row['Relative']))
        assert os.path.commonpath([target,ROOT]) == ROOT
        assert sha(target) == row['SHA256']
    mesh = unreal.load_asset('/Game/DengYingShanHai/Dev/FramePostAsset/Meshes/SM_DY_FramePost_Source')
    assert mesh is not None and mesh.get_num_triangles(0) == 252
    unreal.EditorPythonScripting.set_keep_python_script_alive(True)
    assert unreal.EditorPythonScripting.get_keep_python_script_alive()
    assert unreal.get_editor_subsystem(unreal.AssetEditorSubsystem).open_editor_for_assets([mesh])
    R.update(success=True, object_path=mesh.get_path_name(),
             keep_alive=True, viewer='Native Static Mesh Editor', source_height_cm=2036.121966123581)
    unreal.log('DY FramePost review: one native mesh viewer, not a game or final scale.')
except Exception:
    R['error'] = traceback.format_exc()
    unreal.log_error(R['error'])
    unreal.EditorPythonScripting.set_keep_python_script_alive(False)
finally:
    with open(OUT, 'x', encoding='utf-8') as stream:
        json.dump(R, stream, ensure_ascii=False, indent=2)
