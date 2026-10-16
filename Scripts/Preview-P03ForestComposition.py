"""Unsaved Dev comparison: actual A root, early split, clear central silhouette.

Not formal art/timing/puzzle tuning. Owns only this diagnostic PIE lifetime.
"""
import importlib.util
import json
import os
import sys
import traceback
import unreal

sys.dont_write_bytecode = True
spec = importlib.util.spec_from_file_location("dy_forest_preview_base",
    os.path.join(unreal.Paths.project_dir(), "Scripts", "Preview-P03ForestProjection.py"))
forest = importlib.util.module_from_spec(spec)
spec.loader.exec_module(forest)
base = forest.base
AUDIT = "C:/UEProjects/DengYingShanHai/Saved/Audit-2026-10-04-P03ForestComposition"
base.OUT = os.environ.get("DY_FOREST_COMPOSITION_OUT", AUDIT + "/Run1")
base.require(os.path.commonpath((os.path.abspath(base.OUT), os.path.abspath(AUDIT)))
    == os.path.abspath(AUDIT), "Evidence output must stay within this composition audit")

EDGES = (
    ("root", "fork", 0.0, 0.1, 1.0),
    ("fork", "left_base", 0.1, 0.35, 0.7),
    ("fork", "right_base", 0.1, 0.35, 0.7),
    ("left_base", "left_mid", 0.35, 0.7, 0.7),
    ("right_base", "right_mid", 0.35, 0.7, 0.7),
    ("left_mid", "left_outer", 0.7, 1.0, 0.42),
    ("left_mid", "left_inner", 0.7, 1.0, 0.42),
    ("right_mid", "right_outer", 0.7, 1.0, 0.42),
    ("right_mid", "right_inner", 0.7, 1.0, 0.42),
)
forest.EDGES = EDGES  # Parent methods use their own module's explicit topology.


def record(event, **values):
    unreal.log("DY_OPEN_FOREST " + json.dumps(dict(event=event, **values), ensure_ascii=False))


def corners(lower, upper):
    return [unreal.Vector(x, y, z) for x in (lower.x, upper.x)
        for y in (lower.y, upper.y) for z in (lower.z, upper.z)]


class OpenForestPreview(forest.ForestPreview):
    def begin_samples(self, snapshot):
        r = self.refs
        r["silhouette"] = []
        for field in ("torso", "head"):
            component = r["puppet"].get_editor_property(field)
            lower, upper = component.get_local_bounds()
            r["silhouette"].append(dict(name=field, component=component,
                mesh=component.get_editor_property("static_mesh"), lower=lower, upper=upper,
                transform=component.get_world_transform()))
        super().begin_samples(snapshot)

    def check_identity(self):
        current = super().check_identity()
        for entry in self.refs["silhouette"]:
            component = entry["component"]
            lower, upper = component.get_local_bounds()
            base.require(component.get_world_transform() == entry["transform"]
                and component.get_editor_property("static_mesh") == entry["mesh"]
                and lower == entry["lower"] and upper == entry["upper"],
                "Actual silhouette component changed: " + entry["name"])
        return current

    def build_nodes(self, root_shadow, height, width):
        r = self.refs
        p = r["contact"].projection
        projected = []
        for entry in r["silhouette"]:
            for local in corners(entry["lower"], entry["upper"]):
                world = unreal.MathLibrary.transform_location(entry["transform"], local)
                projected.append(self.project(world).screen_local_position)
        box = (min(q.y for q in projected), max(q.y for q in projected),
            min(q.z for q in projected), max(q.z for q in projected))
        lower, upper = p.screen_local_min, p.screen_local_max
        padding_y = (upper.y - lower.y) * 0.02
        padding_z = (upper.z - lower.z) * 0.02
        gap = (box[0] - padding_y, box[1] + padding_y, box[2] - padding_z, box[3] + padding_z)
        r["gap"] = gap
        origin = root_shadow.screen_local_position
        high_world = unreal.MathLibrary.transform_location(p.screen_transform, origin + unreal.Vector(0, 0, height))
        r["sample_world_height"] = (high_world - root_shadow.world_position).length()
        z_unit = (unreal.MathLibrary.transform_location(p.screen_transform, origin + unreal.Vector(0, 0, 1))
            - root_shadow.world_position).length()
        radius_z = r["sample_world_height"] * 0.0125 / z_unit
        clearance = gap[2] - origin.z - radius_z
        base.require(clearance > radius_z * 0.5,
            "Insufficient low clearance; refuse to move puppet/root/camera to satisfy geometry")
        left_y, right_y = gap[0] - width * 0.12, gap[1] + width * 0.12
        local_nodes = self.make_local_nodes(origin, height, width, clearance, left_y, right_y)
        nodes = {}
        for name, local in local_nodes.items():
            shadow = unreal.MathLibrary.transform_location(p.screen_transform, local)
            point = p.emitter_world + (shadow - p.emitter_world) / root_shadow.ray_parameter
            base.require(base.close_vector(self.project(point).world_position, shadow), "Inverse ray mismatch")
            nodes[name] = point
        record("SilhouetteGap", bounds=box, padded_gap=gap, diagnostic_padding=[padding_y, padding_z],
            root_screen_local=base.xyz(origin), low_clearance=clearance,
            gameplay_tolerance_changed=False, no_central_upright=True,
            nodes={name: base.xyz(point) for name, point in nodes.items()}, branch_count=len(EDGES))
        return nodes

    def make_local_nodes(self, origin, height, width, clearance, left_y, right_y):
        """Default nine-edge U comparison unchanged; diagnostic subclasses may replace it."""
        return {
            "root": origin,
            "fork": unreal.Vector(origin.x, origin.y, origin.z + clearance * 0.3),
            "left_base": unreal.Vector(origin.x, left_y, origin.z + clearance * 0.65),
            "right_base": unreal.Vector(origin.x, right_y, origin.z + clearance * 0.65),
            "left_mid": unreal.Vector(origin.x, left_y - width * 0.04, origin.z + height * 0.66),
            "right_mid": unreal.Vector(origin.x, right_y + width * 0.04, origin.z + height * 0.66),
            "left_outer": unreal.Vector(origin.x, left_y - width * 0.18, origin.z + height * 0.90),
            "left_inner": unreal.Vector(origin.x, left_y - width * 0.02, origin.z + height * 0.98),
            "right_outer": unreal.Vector(origin.x, right_y + width * 0.18, origin.z + height * 0.90),
            "right_inner": unreal.Vector(origin.x, right_y + width * 0.02, origin.z + height * 0.98),
        }

    def branch_diameter(self, root_shadow):
        return self.refs["sample_world_height"] * 0.025 / root_shadow.ray_parameter

    def place_branch(self, index, start, end, diameter, casts):
        super().place_branch(index, start, end, diameter, casts)
        actor = self.refs["forest"][index]
        mesh = actor.static_mesh_component
        lower, upper = mesh.get_local_bounds()
        projected = [self.project(unreal.MathLibrary.transform_location(mesh.get_world_transform(), point))
            .screen_local_position for point in corners(lower, upper)]
        bounds = (min(q.y for q in projected), max(q.y for q in projected),
            min(q.z for q in projected), max(q.z for q in projected))
        gap = self.refs["gap"]
        separated = bounds[1] < gap[0] or bounds[0] > gap[1] or bounds[3] < gap[2]
        base.require(separated, "Actual branch volume intersects protected silhouette gap: %d" % index)
        record("VolumeClear", phase=forest.PHASES[self.index][0], index=index,
            actual_projected_bounds=bounds, protected_gap=gap, corner_checks=8,
            numeric_clearance=True, visual_acceptance=False)


if __name__ == "__main__":
    unreal.EditorPythonScripting.set_keep_python_script_alive(True)
    preview = OpenForestPreview()
    try:
        preview.begin()
    except Exception:
        preview.error = traceback.format_exc()
        unreal.log_error("DY_OPEN_FOREST_SETUP_FAILURE " + preview.error)
        preview.finish()
