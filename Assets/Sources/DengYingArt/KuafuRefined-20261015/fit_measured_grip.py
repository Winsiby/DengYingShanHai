"""Fit a Dev visual assembly from actual PIE bones, never move the native Staff."""
import json
from pathlib import Path
import numpy as np

source=Path(r'D:\灯影山海\Saved\Audit-2026-10-14-ArtAppearance\PuppetPIE-Run2\RESULT.json')
data=json.loads(source.read_text(encoding='utf-8-sig'))
assert data['success'] and data['actual_three_poses_verified']
rows={s['pose']:s for s in data['samples']}
assert len(rows)==3
scale=.8  # Dev assembly candidate, not a changed control/puzzle parameter.
rot=np.diag([-1.,-1.,1.]) # face the source front toward the existing -X operator.
matrices=[];right=[];samples=[]
for name,s in rows.items():
    p=np.array(s['component_bones']['StaffGrip_L'])
    actor=np.array(s['world_bones']['Head'])-np.array(s['component_bones']['Head'])
    # Original unfit SCS has identity transform; verify with every sampled bone.
    assert all(np.max(np.abs(np.array(s['world_bones'][b])-np.array(s['component_bones'][b])-actor))<1e-5 for b in s['component_bones'])
    a=np.array(s['staff']['A'])-actor;b=np.array(s['staff']['B'])-actor
    d=(b-a)/np.linalg.norm(b-a);m=np.eye(3)-np.outer(d,d)
    matrices.append(m);right.append(m@(a-scale*(rot@p)))
    samples.append((name,p,a,b,m))
translation,residual,rank,singular=np.linalg.lstsq(np.vstack(matrices),np.concatenate(right),rcond=None)
assert rank==3 and np.max(np.abs(translation))<200
out={'scope':'MEASURED-DEV-VISUAL-ASSEMBLY-NOT-FORMAL-ACCEPTANCE','native_pie_input':str(source),
     'uniform_scale':scale,'relative_yaw_degrees':180,'relative_translation_cm':translation.tolist(),
     'native_staff_moved':False,'samples':[]}
for name,p,a,b,m in samples:
    point=scale*(rot@p)+translation
    distance=float(np.linalg.norm(m@(point-a)))
    t=float(np.dot(point-a,b-a)/np.dot(b-a,b-a))
    assert distance<1.0 and 0<t<1
    out['samples'].append({'pose':name,'grip_axis_distance_cm':distance,'grip_along_staff_0_1':t})
destination=Path(__file__).with_name('MEASURED_GRIP_FIT.json')
assert not destination.exists()
destination.write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(out,ensure_ascii=False,indent=2))
