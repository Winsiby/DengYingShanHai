"""Bounded, ear-serpent-only cleanup of the trusted authored derivative.

Run with Blender --background --disable-autoexec --python this.py -- --diagnose
or --self-check or --build. No project or original source file is written.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
import math
from pathlib import Path
import sys
import traceback

import bpy
import numpy as np
from mathutils import Vector

STAGE = Path(__file__).resolve().parent
SOURCE = Path(r"D:\灯影山海\Assets\Sources\DengYingArt\KuafuRefined-20261015")
BLEND = SOURCE / "DY_Kuafu_PuppetRefined.blend"
FBX = SOURCE / "SK_DY_Kuafu_PuppetRefined.fbx"
META = SOURCE / "PUPPET_REFINED.json"
EAR_NAMES = {"SM_DY_Kuafu_SnakeEar_R", "SM_DY_Kuafu_SnakeEar_L"}
WELD_CM = 1e-4  # 1 micrometre; selected only after measuring source geometry.


def check(value, message):
    if not value:
        raise AssertionError(message)


def digest(value):
    return hashlib.sha256(json.dumps(value, separators=(",", ":"), sort_keys=True).encode()).hexdigest().upper()


def sha(path):
    check(path.name.casefold() != "licenses.md", "Restricted file must never be accessed")
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def write_json(path, value):
    check(path.resolve().is_relative_to(STAGE), "All output must stay in own stage")
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")


def extract(mesh, row):
    start, stop = row["vertex_start"], row["vertex_start"] + row["vertices"]
    polygons = [p for p in mesh.data.polygons if start <= p.vertices[0] < stop]
    check(len(polygons) == row["triangles"], row["name"] + ": exact ledger triangle ownership")
    check(all(start <= i < stop for p in polygons for i in p.vertices), row["name"] + ": no cross-part triangle")
    sharp = mesh.data.attributes.get("sharp_edge")
    packed = mesh.data.attributes.get("custom_normal")
    return dict(name=row["name"], bone=row["bone"], material=row["material"], kind=row["kind"],
                verts=[list(mesh.data.vertices[i].co) for i in range(start, stop)],
                faces=[list(i-start for i in p.vertices) for p in polygons],
                uv=[[list(mesh.data.uv_layers[0].data[i].uv) for i in p.loop_indices] for p in polygons],
                normals=[[list(mesh.data.corner_normals[i].vector) for i in p.loop_indices] for p in polygons],
                smooth=[p.use_smooth for p in polygons],
                packed_normals=[[list(packed.data[i].value) for i in p.loop_indices] for p in polygons] if packed else None,
                sharp_edges={str(tuple(i-start for i in e.vertices)): bool(sharp.data[e.index].value) for e in mesh.data.edges if all(start <= i < stop for i in e.vertices)} if sharp else {})


def metrics(part, detailed=False):
    v = np.asarray(part["verts"], dtype=np.float64)
    f = np.asarray(part["faces"], dtype=np.int64)
    uv = np.asarray(part["uv"], dtype=np.float64)
    areas = np.linalg.norm(np.cross(v[f[:, 1]]-v[f[:, 0]], v[f[:, 2]]-v[f[:, 0]]), axis=1)*.5
    uv_areas = abs((uv[:, 1, 0]-uv[:, 0, 0])*(uv[:, 2, 1]-uv[:, 0, 1])-(uv[:, 1, 1]-uv[:, 0, 1])*(uv[:, 2, 0]-uv[:, 0, 0]))*.5
    edges = Counter(tuple(sorted((a, b))) for face in part["faces"] for a, b in zip(face, face[1:]+face[:1]))
    dirs = Counter((a, b) for face in part["faces"] for a, b in zip(face, face[1:]+face[:1]))
    lengths = [math.dist(v[a], v[b]) for a, b in edges]
    volume = sum(float(np.dot(v[a], np.cross(v[b], v[c])))/6 for a, b, c in part["faces"])
    neighbors = {i: set() for i in range(len(v))}
    for a, b in edges:
        neighbors[a].add(b)
        neighbors[b].add(a)
    unseen, components = set(neighbors), 0
    while unseen:
        todo = [next(iter(unseen))]
        components += 1
        while todo:
            a = todo.pop()
            if a in unseen:
                unseen.remove(a)
                todo.extend(neighbors[a] & unseen)
    result = dict(vertices=len(v), triangles=len(f), edges=len(edges), connected_components=components,
                  non_two_face_edges=sum(n != 2 for n in edges.values()),
                  inconsistent_winding_edges=sum(dirs[(a, b)] != 1 or dirs[(b, a)] != 1 for a, b in edges),
                  signed_volume_cm3=volume, min_edge_cm=min(lengths),
                  min_triangle_area_cm2=float(areas.min()), zero_triangle_areas=int(np.count_nonzero(areas == 0)),
                  min_uv_triangle_area=float(uv_areas.min()), zero_uv_triangle_areas=int(np.count_nonzero(uv_areas == 0)),
                  bounds_cm=[[float(v[:, j].min()), float(v[:, j].max())] for j in range(3)],
                  short_edges=[dict(vertices=[a, b], length_cm=math.dist(v[a], v[b])) for a, b in edges if math.dist(v[a], v[b]) <= WELD_CM])
    if detailed:
        result["triangle_measurements"] = [dict(index=i, vertices=face, area_cm2=float(areas[i]), uv_area=float(uv_areas[i])) for i, face in enumerate(part["faces"])]
        result["edge_measurements"] = [dict(vertices=[a, b], length_cm=length, incident_triangles=edges[(a, b)]) for (a, b), length in zip(edges, lengths)]
    return result


def merge_map(vertices, threshold):
    # A cluster is allowed only if every member pair is within the stated bound.
    groups = []
    for i, p in enumerate(vertices):
        hit = next((g for g in groups if all(math.dist(p, vertices[j]) <= threshold for j in g)), None)
        if hit is None:
            groups.append([i])
        else:
            hit.append(i)
    representatives = [g[0] for g in groups]
    mapping = {old: new for new, group in enumerate(groups) for old in group}
    return representatives, mapping, groups


def clean_ear(part):
    reps, mapping, groups = merge_map(part["verts"], WELD_CM)
    new = dict(part)
    new["verts"] = [part["verts"][i] for i in reps]
    new["faces"], new["normals"], new["smooth"] = [], [], []
    new["packed_normals"], new["sharp_edges"] = None, {}
    removed = []
    for index, face in enumerate(part["faces"]):
        mapped = [mapping[i] for i in face]
        if len(set(mapped)) < 3:
            removed.append(index)
            continue
        new["faces"].append(mapped)
        a, b, c = [Vector(new["verts"][i]) for i in mapped]
        normal = list((b-a).cross(c-a).normalized())
        new["normals"].append([normal]*3)
        new["smooth"].append(False)
    # Locally normalized dominant-axis UV avoids float collapse of near points
    # in a full-source image atlas; no material uses a texture image.
    bounds = [(min(p[j] for p in new["verts"]), max(p[j] for p in new["verts"])) for j in range(3)]
    new["uv"] = []
    for face, normals in zip(new["faces"], new["normals"]):
        dominant = max(range(3), key=lambda j: abs(normals[0][j]))
        axes = [j for j in range(3) if j != dominant]
        new["uv"].append([[(new["verts"][i][j]-bounds[j][0])/(bounds[j][1]-bounds[j][0])*.8+.1 for j in axes] for i in face])
    displacement = [math.dist(p, new["verts"][mapping[i]]) for i, p in enumerate(part["verts"])]
    check(max(displacement) <= WELD_CM, part["name"] + ": weld displacement bound")
    before, after = metrics(part, True), metrics(new, True)
    check(after["non_two_face_edges"] == after["inconsistent_winding_edges"] == 0, part["name"] + ": closed consistently wound manifold")
    check(after["connected_components"] == 1 and after["signed_volume_cm3"] > 0, part["name"] + ": one positive-volume solid")
    check(after["zero_triangle_areas"] == after["zero_uv_triangle_areas"] == 0, part["name"] + ": positive actual and UV triangle areas")
    check(after["min_edge_cm"] > WELD_CM, part["name"] + ": no short edges remain")
    return new, dict(name=part["name"], method="deterministic complete-link clusters represented by earliest existing vertex; remove only index-collapsed faces", threshold_cm=WELD_CM,
                     max_vertex_displacement_cm=max(displacement), max_cluster_diameter_cm=max(math.dist(part["verts"][a], part["verts"][b]) for g in groups for a in g for b in g),
                     merged_clusters=[dict(source_vertices=g, retained_source_vertex=g[0], positions_cm=[part["verts"][i] for i in g]) for g in groups if len(g) > 1],
                     source_to_clean_vertices=mapping, removed_source_face_indices=removed,
                     before=before, after=after, signed_volume_delta_cm3=after["signed_volume_cm3"]-before["signed_volume_cm3"])


def skeleton(arm):
    return {b.name: dict(parent=b.parent.name if b.parent else None, matrix=[list(r) for r in b.matrix_local], head=list(b.head_local), tail=list(b.tail_local), deform=b.use_deform) for b in arm.data.bones}


def action_data():
    return {a.name: dict(frame_range=list(a.frame_range), fcurves=[dict(path=f.data_path, index=f.array_index, extrapolation=f.extrapolation,
        keys=[dict(co=list(k.co), interpolation=k.interpolation, easing=k.easing, left=list(k.handle_left), right=list(k.handle_right), left_type=k.handle_left_type, right_type=k.handle_right_type) for k in f.keyframe_points]) for f in a.fcurves]) for a in bpy.data.actions}


def poses(arm):
    result = {}
    for action in bpy.data.actions:
        arm.animation_data.action = action
        result[action.name] = {}
        for frame in (1, 16, 31):
            bpy.context.scene.frame_set(frame)
            bpy.context.view_layer.update()
            result[action.name][str(frame)] = {b.name: [list(r) for r in b.matrix] for b in arm.pose.bones}
    return result


def build_mesh(old, parts):
    verts, faces, ledger, face_data, edge_sharp = [], [], [], [], {}
    materials = {m.name.removeprefix("MI_DY_"): i for i, m in enumerate(old.data.materials)}
    for part in parts:
        start = len(verts)
        verts.extend(part["verts"])
        faces.extend([tuple(i+start for i in face) for face in part["faces"]])
        packed = part["packed_normals"] if part["packed_normals"] is not None else [None]*len(part["faces"])
        face_data.extend(zip(part["uv"], part["normals"], part["smooth"], [materials[part["material"]]]*len(part["faces"]), packed))
        for edge, value in part["sharp_edges"].items():
            import ast
            edge_sharp[tuple(i+start for i in ast.literal_eval(edge))] = value
        ledger.append({k: part[k] for k in ("name", "bone", "material", "kind")} | dict(vertex_start=start, vertices=len(part["verts"]), triangles=len(part["faces"])))
    data = bpy.data.meshes.new("SK_DY_Kuafu_PuppetCleanGeometry")
    data.from_pydata(verts, [], faces)
    data.update()
    for material in old.data.materials:
        data.materials.append(material)
    uv = data.uv_layers.new(name=old.data.uv_layers[0].name)
    normals = []
    for poly, (coords, ns, smooth, mid, packed) in zip(data.polygons, face_data):
        poly.material_index, poly.use_smooth = mid, smooth
        for li, co, normal in zip(poly.loop_indices, coords, ns):
            uv.data[li].uv = co
            normals.append(normal)
    data.normals_split_custom_set(normals)
    # Re-encoding a decoded custom normal is lossy. Copy original packed values
    # and their sharp-edge normal-space inputs for all untouched parts instead.
    sharp = data.attributes.get("sharp_edge")
    if sharp is None:
        sharp = data.attributes.new("sharp_edge", "BOOLEAN", "EDGE")
    for edge in data.edges:
        key = tuple(edge.vertices)
        sharp.data[edge.index].value = edge_sharp.get(key, edge_sharp.get(tuple(reversed(key)), False))
    packed_attr = data.attributes["custom_normal"]
    for poly, values in zip(data.polygons, face_data):
        packed = values[4]
        if packed is not None:
            for li, value in zip(poly.loop_indices, packed):
                packed_attr.data[li].value = value
    data.update()
    new = old.copy()
    new.data, new.name = data, "SK_DY_Kuafu_PuppetClean"
    bpy.context.collection.objects.link(new)
    new.vertex_groups.clear()
    for group in old.vertex_groups:
        new.vertex_groups.new(name=group.name)
    for row in ledger:
        new.vertex_groups[row["bone"]].add(list(range(row["vertex_start"], row["vertex_start"]+row["vertices"])), 1, "REPLACE")
    return new, ledger


def self_check():
    reps, mapping, groups = merge_map([(0, 0, 0), (0, 0, .00005), (0, 0, .00014), (0, 1, 0)], .0001)
    check(reps == [0, 2, 3] and mapping == {0: 0, 1: 0, 2: 1, 3: 2}, "Complete-link clustering must not chain beyond threshold")
    check(groups == [[0, 1], [2], [3]], "Deterministic representative is an existing original point")
    print("SELF_CHECK_PASS: bounded non-chaining weld and deterministic representatives", flush=True)


def main(args):
    meta = json.loads(META.read_text(encoding="utf-8"))
    protected = [BLEND, FBX, META] + [Path(p) for p in meta["source_hashes_before"]]
    before_hashes = {str(p): sha(p) for p in protected}
    bpy.ops.wm.open_mainfile(filepath=str(BLEND), use_scripts=False)
    old = bpy.data.objects["SK_DY_Kuafu_PuppetRefined"]
    parts = [extract(old, row) for row in meta["part_ledger"]]
    check(len(parts) == 266 and sum(len(p["verts"]) for p in parts) == len(old.data.vertices), "Exact 266-part complete ownership")
    ear_metrics = {p["name"]: metrics(p, True) for p in parts if p["name"] in EAR_NAMES}
    if args.diagnose:
        write_json(STAGE/"EAR_SOURCE_DIAGNOSTIC.json", dict(source=str(BLEND), units="cm", threshold_candidate_cm=WELD_CM, ears=ear_metrics))
        print(json.dumps({name: {k: value for k, value in m.items() if k not in ("triangle_measurements", "edge_measurements")} for name, m in ear_metrics.items()}, ensure_ascii=False), flush=True)
        return
    index = 1
    while (STAGE / f"Clean-Run{index}").exists():
        index += 1
    out = STAGE / f"Clean-Run{index}"
    out.mkdir()
    report = dict(status="RUNNING", source=str(BLEND), no_ue_started=True, only_changed_parts=sorted(EAR_NAMES), source_hashes_before=before_hashes,
                  skeleton_before=skeleton(old.parent), actions_before=action_data(), pose_matrices_before=poses(old.parent), cleanup=[], unchanged_parts=[])
    try:
        check(all(not any(n.type == "TEX_IMAGE" for n in m.node_tree.nodes) for m in old.data.materials if m.use_nodes), "UV remap affects no texture image; original six material graphs retained")
        cleaned = []
        for part in parts:
            if part["name"] in EAR_NAMES:
                part, row = clean_ear(part)
                report["cleanup"].append(row)
            cleaned.append(part)
        new, ledger = build_mesh(old, cleaned)
        report["part_ledger"] = ledger
        # Re-read built float mesh, not just Python construction inputs.
        built = [extract(new, row) for row in ledger]
        for original, actual in zip(parts, built):
            if original["name"] not in EAR_NAMES:
                check(original == actual, original["name"] + ": unchanged geometry, winding, normals, smooth flags and UV exact")
                report["unchanged_parts"].append(dict(name=original["name"], signature=digest(original)))
            else:
                m = metrics(actual, True)
                check(m["non_two_face_edges"] == m["inconsistent_winding_edges"] == m["zero_triangle_areas"] == m["zero_uv_triangle_areas"] == 0, original["name"] + ": built mesh topology and UV positive")
                report.setdefault("built_ear_metrics", {})[actual["name"]] = m
        report["all_part_metrics"] = {p["name"]: metrics(p) for p in built}
        check(all(m["zero_triangle_areas"] == m["zero_uv_triangle_areas"] == 0 for m in report["all_part_metrics"].values()), "Every actual triangle in full mesh has positive geometry and UV area")
        check(len(new.data.materials) == 6 and len(new.data.uv_layers) == 1, "Six original material objects and one UV retained")
        check(all(len(v.groups) == 1 and v.groups[0].weight == 1 for v in new.data.vertices), "All vertices retain one rigid weight equal to one")
        check(new.matrix_world == old.matrix_world and new.parent == old.parent, "Original object transform and armature parent retained")
        report["skeleton_after"] = skeleton(new.parent)
        report["actions_after"] = action_data()
        report["pose_matrices_after"] = poses(new.parent)
        check(report["skeleton_before"] == report["skeleton_after"] == meta["skeleton"], "All twenty original bones, hierarchy and StaffGrip rest matrices exact")
        check(report["actions_before"] == report["actions_after"] and len(report["actions_after"]) == 3, "All three original complete animation curves exact")
        check(report["pose_matrices_before"] == report["pose_matrices_after"], "All twenty pose matrices exact in three actions at 1/16/31")
        for name, frames in meta["pose_matrices"].items():
            check(report["pose_matrices_after"]["A_DY_Kuafu_"+name] == frames, "Source metadata pose matrices exact: "+name)
        old.hide_render, old.hide_viewport = True, True
        old.hide_set(True)
        arm = new.parent
        arm.animation_data.action = bpy.data.actions["A_DY_Kuafu_StrideMid"]
        bpy.context.scene.frame_set(1)
        bpy.context.view_layer.update()
        bpy.ops.object.select_all(action="DESELECT")
        new.select_set(True)
        arm.select_set(True)
        bpy.context.view_layer.objects.active = new
        new.hide_render, new.hide_viewport = False, False
        new.hide_set(False)
        fbx, blend = out/"SK_DY_Kuafu_PuppetClean.fbx", out/"DY_Kuafu_PuppetClean.blend"
        bpy.ops.export_scene.fbx(filepath=str(fbx), use_selection=True, object_types={"ARMATURE", "MESH"}, global_scale=1,
            apply_unit_scale=True, apply_scale_options="FBX_SCALE_NONE", axis_forward="-Z", axis_up="Y", add_leaf_bones=False,
            primary_bone_axis="Y", secondary_bone_axis="X", armature_nodetype="NULL", use_armature_deform_only=False,
            bake_anim=True, bake_anim_use_all_bones=True, bake_anim_use_all_actions=True, bake_anim_use_nla_strips=False,
            bake_anim_force_startend_keying=True, path_mode="AUTO", embed_textures=False)
        bpy.ops.wm.save_as_mainfile(filepath=str(blend))
        report["mesh"] = dict(name=new.name, vertices=len(new.data.vertices), triangles=len(new.data.polygons), bones=len(arm.data.bones), materials=[m.name for m in new.data.materials], uv_sets=len(new.data.uv_layers))
        report["source_hashes_after"] = {str(p): sha(p) for p in protected}
        check(report["source_hashes_after"] == before_hashes, "Every original/refined source and metadata hash unchanged")
        report["artifacts"] = {p.name: dict(bytes=p.stat().st_size, sha256=sha(p)) for p in (fbx, blend)}
        report["status"] = "PASS_BOUNDED_EAR_ONLY_CLEANUP_PENDING_COLD_FBX_NATIVE_AND_VISUAL_QA"
        print(json.dumps(dict(status=report["status"], mesh=report["mesh"], changed=[dict(name=r["name"], max_displacement_cm=r["max_vertex_displacement_cm"], before_vertices=r["before"]["vertices"], after_vertices=r["after"]["vertices"], before_triangles=r["before"]["triangles"], after_triangles=r["after"]["triangles"], min_edge_cm=r["after"]["min_edge_cm"], min_area_cm2=r["after"]["min_triangle_area_cm2"], min_uv_area=r["after"]["min_uv_triangle_area"]) for r in report["cleanup"]]), ensure_ascii=False), flush=True)
    except Exception:
        report["status"], report["error"] = "FAILED_PRESERVED", traceback.format_exc()
        raise
    finally:
        write_json(out/"PUPPET_CLEAN.json", report)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--diagnose", action="store_true")
    parser.add_argument("--self-check", action="store_true")
    parser.add_argument("--build", action="store_true")
    args = parser.parse_args(sys.argv[sys.argv.index("--")+1:] if "--" in sys.argv else [])
    if args.self_check:
        self_check()
    if args.diagnose or args.build:
        main(args)
