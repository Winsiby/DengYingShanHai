
import unreal
p='/Game/DengYingShanHai/Dev/M3/Forest/BP_DYForestPresentation_Dev'
try:
    a=unreal.load_asset(p)
    print('LOADED', a.get_name(), a.get_path_name())
    cd=a.get_default_object()
    print('CDO', cd.get_name(), len(cd.get_editor_property('branch_layout')) if hasattr(cd,'get_editor_property') else 'na')
except Exception as e:
    print('LOADFAIL', repr(e))
print('PROBE_DONE')
