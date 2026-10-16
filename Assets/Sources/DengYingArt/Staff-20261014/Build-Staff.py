"""Bound-preserving independent wooden staff. Blender output, no project writes.

The original literary text specifies a staff, not its wood species or finish.
This worn plain pole is an interactive adaptation, not historical reconstruction.
Local A=(0,0,-50), B=(0,0,50) intentionally match the existing native contract.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import sys
import bpy
import bmesh
from mathutils import Vector

parser = argparse.ArgumentParser()
parser.add_argument('--out', required=True)
args = parser.parse_args(sys.argv[sys.argv.index('--')+1:])
out = Path(args.out).resolve()
assert not out.exists(), 'Preserve any prior authoring run'
out.mkdir(parents=True)
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
scene = bpy.context.scene
scene.unit_settings.system = 'METRIC'
scene.unit_settings.scale_length = 0.01

# Closed single mesh, UV seam follows the pole; the original component scale is retained.
radial, rings = 48, 32
verts, faces, uvs = [(0.,0.,-50.)], [], []
# Rounded physical 3cm end caps after the native anisotropic component scale;
# a uniform local sphere would incorrectly make the ends look like spear points.
cap_depth = 50*.06/1.55
levels = [(-50+cap_depth*(1-math.cos(math.pi*i/12)),50*math.sin(math.pi*i/12)) for i in range(1,7)]
levels += [(-50+cap_depth+(100-2*cap_depth)*j/20,50.) for j in range(1,20)]
levels += [(50-cap_depth*(1-math.cos(math.pi*i/12)),50*math.sin(math.pi*i/12)) for i in range(6,0,-1)]
assert len(levels)==rings-1
for row,(z,base) in enumerate(levels,1):
    t = (z+50)/100
    grip = 1.0 - 0.045 * math.exp(-((t-.72)/.095)**2)
    for col in range(radial):
        angle = 2*math.pi*col/radial
        ripple = 1.0 - .008*(1-math.cos(angle*7))*math.sin(math.pi*t)
        r = base*grip*ripple
        # Central cross section fixes the same symmetric bounds as the former cylinder.
        if row == rings//2:
            r = 50.0
        verts.append((r*math.cos(angle),r*math.sin(angle),z))
verts.append((0.,0.,50.))
def idx(row,col):
    return 1+(row-1)*radial+(col % radial)
for col in range(radial):
    faces.append((0,idx(1,col+1),idx(1,col)))
    v=(levels[0][0]+50)/100
    uvs.append(((col+.5)/radial,0.,(col+1)/radial,v,col/radial,v))
for row in range(1,rings-1):
    for col in range(radial):
        faces.append((idx(row,col),idx(row,col+1),idx(row+1,col+1),idx(row+1,col)))
        v0=(levels[row-1][0]+50)/100;v1=(levels[row][0]+50)/100
        uvs.append((col/radial,v0,(col+1)/radial,v0,(col+1)/radial,v1,col/radial,v1))
top = len(verts)-1
for col in range(radial):
    faces.append((idx(rings-1,col),idx(rings-1,col+1),top))
    v=(levels[-1][0]+50)/100
    uvs.append((col/radial,v,(col+1)/radial,v,(col+.5)/radial,1.))
mesh = bpy.data.meshes.new('DY_Kuafu_Staff_Geometry')
mesh.from_pydata(verts,[],faces)
mesh.update()
assert not mesh.validate(verbose=True), 'No invalid topology silently repaired'
bm=bmesh.new();bm.from_mesh(mesh)
assert all(e.is_manifold for e in bm.edges), 'Closed two-manifold staff required'
assert all(f.calc_area()>1e-9 for f in bm.faces), 'No degenerate face'
bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(mesh);bm.free()
uv=mesh.uv_layers.new(name='UVMap')
for p,coord in zip(mesh.polygons,uvs):
    for offset,li in enumerate(p.loop_indices):
        circumference,height=coord[offset*2],coord[offset*2+1]
        # Source image grain runs in U; crop V to one examined plank, not its joints.
        uv.data[li].uv=(height,.84+.06*circumference)
for p in mesh.polygons:p.use_smooth=True
obj=bpy.data.objects.new('SM_DY_Kuafu_Staff',mesh)
scene.collection.objects.link(obj)
obj['Source']='Shan Hai Jing / Hai Wai Bei Jing: literary staff motif; geometric finish is a project adaptation'
obj['EndA']=[0.,0.,-50.];obj['EndB']=[0.,0.,50.]
assert tuple(obj.dimensions)==(100.,100.,100.)
assert verts[0]==(0.,0.,-50.) and verts[-1]==(0.,0.,50.)

material=bpy.data.materials.new('MI_DY_Staff_Wood_Reference')
material.use_nodes=True
n=material.node_tree.nodes;links=material.node_tree.links
bsdf=n.get('Principled BSDF');bsdf.inputs['Metallic'].default_value=0.
bsdf.inputs['Roughness'].default_value=.72
source=Path(r'D:\灯影山海\Saved\Audit-2026-10-12-FramePostAsset\Sources')
diffuse=source/'wood_table_diff_2k.png'
normal=source/'wood_table_nor_dx_2k.png'
assert diffuse.is_file() and normal.is_file()
image=n.new('ShaderNodeTexImage');image.image=bpy.data.images.load(str(diffuse),check_existing=True)
links.new(image.outputs['Color'],bsdf.inputs['Base Color'])
data=n.new('ShaderNodeTexImage');data.image=bpy.data.images.load(str(normal),check_existing=True);data.image.colorspace_settings.name='Non-Color'
separate=n.new('ShaderNodeSeparateColor');separate.mode='RGB'
combine=n.new('ShaderNodeCombineColor');combine.mode='RGB'
invert=n.new('ShaderNodeMath');invert.operation='SUBTRACT';invert.inputs[0].default_value=1.
links.new(data.outputs['Color'],separate.inputs[0]);links.new(separate.outputs['Red'],combine.inputs['Red']);links.new(separate.outputs['Green'],invert.inputs[1]);links.new(invert.outputs[0],combine.inputs['Green']);links.new(separate.outputs['Blue'],combine.inputs['Blue'])
nm=n.new('ShaderNodeNormalMap');nm.inputs['Strength'].default_value=.35
links.new(combine.outputs[0],nm.inputs['Color']);links.new(nm.outputs['Normal'],bsdf.inputs['Normal'])
obj.data.materials.append(material)

# The exported mesh has unit transforms, so existing .06/.06/1.55 native scale is untouched.
bpy.ops.object.select_all(action='DESELECT');obj.select_set(True);bpy.context.view_layer.objects.active=obj
fbx=out/'SM_DY_Kuafu_Staff.fbx'
bpy.ops.export_scene.fbx(filepath=str(fbx),use_selection=True,object_types={'MESH'},global_scale=1.,apply_unit_scale=True,axis_forward='-Y',axis_up='Z',use_mesh_modifiers=True,mesh_smooth_type='FACE',bake_anim=False,path_mode='ABSOLUTE')
mesh.calc_loop_triangles()
triangles=len(mesh.loop_triangles)
assert triangles==2976 and triangles<4000

# Read back the actual exported artifact into an empty scene; no intent-only export claim.
before=set(bpy.data.objects)
bpy.ops.import_scene.fbx(filepath=str(fbx),use_anim=False)
imported=[o for o in bpy.data.objects if o not in before and o.type=='MESH']
assert len(imported)==1
imp=imported[0]
bounds=[imp.matrix_world@Vector(c) for c in imp.bound_box]
dimensions=[max(v[i] for v in bounds)-min(v[i] for v in bounds) for i in range(3)]
assert all(abs(v-100)<1e-4 for v in dimensions), dimensions
imp.data.calc_loop_triangles();assert len(imp.data.loop_triangles)==triangles
imported_name=imp.name;bpy.data.objects.remove(imp,do_unlink=True)

obj.hide_render=True;obj.hide_viewport=True
preview=bpy.data.objects.new('Staff_Actual_Component_Scale',mesh)
scene.collection.objects.link(preview);preview.scale=(.06,.06,1.55)
camera_data=bpy.data.cameras.new('ReviewCamera');camera=bpy.data.objects.new('ReviewCamera',camera_data);scene.collection.objects.link(camera)
camera.location=(260.,-320.,115.)
direction=Vector((0.,0.,10.))-camera.location;camera.rotation_euler=direction.to_track_quat('-Z','Y').to_euler()
camera_data.type='ORTHO';camera_data.ortho_scale=190.;scene.camera=camera
for name,location,energy,size in [('Key',(100.,-100.,130.),850.,140.),('Rim',(-75.,45.,65.),650.,90.)]:
    light_data=bpy.data.lights.new(name,'AREA');light_data.energy=energy*2000;light_data.shape='DISK';light_data.size=size
    light=bpy.data.objects.new(name,light_data);scene.collection.objects.link(light);light.location=location;light.rotation_euler=(Vector((0.,0.,0.))-light.location).to_track_quat('-Z','Y').to_euler()
scene.world.color=(.065,.065,.065)
scene.render.engine='BLENDER_EEVEE_NEXT';scene.render.resolution_x=650;scene.render.resolution_y=1100;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG';scene.render.film_transparent=False
scene.view_settings.view_transform='AgX'
bpy.ops.file.pack_all()
blend=out/'DY_Kuafu_Staff.blend';bpy.ops.wm.save_as_mainfile(filepath=str(blend))
scene.render.filepath=str(out/'Staff-ActualScale.png');bpy.ops.render.render(write_still=True)
def record(p):return dict(File=p.name,Bytes=p.stat().st_size,SHA256=hashlib.sha256(p.read_bytes()).hexdigest().upper())
report=dict(Status='PASS-AUTHORED-STAFF-AND-EXPORTED-FBX-READBACK',Blender=bpy.app.version_string,Mesh=obj.name,Vertices=len(mesh.vertices),Triangles=triangles,UVLayers=len(mesh.uv_layers),ClosedManifold=True,LocalMin=[-50.,-50.,-50.],LocalMax=[50.,50.,50.],EndA=[0.,0.,-50.],EndB=[0.,0.,50.],ImportedFBXDimensions=dimensions,ComponentScaleUnchanged=[.06,.06,1.55],ActualLengthCm=155.,CoreProjectFilesWritten=False,ImportedToUE=False,HistoricalWoodSpeciesClaimed=False,Artifacts=[record(p) for p in (fbx,blend,out/'Staff-ActualScale.png')])
(out/'STAFF-RESULT.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(report,ensure_ascii=False))
