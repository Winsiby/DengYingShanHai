"""Build one closed centered-Z branch with four solid narrow leaves in Blender 4.5.

Usage: blender --background --factory-startup --disable-autoexec
  --python-exit-code 1 --python build_canopy.py -- --out <new Source-RunN>
Only the explicit absent sibling output directory is written. No UE or D writes.
"""
import argparse
from collections import Counter
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
from mathutils.bvhtree import BVHTree


HERE = Path(__file__).resolve().parent
OLD_AUTHOR = HERE.parent / 'ForestArt/build_branch.py'
INPUTS = [OLD_AUTHOR,
          Path('D:/灯影山海/Source/DengYingShanHai/Private/Stage/DYForestGeometryLibrary.cpp'),
          Path('D:/灯影山海/Source/DengYingShanHai/Private/Stage/DYForestPresentationActor.cpp'),
          Path('D:/灯影山海/Source/DengYingShanHai/Public/Stage/DYForestPresentationActor.h')]
MESH_NAME = 'SM_DY_ForestBranch_Canopy'
SLOTS = ['Wood0', 'Leaf1']
RADIAL = 14
HEIGHTS = (0., .08, .23, .40, .58, .76, .91, 1.)
ROOT_RADIUS_CM = 11.5
LEAF_STEPS = (.06, .19, .38, .59, .79, .94)
LEAF_RADIAL = 8
CHECKS = []


def require(value, message):
    if not value:
        raise AssertionError(message)
    CHECKS.append(message)
    return value


def sha(file):
    file = Path(file)
    require(str(file).replace('\\', '/').lower() != 'd:/灯影山海/docs/licenses.md', 'Never access restricted license register')
    return hashlib.sha256(file.read_bytes()).hexdigest().upper()


def xyz(v):
    return [float(v[i]) for i in range(3)]


def stem_geometry():
    """Same ring positions/caps/UV as the fully reviewed original build_branch.py."""
    vertices, rings = [], []
    for t in HEIGHTS:
        z = 100. * (t - .5)
        base = ROOT_RADIUS_CM * (1 - .62*t) * (1 + .08*math.exp(-8*t) + .045*math.sin(3*math.pi*t))
        twist = .045*math.sin(math.pi*t)
        first = []
        for j in range(RADIAL//2):
            angle = 2*math.pi*j/RADIAL + twist
            relief = 1 + .055*math.cos(2*angle + .7*t) + .04*math.sin(4*angle - .5*t) + .10*math.cos(6*angle + .8*t)
            radius = base*relief
            first.append((radius*math.cos(angle), radius*math.sin(angle), z))
        ring = first + [(-x, -y, z) for x, y, z in first]
        require(all(abs(sum(p[i] for p in ring)) < 1e-12 for i in (0, 1)), 'Original centered antipodal wood ring ' + str(t))
        vertices.extend(ring)
        rings.append(dict(t=t, z_cm=z, vertices=[list(v) for v in ring]))
    bottom, top = len(vertices), len(vertices) + 1
    vertices.extend([(0, 0, -50), (0, 0, 50)])
    faces, uvs, smooth = [], [], []
    for r in range(len(HEIGHTS) - 1):
        for j in range(RADIAL):
            k = (j + 1) % RADIAL
            faces.append((r*RADIAL+j, r*RADIAL+k, (r+1)*RADIAL+k, (r+1)*RADIAL+j))
            uvs.append(((j/RADIAL, 2*HEIGHTS[r]), ((j+1)/RADIAL, 2*HEIGHTS[r]),
                        ((j+1)/RADIAL, 2*HEIGHTS[r+1]), (j/RADIAL, 2*HEIGHTS[r+1])))
            smooth.append(True)
    for j in range(RADIAL):
        k = (j + 1) % RADIAL
        for ids in ((bottom, k, j), (top, (len(HEIGHTS)-1)*RADIAL+j, (len(HEIGHTS)-1)*RADIAL+k)):
            faces.append(ids)
            uvs.append(tuple((.5 + vertices[i][0]/(4*ROOT_RADIUS_CM), 2.4 + vertices[i][1]/(4*ROOT_RADIUS_CM)) for i in ids))
            smooth.append(False)
    require(len(vertices) == 114 and len(faces) == 126, 'Exact original 114 wood vertices and 126 polygons')
    return dict(name='Stem', vertices=vertices, faces=faces, uvs=uvs, smooth=smooth, material=0, rings=rings)


def basis(axis):
    axis = axis.normalized()
    u = axis.cross(Vector((0, 0, 1)))
    require(u.length > .1, 'Leaf/petiole direction admits a stable horizontal width basis')
    u.normalize()
    v = axis.cross(u).normalized()
    require((u.cross(v) - axis).length < 1e-6, 'Right-handed local shell basis')
    return u, v


def leaf_geometry(name, base, tip, half_width):
    """A pointed, softly bowed lenticular solid; no planes, transparency or modifiers."""
    base, tip = Vector(base), Vector(tip)
    delta = tip - base
    axis, length = delta.normalized(), delta.length
    u, v = basis(axis)
    vertices = []
    for t in LEAF_STEPS:
        width = half_width * math.sin(math.pi*t)**.85
        half_thickness = .10 + .16*math.sin(math.pi*t)
        center = base + delta*t + v*(.55*math.sin(math.pi*t))
        for j in range(LEAF_RADIAL):
            angle = 2*math.pi*j/LEAF_RADIAL
            vertices.append(xyz(center + u*(width*math.cos(angle)) + v*(half_thickness*math.sin(angle))))
    start, end = len(vertices), len(vertices) + 1
    vertices.extend([xyz(base), xyz(tip)])
    faces, uvs = [], []
    for r in range(len(LEAF_STEPS)-1):
        for j in range(LEAF_RADIAL):
            k = (j + 1) % LEAF_RADIAL
            faces.append((r*LEAF_RADIAL+j, r*LEAF_RADIAL+k, (r+1)*LEAF_RADIAL+k, (r+1)*LEAF_RADIAL+j))
            uvs.append(((j/LEAF_RADIAL, LEAF_STEPS[r]), ((j+1)/LEAF_RADIAL, LEAF_STEPS[r]),
                        ((j+1)/LEAF_RADIAL, LEAF_STEPS[r+1]), (j/LEAF_RADIAL, LEAF_STEPS[r+1])))
    last = (len(LEAF_STEPS)-1)*LEAF_RADIAL
    for j in range(LEAF_RADIAL):
        k = (j+1) % LEAF_RADIAL
        faces.extend([(start, k, j), (end, last+j, last+k)])
        uvs.extend([(((j+.5)/LEAF_RADIAL, 0), ((j+1)/LEAF_RADIAL, LEAF_STEPS[0]), (j/LEAF_RADIAL, LEAF_STEPS[0])),
                    (((j+.5)/LEAF_RADIAL, 1), (j/LEAF_RADIAL, LEAF_STEPS[-1]), ((j+1)/LEAF_RADIAL, LEAF_STEPS[-1]))])
    return dict(name=name, vertices=vertices, faces=faces, uvs=uvs, smooth=[True]*len(faces), material=1,
                base_cm=xyz(base), tip_cm=xyz(tip), axis=xyz(axis), length_cm=length,
                max_source_half_width_cm=half_width, minimum_ring_half_thickness_cm=min(.10+.16*math.sin(math.pi*t) for t in LEAF_STEPS))


def petiole_geometry(name, base, tip):
    """One closed six-sided wooden stalk intersecting both branch and leaf solids."""
    base, tip = Vector(base), Vector(tip)
    axis = (tip-base).normalized()
    u, v = basis(axis)
    radius, radial = .8, 6
    vertices = []
    for center in (base, tip):
        for j in range(radial):
            a = 2*math.pi*j/radial
            vertices.append(xyz(center + radius*(u*math.cos(a) + v*math.sin(a))))
    bottom, top = len(vertices), len(vertices)+1
    vertices.extend([xyz(base), xyz(tip)])
    faces, uvs, smooth = [], [], []
    length = (tip-base).length
    for j in range(radial):
        k = (j+1) % radial
        faces.append((j, k, radial+k, radial+j))
        uvs.append(((j/radial, 0), ((j+1)/radial, 0), ((j+1)/radial, length/50), (j/radial, length/50)))
        smooth.append(True)
    for j in range(radial):
        k = (j+1) % radial
        for ids, center in (((bottom, k, j), base), ((top, radial+j, radial+k), tip)):
            faces.append(ids)
            uvs.append(tuple((.5 + (Vector(vertices[i])-center).dot(u)/(4*radius),
                              2.4 + (Vector(vertices[i])-center).dot(v)/(4*radius)) for i in ids))
            smooth.append(False)
    return dict(name=name, vertices=vertices, faces=faces, uvs=uvs, smooth=smooth, material=0,
                start_cm=xyz(base), end_cm=xyz(tip), radius_cm=radius)


def rotated_pair(part, name, z_shift):
    """180-degree Z rotation, then Z translation: positive determinant, same XY envelope."""
    result = dict(part)
    result.update(name=name, vertices=[[-p[0], -p[1], p[2]+z_shift] for p in part['vertices']])
    for key in ('base_cm', 'tip_cm', 'start_cm', 'end_cm'):
        if key in part:
            p = part[key]
            result[key] = [-p[0], -p[1], p[2]+z_shift]
    if 'axis' in part:
        result['axis'] = [-part['axis'][0], -part['axis'][1], part['axis'][2]]
    return result


def freeze_triangles(part):
    """Freeze Blender's actual evaluated triangles/UVs before FBX can retriangulate."""
    mesh = bpy.data.meshes.new('QA_ExplicitTriangles_' + part['name'])
    mesh.from_pydata(part['vertices'], [], part['faces'])
    mesh.update(calc_edges=True)
    uv = mesh.uv_layers.new(name='UV0')
    for polygon, coords, shading in zip(mesh.polygons, part['uvs'], part['smooth']):
        polygon.use_smooth = shading
        for loop, value in zip(polygon.loop_indices, coords):
            uv.data[loop].uv = value
    mesh.calc_loop_triangles()
    original_faces = part['faces']
    part['faces'] = [tuple(t.vertices) for t in mesh.loop_triangles]
    part['uvs'] = [tuple(tuple(float(c) for c in uv.data[loop].uv) for loop in t.loops) for t in mesh.loop_triangles]
    part['smooth'] = [mesh.polygons[t.polygon_index].use_smooth for t in mesh.loop_triangles]
    part['pretriangulation_faces'] = original_faces
    part['triangle_source_polygon'] = [t.polygon_index for t in mesh.loop_triangles]
    bpy.data.meshes.remove(mesh)


def mesh_from_parts(parts, material_slots):
    vertices, faces, uvs, materials, smooth, ranges = [], [], [], [], [], {}
    for part in parts:
        offset, first_face = len(vertices), len(faces)
        vertices.extend(part['vertices'])
        faces.extend(tuple(offset+i for i in f) for f in part['faces'])
        uvs.extend(part['uvs'])
        materials.extend([part['material']]*len(part['faces']))
        smooth.extend(part['smooth'])
        ranges[part['name']] = dict(first_vertex=offset, vertex_count=len(part['vertices']),
                                  first_polygon=first_face, polygon_count=len(part['faces']), material_index=part['material'])
    mesh = bpy.data.meshes.new(MESH_NAME)
    mesh.from_pydata(vertices, [], faces)
    mesh.update(calc_edges=True)
    require(not mesh.validate(verbose=False, clean_customdata=False), 'Combined mesh validates without silent repair')
    for material in material_slots:
        mesh.materials.append(material)
    uv = mesh.uv_layers.new(name='UV0')
    for polygon, coordinates, slot, shading in zip(mesh.polygons, uvs, materials, smooth):
        polygon.material_index = slot
        polygon.use_smooth = shading
        require(len(polygon.loop_indices) == len(coordinates), 'Every actual polygon has matching UV0 corners')
        for loop, coord in zip(polygon.loop_indices, coordinates):
            uv.data[loop].uv = coord
    mesh.update()
    return mesh, ranges


def shell_records(mesh):
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bm.normal_update()
    require(all(e.is_manifold and e.is_contiguous for e in bm.edges), 'All actual shell edges closed and consistently wound')
    require(all(v.link_edges and v.link_faces for v in bm.verts), 'No loose vertices or edges')
    pending, shells = set(bm.verts), []
    while pending:
        found, stack = set(), [next(iter(pending))]
        while stack:
            vertex = stack.pop()
            if vertex in found:
                continue
            found.add(vertex)
            stack.extend(e.other_vert(vertex) for e in vertex.link_edges)
        pending.difference_update(found)
        edges = {e for v in found for e in v.link_edges}
        faces = {f for v in found for f in v.link_faces}
        require(len(found)-len(edges)+len(faces) == 2, 'Each separate closed shell is genus zero')
        volume = 0.
        for f in faces:
            points = [v.co for v in f.verts]
            for i in range(1, len(points)-1):
                volume += points[0].dot(points[i].cross(points[i+1])) / 6
        require(math.isfinite(volume) and volume > 1e-5, 'Each shell has positive signed volume and outward winding')
        shells.append(dict(vertices=len(found), edges=len(edges), polygons=len(faces),
                           signed_volume_cm3=float(volume), material_indices=sorted({f.material_index for f in faces})))
    bm.free()
    require(len(shells) == 9, 'Exactly one wood stem, four closed petioles and four closed leaf shells')
    return sorted(shells, key=lambda r: (r['material_indices'], r['vertices'], r['signed_volume_cm3']))


def mesh_record(mesh, include_geometry=True):
    mesh.calc_loop_triangles()
    uv = require(mesh.uv_layers.active, 'Actual active UV0')
    require(len(mesh.uv_layers) == 1 and len(mesh.materials) == 2, 'Exactly UV0 and Wood0/Leaf1 slots')
    require([m.name.split('.')[0] for m in mesh.materials] == SLOTS, 'Actual source/fresh-FBX material order')
    require(all(math.isfinite(float(c)) for v in mesh.vertices for c in v.co), 'Finite actual vertices')
    require(all(math.isfinite(float(c)) for loop in uv.data for c in loop.uv), 'Finite actual UV0')
    lo = [min(float(v.co[i]) for v in mesh.vertices) for i in range(3)]
    hi = [max(float(v.co[i]) for v in mesh.vertices) for i in range(3)]
    require(all(abs(lo[i]+hi[i]) < .00002 for i in (0, 1))
            and abs(lo[2]+50) < .00002 and abs(hi[2]-50) < .00002, 'Actual centered XY bounds and exact original Z endpoints')
    require(all(min((Vector((0, 0, z))-v.co).length for v in mesh.vertices) < .00002 for z in (-50, 50)), 'Actual wood root/tip vertices on bounds axis')
    triangles = []
    for tri in mesh.loop_triangles:
        require(tri.area > 1e-8, 'Every actual render triangle has nonzero area')
        coords = [[float(c) for c in uv.data[loop].uv] for loop in tri.loops]
        a, b, c = coords
        area = abs((b[0]-a[0])*(c[1]-a[1]) - (b[1]-a[1])*(c[0]-a[0]))*.5
        require(area > 1e-10, 'Every actual triangle has nondegenerate UV0')
        triangles.append(dict(indices=list(tri.vertices), material_index=tri.material_index, uv0=coords,
                              normal=xyz(tri.normal),
                              corner_normals=[xyz(mesh.corner_normals[loop].vector) for loop in tri.loops],
                              source_polygon=tri.polygon_index))
    require(all(abs(p.normal.length-1) < 1e-5 for p in mesh.polygons), 'Actual polygon normals finite and unit length')
    require(len(triangles) <= 1000 and set(t['material_index'] for t in triangles) == {0, 1}, 'Bounded triangle budget with both actual material regions')
    shells = shell_records(mesh)
    result = dict(vertices=len(mesh.vertices), polygons=len(mesh.polygons), triangles=len(triangles), uv_layers=1,
                  bounds_cm=dict(min=lo, max=hi), material_slots=SLOTS[:], shell_count=len(shells), shells=shells,
                  material_triangle_counts={SLOTS[i]: sum(t['material_index'] == i for t in triangles) for i in (0, 1)},
                  closed_shells=True, shell_intersections_intentional=True, boolean_union_claimed=False,
                  no_loose_geometry=True, nondegenerate_triangles_and_uv0=True)
    if include_geometry:
        result.update(vertex_positions_cm=[xyz(v.co) for v in mesh.vertices],
                      faces=[dict(indices=list(p.vertices), material_index=p.material_index,
                                  uv0=[[float(c) for c in uv.data[loop].uv] for loop in p.loop_indices],
                                  normal=xyz(p.normal), smooth=p.use_smooth) for p in mesh.polygons],
                      loop_triangles=triangles)
    return result


def part_tree(part):
    return BVHTree.FromPolygons([Vector(v) for v in part['vertices']], part['faces'], all_triangles=False)


def inside(tree, point, title):
    results = []
    for direction in (Vector((1, .271, .193)), Vector((.317, 1, .223)), Vector((.197, .373, 1))):
        direction.normalize()
        origin, count = Vector(point), 0
        for _ in range(64):
            location, normal, index, distance = tree.ray_cast(origin, direction, 1000.)
            if location is None:
                break
            count += 1
            origin = location + direction*.0001
        else:
            raise AssertionError('Bounded inside/outside ray iteration exhausted ' + title)
        results.append(count)
    require(all(c % 2 == 1 for c in results), 'Actual three-direction closed-shell point-inside ' + title)
    return dict(point_cm=xyz(point), ray_exit_counts=results, inside=True)


def connection_records(parts):
    byname = {p['name']: p for p in parts}
    stem = part_tree(byname['Stem'])
    records = []
    for suffix in ('A', 'B', 'C', 'D'):
        petiole, leaf = byname['Petiole_'+suffix], byname['Leaf_'+suffix]
        pt, lt = part_tree(petiole), part_tree(leaf)
        start, end = Vector(petiole['start_cm']), Vector(petiole['end_cm'])
        axis = Vector(leaf['axis'])
        wood_overlap = start + (end-start)*.18
        leaf_overlap = Vector(leaf['base_cm']) + axis*1.0
        records.append(dict(leaf='Leaf_'+suffix, petiole='Petiole_'+suffix,
                            wood_to_petiole=dict(in_wood=inside(stem, wood_overlap, suffix+' wood'),
                                                 in_petiole=inside(pt, wood_overlap, suffix+' petiole at wood')),
                            petiole_to_leaf=dict(in_petiole=inside(pt, leaf_overlap, suffix+' petiole at blade'),
                                                 in_leaf=inside(lt, leaf_overlap, suffix+' blade'))))
    return records


def triangle_signatures(record):
    result = Counter()
    for tri in record['loop_triangles']:
        corners = [tuple(round(v, 4) for v in record['vertex_positions_cm'][index]) + tuple(round(v, 6) for v in uv)
                   for index, uv in zip(tri['indices'], tri['uv0'])]
        # Cyclic rotations retain winding, unlike sorting the three corners.
        result[(tri['material_index'], min(tuple(corners[i:]+corners[:i]) for i in range(3)))] += 1
    return result


def png_record(file):
    raw = file.read_bytes()
    require(raw[:8] == b'\x89PNG\r\n\x1a\n', 'Actual render PNG signature '+file.name)
    cursor, dimensions = 8, None
    while cursor < len(raw):
        size, kind = struct.unpack_from('>I4s', raw, cursor)
        require(cursor+size+12 <= len(raw), 'Bounded render PNG chunk '+file.name)
        payload = raw[cursor+8:cursor+8+size]
        require(zlib.crc32(kind+payload) & 0xffffffff == struct.unpack_from('>I', raw, cursor+8+size)[0], 'Render PNG CRC '+file.name)
        if kind == b'IHDR':
            dimensions = list(struct.unpack_from('>II', payload))
        cursor += size+12
        if kind == b'IEND':
            break
    require(cursor == len(raw) and kind == b'IEND' and dimensions == [1024, 1280], 'Exact render PNG dimensions and no tail')
    return dict(path=str(file), bytes=file.stat().st_size, sha256=sha(file), dimensions=dimensions, tail_bytes=0)


def aim(obj, target):
    obj.rotation_euler = (Vector(target)-obj.location).to_track_quat('-Z', 'Y').to_euler()


def preview_material(name, color, roughness):
    material = bpy.data.materials.new(name)
    material.use_nodes = True
    material.diffuse_color = (*color, 1)
    principled = material.node_tree.nodes.get('Principled BSDF')
    principled.inputs['Base Color'].default_value = (*color, 1)
    principled.inputs['Roughness'].default_value = roughness
    principled.inputs['Metallic'].default_value = 0
    principled.inputs['Alpha'].default_value = 1
    principled.inputs['Emission Strength'].default_value = 0
    return material


def render_previews(scene, out):
    scene.render.engine = 'CYCLES'
    scene.cycles.device = 'CPU'
    scene.cycles.samples = 40
    scene.cycles.use_denoising = True
    scene.render.resolution_x, scene.render.resolution_y = 1024, 1280
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = 'PNG'
    scene.render.image_settings.color_mode = 'RGB'
    scene.render.film_transparent = False
    scene.view_settings.view_transform = 'AgX'
    if scene.world is None:
        scene.world = bpy.data.worlds.new('QA_World')
    scene.world.use_nodes = True
    background = scene.world.node_tree.nodes.get('Background')
    background.inputs['Color'].default_value = (.12, .12, .12, 1)
    background.inputs['Strength'].default_value = .45
    for name, location, power, size in (('QA_Key', (65, -95, 115), 280000, 85),
                                       ('QA_Fill', (-85, -35, 30), 120000, 100),
                                       ('QA_Rim', (25, 75, 60), 220000, 70)):
        data = bpy.data.lights.new(name, 'AREA')
        data.energy, data.shape, data.size = power, 'DISK', size
        light = bpy.data.objects.new(name, data)
        scene.collection.objects.link(light)
        light.location = location
        aim(light, (0, 0, 0))
    data = bpy.data.cameras.new('QA_Camera')
    data.type, data.ortho_scale, data.clip_end = 'ORTHO', 130, 2000
    camera = bpy.data.objects.new('QA_Camera', data)
    scene.collection.objects.link(camera)
    scene.camera = camera
    result = []
    for name, location in (('01_FullContour', (0, -180, 18)), ('02_SolidLeaves_Oblique', (145, -155, 90))):
        camera.location = location
        aim(camera, (0, 0, 0))
        file = out / (name+'.png')
        scene.render.filepath = str(file)
        bpy.ops.render.render(write_still=True)
        result.append(dict(camera=name, position_cm=list(location), target_cm=[0, 0, 0], ortho_scale_cm=130,
                           generated_by='Actual Blender Cycles CPU render of the exported source mesh',
                           png=png_record(file), UE_or_gameplay_acceptance=False))
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args(sys.argv[sys.argv.index('--')+1:])
    out = args.out
    require(out.is_absolute() and out.drive.lower() != 'd:' and out.parent.resolve() == HERE
            and re.fullmatch(r'Source-Run[1-9][0-9]*', out.name)
            and not out.exists(), 'Only one explicit absent local Source-RunN output is writable')
    require(bpy.app.version[:2] == (4, 5), 'Actual Blender 4.5 runtime')
    frozen = {str(file): sha(file) for file in INPUTS}
    author_file = Path(__file__).resolve()
    author_sha = sha(author_file)
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    scene = bpy.context.scene
    scene.unit_settings.system = 'METRIC'
    scene.unit_settings.scale_length = .01
    scene.unit_settings.length_unit = 'CENTIMETERS'
    stem = stem_geometry()
    leaf_a = leaf_geometry('Leaf_A', (9, 0, -8), (34, 5, 14), 3.0)
    leaf_c = leaf_geometry('Leaf_C', (0, 8, 16), (-4, 28, 34), 2.7)
    leaves = [leaf_a, rotated_pair(leaf_a, 'Leaf_B', 15), leaf_c, rotated_pair(leaf_c, 'Leaf_D', 10)]
    parts = [stem]
    for leaf in leaves:
        base, axis = Vector(leaf['base_cm']), Vector(leaf['axis'])
        petiole = petiole_geometry('Petiole_'+leaf['name'][-1], (0, 0, base.z-2), base+axis*1.8)
        parts.extend([petiole, leaf])
    require(len(parts) == 9 and len(leaves) == 4, 'Exactly four alternating solid leaves and their wooden stalks')
    require(all(-49 < p[2] < 49 for part in parts if part['name'] != 'Stem' for p in part['vertices']), 'All leaves/stalks remain strictly inside original Z endpoint planes')
    connections = connection_records(parts)
    for part in parts:
        freeze_triangles(part)
    wood = preview_material('Wood0', (.19, .15, .105), .85)
    leaf_material = preview_material('Leaf1', (.075, .14, .028), .78)
    mesh, ranges = mesh_from_parts(parts, (wood, leaf_material))
    obj = bpy.data.objects.new(MESH_NAME, mesh)
    scene.collection.objects.link(obj)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    source = mesh_record(mesh)
    require(source['vertices'] == sum(len(p['vertices']) for p in parts)
            and source['polygons'] == sum(len(p['faces']) for p in parts), 'Combined counts equal actual explicitly recorded parts')
    # Check the copied source wood, not just the author formula or its bounds.
    require(all((mesh.vertices[i].co-Vector(p)).length < 1e-5 for i, p in enumerate(stem['vertices']))
            and all(mesh.polygons[i].material_index == 0 for i in range(len(stem['faces']))), 'Original wood positions/material region retained')
    out.mkdir()
    fbx = out / 'forest-branch-leafed.fbx'
    bpy.ops.export_scene.fbx(filepath=str(fbx), check_existing=True, use_selection=True,
        object_types={'MESH'}, global_scale=1, apply_unit_scale=True, apply_scale_options='FBX_SCALE_UNITS',
        axis_forward='-Y', axis_up='Z', bake_space_transform=False, use_mesh_modifiers=False,
        mesh_smooth_type='FACE', use_mesh_edges=False, use_tspace=False, use_triangles=True,
        add_leaf_bones=False, bake_anim=False, path_mode='AUTO', embed_textures=False)
    before = set(bpy.data.objects)
    bpy.ops.import_scene.fbx(filepath=str(fbx), use_anim=False)
    imported = [o for o in bpy.data.objects if o not in before]
    require(len(imported) == 1 and imported[0].type == 'MESH', 'Fresh FBX read returns exactly one combined mesh')
    imported_obj = imported[0]
    roundtrip = mesh_record(imported_obj.data)
    require(roundtrip['triangles'] == source['triangles'] and roundtrip['material_triangle_counts'] == source['material_triangle_counts'], 'Fresh FBX keeps actual per-slot triangle counts')
    require(triangle_signatures(roundtrip) == triangle_signatures(source), 'Every fresh-FBX triangle retains source position/UV0/winding/material identity')
    require(all(abs(roundtrip['bounds_cm'][side][i]-source['bounds_cm'][side][i]) < .0001 for side in ('min', 'max') for i in range(3))
            and imported_obj.location.length < 1e-6 and all(abs(v-1) < 1e-6 for v in imported_obj.scale), 'Fresh FBX centimeter bounds, origin and unit scale retained')
    bpy.data.objects.remove(imported_obj, do_unlink=True)
    previews = render_previews(scene, out)
    require(all(sha(Path(file)) == value for file, value in frozen.items()), 'Old author and read-only project inputs unchanged')
    require(sha(author_file) == author_sha, 'Author script unchanged during generation')
    report = dict(schema='ForestCanopySource.v1', status='PASS-LOCAL-FOUR-LEAF-CANOPY-SOURCE-NATIVE-AND-ART-PENDING',
        blender_version=bpy.app.version_string, blender_binary=bpy.app.binary_path,
        author_tool=dict(path=str(author_file), sha256=author_sha, source_utf8=author_file.read_text(encoding='utf-8')),
        input_sha256=frozen, source_mesh=source, fbx_fresh_read_mesh=roundtrip,
        parts={p['name']: dict(ranges=ranges[p['name']], material_index=p['material'],
                               vertex_positions_cm=p['vertices'], faces=[list(f) for f in p['faces']], uv0=p['uvs'],
                               additional={k: v for k, v in p.items() if k not in ('vertices', 'faces', 'uvs', 'smooth', 'name', 'material')}) for p in parts},
        leaf_connections=connections, wood_axis_endpoints_cm=[[0, 0, -50], [0, 0, 50]],
        material_slots=SLOTS[:], leaf_count=4, petiole_count=4,
        materials=dict(Wood0=dict(role='Stem and petioles; neutral source preview only; native may use existing wood MI', base_color_linear=[.19, .15, .105], roughness=.85),
                       Leaf1=dict(role='Closed solid leaf blades; original stylized candidate, not botanical species', base_color_linear=[.075, .14, .028], roughness=.78),
                       common=dict(metallic=0, alpha=1, emission_strength=0, opaque_intent=True, textures=0, WPO=False, wind=False)),
        units='Source coordinates centimeters; Blender metric scale_length .01; FBX_SCALE_UNITS, forward -Y, up Z; no mesh transform bake',
        native_coordinates='Existing project Blender-FBX-to-UE pipeline predicts (X,-Y,Z); native tool must confirm actual FBX/import metadata and triangle/normal correspondence, not assume this note proves import.',
        fbx=dict(path=str(fbx), bytes=fbx.stat().st_size, sha256=sha(fbx)), previews=previews,
        provenance='Original procedural stylized wood/stalk/four narrow solid leaf geometry with Codex assistance; wood formula reused from recorded local author; no third-party mesh/texture/download/payment/generation service. Not a peach-tree species claim or historical reconstruction.',
        runtime_limitations=['One shared mesh appears on all 15 branches, including root/intermediate branches.',
                             'Runtime bounds-normalized XY scale fixes overall width to DiameterWorld, so source widening does not automatically enlarge canopy.',
                             'XY width is fully present when branch first becomes visible; only Z grows. Initial flattened leaves require actual UE review.',
                             'Slot0 may be overridden by BranchMaterial; slot1 must retain actual leaf material on dynamic components.',
                             'Eight-corner projection bounds and original A contact must be native-verified before any map adoption.'],
        checks=CHECKS[:], check_count=len(CHECKS),
        scope=dict(D_writes=False, UE=False, native_verified=False, art_accepted=False, layout_changed=False,
                   Cpp_or_Tick_or_input_changed=False, paid_or_downloaded_assets=False, actual_render_previews=True))
    (out / 'SOURCE.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    (out / 'README.md').write_text(
        '# Four-leaf solid canopy candidate\n\n'
        'One combined mesh: the original closed tapered stem plus four closed wooden petioles and four closed narrow leaf solids. '
        'Wood0 is slot 0, Leaf1 is slot 1. All nine topological shells are intentionally intersecting, not boolean-unioned; '
        'SOURCE.json records point-inside proof at each stem/stalk and stalk/blade connection, per-shell winding/volume and full vertex/face/UV/material data.\n\n'
        'Original procedural stylized leaf geometry with Codex assistance; no download, paid asset, image/3D generation service or third-party mesh/texture. '
        'Not a botanical peach-tree reconstruction, historical original or traditional-school authenticity claim. '
        'Neutral rough preview materials are not final UE art. The two PNGs are actual Cycles CPU renders of the FBX source geometry, not hand-drawn compositions.\n\n'
        'Centimeters, mesh-local Z [-50,+50], centered XY bounds and real wood root/tip at (0,0,-50)/(0,0,50). '
        'FBX forward -Y/up Z, unit scale applied; the project native axis mapping must still be independently checked. '
        'Export contains only one mesh, one UV0, two materials, no textures, bones, animations, wind or collision helpers.\n\n'
        'This tool does not alter the 15-branch layout or run UE. Overall branch diameter is normalized from the whole mesh bounds, '
        'and early growth scales Z only: flattened leaves/width popping, root continuity, conservative projection bounds, material slot retention, '
        'native source correspondence, actual same-light shadows and final visuals remain unaccepted. Preserve all prior source/BP/map assets.\n', encoding='utf-8')
    print(json.dumps(dict(status=report['status'], vertices=source['vertices'], triangles=source['triangles'],
                          bounds_cm=source['bounds_cm'], material_slots=SLOTS, fbx=report['fbx'],
                          checks=report['check_count']), ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
