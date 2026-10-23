
import bpy, math, json, os, sys
from mathutils import Vector, Quaternion

ARG = sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else ''
SPEC_PATH = r"D:\灯影山海\Assets\Sources\DengYingArt\ThreePuppets-20261022\perf_clips.json"
spec = json.load(open(SPEC_PATH, encoding='utf-8'))
char = ARG
cfg = spec[char]
out_dir = cfg["out"].replace('/', os.sep)
os.makedirs(out_dir, exist_ok=True)
prev_dir = os.path.join(out_dir, 'Preview')
os.makedirs(prev_dir, exist_ok=True)

bpy.ops.wm.open_mainfile(filepath=cfg["blend"].replace('/', os.sep))
scene = bpy.context.scene
scene.render.fps = cfg["fps"]
arm = next(o for o in bpy.data.objects if o.type == 'ARMATURE')
mesh = next(o for o in bpy.data.objects if o.type == 'MESH')
bpy.context.view_layer.objects.active = arm

def world_axis_rotation(pb, deg, axis=(1.0, 0.0, 0.0)):
    m = pb.bone.matrix_local.to_3x3()
    a = (m.inverted() @ Vector(axis)).normalized()
    pb.rotation_mode = 'QUATERNION'
    pb.rotation_quaternion = Quaternion(a, math.radians(deg))

def root_world_offset(pb, dz):
    m = pb.bone.matrix_local.to_3x3()
    pb.location = m.inverted() @ Vector((0.0, 0.0, dz))

bones = {b.name for b in arm.pose.bones}
unknown = sorted({n for c in cfg['clips'] for n in c['tracks'] if n not in bones})
if unknown:
    raise RuntimeError('unknown bones: %s' % unknown)

arm.animation_data_create()
report = {'character': char, 'fps': cfg['fps'], 'clips': [], 'unknown_bones': unknown,
          'bone_count': len(arm.pose.bones)}
made = []
for clip in cfg['clips']:
    name = 'A_DY_%s_%s' % (cfg['id'], clip['name'])
    for old in list(bpy.data.actions):
        if old.name == name:
            bpy.data.actions.remove(old)
    act = bpy.data.actions.new(name)
    act.use_fake_user = True
    arm.animation_data.action = act
    last = clip['frames'] + 1
    for pb in arm.pose.bones:
        pb.rotation_mode = 'QUATERNION'
        pb.rotation_quaternion = Quaternion((1, 0, 0, 0))
        pb.location = (0, 0, 0)
        pb.scale = (1, 1, 1)
    keys = {}
    for bone, track in clip['tracks'].items():
        for frame, deg in track:
            keys.setdefault(frame, {})[bone] = deg
    for frame, dz in clip.get('root_z', []):
        keys.setdefault(frame, {})['__root_z__'] = dz
    keys.setdefault(1, {})
    keys.setdefault(last, {})
    for frame in sorted(keys):
        scene.frame_set(frame)
        for pb in arm.pose.bones:
            pb.rotation_mode = 'QUATERNION'
            angles = keys[frame]
            if pb.name in angles:
                world_axis_rotation(pb, angles[pb.name])
            else:
                # hold nearest explicit value so unkeyed bones stay at rest
                pb.rotation_quaternion = Quaternion((1, 0, 0, 0))
            pb.keyframe_insert(data_path='rotation_quaternion', frame=frame, group=pb.name)
        if '__root_z__' in keys[frame] and 'Root' in bones:
            rb = arm.pose.bones['Root']
            root_world_offset(rb, keys[frame]['__root_z__'])
            rb.keyframe_insert(data_path='location', frame=frame, group='Root')
    # smooth interpolation for loops
    for fc in act.fcurves:
        for kp in fc.keyframe_points:
            kp.interpolation = 'BEZIER'
    act.use_frame_range = True
    act.frame_start = 1
    act.frame_end = last
    made.append((act, clip, last))
    # bounds sanity on sampled frames
    samples = sorted({1, max(2, last // 3), max(3, (2 * last) // 3), last})
    for f in samples:
        scene.frame_set(f)
        ev = mesh.evaluated_get(bpy.context.evaluated_depsgraph_get())
        em = ev.to_mesh()
        zs = [v.co.z for v in em.vertices]
        ys = [v.co.y for v in em.vertices]
        if not all(math.isfinite(v) for v in zs + ys):
            raise RuntimeError('%s frame %d non-finite geometry' % (name, f))
        ev.to_mesh_clear()
    report['clips'].append({'name': name, 'frames': last, 'loop': clip['loop'],
                            'bones_keyed': sorted(clip['tracks']),
                            'samples': samples})

# lighting + camera for the preview sheet
scene.render.engine = 'BLENDER_EEVEE_NEXT'
scene.render.resolution_x = 460
scene.render.resolution_y = 620
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = 'PNG'
scene.view_settings.view_transform = 'AgX'
scene.world.use_nodes = True
scene.world.node_tree.nodes['Background'].inputs['Color'].default_value = (.15, .17, .2, 1)
scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value = .55

def aim(o, target):
    o.rotation_euler = (Vector(target) - o.location).to_track_quat('-Z', 'Y').to_euler()

bb = [mesh.matrix_world @ Vector(c) for c in mesh.bound_box]
height = max(v.z for v in bb) - min(v.z for v in bb)
width = max(v.y for v in bb) - min(v.y for v in bb)
target = (0, 0, height * 0.5)
for loc, power, size in (((300, -160, height + 160), 1600000, 300), ((250, 190, 70), 600000, 260)):
    bpy.ops.object.light_add(type='AREA', location=loc)
    l = bpy.context.object
    l.data.energy = power
    l.data.size = size
    aim(l, target)
bpy.ops.object.camera_add(location=(650, 0, height * 0.5))
cam = bpy.context.object
cam.data.type = 'ORTHO'
cam.data.ortho_scale = max(width * 1.35, height * 1.6)
scene.camera = cam
aim(cam, target)

previews = []
for act, clip, last in made:
    arm.animation_data.action = act
    shots = sorted({1, max(2, last // 3), max(3, (2 * last) // 3), last})
    for f in shots:
        scene.frame_set(f)
        scene.render.filepath = os.path.join(prev_dir, '%s_f%03d.png' % (act.name, f))
        bpy.ops.render.render(write_still=True)
        previews.append(os.path.relpath(scene.render.filepath, out_dir))
        report['clips'][[c[0].name for c in made].index(act.name)]['bounds'] = \
            report['clips'][[c[0].name for c in made].index(act.name)].get('bounds', {})
        report['clips'][[c[0].name for c in made].index(act.name)]['bounds'][str(f)] = \
            [round(min(v.y for v in bb), 2), round(max(v.y for v in bb), 2)]

# export one FBX per clip against the same rig
opts = dict(use_selection=True, object_types={'ARMATURE', 'MESH'}, global_scale=1,
            apply_unit_scale=True, apply_scale_options='FBX_SCALE_NONE',
            axis_forward='-Z', axis_up='Y', add_leaf_bones=False,
            primary_bone_axis='Y', secondary_bone_axis='X', armature_nodetype='NULL',
            use_armature_deform_only=False, path_mode='AUTO', embed_textures=False)
exports = []
for act, clip, last in made:
    arm.animation_data.action = act
    scene.frame_start = 1
    scene.frame_end = last
    scene.frame_set(1)
    bpy.ops.object.select_all(action='DESELECT')
    arm.select_set(True)
    mesh.select_set(True)
    bpy.context.view_layer.objects.active = arm
    path = os.path.join(out_dir, act.name + '.fbx')
    bpy.ops.export_scene.fbx(filepath=path, bake_anim=True, bake_anim_use_all_actions=False,
                             bake_anim_use_nla_strips=False, bake_anim_use_all_bones=True,
                             bake_anim_force_startend_keying=True, **opts)
    exports.append(os.path.basename(path))
report['exports'] = exports
report['previews'] = previews
report['ok'] = len(exports) == len(cfg['clips'])
with open(os.path.join(out_dir, 'perf_anim_report.json'), 'w', encoding='utf-8') as f:
    json.dump(report, f, ensure_ascii=False, indent=2)
print('PERF_DONE ' + json.dumps({'ok': report['ok'], 'clips': len(exports), 'char': char}))
