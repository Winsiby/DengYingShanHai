"""Capture existing live Dev authoring, then save ONE new resource Blueprint.

Capture runs the unchanged native preview. Save is a separate Editor commandlet
process after PIE has ended. No map saves, animation graph, seconds or authority.
"""
import importlib.util
import json
import math
import os
import sys
import traceback
import unreal

sys.dont_write_bytecode = True
spec = importlib.util.spec_from_file_location("dy_forest_asset_native_base",
    os.path.join(unreal.Paths.project_dir(), "Scripts", "Preview-P03NativeForest.py"))
native = importlib.util.module_from_spec(spec)
spec.loader.exec_module(native)
base = native.base
AUDIT = "C:/UEProjects/DengYingShanHai/Saved/Audit-2026-10-04-P03ForestAsset"
BP_DIR = "/Game/DengYingShanHai/Dev/M3/Forest"
BP_NAME = "BP_DYForestPresentation_Dev"
BP_PATH = BP_DIR + "/" + BP_NAME
BASE_MESH = "/Engine/BasicShapes/Cylinder.Cylinder"
base.OUT = os.environ.get("DY_P03_FOREST_ASSET_OUT", AUDIT + "/CaptureRun1")
base.require(os.path.commonpath((os.path.abspath(base.OUT), os.path.abspath(AUDIT)))
    == os.path.abspath(AUDIT), "Forest asset evidence must stay inside its audit")


def record(event, **values):
    unreal.log("DY_FOREST_ASSET_CAPTURE " + json.dumps(dict(event=event, **values), ensure_ascii=False))


def layout_rows(layout):
    return [dict(parent_index=int(item.parent_index),
        start=[float(item.start_screen_offset.x), float(item.start_screen_offset.y)],
        end=[float(item.end_screen_offset.x), float(item.end_screen_offset.y)],
        diameter=float(item.diameter_world), begin=float(item.growth_begin), finish=float(item.growth_end))
        for item in layout]


def rows_equal(left, right):
    if len(left) != len(right):
        return False
    for a, b in zip(left, right):
        if a["parent_index"] != b["parent_index"]:
            return False
        for av, bv in zip(a["start"] + a["end"] + [a["diameter"], a["begin"], a["finish"]],
                b["start"] + b["end"] + [b["diameter"], b["begin"], b["finish"]]):
            # Double serialization comparison only; not a gameplay tolerance.
            if not math.isfinite(av) or not math.isfinite(bv) or abs(av - bv) > 1e-8:
                return False
    return True


def expected_layout(preview, contact):
    r = preview.refs
    origin = contact.projection.end_a.screen_local_position
    offsets = {name: unreal.Vector2D(preview.project(point).screen_local_position.y - origin.y,
        preview.project(point).screen_local_position.z - origin.z) for name, point in r["nodes"].items()}
    offsets["root"] = unreal.Vector2D(0, 0)
    definitions, incoming = [], {}
    for index, (parent, child, begin, finish, thickness) in enumerate(native.refined.EDGES):
        item = unreal.DYForestBranchDefinition()
        item.set_editor_property("parent_index", -1 if parent == "root" else incoming[parent])
        item.set_editor_property("start_screen_offset", offsets[parent])
        item.set_editor_property("end_screen_offset", offsets[child])
        item.set_editor_property("diameter_world", r["diameter"] * thickness)
        item.set_editor_property("growth_begin", begin)
        item.set_editor_property("growth_end", finish)
        definitions.append(item)
        incoming[child] = index
    return definitions


def require_new_asset():
    physical = os.path.join(unreal.Paths.project_dir(), "Content", "DengYingShanHai", "Dev", "M3",
        "Forest", BP_NAME + ".uasset")
    base.require(not os.path.exists(physical) and not unreal.EditorAssetLibrary.does_asset_exist(BP_PATH),
        "Refuse overwrite of existing forest Blueprint")


class CaptureForestAuthoring(native.NativeForestPreview):
    def begin(self):
        require_new_asset()
        super().begin()

    def setup_root(self, contact):
        super().setup_root(contact)
        actor = self.refs["native_actor"]
        material = actor.get_editor_property("branch_material")
        base.require(material is None, "Existing preview acquired an unexpected material override")
        layout = actor.get_editor_property("branch_layout")
        base.require(len(layout) == 15 and rows_equal(layout_rows(layout),
            layout_rows(expected_layout(self, contact))), "Capture differs from accepted 15-branch sample")
        components = actor.get_branch_mesh_components()
        record("AuthoringCaptured", bp_path=BP_PATH,
            mesh=actor.get_editor_property("branch_mesh").get_path_name(), material_override=None,
            actual_component_material=components[0].get_material(0).get_path_name(),
            layout=layout_rows(layout), true_resolve_and_contact=True,
            normalized_only=True, no_runtime_identity_serialized=True, saved_assets=False)


def save_captured_asset():
    require_new_asset()
    # UE needs the authoring DTO inside the editor to set reflected defaults.
    # This data was mechanically extracted from the successful separate live run.
    with open(AUDIT + "/Authoring-FromLiveContact.json", "r", encoding="utf-8-sig") as source:
        data = json.load(source)
    base.require(data["event"] == "AuthoringCaptured" and data["bp_path"] == BP_PATH
        and data["mesh"] == BASE_MESH and data["material_override"] is None
        and data["true_resolve_and_contact"] and data["normalized_only"]
        and data["no_runtime_identity_serialized"], "Capture manifest not from this authorized resource step")
    rows = data["layout"]
    base.require(len(rows) == 15, "Need the original 15 branches")
    definitions = []
    for row in rows:
        item = unreal.DYForestBranchDefinition()
        item.set_editor_property("parent_index", row["parent_index"])
        item.set_editor_property("start_screen_offset", unreal.Vector2D(*row["start"]))
        item.set_editor_property("end_screen_offset", unreal.Vector2D(*row["end"]))
        item.set_editor_property("diameter_world", row["diameter"])
        item.set_editor_property("growth_begin", row["begin"])
        item.set_editor_property("growth_end", row["finish"])
        definitions.append(item)
    base.require(unreal.DYForestGeometryLibrary.is_forest_layout_valid(definitions), "Captured layout invalid")
    factory = unreal.BlueprintFactory()
    factory.set_editor_property("parent_class", unreal.DYForestPresentationActor)
    bp = base.require(unreal.AssetToolsHelpers.get_asset_tools().create_asset(BP_NAME, BP_DIR,
        unreal.Blueprint, factory), "Cannot create new resource Blueprint")
    base.require(bp.get_path_name() == BP_PATH + "." + BP_NAME, "Unexpected asset path; refuse save")
    unreal.BlueprintEditorLibrary.compile_blueprint(bp)
    cdo = unreal.get_default_object(base.require(bp.generated_class(), "No generated class"))
    mesh = base.require(unreal.load_asset(BASE_MESH), "Missing original Engine Cylinder")
    cdo.set_editor_property("branch_mesh", mesh)
    cdo.set_editor_property("branch_material", None)
    cdo.set_editor_property("branch_layout", definitions)
    unreal.BlueprintEditorLibrary.compile_blueprint(bp)
    cdo = unreal.get_default_object(bp.generated_class())
    base.require(rows_equal(rows, layout_rows(cdo.get_editor_property("branch_layout")))
        and cdo.get_editor_property("branch_mesh") == mesh
        and cdo.get_editor_property("branch_material") is None
        and not cdo.has_forest_session() and not cdo.get_branch_mesh_components(),
        "Compile changed authoring or serialized runtime session")
    base.require(unreal.EditorAssetLibrary.save_loaded_asset(bp, only_if_is_dirty=False),
        "Whitelist Blueprint save failed")
    record("AssetSaved", bp_path=bp.get_path_name(), generated_class=bp.generated_class().get_path_name(),
        branch_count=15, material_override=None, saved_only_this_blueprint=True,
        map_saved=False, seconds_authored=False, formal_p03=False)


if __name__ == "__main__":
    if os.environ.get("DY_P03_FOREST_ASSET_MODE", "Capture") == "Save":
        save_captured_asset()
    else:
        native.record = record
        native.continuous.record = record
        unreal.EditorPythonScripting.set_keep_python_script_alive(True)
        preview = None
        try:
            preview = CaptureForestAuthoring()
            preview.begin()
        except Exception:
            failure = traceback.format_exc()
            unreal.log_error("DY_FOREST_ASSET_CAPTURE_FAILURE " + failure)
            if preview is not None:
                preview.error = failure
                preview.finish()
            else:
                unreal.EditorPythonScripting.set_keep_python_script_alive(False)
