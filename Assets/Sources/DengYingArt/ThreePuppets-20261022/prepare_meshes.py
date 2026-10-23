"""Extract articulated, perforated leather solids from existing project design sheets.
The source artwork is read-only. Geometry contains real cutouts; no alpha cards.
"""
from pathlib import Path
import sys,json,hashlib,math
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'Tooling'))
import numpy as np
import cv2
import triangle
from shapely.geometry import Polygon, MultiPolygon, Point
from shapely import set_precision
from PIL import Image

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest().upper()
def area(p):return .5*sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(p,p[1:]+p[:1]))
def clean_ring(c,epsilon=.65):
    p=cv2.approxPolyDP(c,epsilon,True).reshape(-1,2).astype(float).tolist()
    return p if len(p)>=3 and abs(area(p))>2 else None

def prepare(spec_path,out):
    spec=json.loads(spec_path.read_text(encoding='utf-8-sig'))
    spec.update({k:v for k,v in spec.get('closed_eye',{}).items() if k in ('eye_aperture_polygon_px','eyelid_polygon_px')})
    img=np.array(Image.open(spec['reference']).convert('RGB'))
    h,w=img.shape[:2]
    foreground=((img.min(2)<218)&((img.max(2)-img.min(2)>16)|(img.mean(2)<175))).astype('uint8')*255
    if spec.get('eye_aperture_polygon_px'):
        cv2.fillPoly(foreground,[np.rint(spec['eye_aperture_polygon_px']).astype(np.int32)],0)
    all_masks=[];pieces=[];ledger=[]
    for part in spec['parts']:
        select=np.zeros((h,w),np.uint8)
        cv2.fillPoly(select,[np.rint(part['polygon_px']).astype(np.int32)],255)
        for exclude in part.get('exclude_polygons_px',[]):cv2.fillPoly(select,[np.rint(exclude).astype(np.int32)],0)
        mask=cv2.bitwise_and(foreground,select)
        # Close only antialias pinholes. Deliberate punched shapes remain open.
        mask=cv2.morphologyEx(mask,cv2.MORPH_CLOSE,np.ones((3,3),np.uint8))
        mask=cv2.bitwise_and(mask,select)
        n,labs,stats,centers=cv2.connectedComponentsWithStats(mask,8)
        kept=np.zeros_like(mask)
        for n0 in range(1,n):
            if stats[n0,cv2.CC_STAT_AREA]>=part.get('min_component_px',28):kept[labs==n0]=255
        contours,hierarchy=cv2.findContours(kept,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
        assert hierarchy is not None,part['name']+' empty'
        ringsets=[];holes_count=0
        for i,c in enumerate(contours):
            depth=0;parent=hierarchy[0,i,3]
            while parent>=0:depth+=1;parent=hierarchy[0,parent,3]
            if depth%2:continue
            if cv2.contourArea(c)<part.get('min_component_px',28):continue
            outer=clean_ring(c)
            if outer is None:continue
            holes=[];child=hierarchy[0,i,2]
            while child>=0:
                if cv2.contourArea(contours[child])>=part.get('min_hole_px',16):
                    hole=clean_ring(contours[child],.5)
                    if hole:holes.append(hole)
                else:cv2.drawContours(kept,contours,child,255,-1)
                child=hierarchy[0,child,0]
            geom=set_precision(Polygon(outer,holes).buffer(0).buffer(-0.2).buffer(0.2,quad_segs=1).simplify(0.15,preserve_topology=True),0.1)
            geoms=list(geom.geoms) if isinstance(geom,MultiPolygon) else [geom]
            for g in geoms:
                if g.area<28:continue
                def ring_clean(coords):
                    r=[list(p) for p in list(coords)[:-1]]
                    changed=True
                    while changed and len(r)>3:
                        changed=False
                        for q in range(len(r)):
                            a,b,c=r[q-1],r[q],r[(q+1)%len(r)]
                            if abs((b[0]-a[0])*(c[1]-b[1])-(b[1]-a[1])*(c[0]-b[0]))<1e-7:
                                r.pop(q);changed=True;break
                    return r
                rs=[ring_clean(g.exterior.coords)]+[ring_clean(r.coords) for r in g.interiors]
                ringsets.append(rs);holes_count+=len(rs)-1
        assert ringsets,part['name']+' has no solids'
        pieces.append({**part,'ringsets':ringsets})
        all_masks.append(kept)
        ledger.append({'name':part['name'],'bone':part['bone'],'islands':len(ringsets),'real_cutout_count':holes_count,'foreground_pixels':int((kept>0).sum())})
    union=np.maximum.reduce(all_masks)
    ys,xs=np.where(union)
    bounds=[int(xs.min()),int(ys.min()),int(xs.max())+1,int(ys.max())+1]
    u0,v0,u1,v1=bounds
    scale=spec['height_cm']/(v1-v0)
    origin_u=spec['root_px'][0];origin_v=v1
    def xyz(p,x=0):return [round(x,6),round((p[0]-origin_u)*scale,6),round((origin_v-p[1])*scale,6)]
    def uv(p):return [(p[0]-u0)/(u1-u0),1-(p[1]-v0)/(v1-v0)]
    model={'id':spec['id'],'source':spec,'bounds_px':bounds,'scale_cm_per_pixel':scale,'origin_px':[origin_u,origin_v],
           'width_cm':(u1-u0)*scale,'height_cm':spec['height_cm'],'parts':[],'bones':[], 'ledger':ledger}
    for b in spec['bones']:model['bones'].append({**b,'pivot_cm':xyz(b['pivot_px'])})
    for part in pieces:
        vertices=[];faces=[];uvs=[];slots=[];physical_holes=0
        for rings0 in part['ringsets']:
            rings=[]
            # In YZ coordinates positive winding faces +X.
            for ri,r in enumerate(rings0):
                r=list(r)
                if (area([[p[0],-p[1]] for p in r])>0)!=(ri==0):r.reverse()
                rings.append(r)
            points=[p for ring in rings for p in ring]
            ends=np.cumsum([len(r) for r in rings]).astype(np.uint32)
            segments=[];start=0
            for ring in rings:
                segments += [[start+j,start+(j+1)%len(ring)] for j in range(len(ring))]
                start+=len(ring)
            data={'vertices':np.array([[p[0],-p[1]] for p in points],np.float64),'segments':np.array(segments,np.int32)}
            if len(rings)>1:
                data['holes']=np.array([[q.x,-q.y] for q in [Polygon(r).representative_point() for r in rings[1:]]],np.float64)
            result=triangle.triangulate(data,'pQ')
            tri=result['triangles'];points=[[float(p[0]),-float(p[1])] for p in result['vertices']]
            boundary=result['segments']
            region=Polygon([[p[0],-p[1]] for p in rings[0]],[[[p[0],-p[1]] for p in r] for r in rings[1:]])
            expected=abs(area(rings[0]))-sum(abs(area(r)) for r in rings[1:])
            actual=sum(abs(area([points[int(k)] for k in t])) for t in tri)
            assert abs(actual-expected)<max(2,expected*.002),(part['name'],actual,expected)
            n=len(points);offset=len(vertices);layer=float(part.get('layer_cm',0));thickness=spec['thickness_cm']
            vertices += [xyz(p,layer+thickness/2) for p in points]+[xyz(p,layer-thickness/2) for p in points]
            uvs += [uv(p) for p in points]*2
            for t in tri:
                a,b,c=map(int,t)
                cross=np.cross(np.array(vertices[offset+b])-vertices[offset+a],np.array(vertices[offset+c])-vertices[offset+a])
                if cross[0]<0:b,c=c,b
                faces.extend([[offset+a,offset+b,offset+c],[offset+n+c,offset+n+b,offset+n+a]])
                slots.extend([0,0])
            for a,b in boundary:
                a,b=int(a),int(b)
                pa,pb=result['vertices'][a],result['vertices'][b]
                delta=pb-pa;left=np.array([-delta[1],delta[0]])
                test=(pa+pb)*.5+left/max(np.linalg.norm(left),1e-10)*.001
                if not region.contains(Point(*test)):a,b=b,a
                faces.extend([[offset+a,offset+n+a,offset+n+b],[offset+a,offset+n+b,offset+b]])
                slots.extend([1,1])
            physical_holes+=len(rings)-1
        # A closed shell per island must have two incident faces at each edge.
        edges={}
        for f in faces:
            for a,b in zip(f,f[1:]+f[:1]):edges[tuple(sorted((a,b)))]=edges.get(tuple(sorted((a,b))),0)+1
        assert all(n==2 for n in edges.values()),(part['name'],[(e,n,[vertices[k] for k in e]) for e,n in edges.items() if n!=2][:12])
        assert all(np.linalg.norm(np.cross(np.array(vertices[b])-vertices[a],np.array(vertices[c])-vertices[a]))>1e-9 for a,b,c in faces)
        model['parts'].append({'name':part['name'],'bone':part['bone'],'vertices':vertices,'faces':faces,'uv':uvs,'slots':slots,'real_cutouts':physical_holes})
    out.mkdir(parents=True,exist_ok=True)
    # Remove all sheet annotations from the texture: retain only selected puppet pixels.
    # Extend real leather colours across the UV border; do not bake a paper halo.
    solid=cv2.erode(union,np.ones((3,3),np.uint8))
    dist,labels=cv2.distanceTransformWithLabels((solid==0).astype(np.uint8),cv2.DIST_L2,5,labelType=cv2.DIST_LABEL_PIXEL)
    colours=img[solid>0]
    art=colours[np.maximum(labels-1,0)]
    art[solid>0]=img[solid>0]
    cropped=art[v0:v1,u0:u1]
    Image.fromarray(cropped).resize((4096,4096),Image.Resampling.LANCZOS).save(out/f'T_DY_{spec["id"]}_BaseColor.png')
    if spec.get('closed_eye'):
        ce=spec['closed_eye'];sx0,sy0,sx1,sy1=ce['source_bounds_px'];tx0,ty0,tx1,ty1=ce['target_bounds_px']
        patch=Image.fromarray(img[sy0:sy1,sx0:sx1]).resize((tx1-tx0,ty1-ty0),Image.Resampling.LANCZOS)
        closed=Image.fromarray(art);closed.paste(patch,(tx0,ty0))
        closed.crop((u0,v0,u1,v1)).resize((4096,4096),Image.Resampling.LANCZOS).save(out/f'T_DY_{spec["id"]}_ClosedBaseColor.png')
    rng=np.random.default_rng(20261022)
    noise=rng.normal(0,1,(4096,4096)).astype(np.float32)
    smooth=cv2.GaussianBlur(noise,(0,0),1.1)
    dx=cv2.Sobel(smooth,cv2.CV_32F,1,0,ksize=3)*.015
    dy=cv2.Sobel(smooth,cv2.CV_32F,0,1,ksize=3)*.015
    nz=np.ones_like(dx);length=np.sqrt(dx*dx+dy*dy+1)
    normal=np.stack((-dx/length,dy/length,nz/length),2)
    Image.fromarray(np.uint8(np.clip((normal*.5+.5)*255,0,255))).save(out/f'T_DY_{spec["id"]}_NormalDX.png')
    rough=np.uint8(np.clip(190+noise*7,160,220))
    orm=np.stack((np.full_like(rough,255),rough,np.zeros_like(rough)),2)
    Image.fromarray(orm).save(out/f'T_DY_{spec["id"]}_ORM.png')
    Image.fromarray(union[v0:v1,u0:u1]).save(out/'GeometryMask.png')
    model['provenance']={'reference_sha256':sha(spec['reference']),'spec_sha256':sha(spec_path),'method':'Contour-modeled extruded leather pieces from existing project concept; real holes, rigid articulation, cleaned artwork UV atlas; no purchased mesh or new image generation.','texture_note':'Stylized painted artwork, not a scanned physical albedo. Existing design-sheet markings are excluded.'}
    (out/'prepared.json').write_text(json.dumps(model,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
    print(json.dumps({'id':model['id'],'parts':len(model['parts']),'bones':len(model['bones']),'triangles':sum(len(p['faces']) for p in model['parts']),'cutouts':sum(p['real_cutouts'] for p in model['parts']),'width_cm':model['width_cm'],'height_cm':model['height_cm'],'output':str(out)}),flush=True)

if __name__=='__main__':
    run=ROOT/(sys.argv[1] if len(sys.argv)>1 else 'Run1')
    for p in sorted(ROOT.glob('*_spec.json')):prepare(p,run/json.loads(p.read_text(encoding='utf-8-sig'))['id'])






