"""Two passive backstage woodwork candidates; local Blender sources only."""
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
from mathutils.bvhtree import BVHTree


HERE = Path(__file__).resolve().parent
CHECKS = []
UV_CM = 50.


def require(value, message):
    if not value:
        raise AssertionError(message)
    CHECKS.append(message)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def bounds(obj):
    points = [obj.matrix_world @ v.co for v in obj.data.vertices]
    return dict(min=[min(p[i] for p in points) for i in range(3)],
                max=[max(p[i] for p in points) for i in range(3)])


def record(obj):
    mesh = obj.data
    mesh.calc_loop_triangles()
    require(not mesh.validate(verbose=False,clean_customdata=False), 'No mesh repair '+obj.name)
    require(all(math.isfinite(x) for v in mesh.vertices for x in v.co), 'Finite vertices '+obj.name)
    require(all(t.area > 1e-8 for t in mesh.loop_triangles), 'No degenerate triangles '+obj.name)
    require(all(abs(p.normal.length-1) < 1e-5 for p in mesh.polygons), 'Unit face normals '+obj.name)
    require(len(mesh.uv_layers) == 1 and len(mesh.materials) == 1 and mesh.materials[0].name.split('.')[0] == 'Wood',
            'One UV0 and one Wood slot '+obj.name)
    uv = mesh.uv_layers[0].data
    density = []
    for triangle in mesh.loop_triangles:
        a,b,c = [uv[i].uv for i in triangle.loops]
        area = abs((b.x-a.x)*(c.y-a.y)-(b.y-a.y)*(c.x-a.x))*.5
        require(math.isfinite(area) and area > 1e-12, 'Finite nondegenerate UV triangle '+obj.name)
        density.append(area/triangle.area*UV_CM*UV_CM)
    require(min(density) > .975 and max(density) < 1.025, 'Uniform physical wood UV density within 2.5% '+obj.name)
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bm.normal_update()
    require(all(e.is_manifold and e.is_contiguous for e in bm.edges), 'Closed consistently wound wooden shells '+obj.name)
    require(all(v.link_edges and v.link_faces for v in bm.verts), 'No loose geometry '+obj.name)
    volume = bm.calc_volume(signed=True)
    require(math.isfinite(volume) and volume > 0, 'Positive shell volume '+obj.name)
    bm.free()
    return dict(vertices=len(mesh.vertices),edges=len(mesh.edges),polygons=len(mesh.polygons),
                triangles=len(mesh.loop_triangles),bounds_cm=bounds(obj),summed_shell_volume_cm3=volume,
                closed_shells=True,loose_geometry=False,uv0_count=1,material_slots=[mesh.materials[0].name],
                normalized_UV_area_density_range=[min(density),max(density)])


def set_uv(obj, axis):
    mesh = obj.data
    while mesh.uv_layers:
        mesh.uv_layers.remove(mesh.uv_layers[0])
    uv = mesh.uv_layers.new(name='UV0')
    long_axis = Vector(axis)
    for face in mesh.polygons:
        normal = face.normal.normalized()
        v = long_axis-normal*long_axis.dot(normal)
        if v.length < .1:
            alternate = Vector((1,0,0)) if abs(long_axis.x)<.9 else Vector((0,1,0))
            v = (alternate-normal*alternate.dot(normal)).normalized()
        else:
            v.normalize()
        u = v.cross(normal).normalized()
        for loop in face.loop_indices:
            point = mesh.vertices[mesh.loops[loop].vertex_index].co
            uv.data[loop].uv = (point.dot(u)/UV_CM,point.dot(v)/UV_CM)


def part(name, center, size, axis, material, cylinder=False):
    if cylinder:
        bpy.ops.mesh.primitive_cylinder_add(vertices=14,radius=size[0]/2,depth=size[2],location=center)
        obj = bpy.context.object
        if axis == (0,1,0):
            obj.rotation_euler.x = math.pi/2
    else:
        bpy.ops.mesh.primitive_cube_add(size=1,location=center)
        obj = bpy.context.object
        obj.dimensions = size
    obj.name = name
    bpy.ops.object.transform_apply(location=False,rotation=True,scale=True)
    bevel = obj.modifiers.new('Small worn wood edge','BEVEL')
    bevel.width,bevel.segments,bevel.limit_method = .4,3,'ANGLE'
    bpy.ops.object.modifier_apply(modifier=bevel.name)
    obj.data.materials.append(material)
    obj['source_primitive'] = 'CYLINDER14' if cylinder else 'BOX'
    set_uv(obj,axis)
    return obj


def inside(obj, point):
    tree = BVHTree.FromObject(obj,bpy.context.evaluated_depsgraph_get())
    origin = obj.matrix_world.inverted() @ Vector(point)
    direction = Vector((.8123,.4351,.387)).normalized()
    count = 0
    for _ in range(64):
        location,normal,index,distance = tree.ray_cast(origin,direction,10000)
        if location is None:
            return count%2 == 1
        count += 1
        origin = location+direction*.00001
    raise AssertionError('Unexpected unbounded contact ray')


def contact(parts, left, right, point, rows):
    require(inside(parts[left],point) and inside(parts[right],point), 'Actual common interior join '+left+' / '+right)
    rows.append(dict(parts=[left,right],common_interior_world_cm=point,actual_BVH_inside_both=True))


def collision_record(obj):
    mesh = obj.data
    mesh.calc_loop_triangles()
    require(len(mesh.vertices) == 8 and len(mesh.loop_triangles) == 12,
            'Actual UBX eight vertices / twelve triangles '+obj.name)
    require(len(mesh.uv_layers) == 0 and len(mesh.materials) == 0,
            'UBX has no UV or material '+obj.name)
    require(all(math.isfinite(x) for vertex in mesh.vertices for x in vertex.co)
            and all(triangle.area > 1e-8 for triangle in mesh.loop_triangles),
            'UBX finite nondegenerate geometry '+obj.name)
    require(all(abs(v) < 1e-7 for v in obj.location) and all(abs(v) < 1e-7 for v in obj.rotation_euler)
            and all(abs(v-1) < 1e-7 for v in obj.scale),'UBX identity source transforms '+obj.name)
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bm.normal_update()
    require(all(edge.is_manifold and edge.is_contiguous for edge in bm.edges)
            and bm.calc_volume(signed=True) > 0,'UBX closed consistently wound positive volume '+obj.name)
    bm.free()
    box = bounds(obj)
    return dict(name=obj.name,bounds_cm=box,
                center_cm=[(box['min'][i]+box['max'][i])/2 for i in range(3)],
                dimensions_cm=[box['max'][i]-box['min'][i] for i in range(3)],
                vertices=len(mesh.vertices),triangles=len(mesh.loop_triangles),uv_layers=0,material_slots=0)


def ue_box_planes(vertices, faces):
    # Match local UE5.8 AddBoxGeomFromTris, including its DistCount==2 comparison.
    planes,trace = [],[]
    equal = lambda a,b: abs(a-b) < .001
    for index,face in enumerate(faces):
        a,b,c = [Vector(vertices[i]) for i in face]
        normal = (b-a).cross(c-a).normalized()
        require(normal.length > .99,'Nonzero raw FBX UBX triangle normal')
        found = False
        for plane in planes:
            if equal(abs(normal.dot(Vector(plane['normal']))),1):
                distance = a.dot(Vector(plane['normal']))
                trace.append(dict(triangle=index,normal=list(normal),distance=distance,plane_distances_before=list(plane['distances'])))
                if len(plane['distances']) == 1 and not equal(distance,plane['distances'][0]):
                    plane['distances'].append(distance)
                elif len(plane['distances']) == 2 and not equal(distance,plane['distances'][1]):
                    return dict(passed=False,failure='Found more than 2 planes with different distances',
                                failure_triangle=index,planes=planes,trace=trace)
                found = True
                break
        if not found:
            planes.append(dict(normal=list(normal),distances=[a.dot(normal)]))
            trace.append(dict(triangle=index,normal=list(normal),new_plane=True))
    passed = len(planes) == 3 and all(len(p['distances']) == 2 for p in planes)
    if passed:
        passed = equal(abs(Vector(planes[0]['normal']).cross(Vector(planes[1]['normal'])).dot(Vector(planes[2]['normal']))),1)
    return dict(passed=passed,planes=planes,trace=trace)


def fbx_box_order(path, expected_names, should_pass):
    from io_scene_fbx.parse_fbx import parse
    root,version = parse(str(path))
    objects = next(element for element in root.elems if element.id == b'Objects')
    result = {}
    for geometry in objects.elems:
        if geometry.id != b'Geometry':
            continue
        raw_name = geometry.props[1].split(b'\x00\x01')[0].decode('utf-8')
        name = raw_name.split('.')[0]
        if not name.startswith('UBX_'):
            continue
        raw_vertices = next(element.props[0] for element in geometry.elems if element.id == b'Vertices')
        indices = next(element.props[0] for element in geometry.elems if element.id == b'PolygonVertexIndex')
        vertices = [raw_vertices[i:i+3] for i in range(0,len(raw_vertices),3)]
        faces,current = [],[]
        for value in indices:
            current.append(-value-1 if value<0 else value)
            if value<0:
                faces.append(current)
                current = []
        require(not current and len(vertices) == 8 and len(faces) == 12 and all(len(face)==3 for face in faces),
                'Raw physical FBX has 8 points and 12 triangles '+name)
        test = ue_box_planes(vertices,faces)
        require(test['passed'] == should_pass,'Actual raw FBX UE box-plane order expected '+str(should_pass)+' '+name)
        require(name not in result,'Unique normalized raw Geometry name '+name)
        result[name] = dict(raw_geometry_name=raw_name,raw_polygon_vertex_indices=faces,ue_5_8_box_plane_simulation=test)
    require(set(result) == set(expected_names),'Exact raw FBX UBX names '+path.name+' raw_geometry_names='+repr(
        [geometry.props[1] for geometry in objects.elems if geometry.id == b'Geometry']))
    return dict(fbx_version=version,raw_polygon_order=True,boxes=result)


def make_collision(name, source):
    box = bounds(source)
    lo,hi = box['min'],box['max']
    vertices = [(lo[0],lo[1],lo[2]),(hi[0],lo[1],lo[2]),(hi[0],hi[1],lo[2]),(lo[0],hi[1],lo[2]),
                (lo[0],lo[1],hi[2]),(hi[0],lo[1],hi[2]),(hi[0],hi[1],hi[2]),(lo[0],hi[1],hi[2])]
    quads = [(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
    faces = [triangle for a,b,c,d in quads for triangle in ((a,b,c),(a,c,d))]
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(vertices,[],faces)
    mesh.update(calc_edges=True)
    obj = bpy.data.objects.new(name,mesh)
    bpy.context.scene.collection.objects.link(obj)
    obj.hide_render = True
    actual = collision_record(obj)
    require(all(abs(actual['bounds_cm'][side][i]-box[side][i]) < 1e-5
                for side in ('min','max') for i in range(3)),'UBX follows only its real wood part AABB '+name)
    convex_error = max((vertex.co-face.center).dot(face.normal)
                       for face in source.data.polygons for vertex in source.data.vertices)
    require(convex_error < .01,'Convex construction face-plane roundoff below 0.01cm '+source.name+' error_cm='+str(convex_error))
    tree = BVHTree.FromObject(source,bpy.context.evaluated_depsgraph_get())
    inverse = source.matrix_world.inverted()
    distances = []
    for corner in vertices:
        location,normal,index,distance = tree.find_nearest(inverse @ Vector(corner))
        require(location is not None and math.isfinite(distance),'Actual UBX corner distance '+name)
        distances.append(distance)
    gap_bound = math.sqrt(3)*.4
    if source['source_primitive'] == 'CYLINDER14':
        axis = list(source['grain_axis']).index(1)
        cross = [actual['dimensions_cm'][i]/2 for i in range(3) if i != axis]
        inner_radius = min(cross)-.4
        require(inner_radius > 0,'Positive conservative inner rod radius '+name)
        gap_bound = math.hypot(math.hypot(*cross)-inner_radius,.4)
    require(max(distances) <= gap_bound+.001,'Measured UBX corners below conservative construction bound '+name)
    actual.update(source_part=source.name,source_primitive=source['source_primitive'],visual_bevel_cm=.4,
                  max_measured_box_corner_gap_cm=max(distances),conservative_outside_gap_bound_cm=gap_bound+.001,
                  face_plane_roundoff_cm=convex_error,
                  maximum_gap_bound_basis='Source .4cm bevel construction contains the .4cm inset box, or the inset inscribed cylinder for each regular 14-sided rod. Furthest AABB corner distance to that contained solid bounds all box points; add .001cm numeric margin. Measured nearest-surface corners also recorded.',
                  approximation='Unbeveled narrow AABB fills rounded/beveled corners and circular-rod AABB corners; no enclosing prop-wide air-wall.')
    return obj,actual


def visual_signature(mesh):
    mesh.calc_loop_triangles()
    return dict(vertices=[[float(x).hex() for x in vertex.co] for vertex in mesh.vertices],
                triangles=[list(triangle.vertices) for triangle in mesh.loop_triangles],
                uv0=[[float(x).hex() for x in entry.uv] for entry in mesh.uv_layers[0].data],
                corner_normals=[[float(x).hex() for x in normal.vector] for normal in mesh.corner_normals])


def join_prop(name,parts,contacts,ground_names):
    bpy.context.view_layer.update()
    rows = {label:dict(geometry=record(obj),grain_axis_local=list(obj['grain_axis'])) for label,obj in parts.items()}
    joins = []
    for left,right,point in contacts:
        contact(parts,left,right,point,joins)
    ground = []
    for label in ground_names:
        box = bounds(parts[label])
        require(abs(box['min'][2]) < 1e-5, 'Actual foot meets Z0 '+label)
        ground.append(dict(part=label,bounds_cm=box,future_collision='Individual real foot/leg box only; not an enclosing air-wall'))
    collisions = []
    collision_rows = []
    for index,source in enumerate(parts.values()):
        collision,collision_row = make_collision('UBX_'+name+'_'+str(index).zfill(2),source)
        collisions.append(collision)
        collision_rows.append(collision_row)
    bpy.ops.object.select_all(action='DESELECT')
    for obj in parts.values():
        obj.select_set(True)
    bpy.context.view_layer.objects.active = next(iter(parts.values()))
    bpy.ops.object.join()
    obj = bpy.context.object
    obj.name,obj.data.name = name,name
    bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
    require(all(abs(v) < 1e-7 for v in obj.location) and all(abs(v-1) < 1e-7 for v in obj.scale),
            'Applied identity transforms '+name)
    result = record(obj)
    require(abs(result['bounds_cm']['min'][2]) < 1e-5, 'Joined prop ground Z0 '+name)
    return obj,dict(geometry=result,wood_parts=rows,actual_contact_tests=joins,ground_parts=ground,
                    construction='Separate closed beveled solid wood pieces with verified interpenetrating joins; not a Boolean union',
                    grain='Each piece UV V follows projected long axis; end faces planar; 50cm per texture tile',
                    collision_exported=True,collision=dict(boxes=collision_rows,box_count=len(collision_rows),
                    coordinate_space='Applied identity Blender world centimeters; same origin as visual mesh')),collisions


def png(path):
    raw = path.read_bytes()
    require(raw[:8] == b'\x89PNG\r\n\x1a\n','PNG signature '+path.name)
    cursor = 8
    dimensions = None
    while cursor < len(raw):
        count,kind = struct.unpack_from('>I4s',raw,cursor)
        require(cursor+12+count <= len(raw),'Bounded PNG chunk '+path.name)
        payload = raw[cursor+8:cursor+8+count]
        require(zlib.crc32(kind+payload)&0xffffffff == struct.unpack_from('>I',raw,cursor+8+count)[0],
                'PNG CRC '+path.name)
        if kind == b'IHDR':
            dimensions = struct.unpack_from('>II',payload)
        cursor += 12+count
        if kind == b'IEND':
            break
    require(cursor == len(raw) and kind == b'IEND' and dimensions == (1536,1024),'Exact PNG end/dimensions '+path.name)
    return dict(path=str(path),bytes=len(raw),sha256=sha(path),dimensions=dimensions,tail_bytes=0)


def aim(obj,target):
    obj.rotation_euler = (Vector(target)-obj.location).to_track_quat('-Z','Y').to_euler()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out',required=True,type=Path)
    out = parser.parse_args(sys.argv[sys.argv.index('--')+1:]).out
    require(out.is_absolute() and out.parent.resolve() == HERE and not out.exists()
            and re.fullmatch(r'Source-Run[1-9][0-9]*',out.name),'Absent local Source-RunN only')
    require(bpy.app.version[:2] == (4,5),'Actual Blender 4.5 runtime')
    baseline_path = HERE/'Source-Run2'/'SOURCE.json'
    require(sha(baseline_path) == '810978AC7950DED4528D9DB332BD87110F2C7981BCCE1B1FD5B283DF3E9FA6E4',
            'Exact prior Run2 visual source report')
    baseline = json.loads(baseline_path.read_text(encoding='utf-8'))
    baseline_fbx = {}
    for name,row in baseline['props'].items():
        path = Path(row['fbx']['path'])
        require(path.resolve().parent == baseline_path.parent and sha(path) == row['fbx']['sha256'],
                'Exact local Run2 visual FBX '+name)
        baseline_fbx[name] = dict(path=path,sha256=row['fbx']['sha256'])
    run3_path = HERE/'Source-Run3'/'SOURCE.json'
    require(sha(run3_path) == '4CBB47F3E3567187204AF2C64D4B7BDE886EF62FD3215A3A0AAC82A4AF68C2BE',
            'Exact preserved Run3 collision source report')
    run3 = json.loads(run3_path.read_text(encoding='utf-8'))
    engine_source = Path('C:/Program Files/Epic Games/UE_5.8/Engine/Source/Editor/UnrealEd/Private/ImportUtils/StaticMeshImportUtils.cpp')
    require(sha(engine_source) == '0B8E8C4BEAD9E6845BC4EA167C0EF396FF62B39F9DA5478A6CAE2B7167F31143',
            'Exact locally reviewed UE box-plane algorithm source')
    run3_order = {}
    for name,row in run3['props'].items():
        path = Path(row['fbx']['path'])
        require(path.resolve().parent == run3_path.parent and sha(path) == row['fbx']['sha256'],
                'Exact preserved Run3 FBX '+name)
        run3_order[name] = fbx_box_order(path,[box['name'] for box in row['collision']['boxes']],False)
    print('Reproduced UE5.8 raw Run3 triangle-plane ordering failure for all 27 UBX boxes.')
    code = Path(__file__).resolve()
    author_hash = sha(code)
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    scene = bpy.context.scene
    scene.unit_settings.system,scene.unit_settings.scale_length = 'METRIC',.01
    scene.unit_settings.length_unit = 'CENTIMETERS'
    material = bpy.data.materials.new('Wood')
    material.use_nodes = True
    bsdf = material.node_tree.nodes.get('Principled BSDF')
    bsdf.inputs['Base Color'].default_value = (.16,.105,.06,1)
    bsdf.inputs['Roughness'].default_value = .78

    rack = {}
    def add(parts,name,center,size,axis,cylinder=False):
        obj = part(name,center,size,axis,material,cylinder)
        obj['grain_axis'] = axis
        parts[name] = obj
    rack_contacts = []
    for side,x in (('L',-73),('R',73)):
        add(rack,'Foot'+side,(x,0,3),(14,55,6),(0,1,0))
        add(rack,'Post'+side,(x,0,91),(7,7,174),(0,0,1))
        rack_contacts.append(('Foot'+side,'Post'+side,(x,0,5)))
    add(rack,'TopRail',(0,0,180),(180,9,10),(1,0,0))
    add(rack,'LowerRail',(0,0,42),(160,6,7),(1,0,0))
    for side,x in (('L',-73),('R',73)):
        rack_contacts.extend([('Post'+side,'TopRail',(x,0,176.5)),('Post'+side,'LowerRail',(x,0,42))])
    for i,(x,bottom) in enumerate(zip((-48,-16,16,48),(45,56,38,52))):
        add(rack,'Peg'+str(i),(x,-7,178),(2.8,2.8,18),(0,1,0),True)
        add(rack,'Rod'+str(i),(x,-11.5,(178+bottom)/2),(1.8,1.8,178-bottom),(0,0,1),True)
        rack_contacts.extend([('TopRail','Peg'+str(i),(x,0,178)),('Peg'+str(i),'Rod'+str(i),(x,-11.5,177.5))])
    rack_obj,rack_report,rack_collision = join_prop('SM_DY_OperatorRodRack',rack,rack_contacts,['FootL','FootR'])

    bench = {}
    contacts = []
    for side,y in (('Front',-11.3),('Back',11.3)):
        add(bench,'Seat'+side,(0,y,42.5),(180,22.4,5),(1,0,0))
    for xside,x in (('L',-74),('R',74)):
        for yside,y in (('Front',-15),('Back',15)):
            leg = 'Leg'+xside+yside
            add(bench,leg,(x,y,21),(6,6,42),(0,0,1))
            contacts.append((leg,'Seat'+yside,(x,y,41)))
    for side,y in (('Front',-17),('Back',17)):
        add(bench,'Apron'+side,(0,y,36),(148,3,10),(1,0,0))
        contacts.append(('Apron'+side,'Seat'+side,(0,y,40.5)))
        for xside,x in (('L',-73),('R',73)):
            contacts.append(('Apron'+side,'Leg'+xside+side,(x,(-16 if side=='Front' else 16),36)))
    for side,x in (('L',-74),('R',74)):
        add(bench,'Apron'+side,(x,0,36),(3,30,10),(0,1,0))
        add(bench,'EndStretcher'+side,(x,0,14),(4,30,5),(0,1,0))
        for yside,y in (('Front',-14),('Back',14)):
            contacts.extend([('Apron'+side,'Leg'+side+yside,(x,y,36)),
                             ('EndStretcher'+side,'Leg'+side+yside,(x,y,14))])
    add(bench,'LongStretcher',(0,0,14),(148,4,5),(1,0,0))
    contacts.extend([('LongStretcher','EndStretcherL',(-73,0,14)),('LongStretcher','EndStretcherR',(73,0,14))])
    bench_obj,bench_report,bench_collision = join_prop('SM_DY_BackstageBench',bench,contacts,
                                      ['LegLFront','LegLBack','LegRFront','LegRBack'])
    props = [(rack_obj,rack_report,rack_collision),(bench_obj,bench_report,bench_collision)]
    for obj,report,collisions in props:
        old = baseline['props'][obj.name]
        require(all(json.loads(json.dumps(report[field])) == old[field]
                    for field in ('geometry','wood_parts','actual_contact_tests','ground_parts','construction','grain')),
                'All prior visual source geometry/UV density/contact records exactly unchanged '+obj.name)
        require(json.loads(json.dumps(report['collision'])) == run3['props'][obj.name]['collision'],
                'All Run3 collision bounds/centers/dimensions and corner geometry unchanged '+obj.name)
    out.mkdir()
    for obj,report,collisions in props:
        before = set(bpy.data.objects)
        bpy.ops.import_scene.fbx(filepath=str(baseline_fbx[obj.name]['path']),use_anim=False)
        old_imported = [o for o in bpy.data.objects if o not in before]
        require(len(old_imported) == 1 and old_imported[0].type == 'MESH','Run2 read contains only its visual mesh '+obj.name)
        old_signature = visual_signature(old_imported[0].data)
        bpy.data.objects.remove(old_imported[0],do_unlink=True)
        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)
        for collision in collisions:
            collision.select_set(True)
        bpy.context.view_layer.objects.active = obj
        path = out/(obj.name+'.fbx')
        bpy.ops.export_scene.fbx(filepath=str(path),check_existing=True,use_selection=True,object_types={'MESH'},
            global_scale=1,apply_unit_scale=True,apply_scale_options='FBX_SCALE_UNITS',axis_forward='-Y',axis_up='Z',
            bake_space_transform=False,use_mesh_modifiers=False,mesh_smooth_type='FACE',use_tspace=False,
            use_triangles=True,add_leaf_bones=False,bake_anim=False,path_mode='AUTO',embed_textures=False)
        order_check = fbx_box_order(path,[row['name'] for row in report['collision']['boxes']],True)
        before = set(bpy.data.objects)
        bpy.ops.import_scene.fbx(filepath=str(path),use_anim=False)
        imported = [o for o in bpy.data.objects if o not in before]
        visuals = [entry for entry in imported if not entry.name.startswith('UBX_')]
        boxes = [entry for entry in imported if entry.name.startswith('UBX_')]
        require(len(imported) == len(collisions)+1 and len(visuals) == 1 and len(boxes) == len(collisions)
                and all(entry.type == 'MESH' for entry in imported),'FBX fresh read one visual plus all narrow UBX '+obj.name)
        actual = record(visuals[0])
        require(actual['triangles'] == report['geometry']['triangles'] and
                all(abs(actual['bounds_cm'][s][i]-report['geometry']['bounds_cm'][s][i]) < 1e-4
                    for s in ('min','max') for i in range(3)),'FBX actual counts and ground/bounds match '+obj.name)
        require(all(abs(v)<1e-6 for v in visuals[0].location) and all(abs(v-1)<1e-6 for v in visuals[0].scale),
                'FBX actual identity translation/scale '+obj.name)
        require(visual_signature(visuals[0].data) == old_signature,
                'Fresh FBX visual position/topology/UV0/corner-normal floats exactly equal Run2 '+obj.name)
        read_boxes = []
        expected = {row['name']:row for row in report['collision']['boxes']}
        require({box.name.split('.')[0] for box in boxes} == set(expected),'Exact FBX UBX name set '+obj.name)
        for box in boxes:
            row = collision_record(box)
            reference = expected[box.name.split('.')[0]]
            require(all(abs(row['bounds_cm'][side][i]-reference['bounds_cm'][side][i]) < 1e-4
                        for side in ('min','max') for i in range(3)),'FBX UBX actual bounds match '+box.name)
            read_boxes.append(row)
        report['fbx'] = dict(path=str(path),bytes=path.stat().st_size,sha256=sha(path),fresh_read=actual,
                            fresh_read_collision_boxes=read_boxes,visual_bitwise_signature_equal_Run2=True,
                            raw_fbx_ue_box_plane_order=order_check,
                            baseline_visual_fbx_sha256=baseline_fbx[obj.name]['sha256'])
        for entry in imported:
            bpy.data.objects.remove(entry,do_unlink=True)

    rack_obj.location = (-112,20,0)
    bench_obj.location = (112,-24,0)
    scene.render.engine = 'CYCLES'
    scene.cycles.device,scene.cycles.samples,scene.cycles.use_denoising = 'CPU',48,True
    scene.render.resolution_x,scene.render.resolution_y,scene.render.resolution_percentage = 1536,1024,100
    scene.render.image_settings.file_format,scene.render.image_settings.color_mode = 'PNG','RGB'
    scene.view_settings.view_transform = 'AgX'
    scene.world.use_nodes = True
    scene.world.node_tree.nodes['Background'].inputs['Color'].default_value = (.06,.06,.06,1)
    scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value = .45
    for name,location,power,size in (('QA_Key',(100,-300,450),1800000,300),
                                    ('QA_Fill',(-360,-80,200),850000,350),('QA_Rim',(80,300,330),1500000,250)):
        data = bpy.data.lights.new(name,'AREA')
        data.energy,data.shape,data.size = power,'DISK',size
        light = bpy.data.objects.new(name,data)
        scene.collection.objects.link(light)
        light.location = location
        aim(light,(0,0,80))
    data = bpy.data.cameras.new('QA_Camera')
    data.type,data.ortho_scale,data.clip_end = 'ORTHO',480,3000
    camera = bpy.data.objects.new('QA_Camera',data)
    scene.collection.objects.link(camera)
    scene.camera = camera
    previews = []
    for name,location in (('01_Front',(0,-900,170)),('02_Oblique',(420,-800,360))):
        camera.location = location
        aim(camera,(0,0,90))
        path = out/(name+'.png')
        scene.render.filepath = str(path)
        bpy.ops.render.render(write_still=True)
        previews.append(dict(camera=name,location_cm=location,target_cm=[0,0,90],preview_only=True,png=png(path)))
    require(sha(code) == author_hash,'Author source unchanged during run')
    require(sha(baseline_path) == '810978AC7950DED4528D9DB332BD87110F2C7981BCCE1B1FD5B283DF3E9FA6E4'
            and all(sha(row['path']) == row['sha256'] for row in baseline_fbx.values()),'All Run2 evidence unchanged')
    require(sha(run3_path) == '4CBB47F3E3567187204AF2C64D4B7BDE886EF62FD3215A3A0AAC82A4AF68C2BE'
            and all(sha(Path(row['fbx']['path'])) == row['fbx']['sha256'] for row in run3['props'].values()),
            'All Run3 evidence unchanged')
    report = dict(status='PASS-LOCAL-STAGE-PROPS-SOURCES-NATIVE-AND-ART-PENDING',blender_version=bpy.app.version_string,
        author_tool=dict(path=str(code),sha256=author_hash,source_utf8=code.read_text(encoding='utf-8')),
        source_units='Centimeters; Blender metric .01; applied source transforms; FBX_SCALE_UNITS',
        props={obj.name:row for obj,row,collisions in props},previews=previews,
        collision_box_count=sum(len(collisions) for obj,row,collisions in props),
        local_ue_box_algorithm=dict(source=str(engine_source),sha256=sha(engine_source),
            lines='MeshToPrimTolerance/AreEqual/AreParallel and AddBoxGeomFromTris plane loop',
            simulation_not_native_import=True,run3_failure_reproductions=run3_order,
            fix='Construct 12 UBX triangles with same-face triangle pairs adjacent before export, instead of allowing exporter quad triangulation order'),
        provenance='Author-designed backstage creative geometry with Codex assistance; no downloaded mesh/texture, paid resource, invented upstream author or historical reconstruction claim',
        material='One Wood slot, simple neutral preview only; no textures; existing project wood material may be evaluated in UE later',
        checks=CHECKS,check_count=len(CHECKS),
        scope=dict(D_writes=False,UE=False,new_gameplay=False,interactive_staff_changed=False,
                   downloads=False,paid_resources=False,native_verified=False,art_accepted=False))
    (out/'SOURCE.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    (out/'README.md').write_text('# Two backstage woodwork source candidates\n\n'
        'Operator rod rack and waiting/rehearsal bench only; the four hanging rods are passive joined source geometry, not the interactive Staff. '
        'Creative procedural modeling with Codex assistance; no upstream mesh/texture or historical reconstruction claim.\n\n'
        'Each FBX has one visual mesh with UV0/Wood preview slot and 14 rack or 13 bench unmaterialed UV-less UBX boxes. Closed wooden component shells meet through verified common interior points, not a Boolean solid union. '
        'Wood UVs use physical 50cm tiling, with V along the projected long direction and planar end faces. '
        'The preview material is not final wood texture. Each real wooden part has its own UBX AABB, never one enclosing prop-wide air-wall. '
        'Boxes approximate 0.4cm beveled and circular corners; actual convex-source maximum corner gaps are reported. '
        'UBX triangles are explicitly paired per planar face to satisfy this local UE5.8 AddBoxGeomFromTris implementation. '
        'The raw physical Run3 FBX failure is reproduced and raw new FBX triangle-order simulation passes; this is not native UE import acceptance. '
        'No collision is rendered. Prior Run2 visual positions/topology/UV0/corner-normal float signatures match exactly after fresh FBX reads.\n\n'
        'Two studio PNGs are local shape reviews, not UE gameplay, final-lighting, shadow or performance acceptance. '
        'SOURCE.json includes actual component/source/FBX counts, bounds, grounding, contact and source checks. '
        'No map, old fixture, old asset, gameplay code or D-drive file is changed.\n',encoding='utf-8')
    print(json.dumps(dict(status=report['status'],check_count=len(CHECKS),
        collision_boxes=report['collision_box_count'],props={obj.name:row['geometry'] for obj,row,collisions in props}),indent=2))


if __name__ == '__main__':
    main()
