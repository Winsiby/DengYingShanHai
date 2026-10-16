"""Cold-read baked lamp blend, PNG data, FBX geometry/UV0/corner normals."""
import bpy
import hashlib
import json
import math
from pathlib import Path
import numpy as np
from mathutils import Vector
import sys

OUT = Path(__file__).resolve().parent
sys.path.insert(0, str(OUT))
from bake_lamp import uv_test
from io_scene_fbx import parse_fbx
SOURCE = Path(r"D:\灯影山海\Assets\Sources\DengYingArt\Lamp-20261014\RuntimeVariant")
RESULT = {"status": "starting", "textures": [], "meshes": []}


def read_mesh(file):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=str(file))
    objects = [ob for ob in bpy.context.scene.objects if ob.type == "MESH"]
    assert len(objects) == 1
    ob = objects[0]
    ob.data.calc_loop_triangles()
    vertices = np.array([tuple(ob.matrix_world @ v.co) for v in ob.data.vertices])
    rows = []
    for triangle in ob.data.loop_triangles:
        vertices_order = list(triangle.vertices)
        loops = list(triangle.loops)
        first = vertices_order.index(min(vertices_order))
        vertices_order = vertices_order[first:] + vertices_order[:first]
        loops = loops[first:] + loops[:first]
        rows.append((tuple(vertices_order), [ob.data.uv_layers[0].data[i].uv[:] for i in loops],
                     [(ob.matrix_world.to_3x3() @ ob.data.corner_normals[i].vector).normalized()[:] for i in loops]))
    rows.sort(key=lambda row: row[0])
    triangles = np.array([row[0] for row in rows])
    uv0 = np.array([row[1] for row in rows]).reshape(-1, 2)
    normals = np.array([row[2] for row in rows]).reshape(-1, 3)
    assert np.isfinite(vertices).all() and np.isfinite(uv0).all() and np.isfinite(normals).all()
    assert np.max(abs(np.linalg.norm(normals, axis=1) - 1)) < 1e-5
    return ob, vertices, uv0, normals, triangles


def main():
    bake = json.loads((OUT / "LAMP_BAKE.json").read_text(encoding="utf-8"))
    assert bake["status"] in {"baked_rendered_pending_cold_read_and_visual_qa",
                              "PASS_LOCAL_PBR_BAKE_COLD_READ_VISUAL_REVIEW"} and bake["source_unchanged"]
    assert len(bake["bakes"]) == 6
    for row in bake["bakes"]:
        file = Path(row["file"])
        assert hashlib.sha256(file.read_bytes()).hexdigest().upper() == row["sha256"]
        image = bpy.data.images.load(str(file), check_existing=False)
        image.colorspace_settings.name = row["color_space"]
        assert list(image.size) == [2048, 2048] and image.source == "FILE"
        pixels = np.empty(2048 * 2048 * 4, dtype=np.float32)
        image.pixels.foreach_get(pixels)
        pixels = pixels.reshape(-1, 4)
        assert np.isfinite(pixels).all()
        result = {"file": str(file), "pixels": list(image.size), "sha256": row["sha256"],
            "color_space": row["color_space"], "rgb_min": pixels[:, :3].min(0).tolist(),
            "rgb_max": pixels[:, :3].max(0).tolist(), "rgb_std": pixels[:, :3].std(0).tolist(),
            "nonconstant_rgb": bool(np.any(pixels[:, :3] != pixels[0, :3]))}
        assert result["nonconstant_rgb"], "Blank/constant bake: " + file.name
        if file.stem.endswith("ORM"):
            assert np.max(abs(pixels[:, 0] - 1)) < 1e-5, "ORM R must be white AO"
            result["channels"] = "R=1 white AO, G=source Roughness, B=source Metallic"
        elif file.stem.endswith("NormalDX"):
            lengths = np.linalg.norm(pixels[:, :3] * 2 - 1, axis=1)
            result["normal_vector_length_min_max"] = [float(lengths.min()), float(lengths.max())]
            result["normal_length_max_error"] = float(np.max(abs(lengths - 1)))
            assert result["normal_length_max_error"] < .04, "Normal bake contains invalid vectors"
            result["channels"] = "Tangent R +X / G -Y / B +Z; no additional UE green flip"
        RESULT["textures"].append(result)
    bpy.ops.wm.open_mainfile(filepath=str(OUT / "DY_HeroSpotlight_Baked.blend"))
    final = [ob for ob in bpy.context.scene.objects if ob.name in
             ("SM_DY_LampBody_Baked", "SM_DY_LampStand_Baked")]
    assert len(final) == 2
    graph_rows = []
    for ob in final:
        assert len(ob.data.uv_layers) == 2 and ob.data.uv_layers[1].name == "BakeUV1"
        assert ob.data.uv_layers[0].name == "UVMap"
        assert ob.data.has_custom_normals, "Custom weighted corner normals missing"
        for material in ob.data.materials:
            nodes = material.node_tree.nodes
            textures = [node.image for node in nodes if node.type == "TEX_IMAGE"]
            assert len(textures) == 3 and all(image.source == "FILE" and image.packed_file is None for image in textures)
            assert all(Path(bpy.path.abspath(image.filepath)).parent == OUT for image in textures)
            assert not any(node.type in {"TEX_NOISE", "BUMP", "TEX_COORD"} for node in nodes)
            image_nodes = [node for node in nodes if node.type == "TEX_IMAGE"]
            for node in image_nodes:
                assert node.inputs["Vector"].is_linked
                uv_node = node.inputs["Vector"].links[0].from_node
                assert uv_node.type == "UVMAP" and uv_node.uv_map == "BakeUV1"
                expected_space = "sRGB" if "BaseColor" in node.image.name else "Non-Color"
                assert node.image.colorspace_settings.name == expected_space
            normal = next(node for node in nodes if node.type == "NORMAL_MAP")
            assert normal.uv_map == "BakeUV1" and normal.inputs["Strength"].default_value == 1
            bsdf = next(node for node in nodes if node.type == "BSDF_PRINCIPLED")
            row = {"mesh": ob.name, "source_material": material["SourceMaterial"],
                "textures": [bpy.path.abspath(image.filepath) for image in textures],
                "normal_uv": normal.uv_map, "normal_strength": normal.inputs["Strength"].default_value,
                "transmission": bsdf.inputs["Transmission Weight"].default_value,
                "ior": bsdf.inputs["IOR"].default_value,
                "emission_strength": bsdf.inputs["Emission Strength"].default_value}
            if row["source_material"] == "M_DY_OpticalWindow_SOURCE":
                assert abs(row["transmission"] - .38) < 1e-6 and abs(row["emission_strength"] - .15) < 1e-6
                assert abs(row["ior"] - 1.46) < 1e-6
                assert np.max(abs(np.array(bsdf.inputs["Emission Color"].default_value[:3]) - [.8, .37, .10])) < 1e-6
            graph_rows.append(row)
    RESULT["file_texture_graphs"] = graph_rows
    for name in ("LampBody", "LampStand"):
        ref, ref_v, ref_uv, ref_n, ref_t = read_mesh(SOURCE / ("SM_DY_" + name + "_Source.fbx"))
        ref_count = [len(ref.data.vertices), len(ref.data.polygons), len(ref.data.loops)]
        current, v, uv, n, t = read_mesh(OUT / ("SM_DY_" + name + "_Baked.fbx"))
        assert current.data.has_custom_normals
        count = [len(current.data.vertices), len(current.data.polygons), len(current.data.loops)]
        assert count[0] == ref_count[0] and len(t) == len(ref_t), (name, count, ref_count)
        assert len(current.data.uv_layers) == 2
        # Compare the rendered triangles, including winding, despite source n-gons.
        assert np.array_equal(t, ref_t), "Rendered triangle topology changed: " + name
        geometry_error = float(np.max(abs(v - ref_v)))
        uv0_error = float(np.max(abs(uv - ref_uv)))
        normal_error = float(np.degrees(np.arccos(np.clip(np.sum(n * ref_n, axis=1), -1, 1))).max())
        assert geometry_error < 2e-6, (name, "geometry", geometry_error)
        assert uv0_error < 2e-6, (name, "uv0", uv0_error)
        assert normal_error < .1, (name, "corner normals", normal_error)
        uv1 = np.array([tuple(loop.uv) for loop in current.data.uv_layers[1].data])
        assert np.isfinite(uv1).all() and uv1.min() >= 0 and uv1.max() <= 1
        uv_overlap = uv_test([current], current.data.uv_layers[1].name)
        assert uv_overlap["overlap_pairs"] == 0 and uv_overlap["triangles_nonzero_uv"] == len(t)
        root, _version = parse_fbx.parse(str(OUT / ("SM_DY_" + name + "_Baked.fbx")))
        objects = next(element for element in root.elems if element.id == b"Objects")
        geometry = next(element for element in objects.elems if element.id == b"Geometry")
        primary = next(element for element in geometry.elems if element.id == b"Layer" and element.props[0] == 0)
        bindings = {next(child for child in element.elems if child.id == b"Type").props[0]:
                    next(child for child in element.elems if child.id == b"TypedIndex").props[0]
                    for element in primary.elems if element.id == b"LayerElement"}
        assert bindings[b"LayerElementTangent"] == bindings[b"LayerElementBinormal"] == 0
        for element_name in (b"LayerElementTangent", b"LayerElementBinormal"):
            element = next(element for element in geometry.elems if element.id == element_name and element.props[0] == 0)
            assert next(child for child in element.elems if child.id == b"Name").props[0] == b"BakeUV1"
        RESULT["meshes"].append({"file": str(OUT / ("SM_DY_" + name + "_Baked.fbx")),
            "vertices": len(v), "triangles": len(t), "geometry_max_component_error_m": geometry_error,
            "uv0_max_component_error": uv0_error, "corner_normal_max_angle_error_deg": normal_error,
            "uv_layers": [layer.name for layer in current.data.uv_layers], "uv1_finite_0_1": True,
            "uv1_cold_overlap": uv_overlap,
            "primary_fbx_tangent_basis": "BakeUV1 with Tangent/Binormal TypedIndex 0 on Layer 0",
            "topology_matches_source_fbx": True, "reference": str(SOURCE / ("SM_DY_" + name + "_Source.fbx"))})
    RESULT["source_unchanged"] = all(hashlib.sha256(Path(file).read_bytes()).hexdigest().upper() == sha
                                     for file, sha in bake["source_hashes_before"].items())
    assert RESULT["source_unchanged"]
    assert sum(row["triangles"] for row in RESULT["meshes"]) == 33104
    RESULT["status"] = "PASS_COLD_READ_TEXTURES_GEOMETRY_UV0_CORNER_NORMALS"
    RESULT["visual_qa"] = "pending human-readable image inspection"


try:
    main()
except Exception:
    import traceback
    RESULT["status"] = "failed"
    RESULT["error"] = traceback.format_exc()
    raise
finally:
    (OUT / "LAMP_BAKE_COLD_READ.json").write_text(json.dumps(RESULT, ensure_ascii=False, indent=2), encoding="utf-8")
