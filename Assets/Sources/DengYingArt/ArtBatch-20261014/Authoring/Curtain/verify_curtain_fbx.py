"""Cold-process comparison of actual editable blend and exported FBX mesh data."""
from pathlib import Path
import hashlib
import json
import math
import bpy
import bmesh
from mathutils import Vector, kdtree

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "Run2" / "DY_StageWingCurtain_Editable.blend"
FBX = ROOT / "Run2" / "SM_DY_StageWingCurtain.fbx"
OUT = ROOT / "FBX-Verify-Run1"
NAMES = ["SM_DY_StageWingCurtain_Body", "SM_DY_StageWingCurtain_FoldedHem"]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def observe(obj):
    depsgraph = bpy.context.evaluated_depsgraph_get()
    evaluated = obj.evaluated_get(depsgraph)
    mesh = evaluated.to_mesh(preserve_all_data_layers=True, depsgraph=depsgraph)
    mesh.calc_loop_triangles()
    points = [tuple(obj.matrix_world @ vertex.co) for vertex in mesh.vertices]
    uv = [tuple(loop.uv) for loop in mesh.uv_layers.active.data]
    bm = bmesh.new()
    bm.from_mesh(mesh)
    stats = {"name": obj.name, "vertices": len(mesh.vertices), "polygons": len(mesh.polygons), "triangles": len(mesh.loop_triangles),
             "uv_layers": len(mesh.uv_layers), "uv_corners": len(uv), "uv_bounds": [[min(point[axis] for point in uv) for axis in range(2)], [max(point[axis] for point in uv) for axis in range(2)]],
             "bounds_world_metres_z_up": [[min(point[axis] for point in points) for axis in range(3)], [max(point[axis] for point in points) for axis in range(3)]],
             "boundary_edges": sum(edge.is_boundary for edge in bm.edges), "nonmanifold_edges": sum(not edge.is_manifold for edge in bm.edges),
             "positive_closed_volume_m3": bm.calc_volume(signed=True), "zero_area_triangles": sum(tri.area < 1e-12 for tri in mesh.loop_triangles),
             "material_names": [slot.material.name for slot in obj.material_slots], "normal_corner_count": len(mesh.corner_normals)}
    assert stats["boundary_edges"] == stats["nonmanifold_edges"] == stats["zero_area_triangles"] == 0
    assert stats["positive_closed_volume_m3"] > 0 and stats["uv_layers"] == 1 and stats["normal_corner_count"] == len(mesh.loops)
    assert all(math.isfinite(value) for pair in points+uv for value in pair)
    bm.free()
    evaluated.to_mesh_clear()
    return stats, points, uv


def nearest_max(first, second):
    tree = kdtree.KDTree(len(first))
    for index, point in enumerate(first):
        tree.insert(Vector(point), index)
    tree.balance()
    return max(tree.find(Vector(point))[2] for point in second)


def main():
    assert not OUT.exists() and not bpy.context.preferences.filepaths.use_scripts_auto_execute
    blend_hash, fbx_hash = sha(SOURCE), sha(FBX)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    with bpy.data.libraries.load(str(SOURCE), link=False) as (available, requested):
        assert all(name in available.objects for name in NAMES)
        # Blender resolves this assigned list in-place to data-blocks.
        requested.objects = NAMES.copy()
    for obj in requested.objects:
        assert obj.type == "MESH" and obj.parent is None and not obj.constraints
        assert not obj.animation_data
        bpy.context.scene.collection.objects.link(obj)
        obj.matrix_world = obj.matrix_basis.copy()
    bpy.context.view_layer.update()
    original = {obj.name: observe(obj) for obj in requested.objects}
    assert len(original) == 2
    bpy.ops.wm.read_factory_settings(use_empty=True)
    assert not list(bpy.data.objects)
    bpy.ops.import_scene.fbx(filepath=str(FBX), use_custom_normals=True, use_anim=False)
    objects = list(bpy.data.objects)
    print(json.dumps({"actual_fbx_objects": [{"name": obj.name, "type": obj.type, "parent": obj.parent.name if obj.parent else None} for obj in objects]}))
    assert len(objects) == 2 and {obj.name for obj in objects} == set(NAMES)
    assert all(obj.type == "MESH" for obj in objects)
    bpy.context.view_layer.update()
    rows = []
    for obj in objects:
        actual, actual_points, actual_uv = observe(obj)
        expected, expected_points, expected_uv = original[obj.name]
        for field in ["vertices", "polygons", "triangles", "uv_layers", "uv_corners", "material_names", "normal_corner_count"]:
            assert actual[field] == expected[field], (obj.name, field, expected[field], actual[field])
        distance = max(nearest_max(expected_points, actual_points), nearest_max(actual_points, expected_points))
        assert distance < 1e-5, (obj.name, distance)
        assert abs(actual["positive_closed_volume_m3"]-expected["positive_closed_volume_m3"]) < 1e-7
        expected_flat = sorted(value for pair in expected_uv for value in pair)
        actual_flat = sorted(value for pair in actual_uv for value in pair)
        uv_error = max(abs(first-second) for first, second in zip(expected_flat, actual_flat))
        assert uv_error < 1e-6
        rows.append({"source": expected, "fbx": actual, "bidirectional_max_vertex_distance_metres": distance,
                     "maximum_uv_value_difference": uv_error, "procedural_shader_transfer_not_claimed": True})
    assert sha(SOURCE) == blend_hash and sha(FBX) == fbx_hash
    OUT.mkdir()
    report = {"status": "PASS-COLD-FBX-TWO-CLOSED-CURTAIN-MESHES", "blender_version": bpy.app.version_string,
              "source_blend": str(SOURCE), "source_sha256": blend_hash, "fbx": str(FBX), "fbx_sha256": fbx_hash,
              "separate_fresh_process": True, "source_blend_and_fbx_unchanged": True, "meshes": rows,
              "camera_lights_source_reference_exported": False, "ue_imported": False,
              "material_limit": "FBX does not preserve procedural yarn shaders. Rebuild UE material or bake it before production admission."}
    (OUT / "COLD-FBX-VERIFY.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({"status": report["status"], "meshes": [{"name": row["fbx"]["name"], "triangles": row["fbx"]["triangles"], "boundary_edges": row["fbx"]["boundary_edges"], "nonmanifold_edges": row["fbx"]["nonmanifold_edges"], "max_vertex_distance_metres": row["bidirectional_max_vertex_distance_metres"]} for row in rows]}, indent=2))


if __name__ == "__main__":
    main()
