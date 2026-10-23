"""Author a thick, hemmed side-stage curtain from a verified CC0 cloth island.

No main projection screen, UE actor, gameplay parameter or project file changes.
Procedural weave is editable Blender shader code, not a downloaded PBR texture.
"""
from pathlib import Path
import hashlib
import json
import math
import bpy
import bmesh
from mathutils import Vector

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT.parent / "DioramaCurtainParts-Run1" / "DioramaCurtainClothIsland00.obj"
OUT = ROOT / "Run2"
HEIGHT_M = 2.8
THICKNESS_M = 0.004


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def read_obj(path):
    vertices, uv, polygons, face_uv = [], [], [], []
    for line in path.read_text(encoding="utf-8").splitlines():
        fields = line.split()
        if not fields:
            continue
        if fields[0] == "v":
            vertices.append(tuple(map(float, fields[1:])))
        elif fields[0] == "vt":
            uv.append(tuple(map(float, fields[1:])))
        elif fields[0] == "f":
            polygons.append([int(corner.split("/")[0])-1 for corner in fields[1:]])
            face_uv.append([uv[int(corner.split("/")[1])-1] for corner in fields[1:]])
    assert len(vertices) == 289 and len(polygons) == 256 and all(len(poly) == 4 for poly in polygons)
    return vertices, polygons, face_uv


def make_mesh(name, vertices, faces, face_uv):
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    assert not mesh.validate()
    layer = mesh.uv_layers.new(name="UVMap")
    for poly, pairs in zip(mesh.polygons, face_uv):
        for loop, pair in zip(poly.loop_indices, pairs):
            layer.data[loop].uv = pair
        poly.use_smooth = True
    return mesh


def link_mesh(name, mesh):
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    return obj


def select(obj):
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj


def geometry(obj):
    evaluated = obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
    mesh = evaluated.to_mesh(preserve_all_data_layers=True, depsgraph=bpy.context.evaluated_depsgraph_get())
    mesh.calc_loop_triangles()
    points = [obj.matrix_world @ vertex.co for vertex in mesh.vertices]
    assert points and all(math.isfinite(value) for point in points for value in point)
    bm = bmesh.new()
    bm.from_mesh(mesh)
    result = {"name": obj.name, "vertices": len(mesh.vertices), "polygons": len(mesh.polygons), "triangles": len(mesh.loop_triangles),
              "bounds_metres_z_up": [[min(point[axis] for point in points) for axis in range(3)], [max(point[axis] for point in points) for axis in range(3)]],
              "uv_layers": len(mesh.uv_layers), "uv_loops": len(mesh.uv_layers.active.data),
              "boundary_edges": sum(edge.is_boundary for edge in bm.edges), "nonmanifold_edges": sum(not edge.is_manifold for edge in bm.edges),
              "signed_volume_m3": bm.calc_volume(signed=True), "zero_area_triangles": sum(tri.area < 1e-12 for tri in mesh.loop_triangles),
              "materials": [slot.material.name for slot in obj.material_slots]}
    bm.free()
    evaluated.to_mesh_clear()
    assert result["boundary_edges"] == result["nonmanifold_edges"] == result["zero_area_triangles"] == 0
    assert result["uv_layers"] == 1 and result["signed_volume_m3"] > 0
    return result


def math_node(tree, operation, name, first=None, second=None):
    node = tree.nodes.new("ShaderNodeMath")
    node.operation = operation
    node.name = name
    node.label = name
    for index, value in enumerate([first, second]):
        if value is None:
            continue
        if isinstance(value, (int, float)):
            node.inputs[index].default_value = value
        else:
            tree.links.new(value, node.inputs[index])
    return node.outputs[0]


def material(name, hem=False):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    tree = mat.node_tree
    tree.nodes.clear()
    output = tree.nodes.new("ShaderNodeOutputMaterial")
    output.location = (800, 0)
    bsdf = tree.nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.location = (520, 0)
    base = (0.044, 0.002, 0.006, 1) if hem else (0.055, 0.0025, 0.0085, 1)
    bsdf.inputs["Base Color"].default_value = base
    bsdf.inputs["Metallic"].default_value = 0
    bsdf.inputs["Roughness"].default_value = 0.86 if hem else 0.8
    bsdf.inputs["IOR"].default_value = 1.46
    bsdf.inputs["Specular IOR Level"].default_value = 0.28
    bsdf.inputs["Sheen Weight"].default_value = 0.12
    bsdf.inputs["Sheen Roughness"].default_value = 0.85
    bsdf.inputs["Transmission Weight"].default_value = 0
    bsdf.inputs["Alpha"].default_value = 1
    mat.diffuse_color = base
    texcoord = tree.nodes.new("ShaderNodeTexCoord")
    texcoord.location = (-850, 0)
    separate = tree.nodes.new("ShaderNodeSeparateXYZ")
    separate.location = (-650, 100)
    tree.links.new(texcoord.outputs["Object"], separate.inputs[0])
    warp = math_node(tree, "SINE", "Warp (2.4 mm pitch)", math_node(tree, "MULTIPLY", "Warp physical pitch", separate.outputs["X"], 2600.0))
    weft = math_node(tree, "SINE", "Weft (2.8 mm pitch)", math_node(tree, "MULTIPLY", "Weft physical pitch", separate.outputs["Z"], 2240.0))
    weave = math_node(tree, "MULTIPLY", "Interlaced warp-weft height", warp, weft)
    noise = tree.nodes.new("ShaderNodeTexNoise")
    noise.name = "Uneven yarn microfibres"
    noise.inputs["Scale"].default_value = 1400
    noise.inputs["Detail"].default_value = 2
    noise.inputs["Roughness"].default_value = 0.5
    tree.links.new(texcoord.outputs["Object"], noise.inputs["Vector"])
    height = math_node(tree, "ADD", "Woven yarn plus microfibre height", weave, math_node(tree, "MULTIPLY", "Microfibre amplitude", noise.outputs["Fac"], 0.3))
    bump = tree.nodes.new("ShaderNodeBump")
    bump.location = (300, -240)
    bump.inputs["Strength"].default_value = 0.22 if hem else 0.16
    bump.inputs["Distance"].default_value = 0.00024
    tree.links.new(height, bump.inputs["Height"])
    tree.links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    rough = math_node(tree, "ADD", "Yarn roughness variation", math_node(tree, "MULTIPLY", "Roughness variance", noise.outputs["Fac"], 0.055), 0.81 if hem else 0.77)
    tree.links.new(rough, bsdf.inputs["Roughness"])
    tree.links.new(bsdf.outputs["BSDF"], output.inputs["Surface"])
    for index, node in enumerate([node for node in tree.nodes if node.type == "MATH"]):
        node.location = (-420+(index%3)*160, 320-(index//3)*150)
    mat["Source"] = "Project-authored editable procedural weave; no paid or generated bitmap assets"
    mat["NotVelvetScan"] = True
    return mat


def camera_for(objects):
    points = [obj.matrix_world @ corner for obj in objects for corner in [Vector(value) for value in obj.bound_box]]
    minimum = Vector([min(point[axis] for point in points) for axis in range(3)])
    maximum = Vector([max(point[axis] for point in points) for axis in range(3)])
    centre = (minimum+maximum)/2
    data = bpy.data.cameras.new("CurtainReviewCamera")
    obj = bpy.data.objects.new(data.name, data)
    bpy.context.scene.collection.objects.link(obj)
    data.type = "ORTHO"
    data.ortho_scale = (maximum.z-minimum.z)*1.14
    obj.location = centre+Vector((1.2, -4.8, 0.7))
    obj.rotation_euler = (centre-obj.location).to_track_quat("-Z", "Y").to_euler()
    bpy.context.scene.camera = obj
    return obj


def area(name, location, energy, size, target):
    data = bpy.data.lights.new(name, "AREA")
    data.energy = energy
    data.shape = "DISK"
    data.size = size
    obj = bpy.data.objects.new(name, data)
    bpy.context.scene.collection.objects.link(obj)
    obj.location = location
    obj.rotation_euler = (Vector(target)-obj.location).to_track_quat("-Z", "Y").to_euler()


def main():
    assert not OUT.exists() and not bpy.context.preferences.filepaths.use_scripts_auto_execute
    assert sha(SOURCE) == "A4B33C7E061A1956F4F719473C9FEC10737AFC70DBCE54E7148343613B67A5C2"
    OUT.mkdir(parents=True)
    for obj in list(bpy.data.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    scene = bpy.context.scene
    scene.unit_settings.system = "METRIC"
    scene.unit_settings.scale_length = 1
    scene.unit_settings.length_unit = "METERS"
    vertices, faces, uv = read_obj(SOURCE)
    original_height = max(point[2] for point in vertices)-min(point[2] for point in vertices)
    scale = HEIGHT_M/original_height
    vertices = [tuple(value*scale for value in point) for point in vertices]
    mesh = make_mesh("CC0DioramaClothGrid", vertices, faces, uv)
    reference = link_mesh("SOURCE_CC0_DioramaClothIsland00", mesh.copy())
    reference.hide_render = True
    reference.hide_viewport = True
    reference.hide_set(True)
    reference["SourceOBJ"] = str(SOURCE)
    body = link_mesh("SM_DY_StageWingCurtain_Body", mesh)
    body.data.materials.append(material("M_DY_Curtain_ProceduralWoven"))
    subdiv = body.modifiers.new("Source render subdivision 2", "SUBSURF")
    subdiv.subdivision_type = "CATMULL_CLARK"
    subdiv.levels = subdiv.render_levels = 2
    # Preserve the original cut-cloth boundary and UV edge values.
    subdiv.boundary_smooth = "PRESERVE_CORNERS"
    select(body)
    bpy.context.view_layer.update()
    surface = body.evaluated_get(bpy.context.evaluated_depsgraph_get()).to_mesh(preserve_all_data_layers=True, depsgraph=bpy.context.evaluated_depsgraph_get())
    bm = bmesh.new()
    bm.from_mesh(surface)
    bm.faces.ensure_lookup_table()
    edge_faces = sorted({face.index for edge in bm.edges if edge.is_boundary for face in edge.link_faces})
    assert edge_faces
    chosen = [surface.polygons[index] for index in edge_faces]
    used = sorted({index for poly in chosen for index in poly.vertices})
    mapping = {index: number for number, index in enumerate(used)}
    hem_points = [surface.vertices[index].co+surface.vertices[index].normal*0.0032 for index in used]
    hem_faces = [[mapping[index] for index in poly.vertices] for poly in chosen]
    hem_uv = [[tuple(surface.uv_layers.active.data[loop].uv) for loop in poly.loop_indices] for poly in chosen]
    hem = link_mesh("SM_DY_StageWingCurtain_FoldedHem", make_mesh("Folded perimeter hem", hem_points, hem_faces, hem_uv))
    hem.data.materials.append(material("M_DY_Curtain_ProceduralHem", hem=True))
    bm.free()
    body.evaluated_get(bpy.context.evaluated_depsgraph_get()).to_mesh_clear()
    solid = body.modifiers.new("Real 4 mm double-sided fabric volume", "SOLIDIFY")
    solid.thickness = THICKNESS_M
    solid.offset = 0
    solid.use_even_offset = True
    solid.use_quality_normals = True
    solid.use_rim = True
    hem_solid = hem.modifiers.new("Folded 6 mm perimeter reinforcement", "SOLIDIFY")
    hem_solid.thickness = 0.006
    hem_solid.offset = 0
    hem_solid.use_even_offset = True
    hem_solid.use_quality_normals = True
    hem_solid.use_rim = True
    bevel = hem.modifiers.new("Soft hem cut edges", "BEVEL")
    bevel.width = 0.00045
    bevel.segments = 2
    bevel.affect = "EDGES"
    bevel.limit_method = "ANGLE"
    bevel.angle_limit = math.radians(35)
    bpy.context.view_layer.update()
    rows = [geometry(body), geometry(hem)]
    # Export only the two authored closed meshes, never review lights/camera/source.
    bpy.ops.object.select_all(action="DESELECT")
    body.select_set(True)
    hem.select_set(True)
    bpy.context.view_layer.objects.active = body
    target = OUT / "SM_DY_StageWingCurtain.fbx"
    bpy.ops.export_scene.fbx(filepath=str(target), use_selection=True, object_types={"MESH"},
                             use_mesh_modifiers=True, mesh_smooth_type="FACE", use_custom_props=True,
                             add_leaf_bones=False, bake_anim=False, axis_forward="-Y", axis_up="Z", path_mode="AUTO")
    assert target.is_file() and target.stat().st_size > 50000
    camera_for([body, hem])
    area("CurtainKey", (-2.2, -2.8, -0.3), 350, 2.1, (0, 0, -1.4))
    area("CurtainFill", (2.6, -1.3, -1.0), 90, 2.8, (0, 0, -1.4))
    area("CurtainEdge", (0.3, 2.2, -0.6), 200, 1.2, (0, 0, -1.4))
    scene.world.color = (0.055, 0.055, 0.055)
    scene.render.engine = "CYCLES"
    scene.cycles.samples = 32
    scene.cycles.use_denoising = True
    scene.render.resolution_x = 1000
    scene.render.resolution_y = 1200
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.view_settings.view_transform = "AgX"
    previews = []
    for name, base, hem_base in [("Gray", (0.21, 0.21, 0.21, 1), (0.17, 0.17, 0.17, 1)),
                               ("DeepCrimson", (0.055, 0.0025, 0.0085, 1), (0.044, 0.002, 0.006, 1))]:
        for obj, value in [(body, base), (hem, hem_base)]:
            mat = obj.data.materials[0]
            mat.node_tree.nodes.get("Principled BSDF").inputs["Base Color"].default_value = value
            mat.diffuse_color = value
        path = OUT / f"Curtain-{name}.png"
        scene.render.filepath = str(path)
        bpy.ops.render.render(write_still=True)
        previews.append({"name": name, "file": str(path), "bytes": path.stat().st_size, "sha256": sha(path)})
    # A physical close-up proves the weave and folded edge; no screen-space overlay.
    review_camera = scene.camera
    original_camera_matrix = review_camera.matrix_world.copy()
    original_ortho = review_camera.data.ortho_scale
    review_camera.data.ortho_scale = 0.23
    target_detail = Vector((-0.59, -0.03, -1.4))
    review_camera.location = target_detail+Vector((0.13, -0.7, 0.025))
    review_camera.rotation_euler = (target_detail-review_camera.location).to_track_quat("-Z", "Y").to_euler()
    detail = OUT / "Curtain-DeepCrimson-HemWeaveCloseup.png"
    scene.render.filepath = str(detail)
    bpy.ops.render.render(write_still=True)
    previews.append({"name": "DeepCrimsonHemWeaveCloseup", "file": str(detail), "bytes": detail.stat().st_size, "sha256": sha(detail)})
    review_camera.matrix_world = original_camera_matrix
    review_camera.data.ortho_scale = original_ortho
    blend = OUT / "DY_StageWingCurtain_Editable.blend"
    bpy.ops.wm.save_as_mainfile(filepath=str(blend), check_existing=True)
    report = {"status": "PASS-THICK-CURTAIN-AUTHORED-GEOMETRY-PREVIEW-NOT-UE-ADMITTED", "blender_version": bpy.app.version_string,
              "source": str(SOURCE), "source_sha256": sha(SOURCE), "source_license": "CC0 Blender Studio Cube Diorama",
              "source_original": {"vertices": 289, "polygons": 256, "triangles": 512, "single_surface": True, "has_thickness": False},
              "uniform_scale_from_source": scale, "normalized_working_height_metres": HEIGHT_M,
              "model_role": "Opaque thick side-stage wing curtain, never main projection receiver",
              "geometry": rows, "fabric_thickness_metres": THICKNESS_M, "perimeter_fold_thickness_metres": 0.006,
              "editable_blend": {"path": str(blend), "bytes": blend.stat().st_size, "sha256": sha(blend)},
              "fbx": {"path": str(target), "bytes": target.stat().st_size, "sha256": sha(target), "only_selected_two_meshes": True},
              "previews": previews, "material": {"source": "Project-authored editable procedural weave", "downloaded_pbr_textures": False,
                  "bitmap_generation_service": False, "opaque": True, "metallic": 0, "transmission": 0, "alpha": 1,
                  "roughness_base": 0.77, "roughness_variation": 0.055, "bump_distance_metres": 0.00024,
                  "fbx_preserves_procedural_shader": False, "requires_ue_material_rebuild_or_bake": True},
              "uv": "Original UVs retained and subdivided; shell and perimeter fold maintain UVMap",
              "ue_imported": False, "d_product_writes": False, "core_gameplay_changed": False,
              "protected_LICENSES_md_read_or_hashed": False}
    (OUT / "AUTHORING.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({"status": report["status"], "geometry": rows, "blend": str(blend), "fbx": str(target)}, indent=2))


if __name__ == "__main__":
    main()
