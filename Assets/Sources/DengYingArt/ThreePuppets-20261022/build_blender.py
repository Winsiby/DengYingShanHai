"""Build true perforated, rigid-skinned shadow puppets and audit their FBX exports."""
from pathlib import Path
import bpy,bmesh,json,math,sys,hashlib
from mathutils import Vector
ROOT=Path(__file__).resolve().parent
RUN=ROOT/(sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'Run1')
CHECKS=[]
def check(v,msg):
    if not v:raise AssertionError(msg)
    CHECKS.append(msg)
def activate(o):
    bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o

def mat(name,color,rough=.7,metal=0):
    m=bpy.data.materials.new(name);m.use_nodes=True
    b=m.node_tree.nodes.get('Principled BSDF');b.inputs['Base Color'].default_value=(*color,1);b.inputs['Roughness'].default_value=rough;b.inputs['Metallic'].default_value=metal
    return m

def image_mat(name,path,normal=None,orm=None):
    m=mat(name,(.5,.2,.05));ns=m.node_tree.nodes;links=m.node_tree.links;b=ns.get('Principled BSDF')
    t=ns.new('ShaderNodeTexImage');t.image=bpy.data.images.load(str(path));t.image.pack();links.new(t.outputs['Color'],b.inputs['Base Color'])
    if normal:
        t=ns.new('ShaderNodeTexImage');t.image=bpy.data.images.load(str(normal));t.image.colorspace_settings.name='Non-Color';t.image.pack()
        split=ns.new('ShaderNodeSeparateColor');combine=ns.new('ShaderNodeCombineColor');inv=ns.new('ShaderNodeMath');inv.operation='SUBTRACT';inv.inputs[0].default_value=1
        links.new(t.outputs['Color'],split.inputs[0]);links.new(split.outputs[0],combine.inputs[0]);links.new(split.outputs[1],inv.inputs[1]);links.new(inv.outputs[0],combine.inputs[1]);links.new(split.outputs[2],combine.inputs[2])
        n=ns.new('ShaderNodeNormalMap');n.inputs['Strength'].default_value=.45;links.new(combine.outputs[0],n.inputs['Color']);links.new(n.outputs['Normal'],b.inputs['Normal'])
    if orm:
        t=ns.new('ShaderNodeTexImage');t.image=bpy.data.images.load(str(orm));t.image.colorspace_settings.name='Non-Color';t.image.pack();sep=ns.new('ShaderNodeSeparateColor');links.new(t.outputs['Color'],sep.inputs[0]);links.new(sep.outputs[1],b.inputs['Roughness']);links.new(sep.outputs[2],b.inputs['Metallic'])
    return m

def point(model,p,x=0):
    s=model['scale_cm_per_pixel'];u,v=model['origin_px'];return Vector((x,(p[0]-u)*s,(v-p[1])*s))
def mesh_obj(name,v,f,uv,slots,bone,mats):
    mesh=bpy.data.meshes.new(name+'_Geometry');mesh.from_pydata(v,[],f);mesh.update()
    o=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(o)
    for m in mats:mesh.materials.append(m)
    layer=mesh.uv_layers.new(name='UV0')
    for face,slot in zip(mesh.polygons,slots):
        face.material_index=slot
        if slot==1:
            ps=[mesh.vertices[mesh.loops[i].vertex_index].co for i in face.loop_indices]
            axis=1 if max(p.y for p in ps)-min(p.y for p in ps)>max(p.z for p in ps)-min(p.z for p in ps) else 2
            for loop in face.loop_indices:
                p=mesh.vertices[mesh.loops[loop].vertex_index].co;layer.data[loop].uv=(p[axis]*.02,p.x*.5)
        else:
            for loop in face.loop_indices:layer.data[loop].uv=uv[mesh.loops[loop].vertex_index]
    g=o.vertex_groups.new(name=bone);g.add(list(range(len(v))),1,'REPLACE')
    o['rigid_piece']=True;o['bone']=bone
    bm=bmesh.new();bm.from_mesh(mesh)
    check(all(e.is_manifold for e in bm.edges),name+' closed manifold shells')
    check(bm.calc_volume(signed=True)>0,name+' positive volume');bm.free()
    return o

def aim(o,target):o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
def add_pin(name,location,bone,brass):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=12,ring_count=6,radius=1,location=location)
    o=bpy.context.object;o.name='Rivet_'+name;o.scale=(.38,1.45,1.45);bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
    o.data.materials.append(brass)
    for p in o.data.polygons:p.use_smooth=True
    g=o.vertex_groups.new(name=bone);g.add(list(range(len(o.data.vertices))),1,'REPLACE')
    return o

def build(model_path):
    CHECKS.clear();model=json.loads(model_path.read_text(encoding='utf8'));spec=model['source'];ident=model['id'];out=model_path.parent
    # Authored proportion corrections: scale a bone's leather pieces about its anchor joint.
    for adj in spec.get('part_scale',[]):
        pivs={b['name']:Vector(b['pivot_cm']) for b in model['bones']};anc=pivs[adj['anchor']]
        moved=[]
        for p in model['parts']:
            if p['bone'] in adj['bones']:
                for v in p['vertices']:v[1]=anc.y+(v[1]-anc.y)*adj['factor'];v[2]=anc.z+(v[2]-anc.z)*adj['factor']
                moved.append(p['name'])
        # Joints inside the corrected subtree must move with their leather.
        for b in model['bones']:
            if b['name'] in adj['bones'] or (b['parent'] and b['parent'] in adj['bones']):
                q=Vector(b['pivot_cm']);b['pivot_cm']=[q.x,anc.y+(q.y-anc.y)*adj['factor'],anc.z+(q.z-anc.z)*adj['factor']]
        check(bool(moved),'Proportion correction applied to '+','.join(moved))
    bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
    scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=.01;scene.unit_settings.length_unit='CENTIMETERS';scene.render.fps=30;scene.frame_start=1;scene.frame_end=31
    skin=image_mat('Skin',out/f'T_DY_{ident}_BaseColor.png',out/f'T_DY_{ident}_NormalDX.png',out/f'T_DY_{ident}_ORM.png')
    edge=mat('CutEdge',(.105,.028,.012),.82);brass=mat('Brass',(.38,.22,.06),.35,.82);bamboo=mat('Bamboo',(.28,.14,.04),.65)
    mats=[skin,edge,brass];objects=[]
    for p in model['parts']:objects.append(mesh_obj(p['name'],p['vertices'],p['faces'],p['uv'],p['slots'],p['bone'],mats))
    bones=list(model['bones'])
    # A real leather shutter closes the eye aperture in the Night action.
    eye=spec.get('eyelid_polygon_px');closed_material=None
    if eye and (out/f'T_DY_{ident}_ClosedBaseColor.png').exists():
        closed_material=image_mat('EyelidSkin',out/f'T_DY_{ident}_ClosedBaseColor.png')
        phead=next(b for b in bones if b['name']=='Head')
        bones.append({'name':'Eyelid','parent':'Head','pivot_cm':list(point(model,spec['eye_aperture_polygon_px'][0]))})
        from mathutils.geometry import tessellate_polygon
        pts=[point(model,p,1.9) for p in eye]
        if sum(p.y*q.z-q.y*p.z for p,q in zip(pts,pts[1:]+pts[:1]))<0:pts.reverse();eye=list(reversed(eye))
        n=len(pts);vs=[list(p) for p in pts]+[[p.x-.12,p.y,p.z] for p in pts]
        index={tuple(p):i for i,p in enumerate(pts)};faces=[]
        for tri in tessellate_polygon([pts]):
            inds=[int(p) if isinstance(p,int) else index[tuple(p)] for p in tri]
            if (pts[inds[1]]-pts[inds[0]]).cross(pts[inds[2]]-pts[inds[0]]).x<0:inds.reverse()
            faces.extend([inds,[n+i for i in reversed(inds)]])
        for i in range(n):j=(i+1)%n;faces.extend([[i,n+i,n+j],[i,n+j,j]])
        u0,v0,u1,v1=model['bounds_px'];uv=[((p[0]-u0)/(u1-u0),1-(p[1]-v0)/(v1-v0)) for p in eye]*2
        objects.append(mesh_obj('DayNight_EyeShutter',vs,faces,uv,[0]*len(faces),'Eyelid',[closed_material]))
    for b in bones:
        if b['name'] in ('Root','Eyelid'):continue
        loc=Vector(b['pivot_cm']);loc.x=2.1
        objects.append(add_pin(b['name'],loc,b['name'],brass))
    data=bpy.data.armatures.new(ident+'_RigidJoints');arm=bpy.data.objects.new('Armature',data);bpy.context.collection.objects.link(arm);activate(arm);bpy.ops.object.mode_set(mode='EDIT')
    for b in bones:
        eb=data.edit_bones.new(b['name']);eb.head=b['pivot_cm'];eb.tail=Vector(b['pivot_cm'])+Vector((0,0,8));eb.roll=0
        if b['parent']:eb.parent=data.edit_bones[b['parent']]
        eb.use_connect=False
    bpy.ops.object.mode_set(mode='OBJECT');arm.show_in_front=True;data.display_type='STICK'
    # Retain separate, editable construction pieces in the native source file.
    archive=bpy.data.collections.new('AUTHORING_PIECES');scene.collection.children.link(archive);archive.hide_render=True;archive.hide_viewport=True
    for o in objects:
        dup=o.copy();dup.data=o.data.copy();dup.name='Source_'+o.name;archive.objects.link(dup)
    bpy.ops.object.select_all(action='DESELECT')
    for o in objects:o.select_set(True)
    bpy.context.view_layer.objects.active=objects[0];bpy.ops.object.join();mesh=bpy.context.object;mesh.name='SK_DY_'+ident;mesh.parent=arm;mod=mesh.modifiers.new('Rigid cut-leather joints','ARMATURE');mod.object=arm
    check(all(len(v.groups)==1 and abs(v.groups[0].weight-1)<1e-6 for v in mesh.data.vertices),'Every vertex rigidly bound to exactly one bone')
    mesh.data.calc_loop_triangles();triangles=len(mesh.data.loop_triangles)
    check(triangles<26000,'Hero mesh under 26000 triangles')
    for b in bones:check(b['name'] in arm.data.bones,'Bone present '+b['name'])
    rods=[]
    min_z=min(v.co.z for v in mesh.data.vertices)
    grip=Vector((0.0,0.0,min_z-6.0))  # Operator handle directly under the puppet.
    for r in spec['rods']:
        a=point(model,r['attach_px'],-3.4)
        if r.get('spar_px'):
            # Wing/axe/shield spars stay inside their own leather so no line crosses an open gap.
            b=point(model,r['spar_px'],-3.4);length=(b-a).length
        else:
            b=grip;length=(a-b).length
        bpy.ops.mesh.primitive_cylinder_add(vertices=12,radius=.55,depth=length,location=(a+b)/2)
        bpy.context.object.rotation_mode='QUATERNION';bpy.context.object.rotation_quaternion=(b-a).to_track_quat('Z','Y')
        rod=bpy.context.object;rod.name=r['name'];rod.data.materials.append(edge);activate(rod);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
        g=rod.vertex_groups.new(name=r['bone']);g.add(list(range(len(rod.data.vertices))),1,'REPLACE');rod.parent=arm;mod=rod.modifiers.new('Control rod follows rigid joint','ARMATURE');mod.object=arm;rods.append(rod)
    # A brass grip knob terminates the operator handle so the rod reads as held, not cropped.
    if any(not r.get('spar_px') for r in spec['rods']):
        knob=add_pin('GripKnob',grip,'Root',brass);knob.scale=(2.2,1.5,1.5);bpy.ops.object.transform_apply(location=True,rotation=False,scale=True)
        knob.parent=arm;mod=knob.modifiers.new('Grip knob follows body','ARMATURE');mod.object=arm;rods.append(knob)
    # Bake the control rods into the puppet mesh so the UE asset needs no extra components.
    activate(mesh)
    for r in rods:r.select_set(True)
    bpy.ops.object.join()
    mesh=bpy.context.object
    check(len(mesh.vertex_groups)>0 and all(r['bone'] in [g.name for g in mesh.vertex_groups] for r in spec['rods']),'Control rods joined into the puppet mesh on their own bones')
    mesh.data.calc_loop_triangles();triangles=len(mesh.data.loop_triangles)
    check(triangles<26000,'Hero mesh including control rods under 26000 triangles')
    check(all(len(v.groups)==1 and abs(v.groups[0].weight-1)<1e-6 for v in mesh.data.vertices),'Every vertex including rods rigidly bound to exactly one bone')
    def pose(p):
        for b in arm.pose.bones:
            b.rotation_mode='XYZ';b.rotation_euler=(math.radians(p.get('angles_deg',{}).get(b.name,0)),0,0);b.scale=(1,1,1)
            if b.name=='Eyelid':b.scale=(1,1,1) if p['name']=='Night' else (.0001,.0001,.0001)
        bpy.context.view_layer.update()
    arm.animation_data_create();actions=[];pose_bounds=[]
    for p in spec['poses']:
        action=bpy.data.actions.new('A_DY_'+ident+'_'+p['name']);action.use_fake_user=True;arm.animation_data.action=action
        for frame in (1,31):
            scene.frame_set(frame);pose(p)
            for b in arm.pose.bones:
                b.keyframe_insert(data_path='rotation_euler',frame=frame,group=b.name);b.keyframe_insert(data_path='scale',frame=frame,group=b.name)
        scene.frame_set(1);pose(p)
        ev=mesh.evaluated_get(bpy.context.evaluated_depsgraph_get());em=ev.to_mesh();coords=[v.co for v in em.vertices]
        check(all(math.isfinite(v) for co in coords for v in co),p['name']+' finite deformed geometry')
        pose_bounds.append({'pose':p['name'],'bounds_cm':[[min(v[i] for v in coords),max(v[i] for v in coords)] for i in range(3)]});ev.to_mesh_clear();actions.append(action)
    arm.animation_data.action=actions[0];scene.frame_set(1);pose(spec['poses'][0])
    def select_export():
        bpy.ops.object.select_all(action='DESELECT');arm.select_set(True);mesh.select_set(True);bpy.context.view_layer.objects.active=arm
    opts=dict(use_selection=True,object_types={'ARMATURE','MESH'},global_scale=1,apply_unit_scale=True,apply_scale_options='FBX_SCALE_NONE',axis_forward='-Z',axis_up='Y',add_leaf_bones=False,primary_bone_axis='Y',secondary_bone_axis='X',armature_nodetype='NULL',use_armature_deform_only=False,path_mode='AUTO',embed_textures=False)
    select_export();bpy.ops.export_scene.fbx(filepath=str(out/(mesh.name+'.fbx')),bake_anim=False,**opts)
    for action,p in zip(actions,spec['poses']):
        arm.animation_data.action=action;scene.frame_set(1);pose(p);select_export()
        bpy.ops.export_scene.fbx(filepath=str(out/(action.name+'.fbx')),bake_anim=True,bake_anim_use_all_actions=False,bake_anim_use_nla_strips=False,bake_anim_use_all_bones=True,bake_anim_force_startend_keying=True,**opts)
    arm.animation_data.action=actions[0];scene.frame_set(1);pose(spec['poses'][0])
    # Interchange source OBJ contains only the rest-state puppet, never review props.
    activate(mesh);bpy.ops.wm.obj_export(filepath=str(out/('SM_DY_'+ident+'_Rest.obj')),export_selected_objects=True,apply_modifiers=True,forward_axis='NEGATIVE_Z',up_axis='Y',export_materials=True)
    bpy.ops.object.select_all(action='DESELECT')
    # Neutral model review; no source artwork card is rendered.
    scene.render.engine='BLENDER_EEVEE_NEXT';scene.render.resolution_x=1600;scene.render.resolution_y=1200;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.view_settings.view_transform='AgX'
    scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.16,.18,.22,1);scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.6
    height=model['height_cm'];width=model['width_cm'];target=(0,0,height*.51)
    for loc,power,size in (((300,-150,height+150),1800000,300),((250,180,70),650000,260)):
        bpy.ops.object.light_add(type='AREA',location=loc);l=bpy.context.object;l.name='REVIEW_Softbox';l.data.energy=power;l.data.shape='DISK';l.data.size=size;aim(l,target)
    bpy.ops.object.camera_add(location=(650,0,height*.5));cam=bpy.context.object;cam.name='REVIEW_Camera';cam.data.type='ORTHO';cam.data.ortho_scale=max(width*1.18,height*1.5);scene.camera=cam;aim(cam,target)
    previews=[]
    for pi,p in enumerate(spec['poses']):
        arm.animation_data.action=actions[pi];scene.frame_set(1);pose(p);cam.location=(650,0,height*.5);aim(cam,target)
        scene.render.filepath=str(out/('Preview_'+p['name']+'.png'));bpy.ops.render.render(write_still=True);previews.append(scene.render.filepath)
    arm.animation_data.action=actions[0];scene.frame_set(1);pose(spec['poses'][0]);cam.location=(570,-300,height*.75);aim(cam,target);scene.render.filepath=str(out/'Preview_Oblique.png');bpy.ops.render.render(write_still=True);previews.append(scene.render.filepath)
    # Use an actual point light and receiver for a silhouette review.
    for o in list(scene.objects):
        if o.type=='LIGHT':o.hide_render=True
    paper=mat('REVIEW_Paper',(.65,.59,.45),.9)
    bpy.ops.mesh.primitive_plane_add(size=1,location=(-55,0,height*.5),rotation=(0,math.pi/2,0));screen=bpy.context.object;screen.name='REVIEW_ShadowReceiver';screen.scale=(height*2.2,max(width*1.8,240),1);screen.data.materials.append(paper)
    bpy.ops.object.light_add(type='POINT',location=(420,-70,height*.72));key=bpy.context.object;key.name='REVIEW_MovableEquivalentPoint';key.data.energy=1800000;key.data.shadow_soft_size=.4
    scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.04
    cam.location=(650,-5,height*.5);aim(cam,(-55,0,height*.5));cam.data.ortho_scale=max(width*1.65,height*1.9)
    for o in [mesh]:o.hide_render=True
    # Camera-ray visibility disabled only in Cycles: shadow-only capture uses cycles CPU.
    mesh.hide_render=False;scene.render.engine='CYCLES';scene.cycles.samples=16;scene.cycles.use_denoising=True;mesh.visible_camera=False
    scene.render.filepath=str(out/'Preview_RealShadow.png');bpy.ops.render.render(write_still=True);previews.append(scene.render.filepath)
    mesh.visible_camera=True;screen.hide_render=True;key.hide_render=True;scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.6
    for o in scene.objects:
        if o.name.startswith('REVIEW_Softbox'):o.hide_render=False
    scene.render.engine='BLENDER_EEVEE_NEXT';cam.location=(650,0,height*.5);aim(cam,target);cam.data.ortho_scale=max(width*1.18,height*1.5)
    select_export();bpy.ops.wm.save_as_mainfile(filepath=str(out/(ident+'_Puppet_Source.blend')))
    # Cold import the actual exported FBX, compare real units, rig and weights.
    before=set(bpy.data.objects);bpy.ops.import_scene.fbx(filepath=str(out/(mesh.name+'.fbx')),use_anim=False)
    imported=[o for o in bpy.data.objects if o not in before];im=[o for o in imported if o.type=='MESH'];ia=[o for o in imported if o.type=='ARMATURE']
    check(len(im)==1 and len(ia)==1,'Cold FBX import has one skeletal mesh and one armature')
    check(len(ia[0].data.bones)==len(bones),'Cold FBX bone count matches')
    check(all(len(v.groups)==1 for v in im[0].data.vertices),'Cold FBX preserves rigid weights')
    im[0].data.calc_loop_triangles();check(len(im[0].data.loop_triangles)==triangles,'Cold FBX triangle count matches')
    src=[mesh.matrix_world@v.co for v in mesh.data.vertices];fresh=[im[0].matrix_world@v.co for v in im[0].data.vertices]
    source_bounds=[[min(v[i] for v in src),max(v[i] for v in src)] for i in range(3)];fbx_bounds=[[min(v[i] for v in fresh),max(v[i] for v in fresh)] for i in range(3)]
    check(max(abs(a-b) for ra,rb in zip(source_bounds,fbx_bounds) for a,b in zip(ra,rb))<.02,'Cold FBX world centimetre bounds match within 0.02 cm')
    report={'status':'PASS-MODEL-SOURCE-FBX-ROUNDTRIP','id':ident,'vertices':len(mesh.data.vertices),'triangles':triangles,'bone_count':len(bones),'part_count':len(model['parts']),'control_rods_in_mesh':len(spec['rods']),'real_cutouts':sum(p['real_cutouts'] for p in model['parts']),'source_bounds_cm':source_bounds,'fresh_fbx_bounds_cm':fbx_bounds,'skin_thickness_cm':spec['thickness_cm'],'material_slots':[m.name for m in mesh.data.materials],'poses':pose_bounds,'previews':previews,'checks':CHECKS,'provenance':model['provenance'],'runtime_integration':False,'human_art_acceptance':False}
    (out/'MODEL_VERIFICATION.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps({k:report[k] for k in ('status','id','triangles','bone_count','part_count','real_cutouts')}) ,flush=True)

for p in sorted(RUN.glob('*/prepared.json')):
    if len(sys.argv)>sys.argv.index('--')+2 and p.parent.name!=sys.argv[sys.argv.index('--')+2]:continue
    build(p)


