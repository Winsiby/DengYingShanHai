# -*- coding: utf-8 -*-
"""Import authored performance clips and author the four-chapter performance data asset."""
import hashlib, json, os, traceback
import unreal

SOURCE = "D:/灯影山海/Assets/Sources/DengYingArt/ThreePuppets-20261022/Run5/Anim"
BASE = "/Game/DengYingShanHai/Puppets"
AUDIT = "D:/灯影山海/Saved/Audit-2026-10-23-Performance"
PERF = BASE + "/DA_DYPuppetPerformance"
KUAFU_MESH = "/Game/DengYingShanHai/Dev/KuafuAppearance/Puppet/SK_DY_Kuafu_M01_LeftGrip_v04"
MESHES = dict(Kuafu=KUAFU_MESH,
              Jingwei=BASE + "/Meshes/SK_DY_Jingwei",
              Xingtian=BASE + "/Meshes/SK_DY_Xingtian",
              Zhulong=BASE + "/Meshes/SK_DY_Zhulong")

# chapter -> (character, asset title, [clip, seconds, caption, loop]) ; feedback clips share the same shape
ACTS = [
    dict(chapter=0, char="Kuafu", title="第一幕 · 夸父逐日", segments=[
        ("Perf_Run", 2.6, "夸父迈开大步，追着那一轮日头。", True),
        ("Perf_Reach", 2.4, "他把手伸向烈日，杖尖笔直。", True),
        ("Perf_Stagger", 2.2, "日头太近，热浪把他掀得踉跄。", False),
        ("Perf_Fall", 2.4, "力气耗尽，他单膝落地。", False),
        ("Perf_Slump", 2.4, "杖从手里落下——弃杖，化林。", True)],
        feedback=[("Perf_Reach", 1.2, "", True)]),
    dict(chapter=1, char="Jingwei", title="第二幕 · 精卫填海", segments=[
        ("Perf_Flap", 2.4, "精卫振翅，衔石向海。", True),
        ("Perf_Dive", 2.6, "一次俯冲，把石头掷进浪里。", False),
        ("Perf_Hover", 2.4, "她在浪尖悬住，看海又涨起来。", True),
        ("Perf_Dive", 2.6, "再衔一块，再投一次。", False),
        ("Perf_Flap", 2.4, "填海不止，翅声不歇。", True)],
        feedback=[("Perf_Flap", 1.2, "", True)]),
    dict(chapter=2, char="Xingtian", title="第三幕 · 刑天舞干戚", segments=[
        ("Perf_AxeRaise", 2.4, "斧举过头，盾横在胸前。", True),
        ("Perf_AxeSwing", 2.6, "干戚合击，一击劈下。", False),
        ("Perf_Guard", 2.2, "盾影并拢，他站定不动。", True),
        ("Perf_Stomp", 2.4, "一脚踏地，戏台都跟着响。", False),
        ("Perf_Roar", 2.6, "无首之躯，以乳为目、以脐为口，仍舞个不停。", True)],
        feedback=[("Perf_AxeRaise", 1.2, "", True)]),
    dict(chapter=3, char="Zhulong", title="第四幕 · 烛龙昼夜", segments=[
        ("Perf_Coil", 2.4, "烛龙盘身，鳞光在幕上来回。", True),
        ("Perf_HeadRise", 2.6, "它昂起头，睁眼为昼。", True),
        ("Perf_Swim", 2.6, "长身游过，天色转深。", True),
        ("Perf_HeadRise", 2.4, "再睁一次眼，昼夜又换。", True),
        ("Perf_Settle", 2.6, "它伏回暗处，昼夜既定。", True)],
        feedback=[("Perf_HeadRise", 1.2, "", True)]),
]
EAL = unreal.EditorAssetLibrary
TOOLS = unreal.AssetToolsHelpers.get_asset_tools()
R = dict(ok=False, imported=[], acts=[], checks=[], errors=[])


def require(v, m):
    if not v:
        raise RuntimeError(m)
    R["checks"].append(m)
    return v


def pkg(a):
    return a.get_path_name().split(".")[0]


def save(a):
    require(EAL.save_loaded_asset(a, only_if_is_dirty=False), "Saved " + pkg(a))


def create(path, cls, factory):
    if EAL.does_asset_exist(path):
        return require(EAL.load_asset(path), "Loaded " + path)
    return require(TOOLS.create_asset(path.rsplit("/", 1)[1], path.rsplit("/", 1)[0], cls, factory), "Created " + path)


def import_file(filename, dest, options=None):
    require(os.path.isfile(filename), "Source exists " + filename)
    task = unreal.AssetImportTask()
    props = dict(filename=filename, destination_path=dest.rsplit("/", 1)[0], destination_name=dest.rsplit("/", 1)[1],
                 automated=True, replace_existing=True, replace_existing_settings=True, save=False)
    if options is not None:
        props.update(factory=unreal.FbxFactory(), options=options)
    task.set_editor_properties(props)
    TOOLS.import_asset_tasks([task])
    paths = list(task.get_editor_property("imported_object_paths"))
    require(paths, "Importer returned objects " + filename)
    asset = EAL.load_asset(dest)
    if asset is None:
        cands = [EAL.load_asset(p) for p in paths]
        cands = [a for a in cands if a and isinstance(a, unreal.AnimSequence)]
        require(len(cands) == 1, "Single imported anim when the name changed")
        EAL.rename_asset(cands[0].get_path_name().split(".")[0], dest)
        asset = EAL.load_asset(dest)
    require(asset, "Loaded imported " + dest)
    R["imported"].append(dict(source=filename, path=pkg(asset), sha256=hashlib.sha256(open(filename, "rb").read()).hexdigest()))
    return asset


def fbx_options(skeleton, name):
    o = unreal.FbxImportUI()
    o.set_editor_properties(dict(mesh_type_to_import=unreal.FBXImportType.FBXIT_ANIMATION,
                                 import_as_skeletal=True, import_mesh=False, import_animations=True,
                                 import_materials=False, import_textures=False, create_physics_asset=False,
                                 automated_import_should_detect_type=False, override_full_name=True))
    o.set_editor_property("skeleton", skeleton)
    o.set_editor_property("override_animation_name", name)
    d = o.get_editor_property("anim_sequence_import_data")
    d.set_editor_properties(dict(convert_scene=True, convert_scene_unit=True, import_uniform_scale=1.0,
                                 import_bone_tracks=True, use_default_sample_rate=True,
                                 animation_length=unreal.FBXAnimationLengthImportType.FBXALIT_EXPORTED_TIME))
    return o


def text(s):
    # Captions are plain FStrings on the C++ struct: UE Python exposes no FText constructor.
    return s


def segment(anims, char, clip, seconds, caption, loop):
    name = "A_DY_" + char + "_" + clip
    s = unreal.DYPerformanceSegment()
    s.set_editor_property("animation", require(anims[char][name], "Clip resolved " + name))
    s.set_editor_property("seconds", float(seconds))
    s.set_editor_property("caption", str(caption))
    for loop_name in ("b_loop", "loop", "bLoop"):
        try:
            s.set_editor_property(loop_name, bool(loop))
            R.setdefault("loop_property", loop_name)
            break
        except Exception:
            continue
    else:
        raise RuntimeError("No python name found for the segment loop flag")
    return s


def segment_array(items):
    arr = unreal.Array(unreal.DYPerformanceSegment)
    for it in items:
        arr.append(it)
    return arr


try:
    os.makedirs(AUDIT, exist_ok=True)
    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    prev = unreal.SystemLibrary.get_console_variable_int_value("Interchange.FeatureFlags.Import.FBX")
    unreal.SystemLibrary.execute_console_command(world, "Interchange.FeatureFlags.Import.FBX 0", None)
    try:
        meshes = {c: require(EAL.load_asset(p), "Mesh " + c) for c, p in MESHES.items()}
        skels = {c: require(m.get_editor_property("skeleton"), "Skeleton " + c) for c, m in meshes.items()}
        needed = {}
        for a in ACTS:
            for clip, _, _, _ in a["segments"] + a["feedback"]:
                needed.setdefault(a["char"], set()).add(clip)
        anims, clips = {}, {}
        for c, names in needed.items():
            anims[c], clips[c] = {}, []
            for clip in sorted(names):
                name = "A_DY_" + c + "_" + clip
                path = SOURCE + "/" + c + "/" + name + ".fbx"
                a = import_file(path, BASE + "/Animations/" + name, fbx_options(skels[c], name))
                require(isinstance(a, unreal.AnimSequence), "AnimSequence " + name)
                require(a.get_editor_property("skeleton") == skels[c], "Anim skeleton " + name)
                save(a)
                anims[c][name] = a
                clips[c].append(dict(clip=name, path=pkg(a), length=round(float(a.get_play_length()), 4)))
        # Author the data asset.
        factory = unreal.DataAssetFactory()
        factory.set_editor_property("data_asset_class", unreal.DYPuppetPerformanceData)
        da = create(PERF, unreal.DYPuppetPerformanceData, factory)
        acts = unreal.Array(unreal.DYActPerformance)
        for spec in ACTS:
            act = unreal.DYActPerformance()
            act.set_editor_property("chapter_index", int(spec["chapter"]))
            act.set_editor_property("act_title", str(spec["title"]))
            act.set_editor_property("segments", segment_array([segment(anims, spec["char"], *s) for s in spec["segments"]]))
            act.set_editor_property("feedback", segment_array([segment(anims, spec["char"], *s) for s in spec["feedback"]]))
            acts.append(act)
        da.set_editor_property("acts", acts)
        save(da)
    finally:
        unreal.SystemLibrary.execute_console_command(world, "Interchange.FeatureFlags.Import.FBX " + str(prev), None)
    # Read back from disk and assert the authored graph.
    read = require(EAL.load_asset(PERF), "Reloaded " + PERF)
    read_acts = list(read.get_editor_property("acts"))
    require(len(read_acts) == 4, "Four acts authored")
    R["acts"] = []
    for act in read_acts:
        segs = list(act.get_editor_property("segments"))
        fb = list(act.get_editor_property("feedback"))
        durations = [float(s.get_editor_property("seconds")) for s in segs]
        total = round(sum(durations), 3)
        R["acts"].append(dict(chapter=int(act.get_editor_property("chapter_index")),
                              title=str(act.get_editor_property("act_title")),
                              segments=len(segs), feedback=len(fb), seconds=total,
                              clips=[str(s.get_editor_property("animation")) for s in segs],
                              captions=[str(s.get_editor_property("caption")) for s in segs],
                              durations=durations))
        require(12.0 <= total <= 20.0, "Act " + str(act.get_editor_property("chapter_index")) + " runs 12-20 s")
        require(len(fb) >= 1, "Act has feedback clip")
        require(all(str(s.get_editor_property("animation")) for s in segs), "Every segment resolves a clip")
    require([int(a.get_editor_property("chapter_index")) for a in read_acts] == [0, 1, 2, 3], "Chapters 0..3 in order")
    require(abs(sum(R["acts"][0]["durations"]) - R["acts"][0]["seconds"]) < 0.001, "Authored beats sum to the act duration")
    R["clips"] = clips
    R["ok"] = True
except Exception:
    R["errors"].append(traceback.format_exc())
finally:
    os.makedirs(AUDIT, exist_ok=True)
    with open(AUDIT + "/perf-import.json", "w", encoding="utf-8") as f:
        json.dump(R, f, ensure_ascii=False, indent=2)
    print("PERF_IMPORT_DONE", R.get("ok"), len(R.get("checks", [])), R.get("errors"))
    unreal.SystemLibrary.quit_editor()