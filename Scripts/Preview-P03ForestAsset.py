"""Load the persisted Dev Blueprint; never rewrite its mesh/layout defaults.

Editor-only P02 fixture, no formal P03 target/seconds/Skip/R/ending decisions.
"""
import importlib.util
import os
import sys
import traceback
import unreal

sys.dont_write_bytecode = True
spec = importlib.util.spec_from_file_location("dy_forest_asset_creation",
    os.path.join(unreal.Paths.project_dir(), "Scripts", "Create-P03ForestDevAsset.py"))
authoring = importlib.util.module_from_spec(spec)
spec.loader.exec_module(authoring)
native, base = authoring.native, authoring.base
base.OUT = os.environ.get("DY_P03_FOREST_ASSET_OUT", authoring.AUDIT + "/Run1")


def record(event, **values):
    unreal.log("DY_FOREST_ASSET_PREVIEW " + authoring.json.dumps(dict(event=event, **values), ensure_ascii=False))


native.record = record
native.continuous.record = record


class SavedForestPreview(native.NativeForestPreview):
    def prepare_temporary_actors(self):
        exposure = [a for a in self.actors.get_all_level_actors()
            if a.get_actor_label() == "M2_PostProcess_ExposureLock"]
        base.require(len(exposure) == 1, "Missing explicit existing exposure lock")
        self.exposure_name = exposure[0].get_name()
        self.original_native_actor = self.presentation.get_editor_property("forest_presentation_actor")
        self.native_reference_saved = True
        cls = base.require(unreal.EditorAssetLibrary.load_blueprint_class(authoring.BP_PATH),
            "Saved forest Blueprint missing; resource generation must complete first")
        self.cdo = unreal.get_default_object(cls)
        self.initial_rows = authoring.layout_rows(self.cdo.get_editor_property("branch_layout"))
        base.require(len(self.initial_rows) == 15 and self.cdo.get_editor_property("branch_mesh").get_path_name()
            == authoring.BASE_MESH and self.cdo.get_editor_property("branch_material") is None
            and not self.cdo.has_forest_session() and not self.cdo.get_branch_mesh_components(),
            "Saved default resource/session contract invalid")
        actor = base.require(self.actors.spawn_actor_from_class(cls, unreal.Vector(), unreal.Rotator(), False),
            "Cannot spawn saved Dev Blueprint")
        self.temporary_actors.append(actor)
        actor.set_actor_label("DEV_UnsavedSavedForestInstance")
        self.presentation.set_editor_property("forest_presentation_actor", actor)
        self.native_actor_name = actor.get_name()
        record("Prepared", blueprint_class=cls.get_path_name(), branch_count=15,
            defaults_loaded_from_saved_asset=True, mesh_layout_not_rewritten=True,
            native_owns_transforms=True, saved_assets=False)

    def setup_root(self, contact):
        # Only the inherited mathematical composition setup, NOT native.setup_root
        # which fills temporary authoring. This instance keeps saved class defaults.
        native.continuous.ContinuousPreview.setup_root(self, contact)
        r = self.refs
        definitions = r["native_actor"].get_editor_property("branch_layout")
        base.require(authoring.rows_equal(authoring.layout_rows(definitions),
            authoring.layout_rows(authoring.expected_layout(self, contact))),
            "Saved layout no longer matches the same live 15-branch composition")
        base.require(r["presentation"].begin_forest_presentation(contact.token), "Saved class authorization failed")
        components = r["native_actor"].get_branch_mesh_components()
        base.require(len(components) == 15, "Saved Blueprint did not create 15 native resources")
        r["native_components"] = list(components)
        lower, upper = components[0].get_local_bounds()
        r["native_bounds"] = (lower, upper)
        final = unreal.DYForestGeometryLibrary.sample_forest_geometry(contact, definitions, 1.0, lower, upper)
        base.require(final.status == unreal.DYForestGeometryStatus.VALID, "Saved full geometry invalid")
        self.check_protected_gap(final)
        base.require(not r["presentation"].begin_forest_presentation(contact.token), "Duplicate saved session allowed")
        record("NativeSessionStarted", branch_count=15, current_contact_authorized=True,
            final_geometry_preflight=True, duplicate_begin_rejected=True,
            saved_layout_matches_live_sample=True, mesh_layout_not_rewritten=True)

    def restore_and_end(self):
        base.require(authoring.rows_equal(self.initial_rows,
            authoring.layout_rows(self.cdo.get_editor_property("branch_layout")))
            and self.cdo.get_editor_property("branch_mesh").get_path_name() == authoring.BASE_MESH
            and self.cdo.get_editor_property("branch_material") is None
            and not self.cdo.has_forest_session() and not self.cdo.get_branch_mesh_components(),
            "Instance runtime contaminated Blueprint defaults")
        record("DefaultsUnchanged", no_session_in_cdo=True, authoring_unchanged=True)
        super().restore_and_end()


if __name__ == "__main__":
    unreal.EditorPythonScripting.set_keep_python_script_alive(True)
    preview = None
    try:
        preview = SavedForestPreview()
        preview.begin()
    except Exception:
        failure = traceback.format_exc()
        unreal.log_error("DY_FOREST_ASSET_PREVIEW_FAILURE " + failure)
        if preview is not None:
            preview.error = failure
            preview.finish()
        else:
            unreal.EditorPythonScripting.set_keep_python_script_alive(False)
