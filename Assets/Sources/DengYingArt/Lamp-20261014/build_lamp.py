"""Project-specific spotlight exterior; original modeling, not historical reconstruction."""
import bpy
import bmesh
import json
import math
from pathlib import Path
from mathutils import Vector

OUT = Path(__file__).resolve().parent
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.unit_settings.system = 'METRIC'
scene.unit_settings.scale_length = 1.0
scene.unit_settings.length_unit = 'CENTIMETERS'
scene.render.engine = 'CYCLES'
scene.cycles.samples = 80
scene.cycles.use_denoising = True
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = 'PNG'
scene.view_settings.view_transform = 'AgX'
scene.world = bpy.data.worlds.new('ReviewWorld')
scene.world.use_nodes = True
scene.world.node_tree.nodes['Background'].inputs['Color'].default_value = (.15,.18,.22,1)
scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value = .3

root = bpy.data.objects.new('Root_Back_Source', None)
scene.collection.objects.link(root)
root.empty_display_type = 'PLAIN_AXES'
root['Role'] = 'Exact ADYLightRigActor SceneRoot origin; meters in Blender, cm in UE'
root['Emitter_Local_UE_cm'] = [45.0,0.0,0.0]
root['Light_Direction'] = '+X'
root['Historic_Claim'] = 'None; contemporary creative adaptation of a stage spotlight'
parts = []

def node_mat(name, color, metal=0.0, rough=.5):
    m=bpy.data.materials.new(name)
    m.diffuse_color=(*color,1)
    m.use_nodes=True
    bs=m.node_tree.nodes.get('Principled BSDF')
    bs.inputs['Base Color'].default_value=(*color,1)
    bs.inputs['Metallic'].default_value=metal
    bs.inputs['Roughness'].default_value=rough
    return m,bs

bronze, bs = node_mat('M_DY_Bronze_Procedural_SOURCE',(.19,.084,.028),.8,.48)
nt=bronze.node_tree
coord=nt.nodes.new('ShaderNodeTexCoord')
noise=nt.nodes.new('ShaderNodeTexNoise'); noise.inputs['Scale'].default_value=14
noise.inputs['Detail'].default_value=3
nt.links.new(coord.outputs['Object'],noise.inputs['Vector'])
ramp=nt.nodes.new('ShaderNodeValToRGB')
ramp.color_ramp.elements[0].position=.18
ramp.color_ramp.elements[0].color=(.038,.022,.012,1)
ramp.color_ramp.elements[1].position=.85
ramp.color_ramp.elements[1].color=(.17,.105,.044,1)
e=ramp.color_ramp.elements.new(.52);e.color=(.29,.135,.046,1)
e=ramp.color_ramp.elements.new(.75);e.color=(.068,.10,.075,1)
nt.links.new(noise.outputs['Fac'],ramp.inputs[0]); nt.links.new(ramp.outputs[0],bs.inputs['Base Color'])
fine=nt.nodes.new('ShaderNodeTexNoise');fine.inputs['Scale'].default_value=350
fine.inputs['Detail'].default_value=2
nt.links.new(coord.outputs['Object'],fine.inputs['Vector'])
rough=nt.nodes.new('ShaderNodeMapRange');rough.inputs['To Min'].default_value=.35;rough.inputs['To Max'].default_value=.58
nt.links.new(fine.outputs['Fac'],rough.inputs[0]);nt.links.new(rough.outputs[0],bs.inputs['Roughness'])
bump=nt.nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.22;bump.inputs['Distance'].default_value=.00022
nt.links.new(fine.outputs['Fac'],bump.inputs['Height']);nt.links.new(bump.outputs[0],bs.inputs['Normal'])
bronze['Provenance']='Original local procedural shader; no downloaded bronze map, no baked texture'
edge,_=node_mat('M_DY_Bronze_Edge_SOURCE',(.28,.15,.055),.86,.32)
dark,_=node_mat('M_DY_BlackMetal_SOURCE',(.025,.028,.027),.7,.45)
reflector,_=node_mat('M_DY_Reflector_SOURCE',(.21,.205,.17),.9,.29)
rubber,_=node_mat('M_DY_Rubber_SOURCE',(.016,.02,.018),0,.8)
glass,gbs=node_mat('M_DY_OpticalWindow_SOURCE',(.36,.22,.085),.08,.16)
gbs.inputs['Transmission Weight'].default_value=.38
gbs.inputs['IOR'].default_value=1.46
gbs.inputs['Emission Color'].default_value=(.8,.37,.10,1)
gbs.inputs['Emission Strength'].default_value=.15
glass['Role']='Recessed decorative optical window behind the real UE KeyLight; not a replacement light'

wood,wbs=node_mat('M_DY_Wood_CC0_SOURCE',(.08,.046,.025),0,.56)
nt=wood.node_tree
uv=nt.nodes.new('ShaderNodeTexCoord')
images={}
for key,name in [('diff','wood_table_diff_2k.png'),('arm','wood_table_arm_2k.png'),('normal','wood_table_nor_dx_2k.png')]:
    img=bpy.data.images.load(str(OUT/'Sources'/name));img.name=name
    if key!='diff':img.colorspace_settings.name='Non-Color'
    tex=nt.nodes.new('ShaderNodeTexImage');tex.image=img
    nt.links.new(uv.outputs['UV'],tex.inputs['Vector']);images[key]=tex
tint=nt.nodes.new('ShaderNodeMixRGB');tint.blend_type='MULTIPLY';tint.inputs[0].default_value=1
tint.inputs[2].default_value=(.31,.25,.19,1)
nt.links.new(images['diff'].outputs['Color'],tint.inputs[1]);nt.links.new(tint.outputs[0],wbs.inputs['Base Color'])
split=nt.nodes.new('ShaderNodeSeparateColor');nt.links.new(images['arm'].outputs['Color'],split.inputs[0])
nt.links.new(split.outputs['Green'],wbs.inputs['Roughness'])
# Normal source is DirectX. Shader conversion preserves the original image pixels.
normsplit=nt.nodes.new('ShaderNodeSeparateColor');nt.links.new(images['normal'].outputs['Color'],normsplit.inputs[0])
invert=nt.nodes.new('ShaderNodeMath');invert.operation='SUBTRACT';invert.inputs[0].default_value=1
nt.links.new(normsplit.outputs['Green'],invert.inputs[1])
combine=nt.nodes.new('ShaderNodeCombineColor')
nt.links.new(normsplit.outputs['Red'],combine.inputs['Red']);nt.links.new(invert.outputs[0],combine.inputs['Green']);nt.links.new(normsplit.outputs['Blue'],combine.inputs['Blue'])
normal=nt.nodes.new('ShaderNodeNormalMap');normal.inputs['Strength'].default_value=.35
nt.links.new(combine.outputs[0],normal.inputs['Color']);nt.links.new(normal.outputs[0],wbs.inputs['Normal'])
wood['Provenance']='Poly Haven Wood Table, Dimitrios Savva, CC0; all three original 2K PNG files unchanged'

def finish(obj,name,mat,role,group,bevel=0):
    obj.name=name;obj.data.name=name+'_Mesh'
    obj.parent=root
    obj['Part_Role']=role;obj['Export_Group']=group
    if mat:obj.data.materials.append(mat)
    bpy.context.view_layer.objects.active=obj
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    if bevel:
        mod=obj.modifiers.new('Real rounded edge','BEVEL');mod.width=min(bevel,min(obj.dimensions)*.35);mod.segments=4
        mod.limit_method='ANGLE'
        bpy.ops.object.modifier_apply(modifier=mod.name)
    bm=bmesh.new();bm.from_mesh(obj.data)
    bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-8)
    bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=1e-9)
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
    bm.to_mesh(obj.data);bm.free();obj.data.update()
    for poly in obj.data.polygons:poly.use_smooth=True
    mod=obj.modifiers.new('Weighted corner normals','WEIGHTED_NORMAL');mod.keep_sharp=True;mod.weight=50
    # UV0 uses physical 1m repeat; the export adds separately packed UV1.
    if not obj.data.uv_layers:obj.data.uv_layers.new(name='UVMap')
    layer=obj.data.uv_layers.active
    for poly in obj.data.polygons:
        n=poly.normal
        axis=max(range(3),key=lambda i:abs(n[i]))
        for li in poly.loop_indices:
            p=obj.data.vertices[obj.data.loops[li].vertex_index].co
            if axis==0:uvpair=(p.y,p.z)
            elif axis==1:uvpair=(p.x,p.z)
            else:uvpair=(p.x,p.y)
            layer.data[li].uv=(uvpair[0]+.4,uvpair[1]+.2)
    parts.append(obj)
    return obj

def cube(name,loc,size,mat,role,group,bevel=.005):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc)
    o=bpy.context.object;o.dimensions=size
    return finish(o,name,mat,role,group,bevel)

def cylinder(name,loc,radius,depth,mat,role,group,axis='Z',vertices=96):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=radius,depth=depth,location=loc)
    o=bpy.context.object
    if axis=='X':o.rotation_euler[1]=math.pi/2
    elif axis=='Y':o.rotation_euler[0]=math.pi/2
    bpy.ops.object.transform_apply(location=False,rotation=True,scale=False)
    return finish(o,name,mat,role,group,.002)

def torus(name,loc,major,minor,mat,role,group,axis='X'):
    bpy.ops.mesh.primitive_torus_add(major_segments=128,minor_segments=16,location=loc,major_radius=major,minor_radius=minor)
    o=bpy.context.object
    if axis=='X':o.rotation_euler[1]=math.pi/2
    elif axis=='Y':o.rotation_euler[0]=math.pi/2
    bpy.ops.object.transform_apply(location=False,rotation=True,scale=False)
    return finish(o,name,mat,role,group)

def lathe_x(name,profile,mat,role,group,segments=128):
    verts=[];faces=[]
    for x,r in profile:
        for j in range(segments):
            a=math.tau*j/segments;verts.append((x,r*math.cos(a),r*math.sin(a)))
    for i in range(len(profile)-1):
        for j in range(segments):
            j2=(j+1)%segments
            faces.append((i*segments+j,i*segments+j2,(i+1)*segments+j2,(i+1)*segments+j))
    me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update()
    ob=bpy.data.objects.new(name,me);scene.collection.objects.link(ob)
    bpy.context.view_layer.objects.active=ob;ob.select_set(True)
    finish(ob,name,mat,role,group)
    # Cylindrical UV, a real seam at the underside, without tiny random islands.
    uv=ob.data.uv_layers.active
    for p in me.polygons:
        row=p.index//segments;j=p.index%segments
        coords=[(j/segments,row/(len(profile)-1)),((j+1)/segments,row/(len(profile)-1)),((j+1)/segments,(row+1)/(len(profile)-1)),(j/segments,(row+1)/(len(profile)-1))]
        for li,pair in zip(p.loop_indices,coords):uv.data[li].uv=pair
    return ob

# All metal geometry remains behind KeyLight X=.45m. Hollow casing wall: 6mm.
outer=[(-.335,.035),(-.327,.075),(-.31,.116),(-.277,.15),(-.235,.18),(-.18,.204),(-.10,.226),(.02,.239),(.14,.25),(.24,.259),(.335,.263),(.395,.264),(.413,.264)]
inner=[(x,r-.006) for x,r in reversed(outer)]
lathe_x('Lamp_Copper_HollowShell',outer+inner+[outer[0]],bronze,'6mm closed shell wall; empty front aperture','BODY')
torus('Lamp_RolledFrontRim',(.41,0,0),.262,.010,edge,'10mm rolled front rim; tip X42cm','BODY')
torus('Lamp_UpperBodySeam',(-.16,0,0),.211,.004,dark,'Rear casing seam','BODY')
torus('Lamp_RearServiceRing',(-.30,0,0),.132,.007,edge,'Service cap rim','BODY')
# Reflector and optics are behind the real engine emitter.
lathe_x('Lamp_InnerReflector',[(.38,.251),(.30,.245),(.20,.21),(.10,.17),(.01,.125),(-.06,.083),(-.062,.079),(.015,.119),(.106,.164),(.207,.204),(.30,.239),(.38,.245),(.38,.251)],reflector,'Open recessed reflector, 6mm real thickness','BODY')
cylinder('Lamp_RecessedOpticalWindow',(.27,0,0),.201,.012,glass,'Decorative optical window behind KeyLight, not runtime light','BODY','X')
torus('Lamp_OpticalWindowRetainer',(.28,0,0),.201,.007,dark,'Recessed optics retainer','BODY')

# Back handle and fastening construction instead of unrelated ornament.
for side in [-1,1]:
    cube(f'Lamp_HandleSocket_{side}',(-.29,side*.075,.105),(.045,.025,.03),dark,'Rear grip mounting socket','BODY',.004)
    cube(f'Lamp_HandleArm_{side}',(-.365,side*.075,.105),(.16,.018,.018),bronze,'Rear handle bracket','BODY',.006)
cylinder('Lamp_RearWoodGrip',(-.435,0,.105),.019,.167,wood,'Rear tactile wood handle','BODY','Y',48)
for side in [-1,1]:
    cylinder(f'Lamp_GripEnd_{side}',(-.435,side*.087,.105),.022,.014,edge,'Wood grip retaining cap','BODY','Y',64)
    cylinder(f'Lamp_TiltTrunnion_{side}',(-.035,side*.257,-.025),.045,.077,dark,'Mechanical tilt axis across Y','BODY','Y')
    cylinder(f'Lamp_TiltClampWheel_{side}',(-.035,side*.32,-.025),.062,.035,bronze,'Friction clamp wheel, functional circular grip','BODY','Y')
    torus(f'Lamp_TiltClampRim_{side}',(-.035,side*.337,-.025),.051,.007,edge,'Clamp gripping edge','BODY','Y')
    cylinder(f'Lamp_ClampPin_{side}',(-.035,side*.343,-.025),.015,.009,dark,'Visible clamp fastening pin','BODY','Y',32)
for angle in range(0,360,60):
    a=math.radians(angle)
    cylinder(f'Lamp_RimScrew_{angle}',(.385,.25*math.cos(a),.25*math.sin(a)),.009,.011,dark,'Recessed rim screw behind emitter','BODY','X',32)

# Copper U-yoke is the load path from side tilt axes to the wooden mast.
for side in [-1,1]:
    cube(f'Stand_YokeArm_{side}',(-.035,side*.282,-.253),(.047,.028,.488),bronze,'Continuous yoke side arm supports tilt pin','STAND',.014)
cube('Stand_YokeBridge',(-.035,0,-.496),(.065,.585,.045),bronze,'Lower yoke connects both arms','STAND',.014)
cylinder('Stand_YokeStem',(-.035,0,-.556),.039,.105,dark,'Stem under yoke','STAND')
torus('Stand_YokeStemCollar',(-.035,0,-.593),.039,.009,edge,'Upper support collar','STAND','Z')

# One continuous wood mast, fitted metal sleeves, and a low stable sled footprint.
bpy.ops.mesh.primitive_cone_add(vertices=96,radius1=.063,radius2=.047,depth=2.34,location=(-.035,0,-1.78))
mast=finish(bpy.context.object,'Stand_WoodMast',wood,'Continuous tapered wood mast from Z-61cm to -295cm','STAND',.004)
# Wood Table boards run in U. Follow the mast length and sample one narrow board.
for poly in mast.data.polygons:
    for li in poly.loop_indices:
        p=mast.data.vertices[mast.data.loops[li].vertex_index].co
        if abs(poly.normal.z)<.8:
            mast.data.uv_layers.active.data[li].uv=(p.z+1.3,.42+math.atan2(p.y,p.x)/math.tau*.065)
for i,z in enumerate([-.63,-.86,-2.78,-2.91]):
    cylinder(f'Stand_BronzeSleeve_{i}',(-.035,0,z),.067 if z<-2 else .053,.065,bronze,'Protective mast sleeve','STAND')
    torus(f'Stand_SleeveEdge_{i}',(-.035,0,z+.03),.067 if z<-2 else .053,.0035,edge,'Rolled sleeve edge','STAND','Z')
cylinder('Stand_AdjustmentLock',(-.035,-.07,-.85),.028,.028,bronze,'Friction locking knob on clamp sleeve','STAND','Y',64)
cylinder('Stand_AdjustmentBolt',(-.035,-.045,-.85),.009,.05,dark,'Lock bolt','STAND','Y',32)
cube('Stand_BaseCrossTie',(-.035,0,-2.988),(.73,.145,.12),wood,'Wood cross tie distributing mast load','STAND',.009)
for side in [-1,1]:
    x=-.035+side*.32
    cube(f'Stand_Runner_{side}',(x,0,-3.031),(.13,.99,.13),wood,'Longitudinal sled foot; stable movable rail-compatible support','STAND',.008)
    for end in [-1,1]:
        cube(f'Stand_RunnerEndCap_{side}_{end}',(x,end*.455,-3.029),(.144,.058,.14),bronze,'Runner end protector','STAND',.009)
        cylinder(f'Stand_FootFastener_{side}_{end}',(x,end*.40,-2.957),.015,.009,dark,'Foot through-fastener head','STAND','Z',32)
    cube(f'Stand_RunnerSole_{side}',(x,0,-3.096),(.127,.89,.008),rubber,'Thin protective sole, bottom exactly Z-310cm','STAND',.003)

# Source anchors are Empty metadata and never exported as blocking geometry.
for name,loc,role in [('ANCHOR_UE_KeyLight_45cm',(.45,0,0),'Existing Movable SpotLight, retained'),('ANCHOR_UE_LampStand_native',(0,0,-.95),'Existing stand component pivot'),('ANCHOR_Floor_0world',(0,0,-3.10),'At actor world Z310, this is floor world0'),('ANCHOR_TiltAxis',(-.035,0,-.025),'Visual tilt axis only; does not add gameplay')]:
    ob=bpy.data.objects.new(name,None);scene.collection.objects.link(ob);ob.location=loc;ob.parent=root;ob.empty_display_size=.08;ob['Role']=role

def bounds(objects):
    pts=[o.matrix_world@Vector(p) for o in objects for p in o.bound_box]
    return {'min_cm':[round(min(p[i] for p in pts)*100,4) for i in range(3)],'max_cm':[round(max(p[i] for p in pts)*100,4) for i in range(3)],'size_cm':[round((max(p[i] for p in pts)-min(p[i] for p in pts))*100,4) for i in range(3)]}

bpy.context.view_layer.update()
assert max((o.matrix_world@v.co).x for o in parts for v in o.data.vertices)<.45, 'Exterior blocks light forward half space'
assert abs(min((o.matrix_world@v.co).z for o in parts for v in o.data.vertices)+3.1)<.001
assert all(len(o.data.uv_layers)>0 for o in parts)
assert all(p.area>0 for o in parts for p in o.data.polygons), 'Source has zero-area face'
source_data={'name':'DY Spotlight Exterior / 木铜舞台主灯','blender_version':bpy.app.version_string,'source_root':'Root_Back_Source','units':'Blender meter, UE centimeter; FBX_UNIT_SCALE export','authority':['D:/灯影山海/Docs/SCENE_ART_QUALITY_SPEC.md','D:/灯影山海/Source/DengYingShanHai/Private/Interaction/DYLightRigActor.cpp','D:/灯影山海/Saved/Audit-2026-10-12-FramePostPlacementDev/verify-Run1/Result.json scene_contract'], 'runtime_light_unchanged':{'type':'Movable SpotLight','relative_cm':[45,0,0],'forward':'+X','outer_cone_deg':38,'source_radius_cm':4},'design_status':'Contemporary creative adaptation; no historical reconstruction claim','bounds_actor_local':bounds(parts),'groups':{},'part_count':len(parts),'triangles_source':sum(len(p.vertices)-2 for o in parts for p in o.data.polygons),'material_provenance':{'wood':'Poly Haven Wood Table / Dimitrios Savva / CC0 / original 2K images unchanged','metal':'Original procedural shader, not downloaded PBR texture, not baked','optics':'Original local shader; optical window stays behind actual KeyLight'},'parts':[{'name':o.name,'role':o['Part_Role'],'group':o['Export_Group'],'bounds':bounds([o]),'uv0':'physical planar or analytical cylindrical UV'} for o in parts]}
for group in ['BODY','STAND']:
    source_data['groups'][group]=bounds([o for o in parts if o['Export_Group']==group])
source_data['checks']={'all_mesh_geometry_behind_emitter_x45cm':True,'frontmost_geometry_cm':source_data['bounds_actor_local']['max_cm'][0],'minimum_forward_clearance_cm':round(45-source_data['bounds_actor_local']['max_cm'][0],4),'ground_contact_local_z_cm':-310,'uv0_all_source_meshes':True}
(OUT/'LAMP_SOURCE_MANIFEST.json').write_text(json.dumps(source_data,ensure_ascii=False,indent=2),encoding='utf-8')

# Save full editable source with separate named structural parts and packed original images.
bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'DY_HeroSpotlight_Source.blend'))

def export_group(group,pivot,name):
    bpy.ops.object.select_all(action='DESELECT')
    clones=[]
    for orig in parts:
        if orig['Export_Group']!=group:continue
        o=orig.copy();o.data=orig.data.copy();scene.collection.objects.link(o)
        o.parent=None;o.matrix_world=orig.matrix_world.copy();o.select_set(True);clones.append(o)
    bpy.context.view_layer.objects.active=clones[0];bpy.ops.object.join()
    merged=bpy.context.object;merged.name=name
    scene.cursor.location=pivot;bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
    # Local vertices retain native stand location after an identity-scale import.
    merged.location=(0,0,0)
    merged.data.uv_layers.new(name='UVLightmap')
    merged.data.uv_layers.active_index=1
    bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(angle_limit=math.radians(66),island_margin=.006,area_weight=.2)
    bpy.ops.object.mode_set(mode='OBJECT');merged.data.uv_layers.active_index=0
    bpy.ops.export_scene.fbx(filepath=str(OUT/(name+'.fbx')),use_selection=True,object_types={'MESH'},apply_unit_scale=True,apply_scale_options='FBX_SCALE_UNITS',axis_forward='X',axis_up='Z',use_mesh_modifiers=True,mesh_smooth_type='FACE',add_leaf_bones=False,bake_anim=False,path_mode='COPY',embed_textures=False)
    info={'mesh_name':name,'pivot_actor_local_cm':[round(c*100,4) for c in pivot],'bounds_component_local':bounds([merged]),'uv_layers':[u.name for u in merged.data.uv_layers],'material_slots':[m.name for m in merged.data.materials]}
    bpy.data.objects.remove(merged,do_unlink=True)
    return info

exports=[export_group('BODY',(0,0,0),'SM_DY_LampBody_Source'),export_group('STAND',(0,0,-.95),'SM_DY_LampStand_Source')]
(OUT/'LAMP_EXPORT_CONTRACT.json').write_text(json.dumps({'exports':exports,'integration':{'LampBody':{'relative_cm':[0,0,0],'rotation_deg':[0,0,0],'scale':[1,1,1]},'LampStand':{'relative_cm':[0,0,-95],'rotation_deg':[0,0,0],'scale':[1,1,1]},'KeyLight':'Do not change any property','collision':'Preserve existing query interaction profile; use simple collision, never per-poly or blocking movement'}},ensure_ascii=False,indent=2),encoding='utf-8')

# A neutral review scene, excluded from FBX. No spotlight simulation or UE changes.
bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-3.101))
floor=bpy.context.object;floor.name='ReviewFloor_NOT_EXPORT'
fm,_=node_mat('ReviewFloor',(.045,.05,.055),0,.7);floor.data.materials.append(fm)
def area(name,loc,power,size,target,color):
    data=bpy.data.lights.new(name,'AREA');data.energy=power;data.shape='DISK';data.size=size;data.color=color
    ob=bpy.data.objects.new(name,data);scene.collection.objects.link(ob);ob.location=loc
    ob.rotation_euler=(Vector(target)-ob.location).to_track_quat('-Z','Y').to_euler()
area('ReviewKey',(2.5,-3,2.5),950,4,(0,0,-.75),(1,.83,.67))
area('ReviewFill',(-2,-.8,1),700,3,(0,0,-.75),(.61,.73,1))
area('ReviewRim',(0,3,1),1200,3,(0,0,-1),(1,.84,.66))
camdata=bpy.data.cameras.new('ReviewCamera');cam=bpy.data.objects.new('ReviewCamera',camdata);scene.collection.objects.link(cam);scene.camera=cam
def render(name,loc,target,ortho,res):
    cam.location=loc;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler()
    camdata.type='ORTHO';camdata.ortho_scale=ortho
    scene.render.resolution_x=res[0];scene.render.resolution_y=res[1]
    scene.render.filepath=str(OUT/name);bpy.ops.render.render(write_still=True)
render('Lamp_Full_Review.png',(5,-7,2.15),(-.035,0,-1.48),4.5,(1440,1920))
render('Lamp_Head_Review.png',(2.4,-2.8,.85),(0,0,-.17),1.47,(1920,1440))
render('Lamp_Side_Review.png',(0,-8,.2),(-.02,0,-1.48),4.22,(1440,1920))
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'DY_HeroSpotlight_Source.blend'))
print('LAMP_SOURCE_EXPORT_RENDER_COMPLETE', json.dumps(source_data['checks']))
