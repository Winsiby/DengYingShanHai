from pathlib import Path
import json,hashlib,zipfile,ast
from PIL import Image,ImageDraw,ImageFont,ImageOps

ROOT=Path(__file__).resolve().parent
AUDIT=Path('D:/灯影山海/Saved/Audit-2026-10-22-ThreePuppets')
FOURACT=Path('D:/灯影山海/Saved/Audit-2026-10-22-FourAct')
OUT=ROOT/'Deliverables';OUT.mkdir(exist_ok=True)
DOC=Path('D:/灯影山海/Docs/THREE_PUPPETS_MODELS_20261022.md')
IDENTS=['Jingwei','Xingtian','Zhulong'];NAMES=['精卫','刑天','烛龙']
RUN='Run4'
font=lambda size:ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',size)

# ---- overview sheets -------------------------------------------------------
for kind in ['Models','UE']:
 canvas=Image.new('RGB',(1800,700),'#151b20');d=ImageDraw.Draw(canvas)
 d.text((36,18),'灯影山海 · 三具影偶模型 / Run4',font=font(33),fill='#f1dfbe')
 subtitle='Blender 实体模型预览 · 操杆并入网格 + 头身比与姿态修正' if kind=='Models' else 'UE 5.8 实际截图 · 左侧实体 / 右侧 Movable 灯光投影'
 d.text((36,69),subtitle,font=font(22),fill='#b9bec1')
 for i,(ident,name) in enumerate(zip(IDENTS,NAMES)):
  path=ROOT/RUN/ident/'Preview_Rest.png' if kind=='Models' else AUDIT/f'UE-Projection-{ident}-Rest.png'
  im=Image.open(path).convert('RGB');im=ImageOps.contain(im,(566,440),Image.Resampling.LANCZOS)
  x=30+i*590;canvas.paste(im,(x+(566-im.width)//2,135+(440-im.height)//2))
  d.text((x+18,588),name,font=font(28),fill='#f1dfbe')
 d.text((36,660),'Development RunD7 已接入正式四幕 · 公开 Shipping 仍为 Run143',font=font(20),fill='#b9bec1')
 canvas.save(OUT/f'Overview_{kind}.png')

# ---- assertions -----------------------------------------------------------
checks={n:json.loads((AUDIT/n).read_text(encoding='utf-8-sig')) for n in ['UE-Import.json','UE-Projection.json']}
cold=json.loads((AUDIT/'UE-ColdReload-Final.json').read_text(encoding='utf-8-sig'))
assert checks['UE-Import.json']['ok'] is True and checks['UE-Import.json']['warnings']==[]
run4=json.loads((FOURACT/'run4-verify.json').read_text(encoding='utf-8-sig'))
assert run4['ok'] is True and run4['errors']==[]
pkg=json.loads((FOURACT/'packaged-acts-verify.json').read_text(encoding='utf-8-sig'))
assert pkg['ok'] is True
for shot in checks['UE-Projection.json']['shots']:
 assert Path(shot['file']).is_file(),shot['file']

# ---- collect --------------------------------------------------------------
files=[]
def include(p,arc):
 assert Path(p).is_file(),p
 files.append((Path(p),arc))
def suf_ok(p):return p.suffix.lower() in ['.blend','.fbx','.obj','.mtl','.png','.json']
for p in sorted((ROOT/RUN).rglob('*')):
 if p.is_file() and suf_ok(p):include(p,'ThreePuppets-20261022/'+p.relative_to(ROOT).as_posix())
for name in ['README.md','jingwei_spec.json','xingtian_spec.json','zhulong_spec.json','prepare_meshes.py','build_blender.py','import_ue.py','package_delivery.py','package_delivery_run4.py',
             'pose_probe.py','pose_probe_all.py','pose_probe2.py']:
 p=ROOT/name
 if p.suffix=='.py':ast.parse(p.read_text(encoding='utf-8-sig'))
 include(p,'ThreePuppets-20261022/'+name)
for ident in IDENTS:
 include(ROOT.parent/'Concept-20261021'/f'C1_{ident}_Ortho_v01.png','Concept-20261021/'+f'C1_{ident}_Ortho_v01.png')
include(DOC,'THREE_PUPPETS_MODELS_20261022.md')
include(Path('D:/灯影山海/Docs/FOURACT_CAST_20261022.md'),'FOURACT_CAST_20261022.md')
include(Path('D:/灯影山海/Docs/ART_AUDIT_20261022_FOURACT.md'),'ART_AUDIT_20261022_FOURACT.md')
for p in OUT.glob('Overview_*.png'):include(p,p.name)
for name in ['UE-Import.json','UE-Projection.json','UE-ColdReload-Final.json']:include(AUDIT/name,'Verification/'+name)
for shot in checks['UE-Projection.json']['shots']:include(Path(shot['file']),'Verification/'+Path(shot['file']).name)
for name in ['run4-verify.json','packaged-acts-verify.json','title-swap-calls.json','final-acts.json','cast-import.json','shipping144-archive.json','shipping144-verify.json']:
 include(FOURACT/name,'Verification/'+name)
for name in ['Packaged-Acts234.png','Shipping144-Acts.png','Final-Act1.png','Final-Act2.png','Final-Act3.png','Final-Act4.png','Title3-Strip.png']:
 include(FOURACT/name,'Verification/'+name)
for name in ['r7-act2.png','r7-act3.png','r7-act4.png','r7-act2-zoom.png','r7-act3-zoom.png','r7-act4-zoom.png','r7-panel.png']:
 include(FOURACT/name,'Verification/Packaged/'+name)
for ident in IDENTS:
 include(ROOT/RUN/ident/'MODEL_VERIFICATION.json','Verification/'+f'{ident}-MODEL_VERIFICATION.json')
include(ROOT/'Probe'/'ProportionSheet.png','Verification/Probe-ProportionSheet.png')
include(ROOT/'Probe'/'CharacterSilhouettes.png','Verification/Probe-CharacterSilhouettes.png')

manifest={'version':'20261022-Run4',
 'scope':'Three editable layered leather puppet models with control rods merged into the mesh. Imported into the production content folder and wired into the four-act campaign in development builds. ZIP holds source/export/evidence, not a standalone UE migration bundle. Public Shipping entry still Run143.',
 'models':{},'files':[]}
for ident in IDENTS:
 v=json.loads((ROOT/RUN/ident/'MODEL_VERIFICATION.json').read_text(encoding='utf-8-sig'))
 assert v['status']=='PASS-MODEL-SOURCE-FBX-ROUNDTRIP'
 manifest['models'][ident]={k:v[k] for k in ['vertices','triangles','bone_count','real_cutouts','skin_thickness_cm','human_art_acceptance'] if k in v}
for p,arc in files:manifest['files'].append({'path':arc,'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
mp=OUT/'MANIFEST_Run4.json';mp.write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf8')
include(mp,'MANIFEST_Run4.json')

zp=OUT/'DY_ThreePuppets_20261022_Run4.zip'
with zipfile.ZipFile(zp,'w',zipfile.ZIP_DEFLATED,compresslevel=6)as z:
 for p,arc in files:z.write(p,arc)
with zipfile.ZipFile(zp)as z:
 assert z.testzip() is None
 names=z.namelist()
 assert sum(n.endswith('.blend')for n in names)==3
 assert sum('/SK_DY_'in n and n.endswith('.fbx')for n in names)==3
 assert sum('/A_DY_'in n and n.endswith('.fbx')for n in names)==10
 assert sum(n.startswith('Verification/Packaged/') for n in names)==7
 for row in manifest['files']:assert hashlib.sha256(z.read(row['path'])).hexdigest()==row['sha256'],row['path']
result={'ok':True,'archive':zp.name,'bytes':zp.stat().st_size,'sha256':hashlib.sha256(zp.read_bytes()).hexdigest(),
 'files':len(files),'models':3,'editable_blend':3,'mesh_fbx':3,'pose_fbx':10,
 'zip_crc_and_all_file_hashes_verified':True,
 'runtime_integration':'four-act campaign wired in development build RunD7; verified in packaged exe with in-game chapter selection',
 'public_shipping':'Shipping Run144 built and verified in this round; public entry script still points at Run143 and switching requires user approval',
 'evidence':{'run4_verify_checks':run4.get('checks'),'packaged_captures':len(pkg.get('captures',[]))}}
(OUT/'PACKAGE_VERIFICATION_Run4.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(result,ensure_ascii=False,indent=2))
