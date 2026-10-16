"""Bake trusted local lamp shaders; original source files are read-only."""
import bpy
import hashlib
import json
import math
from pathlib import Path
import numpy as np
from mathutils import Vector

OUT = Path(__file__).resolve().parent
SOURCE = Path(r"D:\灯影山海\Assets\Sources\DengYingArt\Lamp-20261014")
VARIANT = SOURCE / "RuntimeVariant"
BLEND = VARIANT / "DY_HeroSpotlight_RuntimeVariant.blend"
GROUPS = {"BODY": ("LampBody", (0, 0, 0)), "STAND": ("LampStand", (0, 0, -.95))}
REPORT = {"status": "starting", "source_blend": str(BLEND), "bakes": [], "uv": {}}


def write_report():
    (OUT / "LAMP_BAKE.json").write_text(json.dumps(REPORT, ensure_ascii=False, indent=2), encoding="utf-8")


def digest(file):
    return hashlib.sha256(file.read_bytes()).hexdigest().upper()


def protected_hashes():
    files = [BLEND, SOURCE / "DY_HeroSpotlight_Source.blend"]
    files += [base / ("SM_DY_" + name + "_Source.fbx") for base in (SOURCE, VARIANT)
              for name in ("LampBody", "LampStand")]
    files += [SOURCE / "Sources" / name for name in
              ("wood_table_diff_2k.png", "wood_table_arm_2k.png", "wood_table_nor_dx_2k.png")]
    return {str(file): digest(file) for file in files}


def bounds(ob, pivot=(0, 0, 0)):
    points = [ob.matrix_world @ v.co + Vector(pivot) for v in ob.data.vertices]
    return {"min": [min(p[i] for p in points) * 100 for i in range(3)],
            "max": [max(p[i] for p in points) * 100 for i in range(3)]}


def uv_test(objects, layer_name):
    """Triangle SAT with a spatial grid; shared edges are not overlaps."""
    triangles = []
    for ob in objects:
        ob.data.calc_loop_triangles()
        layer = ob.data.uv_layers.get(layer_name)
        if layer is None:
            return {"available": False, "object_without_layer": ob.name}
        for tri in ob.data.loop_triangles:
            uv = np.array([layer.data[i].uv[:] for i in tri.loops], dtype=np.float64)
            area = abs(float(np.cross(uv[1] - uv[0], uv[2] - uv[0]))) * .5
            if area > 1e-12:
                triangles.append(uv)
    bins, collisions, tested = {}, [], set()
    for index, uv in enumerate(triangles):
        low, high = np.floor(uv.min(0) * 64).astype(int), np.floor(uv.max(0) * 64).astype(int)
        candidates = set()
        keys = [(x, y) for x in range(low[0], high[0] + 1) for y in range(low[1], high[1] + 1)]
        for key in keys:
            candidates.update(bins.get(key, []))
        for other in candidates:
            pair = (other, index)
            if pair in tested:
                continue
            tested.add(pair)
            second = triangles[other]
            separated = False
            for polygon in (uv, second):
                for edge_index in range(3):
                    edge = polygon[(edge_index + 1) % 3] - polygon[edge_index]
                    axis = np.array([-edge[1], edge[0]])
                    length = np.linalg.norm(axis)
                    if length < 1e-12:
                        continue
                    axis /= length
                    a, b = uv @ axis, second @ axis
                    if min(a.max(), b.max()) - max(a.min(), b.min()) <= 1e-9:
                        separated = True
                        break
                if separated:
                    break
            if not separated:
                collisions.append(pair)
        for key in keys:
            bins.setdefault(key, []).append(index)
    all_uv = np.concatenate(triangles)
    return {"available": True, "triangles_nonzero_uv": len(triangles),
            "overlap_pairs": len(collisions), "first_overlap_pairs": collisions[:10],
            "uv_min": all_uv.min(0).tolist(), "uv_max": all_uv.max(0).tolist(),
            "method": "Strict triangle separating-axis overlap, 1e-9 UV tolerance; edges excluded"}


def select(objects):
    bpy.ops.object.select_all(action="DESELECT")
    for ob in objects:
        ob.select_set(True)
    bpy.context.view_layer.objects.active = objects[0]


def new_image(name, color_space, background):
    image = bpy.data.images.new(name, width=2048, height=2048, alpha=False, float_buffer=False)
    image.colorspace_settings.name = color_space
    image.generated_color = (*background, 1)
    return image


def save_image(image):
    image.filepath_raw = str(OUT / (image.name + ".png"))
    image.file_format = "PNG"
    image.save()
    assert Path(image.filepath_raw).stat().st_size > 1000
    REPORT["bakes"].append({"file": image.filepath_raw, "size": list(image.size),
        "color_space": image.colorspace_settings.name, "sha256": digest(Path(image.filepath_raw))})
    write_report()


def main():
    before = protected_hashes()
    REPORT["source_hashes_before"] = before
    for group, (name, pivot) in GROUPS.items():
        bpy.ops.wm.read_factory_settings(use_empty=True)
        bpy.ops.import_scene.fbx(filepath=str(VARIANT / ("SM_DY_" + name + "_Source.fbx")))
        meshes = [ob for ob in bpy.context.scene.objects if ob.type == "MESH"]
        assert len(meshes) == 1 and len(meshes[0].data.uv_layers) == 2
        REPORT["uv"][group + "_source_fbx"] = uv_test(meshes, meshes[0].data.uv_layers[1].name)
        REPORT.setdefault("source_fbx", {})[group] = {"vertices": len(meshes[0].data.vertices),
            "triangles": sum(len(p.vertices) - 2 for p in meshes[0].data.polygons),
            "bounds_local_cm": bounds(meshes[0]), "pivot_actor_local_m": pivot}
        write_report()
    bpy.ops.wm.open_mainfile(filepath=str(BLEND))
    scene = bpy.context.scene
    manifest = json.loads((VARIANT / "LAMP_SOURCE_MANIFEST.json").read_text(encoding="utf-8"))
    parts = [bpy.data.objects[row["name"]] for row in manifest["parts"]]
    assert len(parts) == 57 and all(ob.get("Export_Group") in GROUPS for ob in parts)
    assert sum(len(p.vertices) - 2 for ob in parts for p in ob.data.polygons) == 33104
    assert scene.unit_settings.scale_length == 1
    REPORT["source_part_uv_layers"] = {ob.name: [u.name for u in ob.data.uv_layers] for ob in parts}
    original_packed = {image.name: hashlib.sha256(image.packed_file.data).hexdigest().upper()
                       for image in bpy.data.images if image.packed_file is not None}
    assert len(original_packed) == 3
    REPORT["packed_original_hashes"] = original_packed
    clones = {}
    depsgraph = bpy.context.evaluated_depsgraph_get()
    for group in GROUPS:
        clones[group] = []
        for original in [ob for ob in parts if ob.get("Export_Group") == group]:
            mesh = bpy.data.meshes.new_from_object(original.evaluated_get(depsgraph),
                preserve_all_data_layers=True, depsgraph=depsgraph)
            ob = bpy.data.objects.new(original.name + "_Baked", mesh)
            scene.collection.objects.link(ob)
            ob.matrix_world = original.matrix_world.copy()
            ob["Export_Group"] = group
            ob["Source_Part"] = original.name
            clones[group].append(ob)
            original.hide_render = True
            original.hide_set(True)
        for ob in clones[group]:
            assert ob.data.uv_layers[0].name == "UVMap"
    scene.render.engine = "CYCLES"
    scene.cycles.device = "CPU"
    scene.cycles.samples = 16
    scene.render.threads_mode = "FIXED"
    scene.render.threads = 4
    scene.render.bake.use_clear = False
    scene.render.bake.margin = 8
    scene.render.bake.normal_space = "TANGENT"
    scene.render.bake.normal_r = "POS_X"
    scene.render.bake.normal_g = "NEG_Y"
    scene.render.bake.normal_b = "POS_Z"
    finished = []
    for group, objects in clones.items():
        name, pivot = GROUPS[group]
        # Use one joined pack, then return UV1 to the original local-coordinate objects.
        lookup, uv0_before, key = {}, {}, 0
        pack_clones = []
        for ob in objects:
            uv0_before[ob.name] = [tuple(loop.uv) for loop in ob.data.uv_layers[0].data]
            attr = ob.data.attributes.new("BakeLoopKey", "INT", "CORNER")
            for item in attr.data:
                item.value = key
                lookup[key] = ob.name
                key += 1
            duplicate = ob.copy(); duplicate.data = ob.data.copy()
            scene.collection.objects.link(duplicate)
            pack_clones.append(duplicate)
        select(pack_clones)
        bpy.ops.object.join()
        packed = bpy.context.object
        packed.data.uv_layers.new(name="BakeUV1")
        packed.data.uv_layers.active_index = len(packed.data.uv_layers) - 1
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.select_all(action="SELECT")
        bpy.ops.uv.smart_project(angle_limit=math.radians(66), island_margin=.015625, area_weight=.2)
        bpy.ops.object.mode_set(mode="OBJECT")
        values = {item.value: tuple(packed.data.uv_layers["BakeUV1"].data[i].uv)
                  for i, item in enumerate(packed.data.attributes["BakeLoopKey"].data)}
        assert len(values) == key
        for ob in objects:
            ob.data.uv_layers.new(name="BakeUV1")
            for i, item in enumerate(ob.data.attributes["BakeLoopKey"].data):
                ob.data.uv_layers["BakeUV1"].data[i].uv = values[item.value]
            ob.data.attributes.remove(ob.data.attributes["BakeLoopKey"])
            assert uv0_before[ob.name] == [tuple(loop.uv) for loop in ob.data.uv_layers[0].data]
            ob.data.uv_layers.active_index = len(ob.data.uv_layers) - 1
            for layer in ob.data.uv_layers:
                layer.active_render = layer.name == "BakeUV1"
        bpy.data.objects.remove(packed, do_unlink=True)
        REPORT["uv"][group + "_BakeUV1"] = uv_test(objects, "BakeUV1")
        assert REPORT["uv"][group + "_BakeUV1"]["overlap_pairs"] == 0
        REPORT["uv"][group + "_uv0_unchanged"] = True
        write_report()
        materials = {}
        for ob in objects:
            for slot in ob.material_slots:
                source_material = slot.material
                if source_material.name not in materials:
                    material = source_material.copy()
                    material.name = source_material.name + "_" + group + "_BAKE"
                    material["SourceMaterial"] = source_material.name
                    for node in material.node_tree.nodes:
                        if node.type == "TEX_COORD":
                            uvmap = material.node_tree.nodes.new("ShaderNodeUVMap")
                            uvmap.uv_map = "UVMap"
                            for link in list(node.outputs["UV"].links):
                                material.node_tree.links.new(uvmap.outputs["UV"], link.to_socket)
                        elif node.type == "NORMAL_MAP":
                            node.uv_map = "UVMap"
                    materials[source_material.name] = material
                slot.material = materials[source_material.name]
        base = new_image("T_DY_" + name + "_BaseColor", "sRGB", (0, 0, 0))
        orm = new_image("T_DY_" + name + "_ORM", "Non-Color", (1, .5, 0))
        normal = new_image("T_DY_" + name + "_NormalDX", "Non-Color", (.5, .5, 1))
        for image, bake_type in ((base, "BASE"), (orm, "ORM"), (normal, "NORMAL")):
            restore = []
            for material in materials.values():
                nodes, links = material.node_tree.nodes, material.node_tree.links
                bsdf = next(node for node in nodes if node.type == "BSDF_PRINCIPLED")
                output = next(node for node in nodes if node.type == "OUTPUT_MATERIAL")
                target = nodes.new("ShaderNodeTexImage"); target.image = image; nodes.active = target
                restore.append((nodes, links, output, output.inputs["Surface"].links[0].from_socket, target))
                if bake_type != "NORMAL":
                    emit = nodes.new("ShaderNodeEmission")
                    if bake_type == "BASE":
                        socket = bsdf.inputs["Base Color"]
                        if socket.is_linked:
                            links.new(socket.links[0].from_socket, emit.inputs["Color"])
                        else:
                            emit.inputs["Color"].default_value = socket.default_value
                    else:
                        combine = nodes.new("ShaderNodeCombineColor")
                        combine.mode = "RGB"; combine.inputs["Red"].default_value = 1
                        for channel, input_name in (("Green", "Roughness"), ("Blue", "Metallic")):
                            socket = bsdf.inputs[input_name]
                            if socket.is_linked:
                                links.new(socket.links[0].from_socket, combine.inputs[channel])
                            else:
                                combine.inputs[channel].default_value = socket.default_value
                        links.new(combine.outputs[0], emit.inputs["Color"])
                    links.new(emit.outputs[0], output.inputs["Surface"])
            select(objects)
            bpy.ops.object.bake(type="NORMAL" if bake_type == "NORMAL" else "EMIT", uv_layer="BakeUV1")
            save_image(image)
            for nodes, links, output, original_socket, target in restore:
                links.new(original_socket, output.inputs["Surface"])
                nodes.remove(target)
        # Render only FILE atlas textures; original optical constants stay on its partition.
        for material in materials.values():
            nodes, links = material.node_tree.nodes, material.node_tree.links
            bsdf = next(node for node in nodes if node.type == "BSDF_PRINCIPLED")
            optical = {key: bsdf.inputs[key].default_value for key in
                       ("Transmission Weight", "IOR", "Emission Strength")}
            emission_color = tuple(bsdf.inputs["Emission Color"].default_value)
            nodes.clear()
            output = nodes.new("ShaderNodeOutputMaterial")
            bsdf = nodes.new("ShaderNodeBsdfPrincipled")
            for key, value in optical.items(): bsdf.inputs[key].default_value = value
            bsdf.inputs["Emission Color"].default_value = emission_color
            links.new(bsdf.outputs[0], output.inputs["Surface"])
            uv = nodes.new("ShaderNodeUVMap"); uv.uv_map = "BakeUV1"
            textures = {}
            for key, image in (("BASE", base), ("ORM", orm), ("NORMAL", normal)):
                file_image = bpy.data.images.load(str(OUT / (image.name + ".png")), check_existing=False)
                file_image.colorspace_settings.name = "sRGB" if key == "BASE" else "Non-Color"
                tex = nodes.new("ShaderNodeTexImage"); tex.image = file_image
                links.new(uv.outputs[0], tex.inputs["Vector"]); textures[key] = tex
            links.new(textures["BASE"].outputs["Color"], bsdf.inputs["Base Color"])
            separate = nodes.new("ShaderNodeSeparateColor")
            links.new(textures["ORM"].outputs["Color"], separate.inputs[0])
            links.new(separate.outputs["Green"], bsdf.inputs["Roughness"])
            links.new(separate.outputs["Blue"], bsdf.inputs["Metallic"])
            normsplit = nodes.new("ShaderNodeSeparateColor")
            links.new(textures["NORMAL"].outputs["Color"], normsplit.inputs[0])
            invert = nodes.new("ShaderNodeMath"); invert.operation = "SUBTRACT"; invert.inputs[0].default_value = 1
            links.new(normsplit.outputs["Green"], invert.inputs[1])
            combine = nodes.new("ShaderNodeCombineColor")
            for channel in ("Red", "Blue"): links.new(normsplit.outputs[channel], combine.inputs[channel])
            links.new(invert.outputs[0], combine.inputs["Green"])
            normalmap = nodes.new("ShaderNodeNormalMap"); normalmap.uv_map = "BakeUV1"
            links.new(combine.outputs[0], normalmap.inputs["Color"])
            links.new(normalmap.outputs[0], bsdf.inputs["Normal"])
        select(objects)
        bpy.ops.object.join()
        merged = bpy.context.object
        merged.name = "SM_DY_" + name + "_Baked"
        scene.cursor.location = pivot
        bpy.ops.object.origin_set(type="ORIGIN_CURSOR")
        merged["Pivot_Actor_Local_m"] = pivot
        merged["BakeUVIndex"] = 1
        assert len(merged.data.uv_layers) == 2, [u.name for u in merged.data.uv_layers]
        assert sum(len(p.vertices) - 2 for p in merged.data.polygons) == REPORT["source_fbx"][group]["triangles"]
        actor_bounds = bounds(merged)
        merged.location = (0, 0, 0)
        bpy.ops.export_scene.fbx(filepath=str(OUT / (merged.name + ".fbx")), use_selection=True,
            object_types={"MESH"}, apply_unit_scale=True, apply_scale_options="FBX_SCALE_UNITS",
            axis_forward="X", axis_up="Z", use_mesh_modifiers=True, mesh_smooth_type="FACE",
            add_leaf_bones=False, bake_anim=False, path_mode="ABSOLUTE", embed_textures=False)
        REPORT.setdefault("exports", {})[group] = {"file": str(OUT / (merged.name + ".fbx")),
            "vertices": len(merged.data.vertices), "triangles": sum(len(p.vertices) - 2 for p in merged.data.polygons),
            "bounds_component_cm": bounds(merged), "bounds_actor_cm": actor_bounds,
            "pivot_actor_local_m": pivot, "uv_layers": [u.name for u in merged.data.uv_layers],
            "material_slots": [m.name for m in merged.data.materials], "has_custom_normals": merged.data.has_custom_normals}
        merged.location = pivot
        finished.append(merged)
        write_report()
    for original in parts:
        bpy.data.objects.remove(original, do_unlink=True)
    scene.cycles.samples = 64
    camera = scene.camera
    for file, location, target, scale, resolution in (
            ("Lamp_Baked_Full.png", (5, -7, 2.15), (-.035, 0, -1.48), 4.5, (1440, 1920)),
            ("Lamp_Baked_Head.png", (2.4, -2.8, .85), (0, 0, -.17), 1.47, (1920, 1440))):
        camera.location = location
        camera.rotation_euler = (Vector(target) - camera.location).to_track_quat("-Z", "Y").to_euler()
        camera.data.type = "ORTHO"; camera.data.ortho_scale = scale
        scene.render.resolution_x, scene.render.resolution_y = resolution
        scene.render.filepath = str(OUT / file)
        bpy.ops.render.render(write_still=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT / "DY_HeroSpotlight_Baked.blend"))
    after = protected_hashes()
    assert before == after, "Protected lamp source changed"
    REPORT["source_hashes_after"] = after
    REPORT["source_unchanged"] = True
    REPORT["status"] = "baked_rendered_pending_cold_read_and_visual_qa"
    write_report()


if __name__ == "__main__":
    try:
        main()
    except Exception:
        import traceback
        REPORT["status"] = "failed"
        REPORT["error"] = traceback.format_exc()
        write_report()
        raise
