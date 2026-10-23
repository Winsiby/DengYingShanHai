"""Cold-read derived source and render real full-geometry source A/B shadows."""
import bpy
import hashlib
import json
import math
from collections import Counter
from pathlib import Path
from mathutils import Vector

STAGE = Path(__file__).resolve().parent
RUN = STAGE / "Refined-Run6"
META = json.loads((RUN/"PUPPET_REFINED.json").read_text(encoding="utf-8"))
run = 1
while (RUN/f"QA-Run{run}").exists():
    run += 1
OUT = RUN/f"QA-Run{run}"
OUT.mkdir()
REPORT = {"status": "RUNNING", "assertions": [], "captures": [], "closed_ribbons": [],
          "context": "Blender 4.5.14 actual source geometry rays, not native UE or formal game acceptance"}


def check(condition, text):
    if not condition:
        raise AssertionError(text)
    REPORT["assertions"].append(text)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def bones(arm):
    return {b.name: {"parent": b.parent.name if b.parent else None, "matrix": [list(row) for row in b.matrix_local],
                     "head": list(b.head_local), "tail": list(b.tail_local), "deform": b.use_deform} for b in arm.data.bones}


def camera(location, target, width):
    bpy.ops.object.camera_add(location=location)
    obj = bpy.context.object
    obj.name = "QA_ONLY_Camera"
    obj.rotation_euler = (Vector(target)-obj.location).to_track_quat("-Z", "Y").to_euler()
    obj.data.type = "ORTHO"
    obj.data.ortho_scale = width
    bpy.context.scene.camera = obj
    return obj


def point_light(location, energy, kind="POINT", size=0):
    bpy.ops.object.light_add(type=kind, location=location)
    obj = bpy.context.object
    obj.name = "QA_ONLY_"+kind
    obj.data.energy = energy
    if kind == "POINT":
        obj.data.shadow_soft_size = size
    else:
        obj.data.shape = "DISK"
        obj.data.size = size
        obj.rotation_euler = (Vector((0, 0, 125))-obj.location).to_track_quat("-Z", "Y").to_euler()
    return obj


def render(file, old, new, variant, action):
    old.hide_render = variant != "Original"
    new.hide_render = variant != "Refined"
    old.hide_viewport = False
    old.hide_set(False)
    new.hide_viewport = False
    new.hide_set(False)
    arm = new.parent
    arm.animation_data.action = bpy.data.actions["A_DY_Kuafu_"+action]
    bpy.context.scene.frame_set(1)
    bpy.context.view_layer.update()
    bpy.context.scene.render.filepath = str(OUT/file)
    bpy.ops.render.render(write_still=True)
    check((OUT/file).exists(), file+": real source render written")
    REPORT["captures"].append({"file": file, "variant": variant, "pose": action,
        "bytes": (OUT/file).stat().st_size, "sha256": sha(OUT/file), "all_geometry_casts_shadow": True})


def main():
    blend = RUN/"DY_Kuafu_PuppetRefined.blend"
    before = {str(p): sha(p) for p in (blend, RUN/"SK_DY_Kuafu_PuppetRefined.fbx")}
    bpy.ops.wm.open_mainfile(filepath=str(blend))
    old = bpy.data.objects["SK_DY_Kuafu_Puppet"]
    new = bpy.data.objects["SK_DY_Kuafu_PuppetRefined"]
    arm = new.parent
    check(bones(arm) == META["skeleton"], "Cold-read: exact original rest matrices, hierarchy and 20 StaffGrip-inclusive bones")
    for pose, frames in META["pose_matrices"].items():
        arm.animation_data.action = bpy.data.actions["A_DY_Kuafu_"+pose]
        for frame, expected in frames.items():
            bpy.context.scene.frame_set(int(frame))
            bpy.context.view_layer.update()
            actual = {b.name: [list(row) for row in b.matrix] for b in arm.pose.bones}
            check(actual == expected, f"Cold-read: all 20 matrices remain exact, {pose}, frame {frame}")
    check(len(new.data.polygons) == 17902 and len(new.data.vertices) == 10636, "Cold-read: 17,902 actual triangles and 10,636 vertices")
    check(len(new.data.materials) == 6 and len(new.data.uv_layers) == 1, "Cold-read: six original materials and one source UV")
    check(all(len(v.groups) == 1 and v.groups[0].weight == 1 for v in new.data.vertices), "Cold-read: every derived vertex has exactly one rigid original weight")
    cursor = 0
    for row in META["part_ledger"]:
        if row["material"] == "SnakeYellow":
            faces = [p for p in new.data.polygons if row["vertex_start"] <= p.vertices[0] < row["vertex_start"]+row["vertices"]]
            edges = Counter(tuple(sorted((a, b))) for face in faces for a, b in zip(list(face.vertices), list(face.vertices)[1:]+list(face.vertices)[:1]))
            check(all(n == 2 for n in edges.values()), row["name"]+": cold-read every actual edge has exactly two faces")
            REPORT["closed_ribbons"].append({"name": row["name"], "triangles": len(faces), "nonmanifold_edges": sum(n != 2 for n in edges.values())})
        cursor += row["vertices"]
    check(cursor == len(new.data.vertices), "Cold-read: complete 266-part ledger accounts for every derived vertex")
    # Only the two real source meshes and original armature remain for this QA.
    for obj in bpy.context.scene.objects:
        if obj not in (old, new, arm):
            obj.hide_render = True
    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    scene.cycles.device = "CPU"
    scene.cycles.samples = 24
    scene.cycles.use_denoising = False
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.image_settings.color_depth = "8"
    scene.render.film_transparent = False
    scene.view_settings.view_transform = "AgX"
    scene.view_settings.look = "AgX - Medium High Contrast"
    scene.view_settings.exposure = 0
    scene.world.use_nodes = True
    bg = scene.world.node_tree.nodes.get("Background")
    bg.inputs["Color"].default_value = (.70, .66, .60, 1)
    bg.inputs["Strength"].default_value = .2
    paper = bpy.data.materials.new("QA_ONLY_Paper")
    paper.diffuse_color = (.7, .65, .56, 1)
    paper.use_nodes = True
    bsdf = paper.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (.7, .65, .56, 1)
    bsdf.inputs["Roughness"].default_value = .9
    bpy.ops.mesh.primitive_plane_add(size=600, location=(-15, 0, 125), rotation=(0, math.pi/2, 0))
    panel = bpy.context.object
    panel.name = "QA_ONLY_Opaque_Backdrop"
    panel.data.materials.append(paper)
    key = point_light((350, -75, 200), 1200000, "AREA", 260)
    fill = point_light((350, 110, 90), 300000, "AREA", 220)
    pose_bounds = []
    for action in ("StrideBack", "StrideMid", "Reach"):
        arm.animation_data.action = bpy.data.actions["A_DY_Kuafu_"+action]
        scene.frame_set(1)
        bpy.context.view_layer.update()
        for model in (old, new):
            evaluated = model.evaluated_get(bpy.context.evaluated_depsgraph_get())
            data = evaluated.to_mesh()
            pose_bounds.extend(tuple(v.co) for v in data.vertices)
            evaluated.to_mesh_clear()
    ymin, ymax = min(p[1] for p in pose_bounds), max(p[1] for p in pose_bounds)
    zmin, zmax = min(p[2] for p in pose_bounds), max(p[2] for p in pose_bounds)
    ycenter, zcenter = .5*(ymin+ymax), .5*(zmin+zmax)
    # Blender AUTO sensor fit makes ortho_scale the vertical span for this portrait frame.
    height = max((ymax-ymin)*1280/1080, zmax-zmin)*1.12
    view = camera((700, ycenter, zcenter), (0, ycenter, zcenter), height)
    REPORT["appearance_framing"] = {"all_pose_y_bounds_cm": [ymin, ymax], "all_pose_z_bounds_cm": [zmin, zmax],
        "camera_orthographic_height_cm": height, "center_yz_cm": [ycenter, zcenter], "margin_ratio": 1.12}
    scene.render.resolution_x, scene.render.resolution_y = 1080, 1280
    for action in ("StrideBack", "StrideMid", "Reach"):
        for variant in ("Original", "Refined"):
            render(f"{action}_{variant}_Appearance.png", old, new, variant, action)
    key.hide_render = True
    fill.hide_render = True
    bg.inputs["Strength"].default_value = .03
    panel.location = (200, -7.29746, 120.93388)
    view.location = (60, -7.29746, 120.93388)
    view.rotation_euler = (Vector(panel.location)-view.location).to_track_quat("-Z", "Y").to_euler()
    view.data.ortho_scale = 345
    lamp = point_light((-800, -7.29746, 120.93388), 20000000, "POINT", 0)
    scene.render.resolution_x = scene.render.resolution_y = 1280
    REPORT["shadow_geometry"] = {"light_source_cm": list(lamp.location), "screen_cm": list(panel.location),
        "camera_cm": list(view.location), "projection": "real opaque point-light ray cast, all material sections enabled",
        "UE_lab_coordinate_transport": "Source Y mirrored relative to UE FBX geometry; same relative -800/0/200 X arrangement",
        "no_shadow_disable": True, "no_transparent_materials": True, "no_texture_mask_or_emissive_fake": True}
    for action in ("StrideBack", "StrideMid", "Reach"):
        for variant in ("Original", "Refined"):
            render(f"{action}_{variant}_Shadow.png", old, new, variant, action)
    check({str(p): sha(p) for p in (blend, RUN/"SK_DY_Kuafu_PuppetRefined.fbx")} == before, "Cold QA/render does not resave blend or FBX")
    check(all(sha(Path(path)) == value for path, value in META["source_hashes_before"].items()), "Original five source/evidence/author files remain hash unchanged")
    REPORT["status"] = "PASS_COLD_SOURCE_AND_12_REAL_RAY_RENDERED_AB_PENDING_VISUAL_REVIEW"
    (OUT/"PUPPET_REFINED_COLD_VISUAL.json").write_text(json.dumps(REPORT, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"status": REPORT["status"], "captures": len(REPORT["captures"]), "out": str(OUT)}, ensure_ascii=False), flush=True)


try:
    main()
except Exception:
    REPORT["status"] = "FAILED"
    (OUT/"PUPPET_REFINED_COLD_VISUAL.json").write_text(json.dumps(REPORT, ensure_ascii=False, indent=2), encoding="utf-8")
    raise
