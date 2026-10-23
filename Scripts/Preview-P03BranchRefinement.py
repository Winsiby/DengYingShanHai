"""Unsaved Dev silhouette comparison only: low escape, bent sides, stepped diameters.

Not final art, animation seconds, puzzle tuning, or a new production Forest Actor.
Actual root/contact/lifecycle and real mesh-volume clearance reuse prior diagnostics.
"""
import importlib.util
import json
import os
import sys
import traceback
import unreal

sys.dont_write_bytecode = True
spec = importlib.util.spec_from_file_location("dy_open_forest_base",
    os.path.join(unreal.Paths.project_dir(), "Scripts", "Preview-P03ForestComposition.py"))
composition = importlib.util.module_from_spec(spec)
spec.loader.exec_module(composition)
forest, base = composition.forest, composition.base
AUDIT = "C:/UEProjects/DengYingShanHai/Saved/Audit-2026-10-04-P03BranchRefinement"
base.OUT = os.environ.get("DY_BRANCH_REFINEMENT_OUT", AUDIT + "/Run1")
base.require(os.path.commonpath((os.path.abspath(base.OUT), os.path.abspath(AUDIT)))
    == os.path.abspath(AUDIT), "Evidence output must stay within this refinement audit")

# Normalized emergence order, NOT seconds. Child starts after its parent completes.
EDGES = (
    ("root", "fork", 0.00, 0.04, 1.00),
    ("fork", "left_near", 0.04, 0.14, 0.80),
    ("fork", "right_near", 0.04, 0.14, 0.80),
    ("left_near", "left_exit", 0.14, 0.28, 0.72),
    ("right_near", "right_exit", 0.14, 0.28, 0.72),
    ("left_exit", "left_lower", 0.28, 0.46, 0.68),
    ("right_exit", "right_lower", 0.28, 0.46, 0.68),
    ("left_lower", "left_upper", 0.46, 0.70, 0.58),
    ("right_lower", "right_upper", 0.46, 0.70, 0.58),
    ("left_lower", "left_side", 0.46, 0.78, 0.42),
    ("right_lower", "right_side", 0.46, 0.78, 0.42),
    ("left_upper", "left_tip", 0.70, 1.00, 0.46),
    ("right_upper", "right_tip", 0.70, 1.00, 0.46),
    ("left_upper", "left_twig", 0.70, 1.00, 0.42),
    ("right_upper", "right_twig", 0.70, 1.00, 0.42),
)
# Both parent modules read their own globals. Do not leave a nine-Actor allocation.
composition.EDGES = forest.EDGES = EDGES


def record(event, **values):
    unreal.log("DY_BRANCH_REFINEMENT " + json.dumps(dict(event=event, **values), ensure_ascii=False))


class RefinedBranchPreview(composition.OpenForestPreview):
    def make_local_nodes(self, origin, height, width, clearance, left_y, right_y):
        gap = self.refs["gap"]
        left_exit_y, right_exit_y = gap[0] - width * .075, gap[1] + width * .09
        def point(y, dz):
            return unreal.Vector(origin.x, y, origin.z + dz)
        nodes = {
            "root": origin,
            "fork": point(origin.y, clearance * .10),
            "left_near": point(origin.y + (left_exit_y - origin.y) * .45, clearance * .22),
            "right_near": point(origin.y + (right_exit_y - origin.y) * .55, clearance * .28),
            "left_exit": point(left_exit_y, clearance * .60),
            "right_exit": point(right_exit_y, clearance * .64),
            "left_lower": point(left_exit_y - width * .19, height * .28),
            "left_upper": point(left_exit_y - width * .32, height * .62),
            "left_tip": point(left_exit_y - width * .40, height * .94),
            "right_lower": point(right_exit_y + width * .17, height * .34),
            "right_upper": point(right_exit_y + width * .29, height * .70),
            "right_tip": point(right_exit_y + width * .43, height * .97),
            "left_side": point(left_exit_y - width * .35, height * .42),
            "left_twig": point(left_exit_y - width * .20, height * .86),
            "right_side": point(right_exit_y + width * .36, height * .53),
            "right_twig": point(right_exit_y + width * .47, height * .84),
        }
        incoming = {child: (parent, finish, radius) for parent, child, begin, finish, radius in EDGES}
        for parent, child, begin, finish, radius in EDGES:
            base.require(parent in nodes and child in nodes and (nodes[child] - nodes[parent]).length() > 1e-6,
                "Missing/zero-length diagnostic branch")
            if parent != "root":
                base.require(begin >= incoming[parent][1] and radius <= incoming[parent][2],
                    "Child emerges before parent or widens toward tip")
        bounds = [min(n.y for n in nodes.values()), max(n.y for n in nodes.values()),
            min(n.z for n in nodes.values()), max(n.z for n in nodes.values())]
        record("RefinementLayout", branch_count=len(EDGES), node_count=len(nodes),
            actual_authored_local_nodes={name: base.xyz(n) for name, n in nodes.items()},
            projected_center_node_bounds=bounds, branch_thickness_factors=[e[4] for e in EDGES],
            stepped_diameters_not_smooth_taper=True, biological_model_claim=False,
            low_connection_retained=True, asymmetry_is_diagnostic=True,
            no_new_time_parameters=True, final_art_approved=False)
        return nodes


if __name__ == "__main__":
    unreal.EditorPythonScripting.set_keep_python_script_alive(True)
    preview = RefinedBranchPreview()
    try:
        preview.begin()
    except Exception:
        preview.error = traceback.format_exc()
        unreal.log_error("DY_BRANCH_REFINEMENT_SETUP_FAILURE " + preview.error)
        preview.finish()
