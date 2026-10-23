from pathlib import Path
import json,hashlib,zipfile,ast
from PIL import Image,ImageDraw,ImageFont,ImageOps
ROOT=Path(__file__).resolve().parent
AUDIT=Path('D:/灯影山海/Saved/Audit-2026-10-22-ThreePuppets')
OUT=ROOT/'Deliverables';OUT.mkdir(exist_ok=True)
DOC=Path('D:/灯影山海/Docs/THREE_PUPPETS_MODELS_20261022.md')
IDENTS=['Jingwei','Xingtian','Zhulong'];NAMES=['精卫','刑天','烛龙']
font=lambda size:ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',size)
for kind in ['Models','UE']:
 canvas=Image.new('RGB',(1800,700),'#151b20');d=ImageDraw.Draw(canvas)
 d.text((36,18),'灯影山海 · 三具影偶模型 / Run2',font=font(33),fill='#f1dfbe')
 subtitle='Blender 实体模型预览 · 分件、厚度、几何镂空' if kind=='Models' else 'UE 5.8 实际截图 · 左侧实体 / 右侧 Movable 灯光投影'
 d.text((36,69),subtitle,font=font(22),fill='#b9bec1')
 for i,(ident,name) in enumerate(zip(IDENTS,NAMES)):
  path=ROOT/'Run2'/ident/'Preview_Rest.png' if kind=='Models' else AUDIT/f'UE-Projection-{ident}-Rest.png'
  im=Image.open(path).convert('RGB');im=ImageOps.contain(im,(566,440),Image.Resampling.LANCZOS)
  x=30+i*590;canvas.paste(im,(x+(566-im.width)//2,135+(440-im.height)//2))
  d.text((x+18,588),name,font=font(28),fill='#f1dfbe')
 d.text((36,660),'Dev 模型验证 · 尚未接入正式四幕',font=font(20),fill='#b9bec1')
 canvas.save(OUT/f'Overview_{kind}.png')
checks={n:json.loads((AUDIT/n).read_text(encoding='utf-8-sig')) for n in ['UE-Import.json','UE-Projection.json','UE-ColdReload-Final.json','Formal-Unchanged.json']}
assert all(v['ok'] for v in checks.values())
assert len(checks['UE-Projection.json']['shots'])==12
assert len(checks['UE-ColdReload-Final.json']['poses'])==10
files=[]
def include(path,archive):
 assert path.is_file(),str(path)
 files.append((path,archive))
for p in (ROOT/'Run2').rglob('*'):
 if p.is_file() and p.suffix.lower() in ['.blend','.fbx','.obj','.mtl','.png','.json']:
  include(p,'ThreePuppets-20261022/'+p.relative_to(ROOT).as_posix())
for name in ['README.md','jingwei_spec.json','xingtian_spec.json','zhulong_spec.json','prepare_meshes.py','build_blender.py','import_ue.py','capture_projection_ue.py','verify_final_ue.py','package_delivery.py']:
 p=ROOT/name
 if p.suffix=='.py':ast.parse(p.read_text(encoding='utf-8-sig'))
 include(p,'ThreePuppets-20261022/'+name)
for ident in IDENTS:
 p=ROOT.parent/'Concept-20261021'/f'C1_{ident}_Ortho_v01.png'
 include(p,'Concept-20261021/'+p.name)
include(DOC,'THREE_PUPPETS_MODELS_20261022.md')
for p in OUT.glob('Overview_*.png'):include(p,p.name)
for name in checks:include(AUDIT/name,'Verification/'+name)
review=AUDIT/'UE-VisualReview.md'
assert review.is_file(),'Final independent visual review missing'
include(review,'Verification/'+review.name)
for shot in checks['UE-Projection.json']['shots']:
 p=Path(shot['file']);include(p,'Verification/'+p.name)
manifest={'version':'20261022-Run2','scope':'Three editable layered leather puppet models. UE Dev imported and verified in the current project. ZIP holds source/export/evidence, not a standalone UE migration bundle. Formal four-act integration and Shipping remain outside this delivery.','models':{},'files':[]}
for ident in IDENTS:
 v=json.loads((ROOT/'Run2'/ident/'MODEL_VERIFICATION.json').read_text(encoding='utf8'));assert v['status']=='PASS-MODEL-SOURCE-FBX-ROUNDTRIP'
 manifest['models'][ident]={k:v[k]for k in ['vertices','triangles','bone_count','real_cutouts','skin_thickness_cm','human_art_acceptance','runtime_integration']}
for p,arc in files:manifest['files'].append({'path':arc,'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
mp=OUT/'MANIFEST.json';mp.write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf8')
include(mp,'MANIFEST.json')
zp=OUT/'DY_ThreePuppets_20261022_Run2.zip'
with zipfile.ZipFile(zp,'w',zipfile.ZIP_DEFLATED,compresslevel=6)as z:
 for p,arc in files:z.write(p,arc)
with zipfile.ZipFile(zp)as z:
 assert z.testzip() is None
 assert sum(n.endswith('.blend')for n in z.namelist())==3
 assert sum('/SK_DY_'in n and n.endswith('.fbx')for n in z.namelist())==3
 assert sum('/A_DY_'in n and n.endswith('.fbx')for n in z.namelist())==10
 for row in manifest['files']:assert hashlib.sha256(z.read(row['path'])).hexdigest()==row['sha256']
result={'ok':True,'archive':str(zp),'bytes':zp.stat().st_size,'sha256':hashlib.sha256(zp.read_bytes()).hexdigest(),'files':len(files),'models':3,'editable_blend':3,'mesh_fbx':3,'pose_fbx':10,'zip_crc_and_all_file_hashes_verified':True,'formal_integration':False}
(OUT/'PACKAGE_VERIFICATION.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(result,ensure_ascii=False,indent=2))