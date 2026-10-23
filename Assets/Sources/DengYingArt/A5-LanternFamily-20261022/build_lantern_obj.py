"""Author a unit-bounded, three-slot octagonal paper lantern using only stdlib."""
from collections import Counter
import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OBJ = ROOT / "SM_DY_LanternFamily_Unit100_v01.obj"
MTL = ROOT / "SM_DY_LanternFamily_Unit100_v01.mtl"
MATERIALS = ("Paper", "Wood", "Brass")
FACES = {name: [] for name in MATERIALS}
UV_QUAD = ((0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0))


def sub(a, b):
    return tuple(x - y for x, y in zip(a, b))


def cross(a, b):
    return (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0])


def dot(a, b):
    return sum(x*y for x, y in zip(a, b))


def unit(v):
    length = math.sqrt(dot(v, v))
    assert length > 1e-10, "Degenerate face"
    return tuple(x / length for x in v)


def triangle(material, part, points, uvs, outward):
    points, uvs = list(points), list(uvs)
    normal = unit(cross(sub(points[1], points[0]), sub(points[2], points[0])))
    if dot(normal, outward) < 0:
        points[1], points[2] = points[2], points[1]
        uvs[1], uvs[2] = uvs[2], uvs[1]
        normal = tuple(-x for x in normal)
    assert dot(normal, outward) > 0, "Face normal points inward"
    FACES[material].append((part, points, uvs, normal))


def quad(material, part, points, outward, uvs=UV_QUAD):
    for ids in ((0, 1, 2), (0, 2, 3)):
        triangle(material, part, [points[i] for i in ids], [uvs[i] for i in ids], outward)


def point(radius, z, i, segments=8, center=(0.0, 0.0)):
    angle = 2.0 * math.pi * i / segments
    return (center[0] + radius*math.cos(angle), center[1] + radius*math.sin(angle), z)


def frustum(material, part, r0, r1, z0, z1, segments=8, center=(0.0, 0.0), caps=(True, True)):
    assert r0 > 0 and r1 > 0 and z1 > z0
    for i in range(segments):
        angle = 2.0*math.pi*(i+0.5)/segments
        side_normal = (math.cos(angle), math.sin(angle), (r0-r1)/(z1-z0))
        quad(material, part,
             [point(r0,z0,i,segments,center), point(r0,z0,i+1,segments,center),
              point(r1,z1,i+1,segments,center), point(r1,z1,i,segments,center)], side_normal)
        for radius, z, normal, enabled in ((r0,z0,(0,0,-1),caps[0]), (r1,z1,(0,0,1),caps[1])):
            if not enabled:
                continue
            a, b = point(radius,z,i,segments,center), point(radius,z,i+1,segments,center)
            triangle(material, part, [(center[0],center[1],z),a,b],
                     [(0.5,0.5),(0.5+0.5*math.cos(2*math.pi*i/segments),0.5+0.5*math.sin(2*math.pi*i/segments)),
                      (0.5+0.5*math.cos(2*math.pi*(i+1)/segments),0.5+0.5*math.sin(2*math.pi*(i+1)/segments))], normal)


def rim(part, z0, z1):
    for i in range(8):
        angle = 2.0*math.pi*(i+0.5)/8
        radial = (math.cos(angle), math.sin(angle), 0.0)
        quad("Wood", part, [point(50,z0,i),point(50,z0,i+1),point(50,z1,i+1),point(50,z1,i)], radial)
        quad("Wood", part, [point(44,z0,i),point(44,z0,i+1),point(44,z1,i+1),point(44,z1,i)],
             tuple(-v for v in radial))
        quad("Wood", part, [point(44,z1,i),point(50,z1,i),point(50,z1,i+1),point(44,z1,i+1)], (0,0,1))
        quad("Wood", part, [point(44,z0,i),point(50,z0,i),point(50,z0,i+1),point(44,z0,i+1)], (0,0,-1))


def hanging_loop():
    # A small vertical loop closes at z42 and reaches z50 without a floating bead.
    major, minor, center_z = 3.3, 0.7, 46.0
    def torus(a, b):
        theta, phi = 2*math.pi*a/16, 2*math.pi*b/8
        ring_radius = major + minor*math.cos(phi)
        return (ring_radius*math.cos(theta), minor*math.sin(phi), center_z+ring_radius*math.sin(theta))
    for a in range(16):
        for b in range(8):
            theta, phi = 2*math.pi*(a+0.5)/16, 2*math.pi*(b+0.5)/8
            normal = (math.cos(phi)*math.cos(theta), math.sin(phi), math.cos(phi)*math.sin(theta))
            quad("Brass", "Brass_HangingLoop", [torus(a,b),torus(a+1,b),torus(a+1,b+1),torus(a,b+1)], normal)


def build():
    # Eight independent paper islands use one circumferential 0..1 strip, matching the existing eight-rib texture.
    for i in range(8):
        angle = 2*math.pi*(i+0.5)/8
        quad("Paper", "Paper_Panels", [point(45,-34,i),point(45,-34,i+1),point(45,34,i+1),point(45,34,i)],
             (math.cos(angle), math.sin(angle), 0),
             ((i/8,0),((i+1)/8,0),((i+1)/8,1),(i/8,1)))
    rim("Wood_UpperRing", 32, 36)
    rim("Wood_LowerRing", -36, -32)
    frustum("Wood", "Wood_UpperCap", 45, 16, 36, 42, caps=(False, True))
    frustum("Wood", "Wood_LowerCap", 14, 45, -42, -36, caps=(True, False))
    for i in range(8):
        angle = 2*math.pi*i/8
        frustum("Wood", "Wood_BambooRibs", 0.7, 0.7, -34, 34, 8,
                (45*math.cos(angle),45*math.sin(angle)))
    frustum("Brass", "Brass_LoopSeat", 4, 4, 42, 43)
    hanging_loop()
    frustum("Brass", "Brass_LowerFinial", 2, 5, -50, -42)


def write_obj():
    lines = ["# Units: centimeter; Z up; centered origin; intended UE bounds [-50,+50] on every axis.",
             "# Single mesh with Paper / Wood / Brass slots; use the imported slot names, not numeric order.",
             "mtllib " + MTL.name, "o SM_DY_LanternFamily_Unit100_v01", "s off"]
    # Separate corner records deliberately retain the eight flat paper faces and hard wood edges.
    index = 0
    for material in MATERIALS:
        lines.append("usemtl " + material)
        previous_part = None
        for part, points, uvs, normal in FACES[material]:
            if part != previous_part:
                lines.append("g " + part)
                previous_part = part
            for p in points:
                lines.append("v " + " ".join(f"{v:.9f}" for v in p))
            for uv in uvs:
                lines.append("vt " + " ".join(f"{v:.9f}" for v in uv))
            for _ in range(3):
                lines.append("vn " + " ".join(f"{v:.9f}" for v in normal))
            ids = [index+1,index+2,index+3]
            lines.append("f " + " ".join(f"{j}/{j}/{j}" for j in ids))
            index += 3
    OBJ.write_text("\n".join(lines)+"\n", encoding="utf-8")
    MTL.write_text(
        "# Preview colors only. UE assigns existing project materials by slot name. No emission.\n"
        "newmtl Paper\nKa 0 0 0\nKd 0.88 0.78 0.62\nKs 0.02 0.02 0.02\nNs 4\nillum 2\n\n"
        "newmtl Wood\nKa 0 0 0\nKd 0.176 0.129 0.094\nKs 0.04 0.04 0.04\nNs 12\nillum 2\n\n"
        "newmtl Brass\nKa 0 0 0\nKd 0.65 0.42 0.14\nKs 0.22 0.18 0.10\nNs 40\nillum 2\n",
        encoding="utf-8")


def check_written_obj():
    # Cold parsing checks the serialized file, rather than trusting only builder arrays.
    vertices, uvs, normals, triangles = [], [], [], []
    used, current_material = [], None
    object_count = 0
    for line in OBJ.read_text(encoding="utf-8").splitlines():
        words = line.split()
        if not words or words[0].startswith("#"):
            continue
        kind, values = words[0], words[1:]
        if kind == "o":
            object_count += 1
        elif kind == "v":
            vertices.append(tuple(map(float, values)))
        elif kind == "vt":
            uvs.append(tuple(map(float, values)))
        elif kind == "vn":
            normals.append(tuple(map(float, values)))
        elif kind == "usemtl":
            current_material = values[0]
            used.append(current_material)
        elif kind == "f":
            assert len(values) == 3 and current_material in MATERIALS
            refs = [tuple(map(int, item.split("/"))) for item in values]
            assert all(len(item)==3 for item in refs)
            triangles.append((current_material, refs))
    assert object_count == 1
    assert used == list(MATERIALS)
    assert len(vertices) == len(uvs) == len(normals) == len(triangles)*3
    assert all(math.isfinite(x) for rows in (vertices,uvs,normals) for row in rows for x in row)
    lo = [min(p[i] for p in vertices) for i in range(3)]
    hi = [max(p[i] for p in vertices) for i in range(3)]
    assert all(abs(value+50)<1e-8 for value in lo), lo
    assert all(abs(value-50)<1e-8 for value in hi), hi
    assert all(0 <= x <= 1 for uv in uvs for x in uv)
    assert all(abs(dot(n,n)-1)<1e-7 for n in normals)
    minimum_area, minimum_normal_dot = float("inf"), 1.0
    counts, paper_uv_ranges = Counter(), Counter()
    for material, refs in triangles:
        assert all(1 <= ref[k] <= len((vertices,uvs,normals)[k]) for ref in refs for k in range(3))
        ps = [vertices[ref[0]-1] for ref in refs]
        area_vector = cross(sub(ps[1],ps[0]),sub(ps[2],ps[0]))
        area = math.sqrt(dot(area_vector,area_vector))/2
        assert area > 1e-8
        normal = unit(area_vector)
        normal_dot = min(dot(normal,normals[ref[2]-1]) for ref in refs)
        assert normal_dot > 0.999999, (material,normal_dot)
        minimum_area = min(minimum_area,area)
        minimum_normal_dot = min(minimum_normal_dot,normal_dot)
        counts[material] += 1
        if material == "Paper":
            panel_uv = [uvs[ref[1]-1] for ref in refs]
            u_min, u_max = min(v[0] for v in panel_uv), max(v[0] for v in panel_uv)
            assert abs((u_max-u_min)-0.125) < 1e-9
            assert min(v[1] for v in panel_uv) == 0 and max(v[1] for v in panel_uv) == 1
            paper_uv_ranges[(u_min,u_max)] += 1
    assert paper_uv_ranges == Counter({(i/8,(i+1)/8):2 for i in range(8)})
    assert all(counts[name] > 0 for name in MATERIALS)
    assert counts["Paper"] == 16
    return dict(vertices=len(vertices), triangles=len(triangles), material_slots=list(MATERIALS),
                triangles_by_material=dict(counts), bounds_min=lo,bounds_max=hi,
                bounds_size=[hi[i]-lo[i] for i in range(3)],uv_count=len(uvs),normal_count=len(normals),
                minimum_triangle_area=minimum_area, minimum_normal_dot=minimum_normal_dot,
                single_object=True, finite=True, indices_valid=True, winding_matches_explicit_normals=True,
                paper_uv="8 independent islands; each spans U=1/8 and V=0..1; total U=0..1",
                paper_uv_range_counts={str(k):v for k,v in sorted(paper_uv_ranges.items())},
                internal_coplanar_cap_faces_removed=True)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def main():
    assert ROOT.name == "A5-LanternFamily-20261022", ROOT
    build()
    write_obj()
    checks = check_written_obj()
    report = dict(
        status="PASS-LOCAL-OBJ-SOURCE-SELF-CHECK",
        units="centimeter", axes="Z up; origin center; +X front", dimensions=[100,100,100],
        geometry="Octagonal paper body diameter90 z[-34,34]; eight solid thin bamboo ribs; two solid octagonal wood rings outer radius50; wood caps; small brass loop/finial to z+/-50.",
        material_semantics={"Paper":"Eight planar independent UV0 islands, each U=[i/8,(i+1)/8], V=0..1; total circumference U=0..1.",
                            "Wood":"Dark wooden rings/caps and eight bamboo ribs.",
                            "Brass":"Small hanging loop, seat and lower finial; no fire bead."},
        intended_usage="Replace only the original Sphere static_mesh at unchanged Actor Transform; root agent must check actual UE bounds, material slots and shadows first.",
        uv_limit="UV strip matches the existing eight-rib LanternPaper texture without shared-material changes. Native appearance still requires inspection.",
        native_import_status="NOT_RUN", runtime_art_status="NOT_VERIFIED",
        source_provenance="Original procedural geometry by Codex using Python standard library; no external resources or downloads.",
        visual_reference="Project A5 concept; flat paper, sparse opaque bamboo/wood, restrained brass; no invented narrative motif.",
        scope={"UE_changes":False,"map_changes":False,"actor_transform_changes":False,
               "downloads":False,"paid_services":False,"new_dependencies":False},
        checks=checks, files=[{"name":p.name,"bytes":p.stat().st_size,"sha256":sha(p)} for p in (Path(__file__),OBJ,MTL)])
    (ROOT/"SOURCE_MANIFEST.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"status":report["status"],"obj":str(OBJ),"checks":checks},ensure_ascii=False,indent=2))


if __name__ == "__main__":
    main()
