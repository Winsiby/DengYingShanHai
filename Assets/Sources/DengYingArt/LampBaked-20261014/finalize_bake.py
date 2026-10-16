"""Normalize baked normal vectors and export UV1 tangent basis, preserving UV0."""
import bpy
import hashlib
import inspect
import json
from pathlib import Path
import numpy as np
from mathutils import Vector
from io_scene_fbx import export_fbx_bin, parse_fbx

OUT = Path(__file__).resolve().parent
REPORT = {"status": "starting", "normal_corrections": [], "tangents": []}
BAKE = json.loads((OUT / "LAMP_BAKE.json").read_text(encoding="utf-8"))
if (OUT / "LAMP_BAKE_FINALIZE.json").exists():
    REPORT["previous_attempt"] = json.loads((OUT / "LAMP_BAKE_FINALIZE.json").read_text(encoding="utf-8"))


def write_report():
    (OUT / "LAMP_BAKE_FINALIZE.json").write_text(json.dumps(REPORT, ensure_ascii=False, indent=2), encoding="utf-8")


def coverage(ob):
    mask = np.zeros((2048, 2048), dtype=bool)
    ob.data.calc_loop_triangles()
    uv = ob.data.uv_layers["BakeUV1"]
    for triangle in ob.data.loop_triangles:
        points = np.array([uv.data[i].uv[:] for i in triangle.loops]) * 2048
        lo = np.maximum(np.floor(points.min(0) - .5).astype(int), 0)
        hi = np.minimum(np.ceil(points.max(0) - .5).astype(int), 2047)
        if np.any(hi < lo): continue
        xs, ys = np.meshgrid(np.arange(lo[0], hi[0] + 1) + .5, np.arange(lo[1], hi[1] + 1) + .5)
        signs = []
        for i in range(3):
            a, b = points[i], points[(i + 1) % 3]
            signs.append((b[0] - a[0]) * (ys - a[1]) - (b[1] - a[1]) * (xs - a[0]))
        inside = ((signs[0] >= -1e-7) & (signs[1] >= -1e-7) & (signs[2] >= -1e-7)) | \
                 ((signs[0] <= 1e-7) & (signs[1] <= 1e-7) & (signs[2] <= 1e-7))
        mask[lo[1]:hi[1] + 1, lo[0]:hi[0] + 1] |= inside
    inner = mask.copy()
    for axis in (0, 1):
        for step in (-1, 1): inner &= np.roll(mask, step, axis)
    return mask, inner


def stat(values):
    return {"count": int(values.size), "min": float(values.min()), "max": float(values.max()),
            "p01_p50_p99": np.percentile(values, [1, 50, 99]).tolist(),
            "error_above_04": int(np.count_nonzero(abs(values - 1) > .04))}


def find(elem, id):
    return next(child for child in elem.elems if child.id == id)


def keep_render_triangles(ob):
    old = ob.data
    old.calc_loop_triangles()
    faces = [tuple(triangle.vertices) for triangle in old.loop_triangles]
    loop_ids = [loop for triangle in old.loop_triangles for loop in triangle.loops]
    normals = [old.corner_normals[loop].vector[:] for loop in loop_ids]
    mesh = bpy.data.meshes.new(old.name + "_RenderTriangles")
    mesh.from_pydata([vertex.co[:] for vertex in old.vertices], [], faces)
    for material in old.materials: mesh.materials.append(material)
    for face, triangle in zip(mesh.polygons, old.loop_triangles):
        face.material_index = old.polygons[triangle.polygon_index].material_index
        face.use_smooth = old.polygons[triangle.polygon_index].use_smooth
    for layer in old.uv_layers:
        new = mesh.uv_layers.new(name=layer.name)
        for loop, source_loop in zip(new.data, loop_ids): loop.uv = layer.data[source_loop].uv
        new.active_render = layer.active_render
    mesh.uv_layers.active_index = 1
    mesh.normals_split_custom_set(normals)
    assert len(mesh.vertices) == len(old.vertices) and len(mesh.polygons) == len(old.loop_triangles)
    assert all(a.co == b.co for a, b in zip(mesh.vertices, old.vertices))
    ob.data = mesh
    REPORT.setdefault("triangulation", []).append({"mesh": ob.name,
        "method": "Copy existing render loop_triangles; original vertex coordinates, UV0/UV1 corner values, normals and material partitions retained",
        "triangles": len(faces), "vertices": len(mesh.vertices), "original_polygons": len(old.polygons)})


def main():
    bpy.ops.wm.open_mainfile(filepath=str(OUT / "DY_HeroSpotlight_Baked.blend"))
    scene = bpy.context.scene
    for name in ("LampBody", "LampStand"):
        ob = bpy.data.objects["SM_DY_" + name + "_Baked"]
        keep_render_triangles(ob)
        file = OUT / ("T_DY_" + name + "_NormalDX.png")
        image = bpy.data.images.load(str(file), check_existing=False)
        image.colorspace_settings.name = "Non-Color"
        pixels = np.empty(2048 * 2048 * 4, dtype=np.float32)
        image.pixels.foreach_get(pixels); pixels = pixels.reshape(2048, 2048, 4)
        vectors = pixels[:, :, :3] * 2 - 1
        lengths = np.linalg.norm(vectors, axis=2)
        mask, inner = coverage(ob)
        row = {"file": str(file), "before_sha256": hashlib.sha256(file.read_bytes()).hexdigest().upper(),
               "all": stat(lengths), "covered": stat(lengths[mask]), "interior": stat(lengths[inner]),
               "boundary": stat(lengths[mask & ~inner]), "outside": stat(lengths[~mask])}
        REPORT["normal_corrections"].append(row); write_report()
        assert np.isfinite(vectors).all() and lengths.min() > .01, "Zero/invalid normal needs further diagnosis"
        pixels[:, :, :3] = (vectors / lengths[:, :, None] + 1) * .5
        image.pixels.foreach_set(pixels.ravel())
        image.filepath_raw = str(file); image.file_format = "PNG"; image.save()
        image.reload()
        image.pixels.foreach_get(pixels.ravel())
        row["after"] = stat(np.linalg.norm(pixels[:, :, :3] * 2 - 1, axis=2))
        assert row["after"]["error_above_04"] == 0
        row["after_sha256"] = hashlib.sha256(file.read_bytes()).hexdigest().upper()
        row["operation"] = "Unit normalize decoded tangent vector; direction preserved, then 8-bit PNG quantization"
        for texture in BAKE["bakes"]:
            if texture["file"] == str(file): texture["sha256"] = row["after_sha256"]
        for material in ob.data.materials:
            for node in material.node_tree.nodes:
                if node.type == "TEX_IMAGE" and Path(bpy.path.abspath(node.image.filepath)) == file:
                    node.image.reload()
    # The installed exporter writes primary TBN from the first UV layer by default.
    # Override only its tangent computation in memory; all UV arrays stay unchanged.
    source = inspect.getsource(export_fbx_bin.fbx_data_mesh_elements)
    assert source.count("me.calc_tangents(uvmap=name)") == 1
    source = source.replace("me.calc_tangents(uvmap=name)", "me.calc_tangents(uvmap='BakeUV1')")
    needle = 'elem_data_single_string_unicode(lay_nor, b"Name", name)'
    assert source.count(needle) == 2
    source = source.replace(needle, 'elem_data_single_string_unicode(lay_nor, b"Name", "BakeUV1")')
    exec(compile(source, export_fbx_bin.__file__, "exec"), export_fbx_bin.__dict__)
    for name in ("LampBody", "LampStand"):
        ob = bpy.data.objects["SM_DY_" + name + "_Baked"]
        bpy.ops.object.select_all(action="DESELECT"); ob.select_set(True)
        bpy.context.view_layer.objects.active = ob
        location = ob.location.copy(); ob.location = (0, 0, 0)
        file = OUT / (ob.name + ".fbx")
        bpy.ops.export_scene.fbx(filepath=str(file), use_selection=True, object_types={"MESH"},
            apply_unit_scale=True, apply_scale_options="FBX_SCALE_UNITS", axis_forward="X", axis_up="Z",
            use_mesh_modifiers=True, mesh_smooth_type="FACE", use_tspace=True,
            add_leaf_bones=False, bake_anim=False, path_mode="ABSOLUTE", embed_textures=False)
        ob.location = location
        root, version = parse_fbx.parse(str(file))
        geometry = next(e for e in find(root, b"Objects").elems if e.id == b"Geometry")
        tangent_sets = [e for e in geometry.elems if e.id == b"LayerElementTangent"]
        binormal_sets = [e for e in geometry.elems if e.id == b"LayerElementBinormal"]
        assert len(tangent_sets) == len(binormal_sets) == 2
        assert [find(e, b"Name").props[0] for e in tangent_sets] == [b"BakeUV1", b"BakeUV1"]
        ts = [np.array(find(e, b"Tangents").props[0]).reshape(-1, 3) for e in tangent_sets]
        bs = [np.array(find(e, b"Binormals").props[0]).reshape(-1, 3) for e in binormal_sets]
        REPORT["last_tbn_check"] = {"file": str(file),
            "tangent_sets_finite": all(np.isfinite(value).all() for value in ts),
            "binormal_sets_finite": all(np.isfinite(value).all() for value in bs),
            "tangent_set_difference": float(np.max(abs(ts[0] - ts[1]))),
            "binormal_set_difference": float(np.max(abs(bs[0] - bs[1])))}
        write_report()
        assert all(np.isfinite(value).all() for value in ts + bs)
        assert np.max(abs(ts[0] - ts[1])) < 1e-5 and np.max(abs(bs[0] - bs[1])) < 1e-5
        ob.data.calc_tangents(uvmap="BakeUV1")
        expected_t = np.array([loop.tangent[:] for loop in ob.data.loops])
        expected_b = np.array([loop.bitangent[:] for loop in ob.data.loops])
        tangent_error = float(np.max(abs(ts[0] - expected_t)))
        binormal_error = float(np.max(abs(bs[0] - expected_b)))
        assert tangent_error < 1e-5 and binormal_error < 1e-5, (tangent_error, binormal_error)
        REPORT["tangents"].append({"file": str(file), "primary_tbn_name": "BakeUV1",
            "loop_vectors": len(ts[0]), "tangent_max_error": tangent_error, "binormal_max_error": binormal_error,
            "uv0_preserved": True, "ue_normal_import": "Import Normals and Tangents",
            "ue_recompute_normals": False, "ue_recompute_tangents": False,
            "ue_generate_lightmap_uvs": False, "ue_atlas_texcoord": 1})
        write_report()
    scene.cycles.samples = 64; scene.render.threads_mode = "FIXED"; scene.render.threads = 4
    for file, location, target, scale, resolution in (
            ("Lamp_Baked_Full.png", (5, -7, 2.15), (-.035, 0, -1.48), 4.5, (1440, 1920)),
            ("Lamp_Baked_Head.png", (2.4, -2.8, .85), (0, 0, -.17), 1.47, (1920, 1440))):
        scene.camera.location = location
        scene.camera.rotation_euler = (Vector(target) - scene.camera.location).to_track_quat("-Z", "Y").to_euler()
        scene.camera.data.type = "ORTHO"; scene.camera.data.ortho_scale = scale
        scene.render.resolution_x, scene.render.resolution_y = resolution
        scene.render.filepath = str(OUT / file); bpy.ops.render.render(write_still=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT / "DY_HeroSpotlight_Baked.blend"))
    BAKE["source_unchanged"] = all(hashlib.sha256(Path(file).read_bytes()).hexdigest().upper() == sha
                                   for file, sha in BAKE["source_hashes_before"].items())
    assert BAKE["source_unchanged"]
    (OUT / "LAMP_BAKE.json").write_text(json.dumps(BAKE, ensure_ascii=False, indent=2), encoding="utf-8")
    REPORT["status"] = "PASS_NORMAL_NORMALIZATION_UV1_PRIMARY_TBN_RENDERED"
    write_report()


try:
    main()
except Exception:
    import traceback
    REPORT["status"] = "failed"; REPORT["error"] = traceback.format_exc(); write_report()
    raise
