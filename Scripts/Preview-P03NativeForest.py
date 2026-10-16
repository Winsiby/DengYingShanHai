"""Unsaved Dev preview: same composition, native Actor owns all branch transforms.

Editor/PIE only. P02 Resolve is a test fixture, not a authored playable P03 puzzle.
No asset saves, new controls, formal seconds, art approval or finale completion.
"""
import importlib.util
import json
import os
import sys
import time
import traceback
import unreal

sys.dont_write_bytecode = True
spec = importlib.util.spec_from_file_location("dy_native_continuous_base",
    os.path.join(unreal.Paths.project_dir(), "Scripts", "Preview-P03Continuous.py"))
continuous = importlib.util.module_from_spec(spec)
spec.loader.exec_module(continuous)
refined, forest, base = continuous.refined, continuous.forest, continuous.base
AUDIT = "C:/UEProjects/DengYingShanHai/Saved/Audit-2026-10-04-P03NativeActor"
base.OUT = os.environ.get("DY_P03_NATIVE_FOREST_OUT", AUDIT + "/Run1")
base.require(os.path.commonpath((os.path.abspath(base.OUT), os.path.abspath(AUDIT)))
    == os.path.abspath(AUDIT), "Native evidence must stay inside this audit")


def record(event, **values):
    unreal.log("DY_NATIVE_FOREST_PREVIEW " + json.dumps(dict(event=event, **values), ensure_ascii=False))


continuous.record = record  # Retag inherited clock/endpoint evidence, no parent file edits.


class NativeForestPreview(continuous.ContinuousPreview):
    def __init__(self):
        super().__init__()
        self.original_native_actor = None
        self.native_reference_saved = False
        self.native_actor_name = None
        self.branch_checks = 0

    def prepare_temporary_actors(self):
        # Inherited forest_names intentionally remains empty: no Python branch Actors.
        exposure = [a for a in self.actors.get_all_level_actors()
            if a.get_actor_label() == "M2_PostProcess_ExposureLock"]
        base.require(len(exposure) == 1, "Missing explicit existing exposure lock")
        self.exposure_name = exposure[0].get_name()
        self.original_native_actor = self.presentation.get_editor_property("forest_presentation_actor")
        self.native_reference_saved = True
        actor = base.require(self.actors.spawn_actor_from_class(unreal.DYForestPresentationActor,
            unreal.Vector(), unreal.Rotator(), False), "Cannot create native Dev actor")
        self.temporary_actors.append(actor)
        actor.set_actor_label("DEV_UnsavedNativeForestPresentation")
        cylinder = base.require(unreal.load_asset("/Engine/BasicShapes/Cylinder"), "Missing Engine Cylinder")
        actor.set_editor_property("branch_mesh", cylinder)
        self.presentation.set_editor_property("forest_presentation_actor", actor)
        self.native_actor_name = actor.get_name()
        record("Prepared", native_class=actor.get_class().get_path_name(),
            geometry_source=cylinder.get_path_name(), native_owns_transforms=True,
            no_python_branch_actors=True, saved_assets=False)

    def start_fixture(self, world, pc):
        super().start_fixture(world, pc)
        actor = self.pie_actor(world, self.native_actor_name)
        self.refs["native_actor"] = actor
        base.require(self.refs["presentation"].get_editor_property("forest_presentation_actor") == actor,
            "Presentation reference is not this PIE Actor copy")
        base.require(not actor.has_forest_session() and not actor.get_branch_mesh_components(),
            "Native branches exist before actual contact")
        base.require(not self.refs["presentation"].begin_forest_presentation(unreal.Guid()),
            "Empty token created a native session")
        record("PreContactRejected", no_components=True, actual_pie=True)

    def setup_root(self, contact):
        super().setup_root(contact)
        r = self.refs
        origin = contact.projection.end_a.screen_local_position
        # nodes are BACKSTAGE world points. Project them to the receiver first;
        # inverse-transforming backstage points directly would shrink the outline.
        offsets = {name: unreal.Vector2D(self.project(point).screen_local_position.y - origin.y,
            self.project(point).screen_local_position.z - origin.z) for name, point in r["nodes"].items()}
        offsets["root"] = unreal.Vector2D(0, 0)
        definitions, incoming = [], {}
        for index, (parent, child, begin, finish, thickness) in enumerate(refined.EDGES):
            item = unreal.DYForestBranchDefinition()
            item.set_editor_property("parent_index", -1 if parent == "root" else incoming[parent])
            item.set_editor_property("start_screen_offset", offsets[parent])
            item.set_editor_property("end_screen_offset", offsets[child])
            item.set_editor_property("diameter_world", r["diameter"] * thickness)
            item.set_editor_property("growth_begin", begin)
            item.set_editor_property("growth_end", finish)
            definitions.append(item)
            incoming[child] = index
        base.require(unreal.DYForestGeometryLibrary.is_forest_layout_valid(definitions),
            "Native layout rejected inherited composition")
        r["native_actor"].set_editor_property("branch_layout", definitions)
        base.require(r["presentation"].begin_forest_presentation(contact.token),
            "Current accepted contact could not authorize native forest")
        components = r["native_actor"].get_branch_mesh_components()
        base.require(len(components) == len(refined.EDGES), "Wrong native resource count")
        r["native_components"] = list(components)
        lower, upper = components[0].get_local_bounds()
        r["native_bounds"] = (lower, upper)
        final = unreal.DYForestGeometryLibrary.sample_forest_geometry(contact, definitions, 1.0, lower, upper)
        base.require(final.status == unreal.DYForestGeometryStatus.VALID, "Full geometry preflight failed")
        self.check_protected_gap(final)
        base.require(not r["presentation"].begin_forest_presentation(contact.token),
            "Active duplicate Begin recreated resources")
        record("NativeSessionStarted", token=contact.token.to_string(), branch_count=len(components),
            current_contact_authorized=True, final_geometry_preflight=True,
            duplicate_begin_rejected=True, native_owns_transforms=True)

    def check_protected_gap(self, sample):
        gap = self.refs["gap"]
        for index, branch in enumerate(sample.branches):
            if branch.visible:
                lo, hi = branch.projected_min, branch.projected_max
                base.require(hi.x < gap[0] or lo.x > gap[1] or hi.y < gap[2],
                    "Native eight-corner envelope intersects protected silhouette: %d" % index)

    def check_identity(self):
        capture = super().check_identity()
        r = self.refs
        actor = r["native_actor"]
        base.require(unreal.SystemLibrary.is_valid(actor)
            and r["presentation"].get_editor_property("forest_presentation_actor") == actor,
            "Native Actor identity changed")
        if r["contact"] is None:
            base.require(not actor.has_forest_session() and not actor.get_branch_mesh_components(),
                "Native tree appeared before contact")
            return capture
        sample = actor.get_forest_geometry_sample()
        base.require(actor.has_forest_session() and sample.status == unreal.DYForestGeometryStatus.VALID
            and sample.contact_token.to_string() == r["contact"].token.to_string(), "Native session/token invalid")
        base.require(base.close_vector(sample.physical_root, r["root"])
            and base.close_vector(sample.shadow_root, r["contact"].contact_world_position), "Native root drift")
        components = actor.get_branch_mesh_components()
        base.require(list(components) == r["native_components"] and len(components) == len(sample.branches),
            "Native components recreated outside the session")
        self.check_protected_gap(sample)
        for index, (component, branch) in enumerate(zip(components, sample.branches)):
            lower, upper = component.get_local_bounds()
            base.require((lower, upper) == r["native_bounds"], "Actual component bounds changed")
            base.require(component.get_editor_property("static_mesh")
                == actor.get_editor_property("branch_mesh"), "Native mesh replaced")
            base.require(component.get_editor_property("mobility") == unreal.ComponentMobility.MOVABLE
                and component.get_collision_enabled() == unreal.CollisionEnabled.NO_COLLISION,
                "Native component movement/collision contract changed")
            base.require(component.is_visible() == branch.visible
                and component.get_editor_property("hidden_in_game") == (not branch.visible)
                and component.get_editor_property("cast_shadow") == branch.visible,
                "Native visibility/shadow flags differ from sample")
            if branch.visible:
                transform = component.get_world_transform()
                base.require(transform == branch.mesh_world_transform, "Native world transform mismatch")
                middle = (lower + upper) * .5
                start = unreal.Vector(middle.x, middle.y, lower.z)
                end = unreal.Vector(middle.x, middle.y, upper.z)
                base.require(base.close_vector(unreal.MathLibrary.transform_location(transform, start), branch.start_world)
                    and base.close_vector(unreal.MathLibrary.transform_location(transform, end), branch.end_world),
                    "Actual native mesh endpoints mismatch")
                material = base.require(component.get_material(0), "Missing native default Engine material")
                base.require(material.get_path_name().startswith("/Engine/"), "Unexpected branch material source")
                self.branch_checks += 1
        return capture

    def apply_progress(self, drop, growth, phase_elapsed=None):
        r = self.refs
        self.check_identity()
        base.require(0 <= self.last_drop <= drop <= 1 and 0 <= self.last_growth <= growth <= 1,
            "Normalized progress regressed")
        base.require(growth == 0 or drop == 1, "Growth before actual staff endpoint")
        r["staff"].set_world_location(r["start_location"] + r["displacement"] * drop, False, False)
        r["expected_staff_transform"] = r["staff"].get_world_transform()
        capture = self.check_identity()
        base.require(r["staff"].get_editor_property("relative_rotation") == r["relative_rotation"]
            and r["staff"].get_editor_property("relative_scale3d") == r["relative_scale"], "Staff rotation/scale changed")
        if r["contact"] is None:
            base.require(not r["presentation"].get_staff_contact_presentation_snapshot().has_contact,
                "Contact consumed outside preview")
            if drop == 1:
                base.require(r["presentation"].try_accept_staff_contact(r["snapshot"].token),
                    "Actual continuous endpoint rejected")
                self.setup_root(r["presentation"].get_staff_contact_presentation_snapshot())
                self.contact_count += 1
                base.require(self.contact_count == 1
                    and not r["presentation"].try_accept_staff_contact(r["snapshot"].token),
                    "Contact did not remain exactly-once")
                record("ContactOnce", count=self.contact_count, duplicate_rejected=True, actual_A=True)
        else:
            base.require(base.close_vector(capture.staff.end_a_world, r["root"]), "Actual A moved after contact")
        if r["contact"] is not None:
            base.require(r["presentation"].set_forest_normalized_growth(r["contact"].token, growth),
                "Authorized native progress failed")
        base.require(r["director"].get_resolved_puzzle_snapshot().is_resolved, "Cosmetic growth revoked success")
        self.check_identity()
        r["probe"].refresh_projection()
        self.last_drop, self.last_growth = drop, growth
        sample = r["native_actor"].get_forest_geometry_sample()
        record("MotionFrame", frame=self.frame, phase=self.state, monotonic_seconds=time.monotonic(),
            drop=drop, growth=growth, phase_elapsed_seconds=phase_elapsed,
            actual_staff_a=base.xyz(capture.staff.end_a_world), shadow_a=base.xyz(capture.end_a.world_position),
            visible_branches=sum(b.visible for b in sample.branches), contact_count=self.contact_count,
            native_owns_transforms=True, puzzle_remains_resolved=True, actual_pie=True)

    def restore_and_end(self):
        if self.refs:
            r = self.refs
            actor = r["native_actor"]
            if actor.has_forest_session():
                base.require(r["presentation"].clear_forest_presentation(r["contact"].token),
                    "Native cleanup rejected current resource owner")
            base.require(not actor.has_forest_session() and not actor.get_branch_mesh_components(),
                "Native components survived cleanup")
            record("NativeCleanup", released_all_components=True, branch_checks=self.branch_checks,
                before_end_pie=True, gameplay_restart_policy=False)
        super().restore_and_end()

    def finish(self):
        try:
            if self.native_reference_saved:
                self.presentation.set_editor_property("forest_presentation_actor", self.original_native_actor)
                self.native_reference_saved = False
        except Exception:
            self.error = (self.error or "") + "\nNative editor cleanup: " + traceback.format_exc()
        super().finish()
        record("Failed" if self.error else "Completed", native_owns_transforms=True,
            branch_checks=self.branch_checks, saved_assets=False, packaged=False,
            formal_p03=False, user_visual_acceptance=False, error=self.error)


if __name__ == "__main__":
    unreal.EditorPythonScripting.set_keep_python_script_alive(True)
    preview = None
    try:
        preview = NativeForestPreview()
        preview.begin()
    except Exception:
        failure = traceback.format_exc()
        unreal.log_error("DY_NATIVE_FOREST_SETUP_FAILURE " + failure)
        if preview is not None:
            preview.error = failure
            preview.finish()
        else:
            unreal.EditorPythonScripting.set_keep_python_script_alive(False)
