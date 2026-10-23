
import unreal, json, traceback
out = {}
try:
    m = unreal.load_asset('/Game/DengYingShanHai/Dev/ForestCanopyM04/Meshes/SM_DY_M04_Canopy_A_v04')
    slots = []
    for i in range(m.get_num_sections(0) if hasattr(m, 'get_num_sections') else 0):
        pass
    mats = m.get_editor_property('static_materials')
    for s in mats:
        mt = s.get_editor_property('material_interface')
        slots.append(mt.get_path_name() if mt else None)
    out['canopy_slots'] = slots
    b = unreal.load_asset('/Game/DengYingShanHai/Dev/ForestArt/Meshes/SM_DY_ForestBranch_Tapered')
    out['branch_slots'] = [ (s.get_editor_property('material_interface').get_path_name() if s.get_editor_property('material_interface') else None) for s in b.get_editor_property('static_materials')]
    mat = unreal.load_asset('/Game/DengYingShanHai/Dev/ForestCanopyM04/Materials/M_DY_M04_CanopyConstantPBR')
    mel = unreal.MaterialEditingLibrary
    out['vector_params'] = [str(x) for x in mel.get_vector_parameter_names(mat)]
    out['scalar_params'] = [str(x) for x in mel.get_scalar_parameter_names(mat)]
    out['texture_params'] = [str(x) for x in mel.get_texture_parameter_names(mat)]
    out['ok'] = True
except Exception as exc:
    out['ok'] = False
    out['error'] = str(exc)
    out['trace'] = traceback.format_exc()
print('CANOPY_PROBE ' + json.dumps(out))
try:
    unreal.SystemLibrary.quit_editor()
except Exception:
    pass
