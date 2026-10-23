"""Independent cold-read and raw FBX inspection of own bounded derivative."""
from collections import Counter
import importlib.util
import json
import math
from pathlib import Path
import sys
import traceback

import bpy
import numpy as np
from io_scene_fbx import parse_fbx
from mathutils import Vector

STAGE = Path(__file__).resolve().parent
RUN = STAGE / "Clean-Run2"
spec = importlib.util.spec_from_file_location("clean", STAGE/"clean_puppet.py")
clean = importlib.util.module_from_spec(spec)
spec.loader.exec_module(clean)
R = dict(status="RUNNING", checks=[], no_ue_started=True, no_original_source_writes=True)


def check(value, message):
    if not value:
        raise AssertionError(message)
    R["checks"].append(message)


def find(e, name):
    return next(c for c in e.elems if c.id == name)


def txt(value):
    return value.decode("utf-8", errors="replace").split("\x00")[0] if isinstance(value, bytes) else value


def layer_values(layer, kind, corners, size):
    values = np.asarray(find(layer, kind).props[0], dtype=np.float64).reshape(-1, size)
    mapping, reference = txt(find(layer, b"MappingInformationType").props[0]), txt(find(layer, b"ReferenceInformationType").props[0])
    ids = np.arange(len(corners)) if mapping == "ByPolygonVertex" else corners
    check(mapping in ("ByPolygonVertex", "ByControlPoint", "ByVertice"), "Recognized actual raw FBX layer mapping")
    if reference in ("IndexToDirect", "Index"):
        ids = np.asarray(find(layer, kind+b"Index").props[0], dtype=np.int64)[ids]
    else:
        check(reference == "Direct", "Recognized raw FBX direct layer")
    return values[ids]


def raw(path):
    root, version = parse_fbx.parse(str(path))
    objects, connections = find(root, b"Objects"), find(root, b"Connections")
    by_id = {e.props[0]: e for e in objects.elems}
    geometries = [e for e in objects.elems if e.id == b"Geometry" and e.props[-1] == b"Mesh"]
    check(len(geometries) == 1, path.name+": exactly one raw FBX mesh")
    geo = geometries[0]
    v = np.asarray(find(geo, b"Vertices").props[0], dtype=np.float64).reshape(-1, 3)
    ix = np.asarray(find(geo, b"PolygonVertexIndex").props[0], dtype=np.int64)
    check(np.all(np.diff(np.r_[-1, np.flatnonzero(ix < 0)]) == 3), path.name+": all actual raw polygons triangles")
    corners = np.where(ix < 0, -ix-1, ix)
    uv_layers = [e for e in geo.elems if e.id == b"LayerElementUV"]
    check(len(uv_layers) == 1, path.name+": exactly one actual raw UV")
    uv = layer_values(uv_layers[0], b"UV", corners, 2)
    normals = layer_values(find(geo, b"LayerElementNormal"), b"Normals", corners, 3)
    links = [tuple(e.props) for e in connections.elems if e.props[0] == b"OO"]
    clusters = [e for e in objects.elems if e.id == b"Deformer" and e.props[-1] == b"Cluster"]
    weights, bone_ids = [[] for _ in v], {}
    for cluster in clusters:
        ids = [c for _, c, p in links if p == cluster.props[0] and by_id.get(c) and by_id[c].id == b"Model"]
        check(len(ids) == 1, path.name+": one real bone per skin cluster")
        name = txt(by_id[ids[0]].props[1])
        bone_ids[name] = ids[0]
        indices = next((e for e in cluster.elems if e.id == b"Indexes"), None)
        ws = next((e for e in cluster.elems if e.id == b"Weights"), None)
        if indices is not None:
            check(ws is not None and len(indices.props[0]) == len(ws.props[0]), "Actual cluster weights account for control points")
            for i, w in zip(indices.props[0], ws.props[0]):
                if w > 1e-7:
                    weights[i].append([name, float(w)])
    parents = {}
    for name, uid in bone_ids.items():
        linked = [p for _, c, p in links if c == uid and p in bone_ids.values()]
        parents[name] = next((n for n, i in bone_ids.items() if linked and i == linked[0]), None)
    check(all(len(w) == 1 and w[0][1] == 1 for w in weights), path.name+": every actual control point rigid to one authored bone at 1.0")
    points = v[corners].reshape(-1, 3, 3)
    tex = uv.reshape(-1, 3, 2)
    areas = np.linalg.norm(np.cross(points[:, 1]-points[:, 0], points[:, 2]-points[:, 0]), axis=1)*.5
    uv_areas = abs((tex[:, 1, 0]-tex[:, 0, 0])*(tex[:, 2, 1]-tex[:, 0, 1])-(tex[:, 1, 1]-tex[:, 0, 1])*(tex[:, 2, 0]-tex[:, 0, 0]))*.5
    animations = []
    all_links = [tuple(e.props) for e in connections.elems]
    for e in objects.elems:
        if e.id == b"AnimationCurve":
            node_links = [c for c in all_links if len(c) > 3 and c[0] == b"OP" and c[1] == e.props[0]]
            check(len(node_links) == 1, "Every raw animation curve has exactly one node/axis binding")
            node_id, axis = node_links[0][2], txt(node_links[0][3])
            targets = [c for c in all_links if len(c) > 3 and c[0] == b"OP" and c[1] == node_id]
            layers = [p for _, c, p in links if c == node_id]
            check(len(targets) == len(layers) == 1, "Every raw curve node has exactly one property target and take layer")
            stacks = [p for _, c, p in links if c == layers[0]]
            check(len(stacks) == 1, "Every raw curve layer belongs to one authored animation take")
            binding = dict(bone=txt(by_id[targets[0][2]].props[1]), property=txt(targets[0][3]), axis=axis,
                           take=txt(by_id[stacks[0]].props[1]), layer=txt(by_id[layers[0]].props[1]))
            animations.append(dict(binding=binding, keys={c.id.decode(): list(c.props[0]) for c in e.elems if c.id in (b"KeyTime", b"KeyValueFloat", b"KeyAttrFlags", b"KeyAttrDataFloat", b"KeyAttrRefCount")}))
    animations.sort(key=lambda v: json.dumps(v["binding"], sort_keys=True))
    return dict(vertices=v, corners=corners, uv=uv, normals=normals, weights=weights, parents=parents, animations=animations,
                summary=dict(vertices=len(v), triangles=len(points), bones=len(bone_ids), uv_sets=1, min_area_cm2=float(areas.min()), min_uv_area=float(uv_areas.min()), zero_geometry_triangles=int(np.count_nonzero(areas == 0)), zero_uv_triangles=int(np.count_nonzero(uv_areas == 0)), raw_animation_curves=len(animations)))


def render_pair():
    bpy.ops.wm.open_mainfile(filepath=str(RUN/"DY_Kuafu_PuppetClean.blend"), use_scripts=False)
    old, new = bpy.data.objects["SK_DY_Kuafu_PuppetRefined"], bpy.data.objects["SK_DY_Kuafu_PuppetClean"]
    arm = new.parent
    arm.animation_data.action = bpy.data.actions["A_DY_Kuafu_StrideMid"]
    bpy.context.scene.frame_set(1)
    scene = bpy.context.scene
    for obj in scene.objects:
        obj.hide_render = obj not in (old, new, arm)
    scene.render.engine = "BLENDER_WORKBENCH"
    scene.display.shading.light = "STUDIO"
    scene.display.shading.color_type = "MATERIAL"
    scene.display.shading.show_shadows = True
    scene.display.shading.show_cavity = False
    scene.display.shading.background_type = "WORLD"
    scene.world.color = (.65, .65, .65)
    bpy.ops.object.camera_add(location=(700, -10, 208))
    camera = bpy.context.object
    camera.rotation_euler = (Vector((0, -10, 208))-camera.location).to_track_quat("-Z", "Y").to_euler()
    camera.data.type, camera.data.ortho_scale = "ORTHO", 90
    scene.camera = camera
    scene.render.resolution_x, scene.render.resolution_y, scene.render.resolution_percentage = 1100, 1100, 100
    scene.render.image_settings.file_format = "PNG"
    captures = []
    for label, shown, hidden in (("RefinedBefore", old, new), ("CleanAfter", new, old)):
        shown.hide_render, shown.hide_viewport = False, False
        shown.hide_set(False)
        hidden.hide_render = True
        hidden.hide_set(True)
        scene.render.filepath = str(RUN/(label+"_Ears.png"))
        bpy.context.view_layer.update()
        bpy.ops.render.render(write_still=True)
        captures.append(dict(file=scene.render.filepath, sha256=clean.sha(Path(scene.render.filepath)), view="actual full source mesh material-color workbench; source StrideMid frame1; no source resave; no transparency or disabled ear sections"))
    R["captures"] = captures
    a = bpy.data.images.load(captures[0]["file"], check_existing=False)
    b = bpy.data.images.load(captures[1]["file"], check_existing=False)
    difference = abs(np.asarray(a.pixels[:], dtype=np.float64)-np.asarray(b.pixels[:], dtype=np.float64))
    R["preview_pixel_comparison"] = dict(resolution=[1100, 1100], unequal_channels=int(np.count_nonzero(difference)), maximum_channel_error=float(difference.max()),
        limitation="Workbench source appearance under one fixed view/pose only; not UE native shadows")


def main():
    report = json.loads((RUN/"PUPPET_CLEAN.json").read_text(encoding="utf-8"))
    before = {str(p): clean.sha(p) for p in (RUN/"DY_Kuafu_PuppetClean.blend", RUN/"SK_DY_Kuafu_PuppetClean.fbx")}
    check(report["status"].startswith("PASS_"), "Construction checks passed before cold inspection")
    bpy.ops.wm.open_mainfile(filepath=str(RUN/"DY_Kuafu_PuppetClean.blend"), use_scripts=False)
    mesh = bpy.data.objects["SK_DY_Kuafu_PuppetClean"]
    check(clean.skeleton(mesh.parent) == report["skeleton_before"], "Cold blend: all 20 authored rest matrices and StaffGrip exact")
    check(clean.action_data() == report["actions_before"], "Cold blend: all three complete authored animation curves exact")
    check(clean.poses(mesh.parent) == report["pose_matrices_before"], "Cold blend: three poses, frames1/16/31, every bone matrix exact")
    parts = [clean.extract(mesh, row) for row in report["part_ledger"]]
    expected = {r["name"]: r["signature"] for r in report["unchanged_parts"]}
    check(len(expected) == 264, "Cold blend: exactly 264 untouched ledger parts")
    for part in parts:
        if part["name"] in expected:
            check(clean.digest(part) == expected[part["name"]], part["name"]+": cold geometry/UV/packed normals/hard edges signature exact")
    R["cold_ear_metrics"] = {p["name"]: clean.metrics(p, True) for p in parts if p["name"] in clean.EAR_NAMES}
    check(all(m["non_two_face_edges"] == m["inconsistent_winding_edges"] == m["zero_triangle_areas"] == m["zero_uv_triangle_areas"] == 0 and m["connected_components"] == 1 and m["signed_volume_cm3"] > 0 for m in R["cold_ear_metrics"].values()), "Cold ears: every edge two triangles, outward, positive volume and geometry/UV areas")
    old_meta = json.loads(clean.META.read_text(encoding="utf-8"))
    old_mesh = bpy.data.objects["SK_DY_Kuafu_PuppetRefined"]
    old_ears = {row["name"]: clean.extract(old_mesh, row) for row in old_meta["part_ledger"] if row["name"] in clean.EAR_NAMES}
    R["surface_correspondence_bounds"] = []
    for repair in report["cleanup"]:
        part = next(p for p in parts if p["name"] == repair["name"])
        old = old_ears[part["name"]]
        mapping = {int(k): v for k, v in repair["source_to_clean_vertices"].items()}
        actual_edges = {tuple(sorted((a, b))) for face in part["faces"] for a, b in zip(face, face[1:]+face[:1])}
        remapped = [[mapping[i] for i in face] for face in old["faces"]]
        kept = [face for face in remapped if len(set(face)) == 3]
        collapsed = [sorted(set(face)) for face in remapped if len(set(face)) < 3]
        check(kept == part["faces"], part["name"]+": every surviving face is original topological correspondence after bounded weld")
        check(all(len(ids) == 1 or tuple(ids) in actual_edges for ids in collapsed), part["name"]+": every collapsed source face maps onto a surviving actual edge/vertex")
        maximum = max(math.dist(p, part["verts"][mapping[i]]) for i, p in enumerate(old["verts"]))
        check(maximum == repair["max_vertex_displacement_cm"] and maximum <= clean.WELD_CM, part["name"]+": cold per-vertex displacement equals measured construction and is below1micrometre")
        R["surface_correspondence_bounds"].append(dict(name=part["name"], symmetric_surface_distance_upper_bound_cm=maximum,
            proof="Every source triangle maps barycentrically to a surviving triangle or its actual edge/vertex; vertex displacement bounds each affine image. Each surviving clean triangle has its source preimage."))
    src, dst = raw(clean.FBX), raw(RUN/"SK_DY_Kuafu_PuppetClean.fbx")
    R["source_raw_fbx"], R["clean_raw_fbx"] = src["summary"], dst["summary"]
    check(dst["parents"] == src["parents"] == {n: b["parent"] for n, b in report["skeleton_before"].items()}, "Raw FBX exactly twenty original skin bones and parent hierarchy")
    check(dst["animations"] == src["animations"] and len(dst["animations"]) > 0, "Raw FBX original baked animation curve key times/values/attributes exact")
    check(dst["summary"]["triangles"] == 17886 and dst["summary"]["zero_geometry_triangles"] == dst["summary"]["zero_uv_triangles"] == 0, "Raw FBX every one of 17,886 geometry and UV triangles positive")
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.context.scene.unit_settings.system, bpy.context.scene.unit_settings.scale_length = "METRIC", .01
    bpy.ops.import_scene.fbx(filepath=str(RUN/"SK_DY_Kuafu_PuppetClean.fbx"), use_anim=False, ignore_leaf_bones=False)
    meshes = [o for o in bpy.context.scene.objects if o.type == "MESH"]
    arms = [o for o in bpy.context.scene.objects if o.type == "ARMATURE"]
    check(len(meshes) == len(arms) == 1 and len(arms[0].data.bones) == 20, "Cold imported FBX one mesh and exactly20 authored bones")
    imported = meshes[0]
    check(len(imported.data.polygons) == 17886 and len(imported.data.uv_layers) == 1 and len(imported.data.materials) == 6, "Cold imported FBX full triangle count, six materials and one UV")
    zero = []
    minimum = math.inf
    for p in imported.data.polygons:
        uv = [imported.data.uv_layers[0].data[i].uv for i in p.loop_indices]
        area = abs((uv[1].x-uv[0].x)*(uv[2].y-uv[0].y)-(uv[1].y-uv[0].y)*(uv[2].x-uv[0].x))*.5
        minimum = min(minimum, area)
        if area == 0:
            zero.append(p.index)
    check(not zero, "Cold imported FBX every UV triangle remains positive after float conversion")
    check(all(len(v.groups) == 1 and v.groups[0].weight == 1 for v in imported.data.vertices), "Cold imported FBX every vertex rigid weight1")
    R["cold_import"] = dict(vertices=len(imported.data.vertices), triangles=len(imported.data.polygons), materials=len(imported.data.materials), uv_sets=1, bones=len(arms[0].data.bones), min_uv_area=minimum, zero_uv_triangles=zero)
    render_pair()
    check(before == {p: clean.sha(Path(p)) for p in before}, "Cold audit and source preview do not resave derivative blend/FBX")
    check(all(clean.sha(Path(p)) == h for p, h in report["source_hashes_before"].items()), "Every original and refined source/evidence/author hash still unchanged")
    R["status"] = "PASS_COLD_BLEND_AND_FBX_BOUNDED_EAR_ONLY_REPAIR_NATIVE_AND_VISUAL_REVIEW_PENDING"
    print(json.dumps({k: R[k] for k in ("status", "source_raw_fbx", "clean_raw_fbx", "cold_import")}, ensure_ascii=False), flush=True)


try:
    main()
except Exception:
    R["status"], R["error"] = "FAILED_PRESERVED", traceback.format_exc()
    raise
finally:
    clean.write_json(RUN/"PUPPET_CLEAN_COLD.json", R)
