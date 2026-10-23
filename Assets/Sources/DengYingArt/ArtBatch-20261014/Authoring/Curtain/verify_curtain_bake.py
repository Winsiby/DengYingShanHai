"""Cold FBX/UV corner correspondence check and real PNG pixel verification."""
from pathlib import Path
import hashlib
import json
import math
import bpy
import bmesh
import numpy as np
from mathutils import Vector, kdtree

ROOT = Path(__file__).resolve().parent
BAKED = ROOT / "Baked-Run2"
OUT = ROOT / "Baked-Verify-Run2"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def observe(obj):
    mesh = obj.data
    mesh.calc_loop_triangles()
    points = [tuple(obj.matrix_world @ vertex.co) for vertex in mesh.vertices]
    layers = {layer.name: [(mesh.loops[index].vertex_index, tuple(item.uv)) for index, item in enumerate(layer.data)] for layer in mesh.uv_layers}
    assert list(layers) == ["BakeUV", "SourceUV"]
    bm = bmesh.new()
    bm.from_mesh(mesh)
    stats = {"vertices": len(mesh.vertices), "polygons": len(mesh.polygons), "triangles": len(mesh.loop_triangles),
             "boundary_edges": sum(edge.is_boundary for edge in bm.edges), "nonmanifold_edges": sum(not edge.is_manifold for edge in bm.edges),
             "volume_m3": bm.calc_volume(signed=True), "uv_layer_order": list(layers), "material_names": [material.name for material in mesh.materials],
             "polygon_material_counts": {str(index): sum(poly.material_index == index for poly in mesh.polygons) for index in range(len(mesh.materials))}}
    assert stats["boundary_edges"] == stats["nonmanifold_edges"] == 0 and stats["volume_m3"] > 0
    bm.free()
    return stats, points, layers


def grouped_corners(values, mapping=None):
    result = {}
    for vertex, uv in values:
        result.setdefault(mapping[vertex] if mapping is not None else vertex, []).append(uv)
    return {vertex: sorted(pairs) for vertex, pairs in result.items()}


def main():
    assert not OUT.exists() and not bpy.context.preferences.filepaths.use_scripts_auto_execute
    report = json.loads((BAKED / "BAKE.json").read_text(encoding="utf-8"))
    blend = Path(report["blend"]["path"])
    fbx = Path(report["fbx"]["path"])
    assert sha(blend) == report["blend"]["sha256"] and sha(fbx) == report["fbx"]["sha256"]
    bpy.ops.wm.read_factory_settings(use_empty=True)
    with bpy.data.libraries.load(str(blend), link=False) as (available, requested):
        assert report["mesh_name"] in available.objects
        requested.objects = [report["mesh_name"]]
    obj = requested.objects[0]
    bpy.context.scene.collection.objects.link(obj)
    obj.matrix_world = obj.matrix_basis.copy()
    bpy.context.view_layer.update()
    expected, expected_points, expected_uv = observe(obj)
    assert expected["triangles"] == 23072 and len(obj.data.materials) == 2
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=str(fbx), use_anim=False, use_custom_normals=True)
    assert len(bpy.data.objects) == 1
    actual_obj = list(bpy.data.objects)[0]
    assert actual_obj.name == report["mesh_name"] and actual_obj.type == "MESH"
    bpy.context.view_layer.update()
    actual, actual_points, actual_uv = observe(actual_obj)
    for key in ["vertices", "polygons", "triangles", "uv_layer_order", "material_names", "polygon_material_counts"]:
        assert actual[key] == expected[key], (key, actual[key], expected[key])
    assert abs(actual["volume_m3"]-expected["volume_m3"]) < 1e-7
    tree = kdtree.KDTree(len(expected_points))
    for index, point in enumerate(expected_points):
        tree.insert(Vector(point), index)
    tree.balance()
    mapped = [tree.find(Vector(point)) for point in actual_points]
    max_distance = max(item[2] for item in mapped)
    assert max_distance < 1e-5
    index_mapping = [item[1] for item in mapped]
    assert len(set(index_mapping)) == len(expected_points), "Point-set equivalence alone cannot prove corner UV correspondence."
    uv_rows = []
    for layer in ["BakeUV", "SourceUV"]:
        expected_groups = grouped_corners(expected_uv[layer])
        actual_groups = grouped_corners(actual_uv[layer], index_mapping)
        assert set(actual_groups) == set(expected_groups)
        error = 0
        for vertex in expected_groups:
            first, second = expected_groups[vertex], actual_groups[vertex]
            assert len(first) == len(second)
            error = max(error, max(abs(a-b) for pair_a, pair_b in zip(first, second) for a, b in zip(pair_a, pair_b)))
        assert error < 1e-6
        uv_rows.append({"name": layer, "same_world_vertex_uv_corner_multisets": True, "max_corner_uv_error": error})
    coverage = np.load(BAKED / "UV-COVERAGE-MASK.npy", allow_pickle=False)
    assert coverage.shape == (2048, 2048) and coverage.dtype == np.bool_ and int(coverage.sum()) == report["uv_coverage"]["covered_pixels"]
    textures = []
    for row in report["textures"]:
        path = Path(row["path"])
        assert sha(path) == row["sha256"]
        raw = path.read_bytes()
        assert raw[:8] == b"\x89PNG\r\n\x1a\n"
        width = int.from_bytes(raw[16:20], "big")
        height = int.from_bytes(raw[20:24], "big")
        assert [width, height] == [2048, 2048]
        image = bpy.data.images.load(str(path), check_existing=False)
        image.colorspace_settings.name = row["color_space"]
        data = np.array(image.pixels[:], dtype=np.float32).reshape((height, width, 4))[::-1]
        # Byte-backed Blender image.pixels exposes stored channel values.
        # Explicitly decode sRGB instead of calling those bytes linear colors.
        if row["color_space"] == "sRGB":
            rgb = data[:, :, :3].astype(np.float64)
            data[:, :, :3] = np.where(rgb <= 0.04045, rgb/12.92, ((rgb+0.055)/1.055)**2.4)
        pixels = data[coverage]
        assert np.isfinite(data).all() and pixels[:, 3].min() > 0.99
        minimum, maximum, deviation = pixels[:, :3].min(axis=0), pixels[:, :3].max(axis=0), pixels[:, :3].std(axis=0)
        mean = pixels[:, :3].mean(axis=0, dtype=np.float64)
        print(json.dumps({"loaded_png": row["name"], "image_colorspace": image.colorspace_settings.name, "rgb_min": minimum.tolist(), "rgb_max": maximum.tolist(), "linear_rgb_mean": mean.tolist()}))
        if row["name"] == "BaseColor":
            assert 0.035 < mean[0] < 0.07 and mean[0] > mean[1]*5
        elif row["name"] == "Roughness":
            assert minimum[0] >= 0.76 and maximum[0] <= 0.88 and deviation[0] > 0.005
            assert np.abs(pixels[:, 0]-pixels[:, 1]).max() < 1e-6 and np.abs(pixels[:, 1]-pixels[:, 2]).max() < 1e-6
        else:
            assert max(deviation[:2]) > 0.002 and minimum[2] >= 0.48
        textures.append({"name": row["name"], "PNG_dimensions": [width, height], "PNG_bit_depth": raw[24], "PNG_color_type": raw[25],
                         "colorspace_for_sampling": row["color_space"], "covered_pixel_count": len(pixels),
                         "linear_rgb_min": minimum.tolist(), "linear_rgb_max": maximum.tolist(), "linear_rgb_std": deviation.tolist(),
                         "covered_alpha_min": float(pixels[:, 3].min()), "sha256": sha(path), "not_flat_placeholder": True})
    assert sha(blend) == report["blend"]["sha256"] and sha(fbx) == report["fbx"]["sha256"]
    OUT.mkdir()
    result = {"status": "PASS-COLD-FBX-ACTUAL-BUFFER-UV-AND-2K-PNG-PIXELS", "blender_version": bpy.app.version_string,
              "mesh": actual, "max_world_vertex_distance_metres": max_distance, "uv_corner_correspondence": uv_rows,
              "textures": textures, "actual_unique_uv_coverage": report["uv_coverage"], "baked_actual_curved_mesh_not_unrelated_plane": True,
              "source_run2_preserved": True, "ue_imported": False, "d_product_writes": False,
              "normal_convention": "Cycles native tangent bake R=+X, G=-Y, B=+Z (DX). UE Normalmap/sRGB=false/FlipGreenChannel=false.",
              "subpixel_uv_note": str(report["uv_coverage"]["triangles_without_pixel_centres"])+" triangles have no 2K pixel centre, mostly small thickness/bevel sides; report and 12px bake padding are retained. Not claimed full-texel-per-triangle.",
              "protected_LICENSES_md_read_or_hashed": False}
    (OUT / "COLD-PBR-VERIFY.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps({"status": result["status"], "mesh_triangles": actual["triangles"], "uv_layers": actual["uv_layer_order"],
                      "max_world_vertex_distance_metres": max_distance, "uv_corner_correspondence": uv_rows,
                      "textures": [{"name": row["name"], "bit_depth": row["PNG_bit_depth"], "covered_alpha_min": row["covered_alpha_min"], "rgb_std": row["linear_rgb_std"]} for row in textures]}, indent=2))


if __name__ == "__main__":
    main()
