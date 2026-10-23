"""Unsaved Editor/PIE diagnostic only; no formal P03 animation or game assets.

Reuses the bounded drop-preview lifecycle. Every branch belongs to a connected
graph rooted at ACTUAL backstage A, only after native contact is accepted.
Normalized samples and branch dimensions are NOT approved timing/art parameters.
"""
import importlib.util
import json
import os
import sys
import traceback
import unreal

sys.dont_write_bytecode = True
_spec = importlib.util.spec_from_file_location("dy_drop_preview_base",
    os.path.join(unreal.Paths.project_dir(), "Scripts", "Preview-P03StaffDrop.py"))
base = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(base)  # __main__ guard prevents starting the old preview.

AUDIT = "C:/UEProjects/DengYingShanHai/Saved/Audit-2026-10-04-P03ForestPreview"
base.OUT = os.environ.get("DY_FOREST_PREVIEW_OUT", AUDIT + "/Run1")
base.require(os.path.commonpath((os.path.abspath(base.OUT), os.path.abspath(AUDIT)))
    == os.path.abspath(AUDIT), "Evidence output must stay inside this step's audit")
base.CANDIDATES = (("High", 0.15),)  # User-confirmed Dev line, not new tuning.
PHASES = (
    ("01-Start", 0.0, 0.0, True),
    ("02-Drop50", 0.5, 0.0, True),
    ("03-Contact", 1.0, 0.0, True),
    ("04-Tree50", 1.0, 0.5, True),
    ("05-Tree100", 1.0, 1.0, True),
    ("06-Tree100-NoTreeShadow", 1.0, 1.0, False),
)
base.PROGRESS = tuple(phase[1] for phase in PHASES)

# Connected bare-branch graybox. Deliberately not a botanical/historical model.
# Node coordinates are fractions of this sample's projected width/height.
NODES = {
    "root": (0.0, 0.0), "fork": (0.0, 0.30),
    "left": (-0.35, 0.57), "middle": (0.05, 0.70), "right": (0.33, 0.53),
    "l1": (-0.55, 0.83), "l2": (-0.20, 0.90),
    "m1": (-0.06, 1.00), "m2": (0.22, 0.96),
    "r1": (0.55, 0.74), "r2": (0.38, 0.88),
}
# Parent must finish before a child emerges. Intervals are normalized, not seconds.
EDGES = (
    ("root", "fork", 0.0, 0.3, 1.0),
    ("fork", "left", 0.3, 0.65, 0.7),
    ("fork", "middle", 0.3, 0.65, 0.7),
    ("fork", "right", 0.3, 0.65, 0.7),
    ("left", "l1", 0.65, 1.0, 0.42),
    ("left", "l2", 0.65, 1.0, 0.42),
    ("middle", "m1", 0.65, 1.0, 0.42),
    ("middle", "m2", 0.65, 1.0, 0.42),
    ("right", "r1", 0.65, 1.0, 0.42),
    ("right", "r2", 0.65, 1.0, 0.42),
)


def record(event, **values):
    unreal.log("DY_FOREST_PREVIEW " + json.dumps(dict(event=event, **values), ensure_ascii=False))


def hidden(actor):
    return actor.get_editor_property("hidden")  # AActor::IsHidden is not a UFUNCTION.


class ForestPreview(base.Preview):
    def __init__(self):
        super().__init__()
        self.forest_names = []

    def prepare_temporary_actors(self):
        exposure = [actor for actor in self.actors.get_all_level_actors()
            if actor.get_actor_label() == "M2_PostProcess_ExposureLock"]
        base.require(len(exposure) == 1, "Expected one existing explicit exposure lock")
        self.exposure_name = exposure[0].get_name()
        cylinder = base.require(unreal.load_asset("/Engine/BasicShapes/Cylinder"), "Missing Engine Cylinder")
        for index in range(len(EDGES)):
            actor = base.require(self.actors.spawn_actor_from_class(unreal.StaticMeshActor,
                unreal.Vector(), unreal.Rotator(), False), "Cannot create unsaved branch")
            self.temporary_actors.append(actor)  # Track before any fallible setup.
            actor.set_actor_label("DEV_UnsavedForestBranch_%02d" % index)
            mesh = actor.static_mesh_component
            mesh.set_mobility(unreal.ComponentMobility.MOVABLE)
            base.require(mesh.set_static_mesh(cylinder), "Cannot assign Cylinder")
            material = base.require(mesh.get_material(0), "Missing installed Engine branch material")
            base.require(material.get_path_name().startswith("/Engine/"),
                "Branch material is not installed Engine content: " + material.get_path_name())
            mesh.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
            mesh.set_cast_shadow(False)
            actor.set_actor_hidden_in_game(True)
            self.forest_names.append(actor.get_name())
        record("Prepared", branch_count=len(EDGES), saved_assets=False,
            geometry_source=cylinder.get_path_name(), material_source=material.get_path_name(),
            material_from_engine=True)

    def screenshot_name(self):
        return PHASES[self.index][0]

    def start_fixture(self, world, pc):
        super().start_fixture(world, pc)
        r = self.refs
        r["forest"] = [self.pie_actor(world, name) for name in self.forest_names]
        r["forest_expected"] = {}
        r["contact"] = None
        r["key_light"] = r["light"].get_editor_property("key_light")
        r["exposure"] = self.pie_actor(world, self.exposure_name)
        for actor in r["forest"]:
            base.require(hidden(actor), "Tree visible before native contact")
            mesh = actor.static_mesh_component
            lower, upper = mesh.get_local_bounds()
            base.require(all(v > 0 for v in base.xyz(upper - lower)), "Degenerate Cylinder bounds")
            base.require(not mesh.get_editor_property("cast_shadow"), "Tree shadows active before contact")
            base.require(mesh.get_editor_property("mobility") == unreal.ComponentMobility.MOVABLE,
                "Branch is not Movable")

    def begin_samples(self, snapshot):
        r = self.refs
        r["fov"] = unreal.GameplayStatics.get_player_camera_manager(r["world"], 0).get_fov_angle()
        fields = ("intensity", "intensity_units", "light_color", "attenuation_radius",
            "source_radius", "inner_cone_angle", "outer_cone_angle", "cast_shadows", "mobility")
        r["light_fields"] = {key: r["key_light"].get_editor_property(key) for key in fields}
        settings = r["exposure"].get_editor_property("settings")
        exposure_fields = ("override_auto_exposure_method", "auto_exposure_method",
            "override_auto_exposure_bias", "auto_exposure_bias",
            "override_auto_exposure_apply_physical_camera_exposure", "auto_exposure_apply_physical_camera_exposure")
        r["exposure_fields"] = {key: settings.get_editor_property(key) for key in exposure_fields}
        base.require(r["exposure_fields"]["override_auto_exposure_method"]
            and "MANUAL" in str(r["exposure_fields"]["auto_exposure_method"]), "Exposure is not the existing manual lock")
        base.require(r["light_fields"]["cast_shadows"], "Main light cannot project geometry")
        base.require(r["light_fields"]["mobility"] == unreal.ComponentMobility.MOVABLE,
            "Main light is not Movable")
        record("LightingBaseline", properties={key: str(value) for key, value in r["light_fields"].items()},
            exposure={key: str(value) for key, value in r["exposure_fields"].items()},
            adjusted=False, renderer="existing DX12/SM6 Lumen/VSM; RT disabled", fps_measured=False)
        super().begin_samples(snapshot)

    def check_identity(self):
        current = super().check_identity()
        r = self.refs
        original = r["snapshot"].projection
        base.require(current.has_geometry, "Actual geometry no longer valid")
        base.require(current.screen_local_min == original.screen_local_min
            and current.screen_local_max == original.screen_local_max, "Receiver local bounds changed")
        base.require(unreal.GameplayStatics.get_player_camera_manager(r["world"], 0).get_fov_angle()
            == r["fov"], "FOV changed")
        for key, value in r["light_fields"].items():
            base.require(r["key_light"].get_editor_property(key) == value, "Main light changed: " + key)
        settings = r["exposure"].get_editor_property("settings")
        for key, value in r["exposure_fields"].items():
            base.require(settings.get_editor_property(key) == value, "Existing exposure changed: " + key)
        for index, expected in r["forest_expected"].items():
            actor = r["forest"][index]
            transform, is_hidden, casts = expected
            base.require(actor.get_actor_transform() == transform and hidden(actor) == is_hidden
                and actor.static_mesh_component.get_editor_property("cast_shadow") == casts,
                "Branch changed outside the recorded sample: %d" % index)
        return current

    def project(self, point):
        p = self.refs["contact"].projection
        result = unreal.DYStaffProjectionLibrary.project_point_to_screen(p.emitter_world, point,
            p.screen_transform, p.screen_local_min, p.screen_local_max)
        base.require(result.status == unreal.DYStaffProjectionStatus.ON_SCREEN,
            "Branch endpoint outside receiver or not between light and screen")
        return result

    def setup_root(self, contact):
        r = self.refs
        record("ContactSnapshotCheck", has_contact=contact.has_contact,
            contact_token=contact.token.to_string(), resolve_token=r["snapshot"].token.to_string(),
            native_token_current=r["director"].is_resolved_token_current(contact.token))
        # FGuid Python wrappers do not provide native value equality. Compare their
        # serialized values AND use the real Director's native identity guard.
        base.require(contact.has_contact and contact.token.to_string() == r["snapshot"].token.to_string()
            and r["director"].is_resolved_token_current(contact.token), "Missing real current contact")
        r["contact"] = contact
        r["root"] = contact.projection.staff.end_a_world
        root_shadow = self.project(r["root"])
        base.require(base.close_vector(root_shadow.world_position, contact.contact_world_position),
            "Physical A does not project to accepted contact")
        base.require(not base.close_vector(r["root"], contact.contact_world_position),
            "Backdrop contact incorrectly used as backstage geometry root")
        p = contact.projection
        lower, upper = p.screen_local_min, p.screen_local_max
        # This sample's outline uses available curtain space, not a fixed final asset size.
        height = (upper.z - root_shadow.screen_local_position.z) * 0.62
        width = (upper.y - lower.y) * 0.48
        r["nodes"] = self.build_nodes(root_shadow, height, width)
        base.require(base.close_vector(r["nodes"]["root"], r["root"]), "Graph root drift")
        r["diameter"] = self.branch_diameter(root_shadow)
        record("ContactAccepted", token=contact.token.to_string(), physical_root=base.xyz(r["root"]),
            shadow_root=base.xyz(root_shadow.world_position), native_contact=True, source_is_actual_A=True,
            root_ray_parameter=root_shadow.ray_parameter, connected_edges=len(EDGES),
            sample_width_fraction=0.48, sample_available_height_fraction=0.62, formal_art_approved=False)

    def build_nodes(self, root_shadow, height, width):
        """Default outline unchanged; derived diagnostic samples may replace it."""
        r = self.refs
        p = r["contact"].projection
        nodes = {}
        for name, (y, z) in NODES.items():
            local = root_shadow.screen_local_position + unreal.Vector(0, y * width, z * height)
            shadow = unreal.MathLibrary.transform_location(p.screen_transform, local)
            point = p.emitter_world + (shadow - p.emitter_world) / root_shadow.ray_parameter
            actual_projection = self.project(point)
            base.require(base.close_vector(actual_projection.world_position, shadow), "Inverse ray mismatch")
            nodes[name] = point
        return nodes

    def branch_diameter(self, root_shadow):
        r = self.refs
        projected_height_world = (r["nodes"]["m1"] - r["root"]).length() * root_shadow.ray_parameter
        return projected_height_world * 0.025 / root_shadow.ray_parameter

    def place_branch(self, index, start, end, diameter, casts):
        r = self.refs
        actor = r["forest"][index]
        mesh = actor.static_mesh_component
        lower, upper = mesh.get_local_bounds()
        extent, center = upper - lower, (upper + lower) * 0.5
        direction = end - start
        base.require(direction.length() > 0.000001, "Do not create zero-length branches")
        scale = unreal.Vector(diameter / extent.x, diameter / extent.y, direction.length() / extent.z)
        if casts:
            actor.set_actor_rotation(unreal.MathLibrary.make_rot_from_z(direction), False)
            actor.set_actor_scale3d(scale)
            transformed_center = unreal.MathLibrary.transform_location(mesh.get_world_transform(), center)
            offset = transformed_center - actor.get_actor_location()
            actor.set_actor_location((start + end) * 0.5 - offset, False, False)
            actor.set_actor_hidden_in_game(False)
        else:
            base.require(not hidden(actor), "Shadow control requires previously visible unchanged geometry")
        mesh.set_cast_shadow(casts)
        local_a = unreal.Vector(center.x, center.y, lower.z)
        local_b = unreal.Vector(center.x, center.y, upper.z)
        actual_a = unreal.MathLibrary.transform_location(mesh.get_world_transform(), local_a)
        actual_b = unreal.MathLibrary.transform_location(mesh.get_world_transform(), local_b)
        base.require(base.close_vector(actual_a, start) and base.close_vector(actual_b, end),
            "Actual mesh bounds endpoints differ from planned connected branch")
        shadow_a, shadow_b = self.project(actual_a), self.project(actual_b)
        record("Branch", phase=PHASES[self.index][0], index=index,
            actual_a=base.xyz(actual_a), actual_b=base.xyz(actual_b),
            shadow_a=base.xyz(shadow_a.world_position), shadow_b=base.xyz(shadow_b.world_position),
            actual_transform=str(mesh.get_world_transform()), casts_shadow=casts)

    def apply_sample(self):
        r = self.refs
        self.check_identity()
        name, drop, growth, casts = PHASES[self.index]
        r["staff"].set_world_location(r["start_location"] + r["displacement"] * drop, False, False)
        r["expected_staff_transform"] = r["staff"].get_world_transform()
        capture = self.check_identity()
        base.require(r["staff"].get_editor_property("relative_rotation") == r["relative_rotation"]
            and r["staff"].get_editor_property("relative_scale3d") == r["relative_scale"], "Staff rotation/scale changed")
        if r["contact"] is None:
            accepted = r["presentation"].try_accept_staff_contact(r["snapshot"].token)
            base.require(accepted == (drop == 1.0), "Unexpected native contact before endpoint")
            if accepted:
                self.setup_root(r["presentation"].get_staff_contact_presentation_snapshot())
        else:
            base.require(not r["presentation"].try_accept_staff_contact(r["snapshot"].token), "Contact repeated")
            base.require(base.close_vector(capture.staff.end_a_world, r["root"]), "Root moved after accepted contact")
        base.require(growth == 0.0 or r["contact"] is not None, "Tree appeared without native contact")
        for index, (parent, child, begin, finish, thickness) in enumerate(EDGES):
            actor = r["forest"][index]
            portion = max(0.0, min(1.0, (growth - begin) / (finish - begin)))
            if portion == 0.0:
                actor.set_actor_hidden_in_game(True)
                actor.static_mesh_component.set_cast_shadow(False)
            else:
                start, full_end = r["nodes"][parent], r["nodes"][child]
                self.place_branch(index, start, start + (full_end - start) * portion,
                    r["diameter"] * thickness, casts)
            r["forest_expected"][index] = (actor.get_actor_transform(), hidden(actor),
                actor.static_mesh_component.get_editor_property("cast_shadow"))
        base.require(r["director"].get_resolved_puzzle_snapshot().is_resolved, "Presentation revoked puzzle success")
        self.check_identity()
        r["probe"].refresh_projection()
        record("Sample", phase=name, normalized_drop=drop, normalized_growth=growth,
            actual_staff_a=base.xyz(capture.staff.end_a_world), shadow_a=base.xyz(capture.end_a.world_position),
            contact_accepted=r["contact"] is not None, puzzle_remains_resolved=True,
            tree_cast_shadow=casts, no_new_time_parameters=True, actual_pie=True)
        self.wait_frame = self.frame + 20  # Screenshot settling only, not animation duration.
        self.state = "wait_render"

    def restore_and_end(self):
        if self.refs:
            for actor in self.refs.get("forest", []):
                if unreal.SystemLibrary.is_valid(actor):
                    actor.set_actor_hidden_in_game(True)
                    actor.static_mesh_component.set_cast_shadow(False)
            record("ForestCleanup", hidden_branch_count=len(self.refs.get("forest", [])), before_end_pie=True)
            self.refs["forest_expected"] = {}
        super().restore_and_end()  # Drops ALL PIE refs before the asynchronous EndPlay.


if __name__ == "__main__":
    unreal.EditorPythonScripting.set_keep_python_script_alive(True)
    _preview = ForestPreview()
    try:
        _preview.begin()
    except Exception:
        _preview.error = traceback.format_exc()
        unreal.log_error("DY_FOREST_PREVIEW_SETUP_FAILURE " + _preview.error)
        _preview.finish()
