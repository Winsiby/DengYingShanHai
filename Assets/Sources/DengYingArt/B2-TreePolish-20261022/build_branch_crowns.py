"""B2 source candidate: two curved, tapered dead-branch crowns; stdlib only."""
from collections import Counter
import hashlib
import json
import math
from pathlib import Path
import random
import struct
import zlib

ROOT = Path(__file__).resolve().parent
SLOT = "MI_DY_TreeTrunk"
DIAGNOSTIC = Path("D:/灯影山海/Saved/Audit-2026-10-22-B2WallPolish/scene-before.json")


def add(a,b):
    return tuple(x+y for x,y in zip(a,b))


def sub(a,b):
    return tuple(x-y for x,y in zip(a,b))


def mul(a,k):
    return tuple(x*k for x in a)


def dot(a,b):
    return sum(x*y for x,y in zip(a,b))


def cross(a,b):
    return (a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0])


def length(a):
    return math.sqrt(dot(a,a))


def unit(a):
    size=length(a)
    assert size>1e-10
    return mul(a,1/size)


def curve(p,t):
    s=1-t
    return tuple(s*s*s*p[0][k]+3*s*s*t*p[1][k]+3*s*t*t*p[2][k]+t*t*t*p[3][k] for k in range(3))


def tangent(p,t):
    s=1-t
    return unit(tuple(3*s*s*(p[1][k]-p[0][k])+6*s*t*(p[2][k]-p[1][k])+3*t*t*(p[3][k]-p[2][k]) for k in range(3)))


def radius(branch,t):
    return branch["r1"]+(branch["r0"]-branch["r1"])*(1-t)**1.08


class Crown:
    def __init__(self,name,seed):
        self.name=name
        self.rng=random.Random(seed)
        self.vertices=[]
        self.faces=[]
        self.branches=[]
        self.parts=[]
        self.flat_cap_faces=set()

    def face(self,ids,uv,expected):
        p=[self.vertices[i] for i in ids]
        normal=cross(sub(p[1],p[0]),sub(p[2],p[0]))
        assert length(normal)>1e-9
        if dot(normal,expected)<0:
            ids=(ids[0],ids[2],ids[1])
            uv=(uv[0],uv[2],uv[1])
        self.faces.append((ids,uv))

    def vertex(self,p):
        self.vertices.append(tuple(p))
        return len(self.vertices)-1

    def branch(self,name,controls,r0,r1,steps,sides,parent=None,at=None):
        branch=dict(name=name,controls=controls,r0=r0,r1=r1,steps=steps,sides=sides,parent=parent,at=at)
        if parent is not None:
            trunk=self.branches[parent]
            assert length(sub(controls[0],curve(trunk["controls"],at)))<1e-8
            assert r0 < radius(trunk,at)*0.8
        branch["first_vertex"]=len(self.vertices)
        first_face=len(self.faces)
        self.branches.append(branch)
        previous_frame=None
        rings=[]
        centers=[]
        tangents=[]
        for j in range(steps+1):
            t=j/steps
            c=curve(controls,t)
            axis=tangent(controls,t)
            if previous_frame is None:
                reference=(0,1,0) if abs(axis[1])<0.85 else (1,0,0)
                frame=unit(cross(reference,axis))
            else:
                frame=unit(sub(previous_frame,mul(axis,dot(previous_frame,axis))))
            other=unit(cross(axis,frame))
            previous_frame=frame
            ring=[]
            for k in range(sides):
                theta=2*math.pi*k/sides
                radial=add(mul(frame,math.cos(theta)),mul(other,math.sin(theta)))
                # Slight non-circular bark section; no noisy spikes or alpha foliage.
                r=radius(branch,t)*(1+0.025*math.sin(3*theta+0.8*t))
                ring.append(self.vertex(add(c,mul(radial,r))))
            rings.append(ring); centers.append(c); tangents.append(axis)
        for j in range(steps):
            c=mul(add(centers[j],centers[j+1]),0.5)
            for k in range(sides):
                k1=(k+1)%sides
                a,b,c1,d=rings[j][k],rings[j][k1],rings[j+1][k1],rings[j+1][k]
                radial=sub(mul(add(self.vertices[a],self.vertices[c1]),0.5),c)
                u0,u1=k/sides,(k+1)/sides
                v0,v1=j/steps,(j+1)/steps
                self.face((a,b,c1),((u0,v0),(u1,v0),(u1,v1)),radial)
                self.face((a,c1,d),((u0,v0),(u1,v1),(u0,v1)),radial)
        # Buried closed base. All child bases start inside their parent sweep.
        base=self.vertex(centers[0])
        base_start_face=len(self.faces)
        for k in range(sides):
            k1=(k+1)%sides
            self.face((base,rings[0][k1],rings[0][k]),((0.5,0),(k1/sides,0),(k/sides,0)),mul(tangents[0],-1))
        self.flat_cap_faces.update(range(base_start_face,len(self.faces)))
        # Blunt round tips instead of long needle cones.
        c=centers[-1]; axis=tangents[-1]
        round_center=add(c,mul(axis,r1*0.65))
        final_ring=[]
        for old in rings[-1]:
            radial=sub(self.vertices[old],c)
            final_ring.append(self.vertex(add(round_center,mul(radial,0.65))))
        for k in range(sides):
            k1=(k+1)%sides
            a,b,c1,d=rings[-1][k],rings[-1][k1],final_ring[k1],final_ring[k]
            out=sub(mul(add(self.vertices[a],self.vertices[c1]),0.5),c)
            self.face((a,b,c1),((k/sides,0.97),(k1/sides,0.97),(k1/sides,0.99)),out)
            self.face((a,c1,d),((k/sides,0.97),(k1/sides,0.99),(k/sides,0.99)),out)
        apex=self.vertex(add(c,mul(axis,r1)))
        for k in range(sides):
            k1=(k+1)%sides
            self.face((final_ring[k],final_ring[k1],apex),((k/sides,0.99),(k1/sides,0.99),(0.5,1)),axis)
        branch["vertex_count"]=len(self.vertices)-branch["first_vertex"]
        branch["face_count"]=len(self.faces)-first_face
        self.parts.append((name,first_face,len(self.faces)))
        return len(self.branches)-1

    def child(self,parent,at,name,end,r1,steps,sides,bend=1):
        trunk=self.branches[parent]
        start=curve(trunk["controls"],at)
        direction=unit(sub(end,start))
        initial=tangent(trunk["controls"],at)
        distance=length(sub(end,start))
        c1=add(start,add(mul(initial,distance*0.30),mul(direction,distance*0.12)))
        c2=add(sub(end,mul(direction,distance*0.23)),(bend*distance*0.035,-bend*distance*0.06,distance*0.16))
        return self.branch(name,[start,c1,c2,end],radius(trunk,at)*0.70,r1,steps,sides,parent,at)

    def normalize(self):
        lo=[min(p[i] for p in self.vertices) for i in range(3)]
        hi=[max(p[i] for p in self.vertices) for i in range(3)]
        center=[(hi[i]+lo[i])/2 for i in range(3)]
        scale=[100/(hi[i]-lo[i]) for i in range(3)]
        self.vertices=[tuple((p[i]-center[i])*scale[i] for i in range(3)) for p in self.vertices]
        self.source_center=center; self.source_scale=scale
        self.root_base=tuple((self.branches[0]["controls"][0][i]-center[i])*scale[i] for i in range(3))
        assert math.hypot(self.root_base[0],self.root_base[1])<10, self.root_base

    def normals(self):
        rows=[(0,0,0) for _ in self.vertices]
        for ids,_ in self.faces:
            a,b,c=(self.vertices[i] for i in ids)
            normal=cross(sub(b,a),sub(c,a))
            for i in ids:
                rows[i]=add(rows[i],normal)
        return [unit(n) for n in rows]

    def export(self):
        self.normalize()
        normals=self.normals()
        normal_overrides={}
        for f in sorted(self.flat_cap_faces):
            ids=self.faces[f][0]
            a,b,c=(self.vertices[i] for i in ids)
            normal_overrides[f]=len(normals)+1
            normals.append(unit(cross(sub(b,a),sub(c,a))))
        obj=ROOT/(self.name+".obj")
        mtl=ROOT/(self.name+".mtl")
        lines=["# centimeters; Z up; origin at normalized bounds center; bounds exactly 100cm cubed.",
               "# One StaticMesh object. Closed curved branch sweeps overlap at verified roots; junctions are not Boolean-welded.",
               "mtllib "+mtl.name,"o "+self.name,"usemtl "+SLOT,"s 1"]
        lines.extend("v "+" ".join(f"{v:.9f}" for v in p) for p in self.vertices)
        lines.extend("vn "+" ".join(f"{v:.9f}" for v in n) for n in normals)
        for _,uvs in self.faces:
            for uv in uvs:
                lines.append("vt "+" ".join(f"{v:.9f}" for v in uv))
        part_at={a:name for name,a,b in self.parts}
        for f,(ids,_) in enumerate(self.faces):
            if f in part_at:
                lines.append("g "+part_at[f])
            lines.append("f "+" ".join(f"{vi+1}/{f*3+k+1}/{normal_overrides.get(f,vi+1)}" for k,vi in enumerate(ids)))
        obj.write_text("\n".join(lines)+"\n",encoding="utf-8")
        mtl.write_text("newmtl "+SLOT+"\nKa 0 0 0\nKd 0.176 0.129 0.094\nKs 0.02 0.02 0.02\nNs 6\nillum 2\n",encoding="utf-8")
        check=cold_check(obj,len(self.branches))
        graph=[]
        for i,b in enumerate(self.branches):
            samples=[curve(b["controls"],t/20) for t in range(21)]
            arc=sum(length(sub(samples[j+1],samples[j])) for j in range(20))
            chord=length(sub(samples[-1],samples[0]))
            graph.append(dict(id=i,name=b["name"],parent=b["parent"],attachment_t=b["at"],
                              radius_start=b["r0"],radius_tip=b["r1"],arc_to_chord=arc/chord))
        assert all(b["parent"] is None if i==0 else b["parent"]<i for i,b in enumerate(self.branches))
        assert sum(g["arc_to_chord"]>1.02 for g in graph)>=len(graph)*0.7
        preview=ROOT/(self.name+"_ortho.png")
        render_preview(self.vertices,self.faces,preview)
        return dict(obj=str(obj),mtl=str(mtl),preview=str(preview),checks=check,
                    root_base_center_cm=self.root_base,source_normalization=dict(center=self.source_center,scale=self.source_scale),
                    branch_graph=graph,logical_attachment_tree_connected=True,
                    junction_limit="Each branch is a closed curved sweep with its base inside its parent. Physical union connected; intersection shells are not Boolean-welded.",
                    files=[dict(name=p.name,bytes=p.stat().st_size,sha256=sha(p)) for p in (obj,mtl,preview)])


def cold_check(path,branch_count):
    v,vt,vn,faces=[],[],[],[]
    objects=[]; materials=[]; groups=[]
    for line in path.read_text(encoding="utf-8").splitlines():
        w=line.split()
        if not w or w[0].startswith("#"): continue
        if w[0]=="v": v.append(tuple(map(float,w[1:])))
        elif w[0]=="vt": vt.append(tuple(map(float,w[1:])))
        elif w[0]=="vn": vn.append(tuple(map(float,w[1:])))
        elif w[0]=="o": objects.append(w[1])
        elif w[0]=="usemtl": materials.append(w[1])
        elif w[0]=="g": groups.append(w[1])
        elif w[0]=="f": faces.append([tuple(map(int,t.split("/"))) for t in w[1:]])
    assert len(objects)==1 and materials==[SLOT]
    assert len(groups)==branch_count and len(faces)<4000
    assert all(math.isfinite(x) for rows in (v,vt,vn) for p in rows for x in p)
    lo=[min(p[i] for p in v) for i in range(3)]; hi=[max(p[i] for p in v) for i in range(3)]
    assert all(abs(x+50)<1e-8 for x in lo) and all(abs(x-50)<1e-8 for x in hi)
    edges=Counter(); areas=[]; normal_dots=[]
    for f in faces:
        assert len(f)==3
        assert all(1<=r[k]<=len((v,vt,vn)[k]) for r in f for k in range(3))
        a,b,c=[v[r[0]-1] for r in f]
        n=cross(sub(b,a),sub(c,a)); area=length(n)/2
        assert area>1e-8
        areas.append(area)
        for r in f:
            assert abs(length(vn[r[2]-1])-1)<1e-7
            normal_dots.append(dot(unit(n),vn[r[2]-1]))
        for j in range(3):
            edges[tuple(sorted((f[j][0],f[(j+1)%3][0])))] += 1
    assert all(n==2 for n in edges.values()), "Every curved branch shell must be closed"
    assert min(normal_dots)>0.05
    assert all(0<=x<=1 for uv in vt for x in uv)
    return dict(vertices=len(v),triangles=len(faces),material_slots=materials,
                bounds_min=lo,bounds_max=hi,bounds_size=[hi[i]-lo[i] for i in range(3)],
                normals=len(vn),uvs=len(vt),finite=True,indices_valid=True,
                minimum_triangle_area=min(areas),minimum_corner_normal_dot=min(normal_dots),
                every_branch_shell_closed=True,branch_shells=branch_count,object_count=1)


def render_preview(vertices,faces,path):
    # Technical orthographic mesh render, not UE lighting/art acceptance.
    tile=480; width=tile*3; height=480
    pixels=bytearray([244,240,231])*(width*height)
    depth=[float("-inf")]*(width*height)
    light=unit((0.55,-0.45,0.8))
    for view,(h_axis,v_axis,d_axis) in enumerate(((1,2,0),(0,2,1),(0,1,2))):
        for ids,_ in faces:
            ps=[vertices[i] for i in ids]
            n=unit(cross(sub(ps[1],ps[0]),sub(ps[2],ps[0])))
            brightness=0.40+0.60*max(0,dot(n,light))
            color=tuple(int(c*brightness) for c in (139,113,78))
            q=[(view*tile+tile/2+p[h_axis]*4.0,tile/2-p[v_axis]*4.0,p[d_axis]) for p in ps]
            x0=max(view*tile,int(min(p[0] for p in q))); x1=min((view+1)*tile-1,int(max(p[0] for p in q))+1)
            y0=max(0,int(min(p[1] for p in q))); y1=min(height-1,int(max(p[1] for p in q))+1)
            a,b,c=q
            area=(b[1]-c[1])*(a[0]-c[0])+(c[0]-b[0])*(a[1]-c[1])
            if abs(area)<1e-8: continue
            for y in range(y0,y1+1):
                py=y+0.5
                for x in range(x0,x1+1):
                    px=x+0.5
                    w0=((b[1]-c[1])*(px-c[0])+(c[0]-b[0])*(py-c[1]))/area
                    w1=((c[1]-a[1])*(px-c[0])+(a[0]-c[0])*(py-c[1]))/area
                    w2=1-w0-w1
                    if min(w0,w1,w2)<-1e-8: continue
                    z=w0*a[2]+w1*b[2]+w2*c[2]
                    index=y*width+x
                    if z>depth[index]:
                        depth[index]=z
                        pixels[index*3:index*3+3]=bytes(color)
    def chunk(kind,data):
        return struct.pack(">I",len(data))+kind+data+struct.pack(">I",zlib.crc32(kind+data)&0xffffffff)
    raw=b"".join(b"\0"+pixels[y*width*3:(y+1)*width*3] for y in range(height))
    png=b"\x89PNG\r\n\x1a\n"+chunk(b"IHDR",struct.pack(">IIBBBBB",width,height,8,2,0,0,0))+chunk(b"IDAT",zlib.compress(raw,8))+chunk(b"IEND",b"")
    path.write_bytes(png)


def make_variant(index):
    crown=Crown("SM_DY_B2_BranchCrown_"+("A" if index==0 else "B")+"_Unit100_v01",128+index)
    root=[(0,0,-49),(3,-1,-29),(-2,1,-14),(1,0,-7)] if index==0 else [(0,0,-49),(-4,2,-31),(-5,0,-13),(0,2,-6)]
    root_id=crown.branch("Root_Graft",root,7.0,4.0,9,10)
    ends=[(7,-48,18),(-18,47,33),(45,14,26),(-45,-13,36),(5,4,48)] if index==0 else [(-5,-47,31),(25,42,23),(45,-7,40),(-42,14,21),(15,6,49)]
    main_ids=[]
    for i,(end,t) in enumerate(zip(ends,(0.48,0.62,0.76,0.84,0.96))):
        main_ids.append(crown.child(root_id,t,"Main_"+str(i),end,0.9+0.12*(i%3),9,8,bend=(-1)**i))
    for i,parent in enumerate(main_ids):
        main=crown.branches[parent]
        phi=math.atan2(main["controls"][-1][1]-main["controls"][0][1],main["controls"][-1][0]-main["controls"][0][0])
        for side,at in ((-1,0.39+0.025*(i%3)),(1,0.69+0.035*((i+1)%3))):
            start=curve(main["controls"],at)
            angle=phi+side*(0.55+0.12*(i%2))
            span=15+4*((i+side+2)%3)
            end=add(start,(math.cos(angle)*span,math.sin(angle)*span,8+4*((i+2)%3)-side*4))
            secondary=crown.child(parent,at,"Secondary_%s_%s"%(i,side),end,0.55,6,6,bend=side)
            sec=crown.branches[secondary]
            start=curve(sec["controls"],0.52+0.08*(i%2))
            angle+=(-side)*(0.7+0.08*i)
            length_tip=9+2*((i+1)%3)
            twig_end=add(start,(math.cos(angle)*length_tip,math.sin(angle)*length_tip,(-3 if i%3==0 else 7)+side*2))
            crown.child(secondary,0.52+0.08*(i%2),"Twig_%s_%s"%(i,side),twig_end,0.30,4,5,bend=-side)
    return crown


def placement_recommendations():
    data=json.loads(DIAGNOSTIC.read_text(encoding="utf-8-sig"))
    assert data["ok"]
    actors={a["label"]:a for a in data["actors"]}
    recommendations={"verified_main_crown_pairs":[],"offset_or_satellite_do_not_replace_blindly":[],"ground_bushes_review":[]}
    for label,a in actors.items():
        comps=a.get("components",[])
        if not comps or comps[0].get("mesh")!="/Engine/BasicShapes/Sphere.Sphere": continue
        if not any("MI_DY_TreeDead" in p for p in comps[0].get("materials",[]) if p): continue
        trunk=None
        if label.startswith("DYTheater_DeadCanopy_"): trunk="DYTheater_DeadTree_"+label.rsplit("_",1)[1]
        elif label.startswith("DYExt12_Crown_"): trunk="DYExt12_Trunk_"+label.rsplit("_",1)[1]
        elif label.startswith("DYExt35_TreeCrown_"): trunk="DYExt35_TreeTrunk_"+label.rsplit("_",1)[1]
        elif label.startswith("DYExt36_Canopy"): trunk=label.replace("Canopy","Trunk")
        if trunk in actors:
            t=actors[trunk]
            xy=math.hypot(a["location"][0]-t["location"][0],a["location"][1]-t["location"][1])
            base=a["center"][2]-a["extent"][2]
            top=t["center"][2]+t["extent"][2]
            row=dict(crown=label,trunk=trunk,xy_center_difference=xy,crown_bbox_bottom=base,trunk_bbox_top=top,
                     original_vertical_gap_cm=max(0,base-top),native_graft_review_required=True)
            if xy<1:
                recommendations["verified_main_crown_pairs"].append(row)
                continue
        row=dict(label=label,center=a["location"],bbox_bottom=a["center"][2]-a["extent"][2],hidden=a.get("hidden"))
        if label.startswith("DYExt7_Bush") or label.startswith("DYExt31_Shrub"):
            recommendations["ground_bushes_review"].append(row)
        else:
            recommendations["offset_or_satellite_do_not_replace_blindly"].append(row)
    recommendations["notes"]=[
        "Main pairs have matching XY centers. Some original trunk/crown boxes already have small vertical gaps; rows record these. Recheck the actual root graft natively.",
        "Small DYExt7_Canopy/DYExt34_Lobe/DYExt30_Lobe/Lobe2 spheres are offset garnish. Replacing each with a root-based whole crown creates floating trees.",
        "Suggested secondary cleanup is to hide exact listed satellite labels only after source/visibility backup; do not delete actors or move trunks.",
        "Ground bushes include elevated bottoms; replacement needs native scene review. This source task does not change their visibility.",
        "Do not restore ART_B1/ART_B2 failed Run99 actors. Both new candidates are single StaticMesh objects, not chains of Actors."
    ]
    recommendations["hide_satellite_labels_exact"]=[r["label"] for r in recommendations["offset_or_satellite_do_not_replace_blindly"]+recommendations["ground_bushes_review"]]
    assert len(recommendations["verified_main_crown_pairs"])==46
    assert len(recommendations["hide_satellite_labels_exact"])==282
    return recommendations


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def main():
    assert ROOT.name=="B2-TreePolish-20261022"
    candidates=[make_variant(i).export() for i in range(2)]
    rec=placement_recommendations()
    report=dict(status="PASS-LOCAL-B2-CANDIDATES",date="2026-10-22",units="centimeter; unit source bbox100x100x100",axes="Z up; normalized bounds center origin",
                candidates=candidates,placement_recommendations=rec,
                material_slot=SLOT,existing_material="/Game/DengYingShanHai/Dev/WorldV2/Materials/MI_DY_TreeTrunk",
                source_provenance="Original standard-library curved cubic-Bezier sweep geometry by Codex; no downloads, Blender, external models or alpha cards.",
                reference="B2_DeadTree_v01.png; previous Final-Entry.png; latest scene-before.json snapshot",
                preview_views_left_to_right=["YZ front","XZ side","XY top"],preview_scope="Source mesh technical raster; not Unreal lighting or runtime acceptance.",
                UE_modified=False,map_modified=False,actor_created=False,transforms_changed=False,native_import_status="NOT_RUN",
                source_script=dict(name=Path(__file__).name,sha256=sha(Path(__file__))),
                diagnostic=dict(path=str(DIAGNOSTIC),sha256=sha(DIAGNOSTIC)))
    (ROOT/"SOURCE_MANIFEST.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(dict(status=report["status"],models=[dict(obj=c["obj"],triangles=c["checks"]["triangles"],root=c["root_base_center_cm"]) for c in candidates],
                          paired_crowns=len(rec["verified_main_crown_pairs"]),offset_satellites=len(rec["offset_or_satellite_do_not_replace_blindly"]),ground_bushes=len(rec["ground_bushes_review"])),
                     ensure_ascii=False,indent=2))


if __name__=="__main__":
    main()
