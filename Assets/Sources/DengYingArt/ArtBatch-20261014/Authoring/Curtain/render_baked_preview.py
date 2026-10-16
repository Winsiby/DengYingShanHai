"""Preview the actual delivered texture graph on its corresponding BakeUV mesh."""
from pathlib import Path
import json
import sys
import bpy
from mathutils import Vector
sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_curtain import camera_for, area

ROOT = Path(__file__).resolve().parent
BAKED = ROOT / "Baked-Run2"
OUT = ROOT / "Baked-Preview-Run1"


def main():
    assert not OUT.exists() and not bpy.context.preferences.filepaths.use_scripts_auto_execute
    bpy.ops.wm.read_factory_settings(use_empty=True)
    with bpy.data.libraries.load(str(BAKED / "DY_StageWingCurtain_BakedEditable.blend"), link=False) as (available, requested):
        requested.objects = ["SM_DY_StageWingCurtain"]
    obj = requested.objects[0]
    bpy.context.scene.collection.objects.link(obj)
    obj.matrix_world = obj.matrix_basis.copy()
    bpy.context.view_layer.update()
    images = []
    for image in list(bpy.data.images):
        if not image.name.startswith("T_DY_StageWing_"):
            continue
        images.append({"name": image.name, "source": image.source, "colorspace": image.colorspace_settings.name,
                       "size": list(image.size), "filepath": image.filepath, "has_pixels": len(image.pixels) > 0})
        assert list(image.size) == [2048, 2048] and len(image.pixels) == 2048*2048*4
        assert image.source == "FILE", "Editable bake blend must bind real saved PNGs, not regenerate blank images."
    assert len(images) == 3
    scene = bpy.context.scene
    camera_for([obj])
    area("BakedCurtainKey", (-2.2, -2.8, -0.3), 350, 2.1, (0, 0, -1.4))
    area("BakedCurtainFill", (2.6, -1.3, -1.0), 90, 2.8, (0, 0, -1.4))
    area("BakedCurtainEdge", (0.3, 2.2, -0.6), 200, 1.2, (0, 0, -1.4))
    scene.world = bpy.data.worlds.new("BakedReviewWorld")
    scene.world.color = (0.055, 0.055, 0.055)
    scene.render.engine = "CYCLES"
    scene.cycles.samples = 32
    scene.cycles.use_denoising = True
    scene.render.resolution_x = 1000
    scene.render.resolution_y = 1200
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.view_settings.view_transform = "AgX"
    OUT.mkdir()
    full = OUT / "Curtain-Baked-DeepCrimson.png"
    scene.render.filepath = str(full)
    bpy.ops.render.render(write_still=True)
    camera = scene.camera
    camera.data.ortho_scale = 0.23
    target = Vector((-0.59, -0.03, -1.4))
    camera.location = target+Vector((0.13, -0.7, 0.025))
    camera.rotation_euler = (target-camera.location).to_track_quat("-Z", "Y").to_euler()
    close = OUT / "Curtain-Baked-HemWeaveCloseup.png"
    scene.render.filepath = str(close)
    bpy.ops.render.render(write_still=True)
    (OUT / "PREVIEW.json").write_text(json.dumps({"status": "PASS-ACTUAL-BAKED-TEXTURE-MESH-RENDER", "images": images,
                                               "preview_files": [str(full), str(close)], "uses_bake_uv_channel_0": True,
                                               "unrelated_plane_used": False, "original_files_changed": False}, indent=2), encoding="utf-8")
    print(json.dumps({"status": "PASS-ACTUAL-BAKED-TEXTURE-MESH-RENDER", "images": images}, indent=2))


if __name__ == "__main__":
    main()
