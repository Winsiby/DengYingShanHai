"""Read-only native UE mesh viewer; no PIE, saves, import or scene placement."""
import hashlib
import json
import os
import traceback
import unreal

ROOT=os.path.realpath(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir()))
AUDIT=os.path.join(ROOT,'Saved','Audit-2026-10-12-FrameBeamAsset')
OUT=os.environ['DY_BEAM_REVIEW_OUT']
R=dict(success=False,assets_saved=[],map_saved=False,game_started=False,scale_changed=False,visual_quality_accepted=False)
DEPS_EXPECTED={
    'Content\\DengYingShanHai\\Dev\\FramePostAsset\\'+name+'.uasset' for name in (
        'Materials\\MI_DY_FramePost_Wood','Materials\\M_DY_FramePost_Master',
        'Textures\\T_DY_FramePost_BaseColor','Textures\\T_DY_FramePost_NormalDX','Textures\\T_DY_FramePost_ARM')
}
def exact_dependencies(rows):
    return isinstance(rows,list) and len(rows)==5 and len({row['Relative'] for row in rows})==5 and {row['Relative'] for row in rows}==DEPS_EXPECTED
def sha(filename):
    digest=hashlib.sha256()
    with open(filename,'rb') as stream:
        for block in iter(lambda:stream.read(1048576),b''): digest.update(block)
    return digest.hexdigest().upper()
try:
    assert os.path.commonpath([os.path.abspath(OUT),AUDIT])==AUDIT and not os.path.exists(OUT)
    with open(os.path.join(AUDIT,'OWN-ASSET.json'),encoding='utf-8-sig') as stream: own=json.load(stream)
    with open(os.path.join(AUDIT,'DEPENDENCIES.json'),encoding='utf-8-sig') as stream: deps=json.load(stream)
    assert own['Status']=='PASS-ONLY-ONE-NEW-MESH' and own['File']['Relative']=='Content\\DengYingShanHai\\Dev\\FrameBeamAsset\\Meshes\\SM_DY_FrameBeam_Source.uasset'
    assert exact_dependencies(deps)
    for row in [own['File']]+deps:
        target=os.path.abspath(os.path.join(ROOT,row['Relative']))
        assert os.path.commonpath([ROOT,target])==ROOT and os.path.normcase(target)!=os.path.normcase(os.path.join(ROOT,'Docs','LICENSES.md'))
        assert sha(target)==row['SHA256']
    mesh=unreal.load_asset('/Game/DengYingShanHai/Dev/FrameBeamAsset/Meshes/SM_DY_FrameBeam_Source')
    assert mesh is not None and mesh.get_num_triangles(0)==28 and mesh.get_num_sections(0)==1
    assert mesh.get_material(0).get_path_name()=='/Game/DengYingShanHai/Dev/FramePostAsset/Materials/MI_DY_FramePost_Wood.MI_DY_FramePost_Wood'
    unreal.EditorPythonScripting.set_keep_python_script_alive(True)
    assert unreal.EditorPythonScripting.get_keep_python_script_alive()
    assert unreal.get_editor_subsystem(unreal.AssetEditorSubsystem).open_editor_for_assets([mesh])
    R.update(success=True,viewer='Native Static Mesh Editor',object_path=mesh.get_path_name(),triangles=28,source_length_cm=2630.546630859375,keep_alive=True)
except Exception:
    R['error']=traceback.format_exc();unreal.log_error(R['error'])
    unreal.EditorPythonScripting.set_keep_python_script_alive(False)
finally:
    with open(OUT,'x',encoding='utf-8') as stream: json.dump(R,stream,ensure_ascii=False,indent=2)
