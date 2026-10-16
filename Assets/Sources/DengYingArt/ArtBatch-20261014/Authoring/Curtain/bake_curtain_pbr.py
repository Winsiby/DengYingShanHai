"""Bake our own procedural shader on the actual closed mesh and export its UV.

Original source UVs overlap across shell/hem, so a unique BakeUV becomes channel
0 of a new FBX; source UV remains channel 1. Run2 is never changed.
"""
from pathlib import Path
import hashlib
import json
import math
import bpy
import bmesh
import numpy as np
from mathutils import Vector

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "Run2" / "DY_StageWingCurtain_Editable.blend"
OUT = ROOT / "Baked-Run2"
SIZE = 2048
NAMES = ["SM_DY_StageWingCurtain_Body", "SM_DY_StageWingCurtain_FoldedHem"]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def uv_coverage(mesh):
    mesh.calc_loop_triangles()
    layer = mesh.uv_layers["BakeUV"]
    counts = np.zeros((SIZE, SIZE), dtype=np.uint16)
    missing = 0
    zero_uv = 0
    for tri in mesh.loop_triangles:
        points = np.array([[layer.data[index].uv.x*SIZE, (1-layer.data[index].uv.y)*SIZE] for index in tri.loops])
        assert np.isfinite(points).all() and points.min() >= -1e-4 and points.max() <= SIZE+1e-4
        minimum = np.maximum(np.floor(points.min(axis=0)).astype(int), 0)
        maximum = np.minimum(np.ceil(points.max(axis=0)).astype(int), SIZE-1)
        width, height = maximum-minimum+1
        if width <= 0 or height <= 0:
            missing += 1
            continue
        x, y = np.meshgrid(np.arange(minimum[0], maximum[0]+1)+0.5, np.arange(minimum[1], maximum[1]+1)+0.5)
        a, b, c = points
        den = (b[1]-c[1])*(a[0]-c[0])+(c[0]-b[0])*(a[1]-c[1])
        if abs(den) < 1e-9:
            zero_uv += 1
            continue
        bary_a = ((b[1]-c[1])*(x-c[0])+(c[0]-b[0])*(y-c[1]))/den
        bary_b = ((c[1]-a[1])*(x-c[0])+(a[0]-c[0])*(y-c[1]))/den
        inside = (bary_a > 1e-7) & (bary_b > 1e-7) & (1-bary_a-bary_b > 1e-7)
        counts[minimum[1]:maximum[1]+1, minimum[0]:maximum[0]+1] += inside.astype(np.uint16)
        if not inside.any():
            missing += 1
    coverage = counts > 0
    result = {"resolution": SIZE, "covered_pixels": int(coverage.sum()), "coverage_percent": float(coverage.mean()*100),
              "overlapping_triangle_interior_pixels": int((counts > 1).sum()), "zero_area_uv_triangles": zero_uv,
              "triangles_without_pixel_centres": missing, "triangles": len(mesh.loop_triangles),
              "method": "actual BakeUV triangle raster at pixel centres; shared edges excluded"}
    assert result["covered_pixels"] > SIZE*SIZE*0.25 and result["zero_area_uv_triangles"] == 0
    assert result["overlapping_triangle_interior_pixels"] == 0, result
    np.save(OUT / "UV-COVERAGE-MASK.npy", coverage)
    return result, coverage


def pixel_stats(image, coverage):
    data = np.array(image.pixels[:], dtype=np.float32).reshape((SIZE, SIZE, 4))[::-1]
    assert np.isfinite(data).all()
    pixels = data[coverage]
    return {"covered_rgb_min": pixels[:, :3].min(axis=0).tolist(), "covered_rgb_max": pixels[:, :3].max(axis=0).tolist(),
            "covered_rgb_std": pixels[:, :3].std(axis=0).tolist(), "covered_alpha_min": float(pixels[:, 3].min()),
            "covered_alpha_max": float(pixels[:, 3].max())}


def main():
    assert not OUT.exists() and not bpy.context.preferences.filepaths.use_scripts_auto_execute
    before = sha(SOURCE)
    OUT.mkdir()
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.unit_settings.system = "METRIC"
    scene.unit_settings.scale_length = 1
    with bpy.data.libraries.load(str(SOURCE), link=False) as (available, requested):
        assert all(name in available.objects for name in NAMES)
        requested.objects = NAMES.copy()
    for obj in requested.objects:
        scene.collection.objects.link(obj)
        obj.matrix_world = obj.matrix_basis.copy()
    bpy.context.view_layer.update()
    for obj in requested.objects:
        bpy.ops.object.select_all(action="DESELECT")
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.convert(target="MESH")
    bpy.ops.object.select_all(action="SELECT")
    bpy.context.view_layer.objects.active = requested.objects[0]
    bpy.ops.object.join()
    obj = bpy.context.object
    obj.name = "SM_DY_StageWingCurtain"
    mesh = obj.data
    assert len(bpy.data.objects) == 1 and len(mesh.materials) == 2
    source_uv = [tuple(item.uv) for item in mesh.uv_layers.active.data]
    for layer in list(mesh.uv_layers):
        mesh.uv_layers.remove(layer)
    bake_uv = mesh.uv_layers.new(name="BakeUV")
    retained_uv = mesh.uv_layers.new(name="SourceUV")
    for item, pair in zip(retained_uv.data, source_uv):
        item.uv = pair
    mesh.uv_layers.active = bake_uv
    bake_uv.active_render = True
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    # Smart projection and packing run on the full closed mesh, never a plane.
    bpy.ops.uv.smart_project(angle_limit=math.radians(66), island_margin=0.006, correct_aspect=True, scale_to_bounds=True)
    bpy.ops.uv.pack_islands(rotate=True, margin=0.004, scale=True)
    bpy.ops.object.mode_set(mode="OBJECT")
    assert mesh.uv_layers[0].name == "BakeUV" and mesh.uv_layers[1].name == "SourceUV"
    assert all((item.uv-Vector(pair)).length < 1e-8 for item, pair in zip(mesh.uv_layers[1].data, source_uv))
    coverage_report, coverage = uv_coverage(mesh)
    bm = bmesh.new()
    bm.from_mesh(mesh)
    assert all(edge.is_manifold for edge in bm.edges) and bm.calc_volume(signed=True) > 0
    bm.free()
    scene.render.engine = "CYCLES"
    scene.cycles.samples = 8
    scene.render.bake.use_clear = True
    scene.render.bake.margin = 12
    scene.render.bake.use_selected_to_active = False
    scene.render.bake.normal_space = "TANGENT"
    scene.render.bake.normal_r = "POS_X"
    scene.render.bake.normal_g = "NEG_Y"
    scene.render.bake.normal_b = "POS_Z"
    targets = {}
    texture_rows = []
    for label, bake_type, color_space in [("BaseColor", "EMIT", "sRGB"), ("Roughness", "ROUGHNESS", "Non-Color"), ("Normal_DX", "NORMAL", "Non-Color")]:
        image = bpy.data.images.new(f"T_DY_StageWing_{label}", width=SIZE, height=SIZE, alpha=True, float_buffer=False)
        image.colorspace_settings.name = color_space
        image.generated_color = (0, 0, 0, 0)
        targets[label] = image
        for mat in mesh.materials:
            node = mat.node_tree.nodes.new("ShaderNodeTexImage")
            node.name = "Baked_"+label
            node.label = "Actual full-mesh BakeUV, "+label
            node.image = image
            mat.node_tree.nodes.active = node
            node.select = True
        if bake_type == "EMIT":
            saved_surface = []
            for mat in mesh.materials:
                tree = mat.node_tree
                output = next(node for node in tree.nodes if node.type == "OUTPUT_MATERIAL")
                bsdf = next(node for node in tree.nodes if node.type == "BSDF_PRINCIPLED")
                assert len(output.inputs["Surface"].links) == 1
                saved_surface.append((tree, output, output.inputs["Surface"].links[0].from_socket))
                emission = tree.nodes.new("ShaderNodeEmission")
                emission.name = "Pure BaseColor bake, no lighting or Sheen"
                emission.inputs["Color"].default_value = bsdf.inputs["Base Color"].default_value
                emission.inputs["Strength"].default_value = 1
                tree.links.new(emission.outputs["Emission"], output.inputs["Surface"])
            bpy.ops.object.bake(type="EMIT")
            for tree, output, source_socket in saved_surface:
                tree.links.new(source_socket, output.inputs["Surface"])
                tree.nodes.remove(tree.nodes["Pure BaseColor bake, no lighting or Sheen"])
        else:
            bpy.ops.object.bake(type=bake_type)
        stats = pixel_stats(image, coverage)
        assert stats["covered_alpha_min"] > 0.99, (label, stats)
        path = OUT / f"T_DY_StageWing_{label}_2K.png"
        image.filepath_raw = str(path)
        image.file_format = "PNG"
        image.save()
        assert path.is_file() and path.stat().st_size > 1000
        texture_rows.append({"name": label, "path": str(path), "bytes": path.stat().st_size, "sha256": sha(path), "color_space": color_space,
                             "native_bake_type": bake_type, "resolution": [SIZE, SIZE], "coverage_stats_stored_channels": stats,
                             "normal_convention": "DirectX tangent normal, negative green/Y; UE FlipGreenChannel=false" if label == "Normal_DX" else None})
    normal_stats = texture_rows[2]["coverage_stats_stored_channels"]
    assert max(normal_stats["covered_rgb_std"][:2]) > 0.002, "A flat default normal is not a weave bake."
    # Texture-backed production material; original procedural nodes remain editable.
    for mat in mesh.materials:
        tree = mat.node_tree
        bsdf = next(node for node in tree.nodes if node.type == "BSDF_PRINCIPLED")
        tree.links.new(tree.nodes["Baked_BaseColor"].outputs["Color"], bsdf.inputs["Base Color"])
        tree.links.new(tree.nodes["Baked_Roughness"].outputs["Color"], bsdf.inputs["Roughness"])
        normal = tree.nodes.new("ShaderNodeNormalMap")
        normal.name = "Baked DX normal converted to Blender GL"
        normal.uv_map = "BakeUV"
        separate = tree.nodes.new("ShaderNodeSeparateColor")
        combine = tree.nodes.new("ShaderNodeCombineColor")
        invert = tree.nodes.new("ShaderNodeMath")
        invert.operation = "SUBTRACT"
        invert.inputs[0].default_value = 1
        tree.links.new(tree.nodes["Baked_Normal_DX"].outputs["Color"], separate.inputs[0])
        tree.links.new(separate.outputs["Red"], combine.inputs["Red"])
        tree.links.new(separate.outputs["Green"], invert.inputs[1])
        tree.links.new(invert.outputs[0], combine.inputs["Green"])
        tree.links.new(separate.outputs["Blue"], combine.inputs["Blue"])
        tree.links.new(combine.outputs[0], normal.inputs["Color"])
        tree.links.new(normal.outputs["Normal"], bsdf.inputs["Normal"])
    fbx = OUT / "SM_DY_StageWingCurtain_BakedUV.fbx"
    bpy.ops.export_scene.fbx(filepath=str(fbx), use_selection=True, object_types={"MESH"}, use_mesh_modifiers=True,
                             mesh_smooth_type="FACE", bake_anim=False, axis_forward="-Y", axis_up="Z", path_mode="RELATIVE")
    blend = OUT / "DY_StageWingCurtain_BakedEditable.blend"
    for image in targets.values():
        image.filepath = "//"+Path(image.filepath_raw).name
    bpy.ops.wm.save_as_mainfile(filepath=str(blend), check_existing=True)
    assert sha(SOURCE) == before
    mesh.calc_loop_triangles()
    report = {"status": "PASS-ACTUAL-CURTAIN-2K-NATIVE-PBR-BAKE-PENDING-COLD-UV-VERIFY", "source_blend": str(SOURCE), "source_sha256": before,
              "source_unchanged": True, "blender_version": bpy.app.version_string, "mesh_name": obj.name,
              "mesh_vertices": len(mesh.vertices), "mesh_polygons": len(mesh.polygons), "mesh_triangles": len(mesh.loop_triangles),
              "uv_channel_0": "BakeUV", "uv_channel_1": "SourceUV", "source_uv_preserved_exactly": True,
              "uv_coverage": coverage_report, "textures": texture_rows,
              "fbx": {"path": str(fbx), "sha256": sha(fbx), "bytes": fbx.stat().st_size},
              "blend": {"path": str(blend), "sha256": sha(blend), "bytes": blend.stat().st_size},
              "bake_on_actual_curved_closed_mesh_not_plane": True, "light_or_ao_baked_into_basecolor": False,
              "normal_ue": "DX negative Y; import Non-Color/Normalmap, do not flip green", "normal_blender": "Blender GL uses green inversion node when previewing DX texture",
              "normal_fbx_auto_import_limit": "Do not trust FBX procedural-normal link conversion; explicitly assign delivered DX normal in UE material.",
              "bitmap_image_generation_service": False, "downloaded_source_images_edited": False, "ue_imported": False, "d_product_writes": False}
    (OUT / "BAKE.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({"status": report["status"], "uv_coverage": coverage_report, "textures": [{"name": row["name"], "bytes": row["bytes"], "color_space": row["color_space"]} for row in texture_rows]}, indent=2))


if __name__ == "__main__":
    main()
