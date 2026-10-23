"""Blender 4.5 author: source-traced 2.5D Kuafu with rigid articulated pieces.

Run with --background --factory-startup --disable-autoexec --python-exit-code 1.
Each run writes into a new RunN folder, never overwriting a previous artifact.
The source PNG/SVG and the UE project are read-only inputs.
"""

from __future__ import annotations

import bpy
import bmesh
import hashlib
import json
import math
import runpy
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from mathutils import Matrix, Vector

STAGE = Path(__file__).resolve().parent
sys.path.insert(0, str(STAGE))
import kuafu_outline_data as DATA

SOURCE_DIR = Path(r"D:\灯影山海\Saved\SourceReadiness-20261014\Kuafu\Run2")
SOURCE_PNG = SOURCE_DIR / "Kuafu-original.png"
SOURCE_SVG = SOURCE_DIR / "Kuafu-auto-vector.svg"
EXPECTED_PNG_SHA = "365F2159C710F50E42AC1ED15C8D82131F17FC7C5276B0FBDDF82D34401EC0E1"
EXPECTED_SVG_SHA = "3F641F136AB354041FEB6571368D29D7EA9128AEAB2A7A4632AA6BCCDE8106D0"
PARSER = STAGE.parent / "VectorEvidence" / "analyze_kuafu_svg.py"
ASSERTS = []
PART_LEDGER = []
OBJECTS = []
MATERIALS = {}
REFERENCE_DISPLAY = {}


def check(condition, message):
    if not condition:
        raise AssertionError(message)
    ASSERTS.append(message)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def yz(point, x=0):
    px, py = point
    return Vector((x, (px - DATA.PELVIS_X) * DATA.SCALE_CM_PER_PIXEL, (DATA.GROUND_Y - py) * DATA.SCALE_CM_PER_PIXEL))


def area2(points):
    return sum(a[0] * b[1] - b[0] * a[1] for a, b in zip(points, points[1:] + points[:1]))


def orientation(a, b, c):
    return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])


def crossing(a, b, c, d):
    return orientation(a, b, c) * orientation(a, b, d) < -1e-6 and orientation(c, d, a) * orientation(c, d, b) < -1e-6


def validate_outline(name, points):
    check(len(points) >= 3 and abs(area2(points)) > 1.0, f"{name}: nonzero closed outline")
    check(all(math.isfinite(v) for p in points for v in p), f"{name}: finite source coordinates")
    n = len(points)
    for i in range(n):
        for j in range(i + 1, n):
            if j == i + 1 or (i == 0 and j == n - 1):
                continue
            if crossing(points[i], points[(i + 1) % n], points[j], points[(j + 1) % n]):
                raise AssertionError(f"{name}: self-crossing outline at edges {i}/{j}")


def material(name, color, roughness=0.48, metallic=0.0, leather=False):
    mat = bpy.data.materials.new("MI_DY_" + name)
    mat.diffuse_color = (*color, 1.0)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    if leather:
        noise = mat.node_tree.nodes.new("ShaderNodeTexNoise")
        noise.inputs["Scale"].default_value = 650.0
        noise.inputs["Detail"].default_value = 2.0
        bump = mat.node_tree.nodes.new("ShaderNodeBump")
        bump.inputs["Strength"].default_value = 0.13
        bump.inputs["Distance"].default_value = 0.018
        mat.node_tree.links.new(noise.outputs["Fac"], bump.inputs["Height"])
        mat.node_tree.links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    MATERIALS[name] = mat
    return mat


def activate(obj):
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj


def map_uv(obj):
    for existing in list(obj.data.uv_layers):
        obj.data.uv_layers.remove(existing)
    layer = obj.data.uv_layers.new(name="SourceUV")
    for poly in obj.data.polygons:
        # A single YZ projection collapses every thickness-side triangle.
        # Preserve woodcut coordinates on front/back; use the actual dominant
        # normal to project thickness sides at the same physical texel scale.
        dominant = max(range(3), key=lambda axis: abs(poly.normal[axis]))
        for loop in poly.loop_indices:
            p = obj.data.vertices[obj.data.loops[loop].vertex_index].co
            if dominant == 0:
                px = p.y / DATA.SCALE_CM_PER_PIXEL + DATA.PELVIS_X
                py = DATA.GROUND_Y - p.z / DATA.SCALE_CM_PER_PIXEL
                value = (px / 1682.0, 1 - py / 2488.0)
            elif dominant == 1:
                value = (p.x / (DATA.SCALE_CM_PER_PIXEL * 1682.0),
                         1 - (DATA.GROUND_Y-p.z/DATA.SCALE_CM_PER_PIXEL)/2488.0)
            else:
                value = ((p.y/DATA.SCALE_CM_PER_PIXEL+DATA.PELVIS_X)/1682.0,
                         p.x / (DATA.SCALE_CM_PER_PIXEL * 2488.0))
            layer.data[loop].uv = value
        uv = [layer.data[index].uv for index in poly.loop_indices]
        check(abs((uv[1].x-uv[0].x)*(uv[2].y-uv[0].y)
                  -(uv[1].y-uv[0].y)*(uv[2].x-uv[0].x)) > 1e-15,
              f"{obj.name}: nonzero triangle UV area")


def finish_piece(obj, bone, mat_name, kind, source_points=None, bevel=0.0):
    obj.data.materials.append(MATERIALS[mat_name])
    group = obj.vertex_groups.new(name=bone)
    group.add(list(range(len(obj.data.vertices))), 1.0, "REPLACE")
    activate(obj)
    if bevel:
        mod = obj.modifiers.new("Physical cut edge", "BEVEL")
        mod.width = bevel
        mod.segments = 1
        mod.affect = "EDGES"
        mod.use_clamp_overlap = True
        bpy.ops.object.modifier_apply(modifier=mod.name)
    tri = obj.modifiers.new("Export triangulation", "TRIANGULATE")
    tri.keep_custom_normals = True
    bpy.ops.object.modifier_apply(modifier=tri.name)
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(obj.data)
    bm.free()
    obj.data.update()
    # Rigid pieces keep a single 1.0 weight, including every bevel-created vertex.
    obj.vertex_groups[bone].add(list(range(len(obj.data.vertices))), 1.0, "REPLACE")
    map_uv(obj)
    check(len(obj.data.vertices) >= 3 and len(obj.data.polygons) >= 1, f"{obj.name}: geometry exists")
    check(all(poly.area > 1e-9 and len(poly.vertices) == 3 for poly in obj.data.polygons), f"{obj.name}: nondegenerate triangles")
    check(all(v.groups and all(abs(g.weight - 1) < 1e-6 for g in v.groups) for v in obj.data.vertices), f"{obj.name}: one rigid bone weight")
    check(all(abs(v.normal.length - 1) < 1e-3 for v in obj.data.vertices), f"{obj.name}: normalized normals")
    check(all(math.isfinite(c) for uv in obj.data.uv_layers.active.data for c in uv.uv), f"{obj.name}: finite source UV")
    obj["SourceBone"] = bone
    obj["PartKind"] = kind
    OBJECTS.append(obj)
    PART_LEDGER.append({"name": obj.name, "bone": bone, "kind": kind, "material": mat_name, "vertices": len(obj.data.vertices), "triangles": len(obj.data.polygons), "source_outline_px": source_points})
    return obj


def plate(name, points, bone, mat_name, layer, thickness=0.65, bevel=0.055, kind="source-traced articulated plate"):
    points = [tuple(p) for p in points]
    validate_outline(name, points)
    positions = [yz(p) for p in points]
    # Positive winding in YZ gives the front cap its +X normal.
    if area2([(v.y, v.z) for v in positions]) < 0:
        positions.reverse()
    n = len(positions)
    verts = [(layer + thickness / 2, v.y, v.z) for v in positions] + [(layer - thickness / 2, v.y, v.z) for v in positions]
    faces = [tuple(range(n)), tuple(range(n * 2 - 1, n - 1, -1))]
    faces += [(i, (i + 1) % n, (i + 1) % n + n, i + n) for i in range(n)]
    mesh = bpy.data.meshes.new(name + "Geometry")
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    obj = bpy.data.objects.new("SM_DY_Kuafu_" + name, mesh)
    bpy.context.collection.objects.link(obj)
    return finish_piece(obj, bone, mat_name, kind, points, bevel)


def soften_outline(points, radius):
    # Round only the traced corners; the new arc stays inside its source corner.
    result = []
    for i, source in enumerate(points):
        previous = Vector(points[i-1])
        current = Vector(source)
        following = Vector(points[(i+1)%len(points)])
        before = previous-current
        after = following-current
        enter = current + before.normalized()*min(radius,before.length*0.22)
        leave = current + after.normalized()*min(radius,after.length*0.22)
        result += [tuple(enter),tuple(0.25*enter+0.5*current+0.25*leave),tuple(leave)]
    return result


def rounded_joint_cap(name, bone, center, radius_px, layer, mat_name):
    points = [(center[0] + radius_px * math.cos(i * math.tau / 16), center[1] + radius_px * math.sin(i * math.tau / 16)) for i in range(16)]
    return plate(name, points, bone, mat_name, layer, 0.55, 0.0, "hidden joint overlap - contemporary rig adaptation")


def catmull_rom(points, samples=5):
    result = []
    source = [Vector(p) for p in points]
    for i in range(len(source) - 1):
        p0 = source[max(0, i - 1)]
        p1 = source[i]
        p2 = source[i + 1]
        p3 = source[min(len(source) - 1, i + 2)]
        for step in range(samples):
            t = step / samples
            result.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2*p0 - 5*p1 + 4*p2 - p3) * t*t + (-p0 + 3*p1 - 3*p2 + p3) * t*t*t))
    result.append(source[-1])
    return result


def snake(s):
    points = catmull_rom(s["centerline"], 4)
    normals = []
    widths = []
    for i, p in enumerate(points):
        tangent = (points[min(len(points)-1, i+1)] - points[max(0, i-1)]).normalized()
        normal = Vector((-tangent.y, tangent.x))
        head_factor = 1.0 + 0.55 * max(0, (i / (len(points)-1) - 0.87) / 0.13)
        width = s["radius_px"] * head_factor
        normals.append(normal)
        widths.append(width)
    # Original serpent coils can overlap themselves. A union-filled 2D Curve,
    # rather than a single self-crossing prism polygon, resolves those overlaps.
    outline = [tuple(p + n*w) for p,n,w in zip(points,normals,widths)] + [tuple(p - n*w) for p,n,w in reversed(list(zip(points,normals,widths)))]
    obj = filled_curves("SM_DY_Kuafu_" + s["name"], [outline], s["layer"], 0.62)
    finish_piece(obj, s["bone"], "SnakeYellow", "four snakes; ear flow traced, forearm relocation adapted", [list(p) for p in outline], 0.035)
    for i in range(4, len(points) - 5, 6):
        p, n, w = points[i], normals[i], widths[i] * 0.75
        tangent = (points[i+1] - points[i-1]).normalized()
        stripe = [tuple(p+n*w+tangent*0.65), tuple(p-n*w+tangent*0.65), tuple(p-n*w-tangent*0.65), tuple(p+n*w-tangent*0.65)]
        plate(s["name"] + f"Scale{i}", stripe, s["bone"], "Ink", s["layer"] + 0.355, 0.024, 0, "snake engraving detail")
    eye = points[-2] + normals[-2] * widths[-2] * 0.43
    rounded_joint_cap(s["name"] + "Eye", s["bone"], eye, 1.65, s["layer"] + 0.40, "Ink")


def filled_curves(name, runs, layer, extrusion=0.0):
    curve = bpy.data.curves.new(name + "Curves", "CURVE")
    curve.dimensions = "2D"
    curve.resolution_u = 1
    curve.fill_mode = "BOTH"
    curve.extrude = extrusion / 2
    for run in runs:
        # Consecutive duplicate endpoints make zero-length geometry; remove them.
        clean = []
        for point in run:
            if not clean or (Vector(point) - Vector(clean[-1])).length > 0.03:
                clean.append(point)
        if len(clean) > 1 and (Vector(clean[0])-Vector(clean[-1])).length < 0.03:
            clean.pop()
        if len(clean) < 3:
            continue
        spline = curve.splines.new("POLY")
        spline.points.add(len(clean)-1)
        for p, source in zip(spline.points, clean):
            co = yz(source)
            p.co = (co.y, co.z, 0.0, 1.0)
        spline.use_cyclic_u = True
    obj = bpy.data.objects.new(name, curve)
    bpy.context.collection.objects.link(obj)
    obj.matrix_world = Matrix(((0,0,1,layer),(1,0,0,0),(0,1,0,0),(0,0,0,1)))
    activate(obj)
    bpy.ops.object.convert(target="MESH")
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    return bpy.context.object


def rdp(points, tolerance=0.35):
    if len(points) < 4:
        return points
    a, b = Vector(points[0]), Vector(points[-1])
    delta = b - a
    length = delta.length
    distances = [abs(delta.x*(Vector(p).y-a.y)-delta.y*(Vector(p).x-a.x))/length if length > 1e-9 else (Vector(p)-a).length for p in points[1:-1]]
    if not distances:
        return points
    maximum = max(distances)
    if maximum <= tolerance:
        return [points[0], points[-1]]
    index = distances.index(maximum) + 1
    return rdp(points[:index+1], tolerance)[:-1] + rdp(points[index:], tolerance)


def source_ink():
    helpers = runpy.run_path(str(PARSER))
    paths = ET.fromstring(SOURCE_SVG.read_bytes()).findall(".//" + helpers["NS"] + "path")
    selected = []
    for index, element in enumerate(paths):
        bbox, runs, area, commands = helpers["parse_path"](element.attrib["d"])
        if area < 2.0:
            continue
        all_points = [p for run in runs for p in run]
        candidates = []
        for part in DATA.PARTS:
            if part["name"] in ("Hair", "UpperArm_R", "PelvisRobe"):
                continue
            coverage = sum(helpers["point_in_polygon"](p, part["outline"]) for p in all_points) / len(all_points)
            if coverage >= 0.985:
                candidates.append((coverage, part))
        if not candidates:
            continue
        # Prefer the visible front plate when anatomy and robe overlap.
        part = max(candidates, key=lambda item: (item[0], item[1]["layer"]))[1]
        loops = [rdp(run, 0.35) for run in runs]
        # Printed engraving is a planar surface detail, not another thick plate.
        obj = filled_curves(f"SM_DY_Kuafu_SourceInk{index:04d}", loops, part["layer"] + 0.355, 0.0)
        if not obj.data.polygons:
            bpy.data.objects.remove(obj, do_unlink=True)
            continue
        finish_piece(obj, part["bone"], "Ink", "unaltered ancient source path; simplified <=0.35 source pixel", None)
        selected.append({"source_path_index": index, "bone": part["bone"], "part": part["name"], "bbox_px": bbox, "source_coverage": max(c[0] for c in candidates)})
    check(sum(s["part"] == "Head" for s in selected) >= 35, "At least 35 authentic source face ink paths retained")
    return selected


def rivet(name, bone, point):
    center = yz(point, 1.2)
    bpy.ops.mesh.primitive_torus_add(major_segments=16, minor_segments=6, location=center, rotation=(0,math.pi/2,0), major_radius=1.28, minor_radius=0.22)
    obj = bpy.context.object
    obj.name = "SM_DY_Kuafu_Rivet_" + name
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    finish_piece(obj, bone, "AgedBrass", "visible joint eyelet - contemporary shadow-puppet mechanism")
    rounded_joint_cap("RivetPin_" + name, bone, point, 2.0, 1.30, "AgedBrass")


def armature():
    data = bpy.data.armatures.new("SKEL_DY_Kuafu_Puppet")
    # UE's native Blender importer strips only this NULL object, not real Root.
    obj = bpy.data.objects.new("Armature", data)
    bpy.context.collection.objects.link(obj)
    activate(obj)
    bpy.ops.object.mode_set(mode="EDIT")
    for name, spec in DATA.BONES.items():
        bone = data.edit_bones.new(name)
        bone.head = yz(spec["head"])
        bone.tail = yz(spec["tail"])
        # Local Z follows the plane normal, so all pose bends remain in YZ.
        bone.align_roll(Vector((1,0,0)))
        if spec["parent"]:
            bone.parent = data.edit_bones[spec["parent"]]
        bone.use_connect = False
        bone.use_deform = not name.startswith("StaffGrip_") and name != "Root"
    bpy.ops.object.mode_set(mode="OBJECT")
    obj.show_in_front = True
    data.display_type = "STICK"
    check(set(data.bones.keys()) == set(DATA.BONES), "Bone names and hierarchy exactly match source-joint rig")
    check(len(data.bones) == 20 and data.bones["Head"].parent.name == "Spine", "20-bone minimal rig; no facial/combat rig")
    for bone in data.bones:
        check(bone.length > 0.5 and abs(bone.head_local.x) < 1e-6 and abs(bone.tail_local.x) < 1e-6, f"{bone.name}: finite nonzero planar bone")
    return obj


def combine(arm):
    bpy.ops.object.select_all(action="DESELECT")
    for obj in OBJECTS:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = OBJECTS[0]
    bpy.ops.object.join()
    mesh = bpy.context.object
    mesh.name = "SK_DY_Kuafu_Puppet"
    mesh.data.name = "SK_DY_Kuafu_PuppetGeometry"
    mesh.parent = arm
    mod = mesh.modifiers.new("Rigid articulated leather pieces", "ARMATURE")
    mod.object = arm
    mod.use_deform_preserve_volume = False
    check(all(len(v.groups) == 1 and abs(v.groups[0].weight - 1) < 1e-6 for v in mesh.data.vertices), "Joined mesh: every vertex has exactly one rigid weight")
    check(all(g.name in DATA.BONES for g in mesh.vertex_groups), "Joined mesh: no orphan vertex groups")
    check(len(mesh.data.uv_layers) == 1 and mesh.data.uv_layers.active.name == "SourceUV", "Joined mesh: one source-coordinate UV set")
    print(f"DY_KUAFU_PREJOIN_TRIANGLES={len(mesh.data.polygons)}", flush=True)
    check(len(mesh.data.polygons) <= 20000, "Hero mesh <=20,000 triangles")
    return mesh


def apply_pose(arm, name):
    for bone in arm.pose.bones:
        bone.rotation_mode = "XYZ"
        bone.rotation_euler = (0,0,math.radians(DATA.POSES[name].get(bone.name, 0)))
        bone.location = (0,0,0)
        bone.scale = (1,1,1)
    bpy.context.view_layer.update()


def actions(arm, mesh):
    arm.animation_data_create()
    outputs = []
    for name in DATA.POSES:
        action = bpy.data.actions.new("A_DY_Kuafu_" + name)
        action.use_fake_user = True
        arm.animation_data.action = action
        apply_pose(arm, name)
        for frame in (1, 31):
            bpy.context.scene.frame_set(frame)
            for bone in arm.pose.bones:
                bone.keyframe_insert(data_path="rotation_euler", frame=frame, group=bone.name)
                bone.keyframe_insert(data_path="location", frame=frame, group=bone.name)
                bone.keyframe_insert(data_path="scale", frame=frame, group=bone.name)
        bpy.context.scene.frame_set(1)
        bpy.context.view_layer.update()
        depsgraph = bpy.context.evaluated_depsgraph_get()
        evaluated = mesh.evaluated_get(depsgraph)
        evaluated_mesh = evaluated.to_mesh()
        x_values = [v.co.x for v in evaluated_mesh.vertices]
        check(max(abs(x) for x in x_values) < 2.5, f"{name}: articulation remains a thin YZ puppet")
        check(all(math.isfinite(c) for v in evaluated_mesh.vertices for c in v.co), f"{name}: finite pose-deformed geometry")
        bbox = [[min(v.co[i] for v in evaluated_mesh.vertices), max(v.co[i] for v in evaluated_mesh.vertices)] for i in range(3)]
        evaluated.to_mesh_clear()
        grips = {n: list(arm.pose.bones[n].matrix.translation) for n in ("StaffGrip_R", "StaffGrip_L")}
        outputs.append({"pose": name, "action": action.name, "rotation_local_z_deg": DATA.POSES[name], "bounds_cm": bbox, "hand_grip_cm": grips})
    return outputs


def camera_at(name, location, target, ortho):
    bpy.ops.object.camera_add(location=location)
    camera = bpy.context.object
    camera.name = name
    camera.rotation_euler = (Vector(target)-camera.location).to_track_quat("-Z", "Y").to_euler()
    camera.data.type = "ORTHO"
    camera.data.ortho_scale = ortho
    bpy.context.scene.camera = camera
    return camera


def reference_panel():
    # A source image plane uses unchanged pixels, merely a camera framing crop.
    panel = bpy.data.meshes.new("AncientReferencePanelGeometry")
    xmin,ymin,xmax,ymax = 595,1023,1545,1985
    width = (xmax-xmin)*DATA.SCALE_CM_PER_PIXEL
    height = (ymax-ymin)*DATA.SCALE_CM_PER_PIXEL
    center_y = -286
    panel.from_pydata([(-0.5,center_y-width/2,0),(-0.5,center_y+width/2,0),(-0.5,center_y+width/2,height),(-0.5,center_y-width/2,height)], [], [(0,1,2,3)])
    obj = bpy.data.objects.new("REFERENCE_ONLY_UnchangedPublicDomainWoodcut", panel)
    bpy.context.collection.objects.link(obj)
    uv = panel.uv_layers.new(name="SourceImageFraming")
    coords = [(xmin/1682,1-ymax/2488),(xmax/1682,1-ymax/2488),(xmax/1682,1-ymin/2488),(xmin/1682,1-ymin/2488)]
    for loop, value in zip(uv.data,coords):
        loop.uv = value
    mat = bpy.data.materials.new("ReferenceOnly_SourceWoodcut")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()
    texture = nodes.new("ShaderNodeTexImage")
    texture.image = bpy.data.images.load(str(SOURCE_PNG))
    texture.image.pack()
    decoder_pixel = list(texture.image.pixels[:4])
    # The archived 1-bit PNG has a transparent white background (observed RGBA
    # corner 1,1,1,0). Composite it over white like the image viewer; do not
    # invert ink or edit the original raster to work around premultiplied alpha.
    REFERENCE_DISPLAY.update({"source_png_unmodified":True,"blender_decoder_corner_rgba":decoder_pixel,
                              "white_background_shader_composite":True,"shader_colour_inversion":False})
    emission = nodes.new("ShaderNodeEmission")
    output = nodes.new("ShaderNodeOutputMaterial")
    composite = nodes.new("ShaderNodeMixRGB")
    composite.blend_type = "MIX"
    composite.inputs[1].default_value = (1,1,1,1)
    mat.node_tree.links.new(texture.outputs["Alpha"],composite.inputs[0])
    mat.node_tree.links.new(texture.outputs["Color"],composite.inputs[2])
    mat.node_tree.links.new(composite.outputs[0],emission.inputs["Color"])
    mat.node_tree.links.new(emission.outputs[0],output.inputs["Surface"])
    obj.data.materials.append(mat)
    return obj


def label(text, position, size=8):
    curve = bpy.data.curves.new(text, "FONT")
    curve.body = text
    curve.size = size
    curve.align_x = "CENTER"
    obj = bpy.data.objects.new(text,curve)
    bpy.context.collection.objects.link(obj)
    # Text's XY plane is rotated so its normal is +X, its right direction +Y.
    obj.matrix_world = Matrix(((0,0,1,position[0]),(1,0,0,position[1]),(0,1,0,position[2]),(0,0,0,1)))
    obj.data.materials.append(MATERIALS["Ink"])
    return obj


def review_scene():
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE_NEXT"
    scene.render.resolution_x = 1800
    scene.render.resolution_y = 1300
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.view_settings.view_transform = "AgX"
    scene.world.color = (0.7,0.65,0.55)
    world_nodes = scene.world.node_tree.nodes if scene.world.use_nodes else None
    if world_nodes:
        world_nodes.get("Background").inputs["Color"].default_value = (0.65,0.58,0.46,1)
        world_nodes.get("Background").inputs["Strength"].default_value = 0.55
    bpy.ops.mesh.primitive_plane_add(size=1600, location=(-6,-150,140),rotation=(0,math.pi/2,0))
    backdrop = bpy.context.object
    backdrop.name = "REVIEW_ONLY_PaperBackdrop"
    backdrop.data.materials.append(MATERIALS["ReviewPaper"])
    bpy.ops.object.light_add(type="AREA",location=(280,-20,360))
    lamp = bpy.context.object
    lamp.name = "REVIEW_ONLY_BroadSoftbox"
    lamp.data.energy = 1200000
    lamp.data.shape = "DISK"
    lamp.data.size = 260
    lamp.rotation_euler = (Vector((0,0,120))-lamp.location).to_track_quat("-Z","Y").to_euler()
    bpy.ops.object.light_add(type="AREA",location=(190,160,130))
    fill = bpy.context.object
    fill.name = "REVIEW_ONLY_Fill"
    fill.data.energy = 400000
    fill.data.size = 220
    fill.rotation_euler = (Vector((0,0,130))-fill.location).to_track_quat("-Z","Y").to_euler()
    reference_panel()
    label("Public-domain woodcut / source composited over white", (1,-286,-18),6.0)
    name_label = label("Articulated leather puppet - StrideMid", (3,0,-18),7.0)
    label("Contemporary digital shadow-puppet adaptation | centimetres | no purchased assets", (3,-145,278),6.2)
    camera_at("REVIEW_ONLY_ComparisonCamera",(800,-145,125),(0,-145,125),650)
    return name_label


def main():
    check(sha(SOURCE_PNG) == EXPECTED_PNG_SHA and sha(SOURCE_SVG) == EXPECTED_SVG_SHA, "Unmodified public-domain source hashes match archived evidence")
    run_index = 1
    while (STAGE / f"Run{run_index}").exists():
        run_index += 1
    output = STAGE / f"Run{run_index}"
    output.mkdir()
    print(f"DY_KUAFU_RUN={output}", flush=True)
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    scene = bpy.context.scene
    scene.unit_settings.system = "METRIC"
    scene.unit_settings.scale_length = 0.01
    scene.unit_settings.length_unit = "CENTIMETERS"
    scene.render.fps = 30
    scene.frame_start = 1
    scene.frame_end = 31
    material("LeatherOchre",(0.49,0.245,0.095),0.5,leather=True)
    material("LacquerOxBlood",(0.245,0.018,0.018),0.39,leather=True)
    material("SnakeYellow",(0.68,0.41,0.022),0.43,leather=True)
    material("HairInk",(0.024,0.010,0.005),0.65)
    material("Ink",(0.012,0.005,0.003),0.7)
    material("AgedBrass",(0.34,0.22,0.055),0.36,0.75)
    material("ReviewPaper",(0.69,0.64,0.54),0.85)
    for part in DATA.PARTS:
        radius = 2.0 if part["name"] in ("Head","Hair","Hand_R","Hand_L","ShinFoot_R","ShinFoot_L") else 7.0
        plate(part["name"],soften_outline(part["outline"],radius),part["bone"],part["material"],part["layer"])
    for name,(bone,point) in DATA.JOINT_RIVETS.items():
        rounded_joint_cap("Overlap_"+name,bone,point,15,-0.9,"LeatherOchre")
        rivet(name,bone,point)
    for spec in DATA.SNAKES:
        snake(spec)
    source_paths = source_ink()
    (output/"PART_LEDGER_PREJOIN.json").write_text(json.dumps(PART_LEDGER,ensure_ascii=False,indent=2),encoding="utf-8")
    arm = armature()
    mesh = combine(arm)
    pose_data = actions(arm,mesh)
    arm.animation_data.action = bpy.data.actions["A_DY_Kuafu_StrideMid"]
    apply_pose(arm,"StrideMid")
    scene.frame_set(1)
    check(len(DATA.SNAKES) == 4 and all(s["bone"] in arm.data.bones for s in DATA.SNAKES),"Two ear snakes and two forearm snakes each have an independent bone")
    check(set(DATA.POSES) == {"StrideBack","StrideMid","Reach"},"Exactly three required non-combat poses")
    name_label = review_scene()
    activate(mesh)
    arm.select_set(True)
    fbx = output / "SK_DY_Kuafu_Puppet.fbx"
    bpy.ops.export_scene.fbx(filepath=str(fbx),use_selection=True,object_types={"ARMATURE","MESH"},global_scale=1,apply_unit_scale=True,apply_scale_options="FBX_SCALE_NONE",axis_forward="-Z",axis_up="Y",add_leaf_bones=False,primary_bone_axis="Y",secondary_bone_axis="X",armature_nodetype="NULL",use_armature_deform_only=False,bake_anim=True,bake_anim_use_all_bones=True,bake_anim_use_all_actions=True,bake_anim_use_nla_strips=False,bake_anim_force_startend_keying=True,path_mode="AUTO",embed_textures=False)
    check(fbx.exists() and fbx.stat().st_size > 10000,"Skeletal FBX exported to this new run")
    for name in DATA.POSES:
        arm.animation_data.action = bpy.data.actions["A_DY_Kuafu_"+name]
        scene.frame_set(1)
        apply_pose(arm,name)
        name_label.data.body = "Articulated leather puppet - " + name
        scene.render.filepath = str(output / f"COMPARE_{name}.png")
        bpy.ops.render.render(write_still=True)
        check((output/f"COMPARE_{name}.png").exists(),f"{name}: source/model comparison rendered")
    arm.animation_data.action = bpy.data.actions["A_DY_Kuafu_StrideMid"]
    scene.frame_set(1)
    apply_pose(arm,"StrideMid")
    name_label.data.body = "Articulated leather puppet - StrideMid"
    activate(mesh)
    blend = output / "DY_Kuafu_Puppet_Source.blend"
    bpy.ops.wm.save_as_mainfile(filepath=str(blend))
    check(blend.exists() and blend.stat().st_size > 10000,"Editable Blender source saved")
    check(sha(SOURCE_PNG)==EXPECTED_PNG_SHA and sha(SOURCE_SVG)==EXPECTED_SVG_SHA,"Source PNG/SVG unchanged after authoring")
    result = {"status":"PASS-STAGED-KUAFU-MODEL-EXPORT-PENDING-VISUAL-REVIEW","blender_version":bpy.app.version_string,"run":str(output),"source_sha256":{"png":EXPECTED_PNG_SHA,"svg":EXPECTED_SVG_SHA},"units":"numeric centimetres; scene metric scale 0.01; puppet plane YZ with thin X","rig_convention":"Image-left foreground is R, image-right rear is L. Engineering labels do not assert historical handedness.","historical_features":["source-traced face/hair and short robe","bare feet and running pose","two ear serpents plus two hand serpents"],"creative_adaptations":["rigid articulated joint separation/caps/eyelets","ochre leather, dark-red robe, yellow snakes","hand snakes relocated onto forearms to free staff grips","three constrained non-combat poses"],"scope":{"UE_project_written":False,"core_cpp_written":False,"independent_staff_included":False,"raster_source_edited":False},"source_joint_coordinates":DATA.BONES,"part_ledger":PART_LEDGER,"unaltered_source_ink_paths":source_paths,"mesh":{"vertices":len(mesh.data.vertices),"triangles":len(mesh.data.polygons),"materials":[m.name for m in mesh.data.materials],"bones":len(arm.data.bones),"rigid_weights":True,"uv_sets":len(mesh.data.uv_layers)},"poses":pose_data,"assertions":ASSERTS,"artifacts":{p.name:{"bytes":p.stat().st_size,"sha256":sha(p)} for p in [fbx,blend]+[output/f"COMPARE_{n}.png" for n in DATA.POSES]}}
    result["reference_display"] = REFERENCE_DISPLAY
    result["uv_mapping"] = {"channels":1,"front_back":"source YZ coordinates",
                            "thickness_sides":"actual dominant-normal XY/XZ projection at matching physical scale",
                            "zero_area_uv_triangles":0,"overlap_is_intentional_for_tiled_materials":True,
                            "not_a_lightmap_or_unique_bake_atlas":True}
    result["animation_export"] = {"fps":30,"frame_start":1,"frame_end":31,"length_seconds":1.0,"action_names":["A_DY_Kuafu_"+n for n in DATA.POSES],"expected_animation_takes":3,"single_fbx":True,"all_bones_baked":True,"nla_strips":False,"armature_object":"Armature","armature_nodetype":"NULL","add_leaf_bones":False,"use_armature_deform_only":False,"axis_forward":"-Z","axis_up":"Y","apply_unit_scale":True,"global_scale":1.0,"apply_scale_options":"FBX_SCALE_NONE"}
    (output/"MODEL_EVIDENCE.json").write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps({"status":result["status"],"mesh":result["mesh"],"retained_original_ink_paths":len(source_paths),"assertions":len(ASSERTS),"run":str(output)},ensure_ascii=False),flush=True)


if __name__ == "__main__":
    main()
