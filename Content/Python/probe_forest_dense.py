
import unreal, json, traceback
out = {}
try:
    les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    les.load_level("/Game/DengYingShanHai/Maps/L_DY_Main")
    eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    forest = None
    screen = None
    line = None
    for a in eas.get_all_level_actors():
        lbl = a.get_actor_label()
        if lbl == "M3_RuntimeForest":
            forest = a
        if "BackScreen" in lbl or lbl == "DEV_BackScreen":
            screen = a
        if "NarrativeGroundLine" in lbl:
            line = a
    if forest is None:
        raise RuntimeError("forest actor missing")
    out["class"] = forest.get_class().get_name()
    t = forest.get_actor_transform()
    out["actor_loc"] = [t.translation.x, t.translation.y, t.translation.z]
    def mesh_info(m):
        if not m: return None
        b = m.get_bounds()
        return {
            "path": m.get_path_name(),
            "origin": [b.origin.x, b.origin.y, b.origin.z],
            "box_extent": [b.box_extent.x, b.box_extent.y, b.box_extent.z],
            "sphere_radius": b.sphere_radius,
        }
    bm = forest.get_editor_property("branch_mesh")
    cm = forest.get_editor_property("canopy_mesh")
    mat = forest.get_editor_property("branch_material")
    out["branch_mesh"] = mesh_info(bm)
    out["canopy_mesh"] = mesh_info(cm)
    out["branch_material"] = mat.get_path_name() if mat else None
    out["canopy_world_scale"] = forest.get_editor_property("canopy_world_scale")
    out["canopy_branches"] = list(forest.get_editor_property("canopy_branches"))
    wo = forest.get_editor_property("world_offset")
    out["world_offset"] = [wo.x, wo.y, wo.z]
    layout = forest.get_editor_property("branch_layout")
    rows = []
    for i, b in enumerate(layout):
        s = b.get_editor_property("start_screen_offset")
        e = b.get_editor_property("end_screen_offset")
        rows.append({
            "i": i,
            "parent": b.get_editor_property("parent_index"),
            "start": [round(s.x, 2), round(s.y, 2)],
            "end": [round(e.x, 2), round(e.y, 2)],
            "diam": round(b.get_editor_property("diameter_world"), 2),
            "gb": round(b.get_editor_property("growth_begin"), 3),
            "ge": round(b.get_editor_property("growth_end"), 3),
        })
    out["layout"] = rows
    if screen is not None:
        b = screen.get_actor_bounds(False)
        out["screen"] = {"label": screen.get_actor_label(), "loc": [b[0].x, b[0].y, b[0].z], "ext": [b[1].x, b[1].y, b[1].z]}
    if line is not None:
        l = line.get_actor_location()
        out["ground_line"] = [l.x, l.y, l.z]
    out["ok"] = True
except Exception as exc:
    out["ok"] = False
    out["error"] = str(exc)
    out["trace"] = traceback.format_exc()
print("FOREST_DENSE_PROBE " + json.dumps(out))
try:
    unreal.SystemLibrary.quit_editor()
except Exception:
    pass
