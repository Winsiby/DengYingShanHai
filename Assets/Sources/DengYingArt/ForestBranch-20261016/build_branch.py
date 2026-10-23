"""Build one centered-Z, capped branch candidate; local source and previews only."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import re
import struct
import sys
import zlib

import bmesh
import bpy
from mathutils import Vector


HERE = Path(__file__).resolve().parent
RADIAL = 14
HEIGHTS = (0., .08, .23, .40, .58, .76, .91, 1.)
LENGTH_CM = 100.
ROOT_RADIUS_CM = 11.5
INPUTS = [
    Path('D:/灯影山海/Source/DengYingShanHai/Private/Stage/DYForestGeometryLibrary.cpp'),
    Path('D:/灯影山海/Source/DengYingShanHai/Private/Stage/DYForestPresentationActor.cpp'),
    Path('D:/灯影山海/Source/DengYingShanHai/Public/Stage/DYForestPresentationActor.h'),
    Path('D:/灯影山海/Docs/P03_FOREST_DEV_ASSET.md'),
]
CHECKS = []


def require(value, message):
    if not value:
        raise AssertionError(message)
    CHECKS.append(message)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def mesh_record(mesh, expected_faces):
    mesh.calc_loop_triangles()
    require(len(mesh.vertices) == 114 and len(mesh.polygons) == expected_faces,
            'Actual mesh vertex/polygon counts '+mesh.name)
    require(len(mesh.loop_triangles) == 224 and len(mesh.uv_layers) == 1,
            'Actual 224 triangles and one UV0 '+mesh.name)
    require(all(math.isfinite(x) for v in mesh.vertices for x in v.co), 'Finite coordinates '+mesh.name)
    minimum = [min(v.co[i] for v in mesh.vertices) for i in range(3)]
    maximum = [max(v.co[i] for v in mesh.vertices) for i in range(3)]
    require(abs(minimum[0]+maximum[0]) < 1e-6 and abs(minimum[1]+maximum[1]) < 1e-6
            and abs(minimum[2]+50) < 1e-5 and abs(maximum[2]-50) < 1e-5,
            'Bounds axis endpoints (0,0,-50)/(0,0,50) '+mesh.name)
    require(all(math.isfinite(x) for uv in mesh.uv_layers[0].data for x in uv.uv), 'Finite UV0 '+mesh.name)
    require(all(t.area > 1e-8 for t in mesh.loop_triangles), 'No degenerate triangles '+mesh.name)
    require(all(abs(p.normal.length-1) < 1e-5 for p in mesh.polygons), 'Finite unit face normals '+mesh.name)
    require(all((p.center.x*p.normal.x+p.center.y*p.normal.y > 0)
                if abs(p.normal.z) < .99 else True for p in mesh.polygons),
            'Side face normals point outward '+mesh.name)
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bm.normal_update()
    volume = bm.calc_volume(signed=True)
    require(all(e.is_manifold and e.is_contiguous for e in bm.edges), 'Closed consistently wound manifold '+mesh.name)
    require(all(v.link_edges and v.link_faces for v in bm.verts), 'No loose vertices '+mesh.name)
    require(len(bm.verts)-len(bm.edges)+len(bm.faces) == 2, 'Single genus-zero closed surface '+mesh.name)
    require(math.isfinite(volume) and volume > 0, 'Positive actual signed volume '+mesh.name)
    edge_count = len(bm.edges)
    bm.free()
    return dict(vertices=len(mesh.vertices), edges=edge_count, polygons=len(mesh.polygons),
                triangles=len(mesh.loop_triangles), uv_layers=len(mesh.uv_layers),
                bounds_cm=dict(min=minimum, max=maximum), signed_volume_cm3=volume,
                material_slots=len(mesh.materials), loose_geometry=False,
                closed_manifold=True, consistently_wound=True,
                normals='Actual outward unit face normals; sides smooth, caps flat')


def png_record(path):
    raw = path.read_bytes()
    require(raw[:8] == b'\x89PNG\r\n\x1a\n', 'PNG signature '+path.name)
    cursor = 8
    dimensions = None
    while cursor < len(raw):
        count, kind = struct.unpack_from('>I4s', raw, cursor)
        require(cursor+12+count <= len(raw), 'Bounded PNG chunk '+path.name)
        payload = raw[cursor+8:cursor+8+count]
        require(zlib.crc32(kind+payload) & 0xffffffff == struct.unpack_from('>I',raw,cursor+8+count)[0],
                'PNG CRC '+path.name)
        if kind == b'IHDR':
            dimensions = struct.unpack_from('>II', payload)
        cursor += 12+count
        if kind == b'IEND':
            break
    require(cursor == len(raw) and kind == b'IEND' and dimensions == (1024, 1280),
            'Exact PNG end and dimensions '+path.name)
    return dict(path=str(path), bytes=len(raw), sha256=sha(path), dimensions=dimensions, tail_bytes=0)


def aim(obj, target):
    obj.rotation_euler = (Vector(target)-obj.location).to_track_quat('-Z','Y').to_euler()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', required=True, type=Path)
    out = parser.parse_args(sys.argv[sys.argv.index('--')+1:]).out
    require(out.is_absolute() and out.parent.resolve() == HERE
            and re.fullmatch(r'Source-Run[1-9][0-9]*', out.name) and not out.exists(),
            'Only an absent local Source-RunN directory is writable')
    require(bpy.app.version[:2] == (4,5), 'Actual Blender 4.5 runtime')
    frozen = {str(p):sha(p) for p in INPUTS}
    code_path = Path(__file__).resolve()
    author_hash = sha(code_path)
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    scene = bpy.context.scene
    scene.unit_settings.system = 'METRIC'
    scene.unit_settings.scale_length = .01
    scene.unit_settings.length_unit = 'CENTIMETERS'

    vertices = []
    ring_info = []
    for t in HEIGHTS:
        z = LENGTH_CM*(t-.5)
        base = ROOT_RADIUS_CM*(1-.62*t)*(1+.08*math.exp(-8*t)+.045*math.sin(3*math.pi*t))
        twist = .045*math.sin(math.pi*t)
        first = []
        for j in range(RADIAL//2):
            theta = 2*math.pi*j/RADIAL+twist
            relief = 1+.055*math.cos(2*theta+.7*t)+.04*math.sin(4*theta-.5*t)+.10*math.cos(6*theta+.8*t)
            radius = base*relief
            first.append((radius*math.cos(theta),radius*math.sin(theta),z))
        ring = first+[(-x,-y,z) for x,y,z in first]
        require(all(abs(sum(p[i] for p in ring)) < 1e-12 for i in (0,1)), 'Centered antipodal cross-section '+str(t))
        require(all(Vector(ring[j]).cross(Vector(ring[(j+1)%RADIAL])).z > 0 for j in range(RADIAL)),
            'Ordered positive-radius star-shaped cross-section '+str(t))
        ring_info.append(dict(height_fraction=t,z_cm=z,mean_radius_cm=sum(math.hypot(p[0],p[1]) for p in ring)/RADIAL,
                              centroid_xy_cm=[sum(p[i] for p in ring)/RADIAL for i in (0,1)]))
        vertices.extend(ring)
    bottom, top = len(vertices), len(vertices)+1
    vertices.extend([(0,0,-50),(0,0,50)])
    faces, face_uv = [], []
    for r in range(len(HEIGHTS)-1):
        for j in range(RADIAL):
            k = (j+1)%RADIAL
            faces.append((r*RADIAL+j,r*RADIAL+k,(r+1)*RADIAL+k,(r+1)*RADIAL+j))
            face_uv.append(((j/RADIAL,2*HEIGHTS[r]),((j+1)/RADIAL,2*HEIGHTS[r]),
                            ((j+1)/RADIAL,2*HEIGHTS[r+1]),(j/RADIAL,2*HEIGHTS[r+1])))
    for j in range(RADIAL):
        k = (j+1)%RADIAL
        for ids in ((bottom,k,j),(top,(len(HEIGHTS)-1)*RADIAL+j,(len(HEIGHTS)-1)*RADIAL+k)):
            faces.append(ids)
            face_uv.append(tuple((.5+vertices[i][0]/(4*ROOT_RADIUS_CM),
                                  2.4+vertices[i][1]/(4*ROOT_RADIUS_CM)) for i in ids))
    mesh = bpy.data.meshes.new('SM_DY_ForestBranch_Tapered')
    mesh.from_pydata(vertices, [], faces)
    mesh.update(calc_edges=True)
    require(not mesh.validate(verbose=False, clean_customdata=False), 'Blender mesh.validate made no repairs')
    uv = mesh.uv_layers.new(name='UV0')
    for polygon, coordinates in zip(mesh.polygons,face_uv):
        polygon.use_smooth = polygon.index < (len(HEIGHTS)-1)*RADIAL
        for loop, coordinate in zip(polygon.loop_indices,coordinates):
            uv.data[loop].uv = coordinate
    branch = bpy.data.objects.new(mesh.name,mesh)
    scene.collection.objects.link(branch)
    bpy.context.view_layer.objects.active = branch
    branch.select_set(True)
    material = bpy.data.materials.new('M_Branch_Neutral_Preview_Only')
    material.use_nodes = True
    bsdf = material.node_tree.nodes.get('Principled BSDF')
    bsdf.inputs['Base Color'].default_value = (.19,.15,.105,1)
    bsdf.inputs['Roughness'].default_value = .85
    mesh.materials.append(material)
    source_record = mesh_record(mesh,126)
    ratios = []
    for r in range(len(HEIGHTS)-1):
        for j in range(RADIAL):
            p,q = Vector(vertices[r*RADIAL+j]),Vector(vertices[(r+1)*RADIAL+j])
            ratios.append((q-p).length/(q.z-p.z))
            p_uv = uv.data[mesh.polygons[r*RADIAL+j].loop_start].uv
            q_uv = uv.data[mesh.polygons[r*RADIAL+j].loop_start+3].uv
            require(abs((q_uv.y-p_uv.y)-(q.z-p.z)/50) < 2e-7, 'UV0 V follows actual uneven axial spacing')
    require(max(ratios) < 1.02, 'Axial UV edge/surface distortion under two percent')
    require(ring_info[0]['mean_radius_cm'] > 2*ring_info[-1]['mean_radius_cm'], 'Visible coarse-root to fine-tip taper')
    out.mkdir()
    fbx = out/'forest-branch-tapered.fbx'
    bpy.ops.export_scene.fbx(filepath=str(fbx),check_existing=True,use_selection=True,
        object_types={'MESH'},global_scale=1,apply_unit_scale=True,apply_scale_options='FBX_SCALE_UNITS',
        axis_forward='-Y',axis_up='Z',bake_space_transform=False,use_mesh_modifiers=False,
        mesh_smooth_type='FACE',use_mesh_edges=False,use_tspace=False,use_triangles=True,
        add_leaf_bones=False,bake_anim=False,path_mode='AUTO',embed_textures=False)
    before = set(bpy.data.objects)
    bpy.ops.import_scene.fbx(filepath=str(fbx),use_anim=False)
    imported = [o for o in bpy.data.objects if o not in before]
    require(len(imported) == 1 and imported[0].type == 'MESH', 'Fresh FBX read creates exactly one mesh')
    roundtrip = mesh_record(imported[0].data,224)
    require(all(abs(source_record['bounds_cm'][side][i]-roundtrip['bounds_cm'][side][i]) < 1e-4
                for side in ('min','max') for i in range(3)), 'FBX fresh-read local bounds match source')
    require((imported[0].matrix_world.translation-branch.matrix_world.translation).length < 1e-6
            and all(abs(v-1)<1e-6 for v in imported[0].scale), 'FBX fresh-read unit scale and no translation')
    bpy.data.objects.remove(imported[0],do_unlink=True)

    scene.render.engine = 'CYCLES'
    scene.cycles.device = 'CPU'
    scene.cycles.samples = 48
    scene.cycles.use_denoising = True
    scene.render.resolution_x,scene.render.resolution_y = 1024,1280
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = 'PNG'
    scene.render.image_settings.color_mode = 'RGB'
    scene.render.film_transparent = False
    scene.view_settings.view_transform = 'AgX'
    scene.world.use_nodes = True
    scene.world.node_tree.nodes['Background'].inputs['Color'].default_value = (.055,.055,.055,1)
    scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value = .45
    for name,location,power,size in (
        ('QA_Key',(65,-95,115),280000,85),
        ('QA_Fill',(-85,-35,30),120000,100),
        ('QA_Rim',(25,75,60),220000,70)):
        light_data = bpy.data.lights.new(name,'AREA')
        light_data.energy,light_data.shape,light_data.size = power,'DISK',size
        light = bpy.data.objects.new(name,light_data)
        scene.collection.objects.link(light)
        light.location = location
        aim(light,(0,0,0))
    camera_data = bpy.data.cameras.new('QA_Camera')
    camera_data.type,camera_data.ortho_scale = 'ORTHO',126
    camera_data.clip_end = 2000
    camera = bpy.data.objects.new('QA_Camera',camera_data)
    scene.collection.objects.link(camera)
    scene.camera = camera
    previews = []
    for name,location,target in (
        ('01_FullShape',(90,-150,38),(0,0,0)),
        ('02_UpperOblique',(-95,-125,135),(0,0,2))):
        camera.location = location
        aim(camera,target)
        image = out/(name+'.png')
        scene.render.filepath = str(image)
        bpy.ops.render.render(write_still=True)
        previews.append(dict(camera=name,location_cm=location,target_cm=target,ortho_scale_cm=126,
                             preview_only=True,png=png_record(image)))
    require(all(sha(Path(path)) == expected for path,expected in frozen.items()), 'Read-only project contract inputs unchanged')
    require(sha(code_path) == author_hash, 'Author tool unchanged during generation')
    report = dict(status='PASS-LOCAL-BRANCH-SOURCE-NATIVE-AND-ART-PENDING',
        blender_version=bpy.app.version_string,blender_binary=bpy.app.binary_path,
        author_tool=dict(path=str(code_path),sha256=author_hash,source_utf8=code_path.read_text(encoding='utf-8')),contract_inputs=frozen,
        model='One centered local-Z irregular tapered capped branch segment; no forks or leaves',
        provenance='Author-designed procedural candidate with Codex assistance; not a downloaded scan, historical reconstruction or botanical species claim; no third-party mesh/texture used',
        units='Source coordinates in centimeters; Blender metric scale_length .01; FBX unit scale applied',
        parameters=dict(radial_segments=RADIAL,height_rings=len(HEIGHTS),height_fractions=HEIGHTS,
                        length_cm=LENGTH_CM,root_nominal_radius_cm=ROOT_RADIUS_CM),
        source_mesh=source_record,fbx_fresh_read_mesh=roundtrip,ring_samples=ring_info,
        uv0=dict(side_U='Unwrapped ring fraction with longitudinal seam',side_V='Local height / 50cm; nonuniform height rings preserve axial spacing',
                 caps='Separate planar disk islands above side sheet; UV Wrap may repeat',
                 max_axial_surface_to_UV_axis_ratio=max(ratios),world_scale_density_invariance_claimed=False),
        endpoints_local_cm=[[0,0,-50],[0,0,50]],
        fbx=dict(path=str(fbx),bytes=fbx.stat().st_size,sha256=sha(fbx)),previews=previews,
        preview_material='Simple neutral rough Principled material, not final wood art',
        check_count=len(CHECKS),checks=CHECKS,
        scope=dict(D_writes=False,UE=False,downloads=False,paid_assets=False,core_logic_changed=False,
                   token_or_staffA_or_Z70_or_15branch_changed=False,native_verified=False,art_accepted=False))
    (out/'SOURCE.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    (out/'README.md').write_text(
        '# Local forest branch art candidate\n\n'
        'One closed tapered centered-Z branch replaces the visual idea of a mechanical cylinder, not the 15-branch layout or growth system. '
        'Creative procedural geometry authored with Codex assistance; no upstream mesh, scan, paid asset, texture or download. '
        'Not a historical or peach-tree species reconstruction.\n\n'
        'FBX contains one mesh, one UV0 and one simple neutral preview material. Two PNGs are Blender shape reviews only, not UE real-shadow or gameplay acceptance. '
        'SOURCE.json records actual Blender mesh counts, closed manifold/volume/axis/UV checks and a fresh FBX read. '
        'build_branch.py is the reproducible source; no .blend is necessary. Future UE material/import and actual contact-to-forest validation remain pending.\n',encoding='utf-8')
    print(json.dumps({k:report[k] for k in ('status','blender_version','source_mesh','fbx','check_count')},indent=2))


if __name__ == '__main__':
    main()
