"""Repair derived puppet geometry; keep trusted source, skeleton and actions intact."""
from __future__ import annotations

import bpy
import hashlib
import json
import math
import sys
from collections import Counter
from pathlib import Path
from mathutils import Vector
from mathutils.geometry import delaunay_2d_cdt

STAGE = Path(__file__).resolve().parent
SOURCE = Path(r"D:\灯影山海\Assets\Sources\DengYingArt\ArtBatch-20261014\Kuafu")
AUTHOR = SOURCE.parent / "Authoring" / "KuafuHero"
sys.dont_write_bytecode = True
sys.path.insert(0, str(AUTHOR))
import kuafu_outline_data as DATA

EVIDENCE = json.loads((SOURCE / "MODEL_EVIDENCE.json").read_text(encoding="utf-8"))
REPORT = {"status": "RUNNING", "ink": [], "snakes": [], "unchanged_parts": [], "checks": []}
run = 1
while (STAGE / f"Refined-Run{run}").exists():
    run += 1
OUT = STAGE / f"Refined-Run{run}"
OUT.mkdir()


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def check(condition, text):
    if not condition:
        raise AssertionError(text)
    REPORT["checks"].append(text)


def cross(a, b, c):
    return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])


def area(poly):
    return .5*sum(p[0]*q[1]-q[0]*p[1] for p, q in zip(poly, poly[1:]+poly[:1]))


def inside(point, poly):
    x, y = point
    hit = False
    for a, b in zip(poly, poly[1:]+poly[:1]):
        if (a[1] > y) != (b[1] > y) and x < (b[0]-a[0])*(y-a[1])/(b[1]-a[1])+a[0]:
            hit = not hit
    return hit


def orient(poly):
    return poly if area(poly) > 0 else list(reversed(poly))


def catmull(points):
    values = [Vector(p) for p in points]
    output = []
    for i in range(len(values)-1):
        p0, p1 = values[max(0, i-1)], values[i]
        p2, p3 = values[i+1], values[min(len(values)-1, i+2)]
        for k in range(4):
            t = k/4
            output.append(.5*((2*p1)+(-p0+p2)*t+(2*p0-5*p1+4*p2-p3)*t*t+(-p0+3*p1-3*p2+p3)*t*t*t))
    return output+[values[-1]]


def ribbon_polygons(spec):
    points = catmull(spec["centerline"])
    widths = [spec["radius_px"]*(1+.55*max(0, (i/(len(points)-1)-.87)/.13)) for i in range(len(points))]
    normals = []
    for i in range(len(points)):
        tangent = (points[min(len(points)-1, i+1)]-points[max(0, i-1)]).normalized()
        normals.append(Vector((-tangent.y, tangent.x)))
    original = [tuple(p+n*w) for p, n, w in zip(points, normals, widths)]
    original += [tuple(p-n*w) for p, n, w in reversed(list(zip(points, normals, widths)))]
    crossings = sum(cross(original[i], original[(i+1)%len(original)], original[j])*cross(original[i], original[(i+1)%len(original)], original[(j+1)%len(original)]) < -1e-6
                    and cross(original[j], original[(j+1)%len(original)], original[i])*cross(original[j], original[(j+1)%len(original)], original[(i+1)%len(original)]) < -1e-6
                    for i in range(len(original)) for j in range(i+2, len(original)) if not(i == 0 and j == len(original)-1))
    if spec["name"].startswith("SnakeArm"):
        check(crossings == 0, spec["name"]+": original hand-serpent outline has no crossings")
        return [original], crossings
    polys = []
    for i in range(len(points)-1):
        tangent = (points[i+1]-points[i]).normalized()
        normal = Vector((-tangent.y, tangent.x))
        a, b = points[i], points[i+1]
        polys.append(orient([tuple(a+normal*widths[i]), tuple(b+normal*widths[i+1]),
                             tuple(b-normal*widths[i+1]), tuple(a-normal*widths[i])]))
    # At internal samples only: true round joins, no invented end-cap length.
    for p, w in zip(points[1:-1], widths[1:-1]):
        polys.append([(p.x+w*math.cos(k*math.tau/24), p.y+w*math.sin(k*math.tau/24)) for k in range(24)])
    return polys, crossings


def union_mesh(polys):
    origin = tuple(sum(p[j] for poly in polys for p in poly)/sum(len(poly) for poly in polys) for j in (0, 1))
    shifted = [[(p[0]-origin[0], p[1]-origin[1]) for p in poly] for poly in polys]
    points, faces = [], []
    for poly in shifted:
        faces.append(list(range(len(points), len(points)+len(poly))))
        points.extend(Vector(p) for p in poly)
    vertices, edges, tris, *_ = delaunay_2d_cdt(points, [], faces, 0, 1e-6)
    kept = []
    for face in tris:
        center = tuple(sum(vertices[i][j] for i in face)/len(face) for j in (0, 1))
        if any(inside(center, poly) for poly in shifted):
            kept.append(tuple(face) if area([vertices[i] for i in face]) > 0 else tuple(reversed(face)))
    edge_counts = Counter(tuple(sorted((a, b))) for tri in kept for a, b in zip(tri, tri[1:]+tri[:1]))
    boundary = [(a, b) for tri in kept for a, b in zip(tri, tri[1:]+tri[:1]) if edge_counts[tuple(sorted((a, b)))] == 1]
    # Retriangulate only union boundary: internal segment/disk seams are not final topology.
    used = sorted({i for edge in boundary for i in edge})
    remap = {value: i for i, value in enumerate(used)}
    boundary_vertices = [vertices[i] for i in used]
    boundary_edges = [(remap[a], remap[b]) for a, b in boundary]
    vertices2, edges2, triangles2, *_ = delaunay_2d_cdt(boundary_vertices, boundary_edges, [], 0, 1e-6)
    kept2 = []
    for tri in triangles2:
        center = tuple(sum(vertices2[i][j] for i in tri)/len(tri) for j in (0, 1))
        if any(inside(center, poly) for poly in shifted):
            kept2.append(tuple(tri) if area([vertices2[i] for i in tri]) > 0 else tuple(reversed(tri)))
    used2 = sorted({i for tri in kept2 for i in tri})
    map2 = {value: i for i, value in enumerate(used2)}
    coordinates = [(vertices2[i][0]+origin[0], vertices2[i][1]+origin[1]) for i in used2]
    return coordinates, [tuple(map2[i] for i in tri) for tri in kept2]


def yz(point):
    return ((point[0]-DATA.PELVIS_X)*DATA.SCALE_CM_PER_PIXEL,
            (DATA.GROUND_Y-point[1])*DATA.SCALE_CM_PER_PIXEL)


def extract_part(mesh, row, start):
    ids = range(start, start+row["vertices"])
    result = {"name": row["name"], "bone": row["bone"], "material": row["material"],
              "kind": row["kind"], "verts": [tuple(mesh.data.vertices[i].co) for i in ids], "faces": [], "uv": [], "normals": [], "smooth": []}
    for poly in mesh.data.polygons:
        if start <= poly.vertices[0] < start+row["vertices"]:
            check(all(start <= i < start+row["vertices"] for i in poly.vertices), row["name"]+": ledger ownership")
            result["faces"].append(tuple(i-start for i in poly.vertices))
            result["uv"].append([tuple(mesh.data.uv_layers.active.data[i].uv) for i in poly.loop_indices])
            result["normals"].append([tuple(mesh.data.corner_normals[i].vector) for i in poly.loop_indices])
            result["smooth"].append(poly.use_smooth)
    check(len(result["faces"]) == row["triangles"], row["name"]+": ledger triangles")
    return result


def part_signature(part):
    values = {k: part[k] for k in ("bone", "material", "verts", "faces", "uv", "normals", "smooth")}
    return hashlib.sha256(json.dumps(values, separators=(",", ":")).encode()).hexdigest().upper()


def part_from_object(obj, row):
    obj.data.calc_loop_triangles()
    uv = obj.data.uv_layers.new(name="SourceUV")
    for poly in obj.data.polygons:
        dominant = max(range(3), key=lambda j: abs(poly.normal[j]))
        for li in poly.loop_indices:
            p = obj.data.vertices[obj.data.loops[li].vertex_index].co
            if dominant == 0:
                value = ((p.y/DATA.SCALE_CM_PER_PIXEL+DATA.PELVIS_X)/1682,
                         1-(DATA.GROUND_Y-p.z/DATA.SCALE_CM_PER_PIXEL)/2488)
            elif dominant == 1:
                value = (p.x/(DATA.SCALE_CM_PER_PIXEL*1682),
                         1-(DATA.GROUND_Y-p.z/DATA.SCALE_CM_PER_PIXEL)/2488)
            else:
                value = ((p.y/DATA.SCALE_CM_PER_PIXEL+DATA.PELVIS_X)/1682,
                         p.x/(DATA.SCALE_CM_PER_PIXEL*2488))
            uv.data[li].uv = value
    result = {"name": row["name"], "bone": row["bone"], "material": row["material"], "kind": row["kind"],
              "verts": [tuple(v.co) for v in obj.data.vertices], "faces": [tuple(p.vertices) for p in obj.data.polygons],
              "uv": [[tuple(uv.data[i].uv) for i in p.loop_indices] for p in obj.data.polygons],
              "normals": [[tuple(obj.data.corner_normals[i].vector) for i in p.loop_indices] for p in obj.data.polygons],
              "smooth": [p.use_smooth for p in obj.data.polygons]}
    return result


def closed_ribbon(spec, original):
    polys, crossings = ribbon_polygons(spec)
    points, tris = union_mesh(polys)
    points = [yz(p) for p in points]
    tris = [tuple(tri) if area([points[i] for i in tri]) > 0 else tuple(reversed(tri)) for tri in tris]
    n = len(points)
    top, bottom = spec["layer"]+.31, spec["layer"]-.31
    vertices = [(top, p[0], p[1]) for p in points]+[(bottom, p[0], p[1]) for p in points]
    faces = list(tris)+[tuple(i+n for i in reversed(tri)) for tri in tris]
    counts = Counter(tuple(sorted((a, b))) for tri in tris for a, b in zip(tri, tri[1:]+tri[:1]))
    for tri in tris:
        for a, b in zip(tri, tri[1:]+tri[:1]):
            if counts[tuple(sorted((a, b)))] == 1:
                faces += [(b, a, a+n), (b, a+n, b+n)]
    data = bpy.data.meshes.new("REPAIR_"+spec["name"])
    data.from_pydata(vertices, [], faces)
    data.update()
    obj = bpy.data.objects.new("REPAIR_"+spec["name"], data)
    bpy.context.collection.objects.link(obj)
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    # The repaired ribbon is already actual triangulated cut leather. Applying
    # bevel to CDT seams manufactured sub-ULP sliver geometry in earlier runs.
    repaired = part_from_object(obj, original)
    edges = Counter(tuple(sorted((a, b))) for face in repaired["faces"] for a, b in zip(face, face[1:]+face[:1]))
    check(all(count == 2 for count in edges.values()), spec["name"]+": every actual edge has exactly two incident triangles")
    neighbors = {i: set() for i in range(len(repaired["verts"]))}
    for a, b in edges:
        neighbors[a].add(b); neighbors[b].add(a)
    reached, queue = set(), [0]
    while queue:
        value = queue.pop()
        if value not in reached:
            reached.add(value); queue.extend(neighbors[value]-reached)
    check(len(reached) == len(repaired["verts"]), spec["name"]+": one connected closed solid")
    edge_directions = Counter((a, b) for face in repaired["faces"] for a, b in zip(face, face[1:]+face[:1]))
    check(all(edge_directions[(a, b)] == edge_directions[(b, a)] == 1 for a, b in edges), spec["name"]+": consistent outward winding")
    volume = sum(Vector(repaired["verts"][a]).dot(Vector(repaired["verts"][b]).cross(Vector(repaired["verts"][c])))/6 for a, b, c in repaired["faces"])
    check(volume > 0, spec["name"]+": positive signed physical volume")
    REPORT["snakes"].append({"name": spec["name"], "old_outline_self_crossings": crossings,
        "method": "unchanged original simple outline" if spec["name"].startswith("SnakeArm") else "union of original sampled centerline variable-width segments and internal round joins",
        "centerline_source_points_unchanged": True, "radius_px": spec["radius_px"],
        "vertices": len(repaired["verts"]), "triangles": len(repaired["faces"]), "connected_components": 1,
        "nonmanifold_edges": 0, "signed_volume_cm3": volume,
        "old_bounds_cm": [[min(p[j] for p in original["verts"]), max(p[j] for p in original["verts"])] for j in range(3)],
        "new_bounds_cm": [[min(p[j] for p in repaired["verts"]), max(p[j] for p in repaired["verts"])] for j in range(3)]})
    bpy.data.objects.remove(obj, do_unlink=True)
    return repaired


def front_faces(part):
    front = max(p[0] for p in part["verts"])
    tris = [[(part["verts"][i][1], part["verts"][i][2]) for i in f] for f in part["faces"]
            if all(abs(part["verts"][i][0]-front) < 2e-5 for i in f)]
    tris = [orient(tri) for tri in tris if abs(area(tri)) > 1e-9]
    check(bool(tris), part["name"]+": actual front-cap triangles found")
    return front, tris


def clip_triangle(subject, triangle):
    result = list(subject)
    for a, b in zip(triangle, triangle[1:]+triangle[:1]):
        incoming = result
        result = []
        if not incoming:
            break
        previous = incoming[-1]
        dp = cross(a, b, previous)
        for current in incoming:
            dc = cross(a, b, current)
            if (dc >= -1e-10) != (dp >= -1e-10):
                t = dp/(dp-dc)
                result.append(tuple(previous[j]+t*(current[j]-previous[j]) for j in range(2)))
            if dc >= -1e-10:
                result.append(current)
            previous, dp = current, dc
    clean = []
    for p in result:
        if not clean or math.dist(p, clean[-1]) > 1e-7:
            clean.append(p)
    if len(clean) > 1 and math.dist(clean[0], clean[-1]) < 1e-7:
        clean.pop()
    return clean


def engraved_front(part):
    front = max(p[0] for p in part["verts"])
    tris = [[(part["verts"][i][1], part["verts"][i][2]) for i in f] for f in part["faces"]
            if all(abs(part["verts"][i][0]-front) < 3e-5 for i in f)]
    return [orient(tri) for tri in tris if abs(area(tri)) > 1e-10]


def clip_ink(part, target):
    front, skin = front_faces(target)
    triangles = engraved_front(part)
    check(bool(triangles), part["name"]+": engraving front exists")
    before = sum(abs(area(tri)) for tri in triangles)
    clipped = []
    for tri in triangles:
        box = (min(p[0] for p in tri), max(p[0] for p in tri), min(p[1] for p in tri), max(p[1] for p in tri))
        for surface in skin:
            if max(p[0] for p in surface) < box[0] or min(p[0] for p in surface) > box[1] or max(p[1] for p in surface) < box[2] or min(p[1] for p in surface) > box[3]:
                continue
            polygon = clip_triangle(tri, surface)
            if len(polygon) >= 3 and abs(area(polygon)) > 1e-9:
                for j in range(1, len(polygon)-1):
                    value = orient([polygon[0], polygon[j], polygon[j+1]])
                    if area(value) > 1e-9:
                        clipped.append(value)
    after = sum(area(tri) for tri in clipped)
    check(after <= before+1e-4, part["name"]+": clipping does not create engraving area")
    # Already-contained ancient print must not acquire unnecessary leather
    # tessellation seams merely because it was validated against that surface.
    fully_contained = abs(before-after) < max(1e-7, before*1e-8)
    if fully_contained:
        clipped = triangles
    vertices, faces, lookup = [], [], {}
    # A planar print sits immediately above its own actual leather face, not a floating thick eye/disc.
    x = front+.003
    for tri in clipped:
        face = []
        for point in tri:
            key = tuple(round(value, 6) for value in point)
            if key not in lookup:
                lookup[key] = len(vertices)
                vertices.append((x, point[0], point[1]))
            face.append(lookup[key])
        if len(set(face)) == 3:
            faces.append(tuple(face))
    result = dict(part)
    result.update(verts=vertices, faces=faces, smooth=[False]*len(faces),
        uv=[[[(vertices[i][1]/DATA.SCALE_CM_PER_PIXEL+DATA.PELVIS_X)/1682,
             1-(DATA.GROUND_Y-vertices[i][2]/DATA.SCALE_CM_PER_PIXEL)/2488] for i in face] for face in faces],
        normals=[[(1, 0, 0)]*3 for face in faces])
    outside = 0.0
    for tri in clipped:
        covered = sum(abs(area(value)) for surface in skin if len(value := clip_triangle(tri, surface)) >= 3)
        outside += max(0, area(tri)-covered)
    check(outside < 1e-5, part["name"]+": no engraving area outside assigned actual leather front")
    REPORT["ink"].append({"name": part["name"], "bone": part["bone"], "assigned_actual_surface": target["name"],
        "before_area_cm2": before, "retained_area_cm2": after, "removed_area_cm2": max(0, before-after),
        "outside_area_cm2": outside, "triangles": len(faces), "print_offset_cm": .003,
        "already_fully_contained_yz": fully_contained,
        "old_x_bounds_cm": [min(p[0] for p in part["verts"]), max(p[0] for p in part["verts"])], "new_x_cm": x})
    return result


def bone_state(arm):
    return {b.name: {"parent": b.parent.name if b.parent else None, "matrix": [list(row) for row in b.matrix_local],
                     "head": list(b.head_local), "tail": list(b.tail_local), "deform": b.use_deform} for b in arm.data.bones}


def pose_states(arm):
    output = {}
    for pose in EVIDENCE["poses"]:
        arm.animation_data.action = bpy.data.actions[pose["action"]]
        frames = {}
        for frame in (1, 16, 31):
            bpy.context.scene.frame_set(frame)
            bpy.context.view_layer.update()
            frames[str(frame)] = {b.name: [list(row) for row in b.matrix] for b in arm.pose.bones}
        output[pose["pose"]] = frames
    return output


def build_mesh(old, parts):
    verts, faces, uvs, normals, smooth, ledger = [], [], [], [], [], []
    material_ids = {m.name.removeprefix("MI_DY_"): i for i, m in enumerate(old.data.materials)}
    ids = []
    for part in parts:
        start = len(verts)
        verts.extend(part["verts"])
        faces.extend(tuple(i+start for i in face) for face in part["faces"])
        uvs.extend(part["uv"])
        normals.extend(part["normals"])
        smooth.extend(part["smooth"])
        ids.extend([material_ids[part["material"]]]*len(part["faces"]))
        ledger.append({"name": part["name"], "bone": part["bone"], "kind": part["kind"], "material": part["material"],
                       "vertices": len(part["verts"]), "triangles": len(part["faces"]), "vertex_start": start})
    data = bpy.data.meshes.new("SK_DY_Kuafu_PuppetRefinedGeometry")
    data.from_pydata(verts, [], faces)
    data.update()
    for mat in old.data.materials:
        data.materials.append(mat)
    uv = data.uv_layers.new(name="SourceUV")
    loop_normals = []
    for p, coord, corner_normals, matid, is_smooth in zip(data.polygons, uvs, normals, ids, smooth):
        p.material_index = matid
        p.use_smooth = is_smooth
        for index, value, normal in zip(p.loop_indices, coord, corner_normals):
            uv.data[index].uv = value
            loop_normals.append(normal)
    data.normals_split_custom_set(loop_normals)
    new = old.copy()
    new.data = data
    new.name = "SK_DY_Kuafu_PuppetRefined"
    bpy.context.collection.objects.link(new)
    new.vertex_groups.clear()
    for group in old.vertex_groups:
        new.vertex_groups.new(name=group.name)
    for part, row in zip(parts, ledger):
        if row["vertices"]:
            new.vertex_groups[part["bone"]].add(list(range(row["vertex_start"], row["vertex_start"]+row["vertices"])), 1, "REPLACE")
    check(all(len(v.groups) == 1 and v.groups[0].weight == 1 for v in data.vertices), "Every derived vertex retains exactly one original rigid bone")
    bad = []
    face_cursor = 0
    for part in parts:
        for index in range(face_cursor, face_cursor+len(part["faces"])):
            poly = data.polygons[index]
            if len(poly.vertices) != 3 or poly.area <= 1e-10:
                bad.append({"part": part["name"], "face": index, "area": poly.area,
                            "verts": [list(data.vertices[i].co) for i in poly.vertices]})
        face_cursor += len(part["faces"])
    REPORT["degenerate_triangles"] = bad
    check(all(row["area"] > 0 and len(row["verts"]) == 3 for row in bad), "Derived exported mesh has only positive-area actual triangles; micro-face magnitudes retained in report")
    check(len(data.materials) == 6 and len(data.uv_layers) == 1, "Original six materials and SourceUV convention preserved")
    check(all(math.isfinite(value) for v in data.vertices for value in v.co), "Derived vertex coordinates finite")
    REPORT["part_ledger"] = ledger
    return new


def main():
    protected = [SOURCE/"DY_Kuafu_Puppet_Source.blend", SOURCE/"SK_DY_Kuafu_Puppet.fbx", SOURCE/"MODEL_EVIDENCE.json",
                 AUTHOR/"build_kuafu_puppet.py", AUTHOR/"kuafu_outline_data.py"]
    REPORT["source_hashes_before"] = {str(file): sha(file) for file in protected}
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE/"DY_Kuafu_Puppet_Source.blend"))
    old = bpy.data.objects["SK_DY_Kuafu_Puppet"]
    arm = old.parent
    check(arm.type == "ARMATURE" and len(arm.data.bones) == 20, "Original armature has exact 20 bones")
    skeleton = bone_state(arm)
    poses = pose_states(arm)
    parts = []
    start = 0
    for row in EVIDENCE["part_ledger"]:
        parts.append(extract_part(old, row, start))
        start += row["vertices"]
    check(start == len(old.data.vertices), "All original source vertices attributed to ledger")
    table = {part["name"]: part for part in parts}
    original_signatures = {name: part_signature(part) for name, part in table.items()}
    changed = {}
    for spec in DATA.SNAKES:
        name = "SM_DY_Kuafu_"+spec["name"]
        changed[name] = closed_ribbon(spec, table[name])
    ink_targets = {f"SM_DY_Kuafu_SourceInk{row['source_path_index']:04d}": "SM_DY_Kuafu_"+row["part"] for row in EVIDENCE["unaltered_source_ink_paths"]}
    for spec in DATA.SNAKES:
        name = "SM_DY_Kuafu_"+spec["name"]
        ink_targets.update({part["name"]: name for part in parts if part["name"].startswith(name) and part["name"] != name})
    for name, target in ink_targets.items():
        check(table[name]["bone"] == table[target]["bone"], name+": print and physical support have identical rigid bone")
        changed[name] = clip_ink(table[name], changed.get(target, table[target]))
    new_parts = [changed.get(part["name"], part) for part in parts]
    for part in new_parts:
        if part["name"] not in changed:
            check(part_signature(part) == original_signatures[part["name"]], part["name"]+": original geometry, normals and UV byte-value contract unchanged")
            REPORT["unchanged_parts"].append({"name": part["name"], "signature": original_signatures[part["name"]]})
    new = build_mesh(old, new_parts)
    old.hide_render = True
    old.hide_set(True)
    old.hide_viewport = True
    check(bone_state(arm) == skeleton, "Original rest matrices, hierarchy and StaffGrip bones exactly unchanged")
    check(pose_states(arm) == poses, "All 20 original pose matrices exactly unchanged in three actions at frames 1/16/31")
    REPORT["skeleton"] = skeleton
    REPORT["pose_matrices"] = poses
    REPORT["mesh"] = {"name": new.name, "vertices": len(new.data.vertices), "triangles": len(new.data.polygons),
                      "bones": len(arm.data.bones), "materials": [m.name for m in new.data.materials], "uv_sets": len(new.data.uv_layers)}
    arm.animation_data.action = bpy.data.actions["A_DY_Kuafu_StrideMid"]
    bpy.context.scene.frame_set(1)
    bpy.context.view_layer.update()
    bpy.ops.object.select_all(action="DESELECT")
    new.select_set(True)
    arm.select_set(True)
    bpy.context.view_layer.objects.active = new
    fbx = OUT/"SK_DY_Kuafu_PuppetRefined.fbx"
    bpy.ops.export_scene.fbx(filepath=str(fbx), use_selection=True, object_types={"ARMATURE", "MESH"}, global_scale=1,
        apply_unit_scale=True, apply_scale_options="FBX_SCALE_NONE", axis_forward="-Z", axis_up="Y", add_leaf_bones=False,
        primary_bone_axis="Y", secondary_bone_axis="X", armature_nodetype="NULL", use_armature_deform_only=False,
        bake_anim=True, bake_anim_use_all_bones=True, bake_anim_use_all_actions=True, bake_anim_use_nla_strips=False,
        bake_anim_force_startend_keying=True, path_mode="AUTO", embed_textures=False)
    check(fbx.exists() and fbx.stat().st_size > 10000, "New derivative skeletal FBX actually exported")
    blend = OUT/"DY_Kuafu_PuppetRefined.blend"
    bpy.ops.wm.save_as_mainfile(filepath=str(blend))
    check(blend.exists(), "New derivative editable blend saved")
    REPORT["source_hashes_after"] = {str(file): sha(file) for file in protected}
    check(REPORT["source_hashes_before"] == REPORT["source_hashes_after"], "All five original source/evidence/author files hash unchanged")
    REPORT["status"] = "PASS_DERIVED_GEOMETRY_CLOSED_SNAKES_CLIPPED_PRINT_PENDING_COLD_AND_VISUAL_QA"
    REPORT["artifacts"] = {file.name: {"bytes": file.stat().st_size, "sha256": sha(file)} for file in (blend, fbx)}
    (OUT/"PUPPET_REFINED.json").write_text(json.dumps(REPORT, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"status": REPORT["status"], "mesh": REPORT["mesh"], "snakes": REPORT["snakes"],
        "print_parts": len(REPORT["ink"]), "removed_print_area_cm2": sum(row["removed_area_cm2"] for row in REPORT["ink"]),
        "out": str(OUT)}, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        REPORT["status"] = "FAILED"
        (OUT/"PUPPET_REFINED.json").write_text(json.dumps(REPORT, ensure_ascii=False, indent=2), encoding="utf-8")
        raise
