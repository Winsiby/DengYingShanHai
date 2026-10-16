"""Cold, fail-closed authoring of ONLY /Dev/ThreeAct assets.

Use separate Editor processes for source_probe, create, configure_map, verify.
source_probe and verify never save assets. create refuses every destination;
configure_map edits only the previously saved copy and replaces one identified
presentation and one identified geometry probe. No Python gameplay dependency.

Environment: DY_THREE_ACT_AUTHOR_PHASE, DY_THREE_ACT_AUTHOR_OUT and, for writes,
DY_THREE_ACT_SOURCE_PROBE (the successful cold source_probe report).
"""
import hashlib
import json
import os
import re
import traceback
import unreal


ROOT = "/Game/DengYingShanHai/Dev/ThreeAct"
MAP = ROOT + "/Maps/LV_ThreeActDev"
SOURCE_MAP = "/Game/DengYingShanHai/Dev/M3/Maps/LV_M3RuntimeCandidate"
OLD = "/Game/DengYingShanHai/Dev/M3/Runtime/"
FONT = "/Game/DengYingShanHai/Dev/M2/UI/FF_DYSourceHanSansSC_Font"
FOREST = "/Game/DengYingShanHai/Dev/M3/Forest/BP_DYForestPresentation_Dev"
DEFINITIONS = (
    ("/Game/DengYingShanHai/Dev/M1/Data/DA_DY_P01_SunAwakening", "P01_SunAwakening", "引日启幕", .68, None),
    ("/Game/DengYingShanHai/Dev/M2/Data/DA_DY_P02_ChaseForm", "P02_ChaseForm", "逐光成形", .72, .80),
    (OLD + "DA_P03RuntimeCandidate", "P03_DevPlayableCandidate", "杖落成林", .72, .85),
)
DEST = {
    "cue": ROOT + "/UI/WBP_DYThreeActCue",
    "stage": ROOT + "/Stage/BP_DYThreeActPresentation",
    "widget": ROOT + "/UI/WBP_DYThreeActHUD",
    "hud": ROOT + "/UI/BP_DYThreeActHUD",
    "mode": ROOT + "/Core/BP_DYThreeActGameMode",
}
SOURCES = {
    "cue": OLD + "WBP_DYP03RuntimeCue",
    "stage": OLD + "BP_DYP03RuntimePresentation",
    "widget": OLD + "WBP_DYP03RuntimeHUD",
    "hud": OLD + "BP_DYP03RuntimeHUD",
    "mode": OLD + "BP_DYP03RuntimeGameMode",
}
NATIVE = "/Script/DengYingShanHai."
STAGE = NATIVE + "DYStagePresentation."
DIR = NATIVE + "DYPuzzleDirector."
MATH = "/Script/Engine.KismetMathLibrary."
BEL = unreal.BlueprintEditorLibrary
BGE = unreal.BlueprintGraphEditor
PHASE = os.environ.get("DY_THREE_ACT_AUTHOR_PHASE", "source_probe")
OUT = os.environ.get("DY_THREE_ACT_AUTHOR_OUT", os.path.join(
    unreal.Paths.project_saved_dir(), "Audit-2026-10-09-ThreeActIntegration", PHASE + ".json"))
REPORT = dict(success=False, phase=PHASE, error=None, saved=[], map=MAP,
              python_runtime_dependency=False, changes_old_assets=False)
ALLOWED_SAVES = set(DEST.values()) | {MAP}
NODE_EXPORT_CACHE = {}


def require(value, why):
    if not value:
        raise RuntimeError(why)
    return value


def exact_float(value, expected, why):
    require(abs(float(value) - expected) <= 1.e-8, why)


def path(obj):
    return obj.get_path_name() if obj else None


def package_file(package):
    require(package.startswith("/Game/"), "Only project source packages may be hashed")
    base = os.path.join(unreal.Paths.project_content_dir(), package[len("/Game/"):].replace("/", os.sep))
    candidates = [p for p in (base + ".uasset", base + ".umap") if os.path.isfile(p)]
    require(len(candidates) == 1, "Exactly one saved package file: " + package)
    return candidates[0]


def identities():
    packages = sorted(set(SOURCES.values()) | {SOURCE_MAP, FONT, FOREST}
                      | {item[0] for item in DEFINITIONS})
    result = {}
    for package in packages:
        filename = package_file(package)
        digest = hashlib.sha256()
        with open(filename, "rb") as stream:
            for chunk in iter(lambda: stream.read(1048576), b""):
                digest.update(chunk)
        result[package] = dict(bytes=os.path.getsize(filename), sha256=digest.hexdigest().upper())
    return result


def connect(source, target):
    require(source.is_valid() and target.is_valid(), "Missing graph pin")
    require(source.try_create_connection(target), "Cannot connect "
            + str(source.get_pin_name()) + " -> " + str(target.get_pin_name()))


def literal(pin, value):
    require(pin.is_valid() and pin.set_pin_value(str(value)), "Invalid literal " + str(value))


def text_source(pin):
    # The cold source report proves these FText pins are NSLOCTEXT exports,
    # not raw strings. Read the exact source-string field, preserving the
    # namespace/key serialization in the audit and never guessing by substring.
    raw = pin.get_pin_value()
    if raw.startswith("NSLOCTEXT("):
        fields = re.fullmatch(r'NSLOCTEXT\(("(?:[^"\\]|\\.)*"),\s*("(?:[^"\\]|\\.)*"),\s*("(?:[^"\\]|\\.)*")\)', raw)
        require(fields, "Unrecognized exported localized-text literal")
        return json.loads(fields.group(3))
    return raw


def node_metadata(node):
    """Read identity from the official exporter, not protected Python fields."""
    key = path(node)
    if key in NODE_EXPORT_CACHE:
        return NODE_EXPORT_CACHE[key]
    folder = os.path.join(os.path.dirname(os.path.abspath(OUT)), "NodeTextExports")
    os.makedirs(folder, exist_ok=True)
    exports = REPORT.setdefault("node_text_exports", [])
    filename = os.path.join(folder, "%04d-%s.copy" % (len(exports), node.get_name()))
    require(not os.path.exists(filename), "Preserve existing node text export " + filename)
    task = unreal.AssetExportTask()
    task.set_editor_properties(dict(object=node, exporter=unreal.ObjectExporterT3D(), filename=filename,
        automated=True, prompt=False, selected=False, replace_identical=False,
        use_file_archive=False, write_empty_files=False))
    okay = unreal.Exporter.run_asset_export_task(task)
    record = dict(node=key, node_class=path(node.get_class()), export_file=filename,
                  exporter_success=okay, errors=[str(v) for v in task.get_editor_property("errors")])
    exports.append(record)
    require(okay and os.path.isfile(filename), "Official node text export failed: " + key)
    with open(filename, "rb") as stream:
        payload = stream.read()
    text = payload.decode("utf-16" if payload.startswith((b"\xff\xfe", b"\xfe\xff")) else "utf-8-sig")
    record["sha256"] = hashlib.sha256(payload).hexdigest().upper()
    lines = text.splitlines()
    require(lines and "ExportPath=" in lines[0] and key in lines[0], "Exported node identity is not exact")
    record["export_header"] = lines[0]
    record["references"] = {}
    for prop in ("FunctionReference", "VariableReference"):
        matching = [line.strip() for line in lines if line.strip().startswith(prop + "=")]
        require(len(matching) <= 1, "Ambiguous exported " + prop + ": " + key)
        if matching:
            names = re.findall(r'MemberName="([^"\\]*(?:\\.[^"\\]*)*)"', matching[0])
            require(len(names) == 1, "Missing exact exported MemberName: " + key)
            parent_match = re.search(r'MemberParent="([^"\\]*(?:\\.[^"\\]*)*)"', matching[0])
            # Exported object references are Type'/Actual/Object.Path'; the type
            # prefix is NOT the MemberParent identity (both may start /Script).
            parent_paths = re.findall(r"'(/(?:Game|Script)/[^']+)'", parent_match.group(1)) if parent_match else []
            require(len(parent_paths) <= 1, "Ambiguous exported MemberParent: " + key)
            record["references"][prop] = dict(member_name=names[0],
                member_parent=parent_paths[0] if parent_paths else None, raw=matching[0])
    guids = [line.strip().split("=", 1)[1] for line in lines if line.strip().startswith("NodeGuid=")]
    require(len(guids) == 1, "Exact exported NodeGuid required")
    record["node_guid"] = guids[0]
    NODE_EXPORT_CACHE[key] = record
    return record


def member_reference(node, prop):
    field = {"function_reference": "FunctionReference", "variable_reference": "VariableReference"}[prop]
    reference = require(node_metadata(node)["references"].get(field), "Exact exported member reference missing")
    return reference["member_name"]


def function_name(node):
    # K2Node_PromotableOperator inherits UK2Node_CallFunction in the
    # installed UE 5.8 header; comparisons may be saved using that subclass.
    if node.get_class().get_name() in ("K2Node_CallFunction", "K2Node_CallParentFunction", "K2Node_PromotableOperator"):
        return member_reference(node, "function_reference")
    return None


def variable_name(node):
    if node.get_class().get_name() in ("K2Node_VariableGet", "K2Node_VariableSet"):
        return member_reference(node, "variable_reference")
    return None


def graph_editor(bp, name):
    graphs = [g for g in BEL.list_graphs(bp) if str(g.get_name()) == name]
    require(len(graphs) == 1, "Exactly one existing function graph " + name)
    return BGE.get_graph_editor(graphs[0])


def calls(editor, name):
    return [n for n in editor.list_all_nodes() if function_name(n) == name]


def compile_bp(bp):
    require(BEL.compile_blueprint(bp), "Compile failed: " + path(bp))
    NODE_EXPORT_CACHE.clear()  # Compilation may reconstruct nodes/references.
    for graph in BEL.list_graphs(bp):
        require(not BGE.get_graph_editor(graph).list_nodes_with_errors(),
                "Actual cold graph errors: " + path(graph))
    require(bp.generated_class(), "No generated class: " + path(bp))


def graph_inventory(bp):
    result = []
    for graph in BEL.list_graphs(bp):
        editor = BGE.get_graph_editor(graph)
        nodes = []
        for node in editor.list_all_nodes():
            pins = []
            for pin in node.list_all_pins():
                pins.append(dict(name=str(pin.get_pin_name()), direction=str(pin.get_pin_direction()),
                    type=pin.get_pin_type_as_json_schema(), literal=pin.get_pin_value(),
                    connected=[dict(node=path(p.get_owning_node()), pin=str(p.get_pin_name()))
                               for p in pin.list_connected_pins()]))
            nodes.append(dict(path=path(node), node_class=path(node.get_class()),
                              title=node.get_node_title(), function=function_name(node),
                              variable=variable_name(node), pins=pins))
        result.append(dict(name=str(graph.get_name()), path=path(graph), nodes=nodes,
            errors=[path(n) for n in editor.list_nodes_with_errors()],
            warnings=[path(n) for n in editor.list_nodes_with_warnings()]))
    return result


def inspect_complete_growth(bp, patched=False):
    editor = graph_editor(bp, "CompleteGrowth")
    completed = [n for n in editor.list_all_nodes()
                 if n.get_class().get_name() == "K2Node_VariableSet" and variable_name(n) == "Completed"]
    require(len(completed) == 1, "One actual Completed setter")
    require(completed[0].find_input_pin("Completed").get_pin_value().lower() == "true",
            "Completed must only be assigned true at the actual successful endpoint")
    following = completed[0].find_then_pin().list_connected_pins()
    require(len(following) == 1 and function_name(following[0].get_owning_node()) == "ShowCaption",
            "Successful Completed then must lead to the existing ShowCaption")
    caption = following[0].get_owning_node()
    require(caption.find_input_pin("Text").is_valid(), "Actual caption Text input")
    after = caption.find_then_pin().list_connected_pins()
    if patched:
        require(len(after) == 1 and function_name(after[0].get_owning_node()) == "SubmitForestFinaleCompletion",
                "Successful tail must submit to the native Stage boundary")
        submit = after[0].get_owning_node()
        require(not submit.find_then_pin().list_connected_pins(), "No stale writes after external completion callback")
        require(submit.find_input_pin("Token").list_connected_pins(), "Actual callback Token link")
    else:
        require(not after, "Source terminal caption unexpectedly has a successor; stop before mutation")
        require(not calls(editor, "SubmitForestFinaleCompletion"), "Source must remain old single-act behavior")
    normalized = calls(editor, "SetForestNormalizedGrowth")
    require(len(normalized) == 1, "One actual final growth call")
    exact_float(normalized[0].find_input_pin("Progress").get_pin_value(), 1.0, "Actual final growth=1")
    return editor, caption


def inspect_stage(bp, patched=False):
    compile_bp(bp)
    editor, caption = inspect_complete_growth(bp, patched)
    event_graph = BGE.get_graph_editor(BEL.find_event_graph(bp))
    timeline_nodes = [n for n in event_graph.list_all_nodes() if n.get_class().get_name() == "K2Node_Timeline"]
    require(len(timeline_nodes) == 2, "Keep exactly the two native Blueprint Timelines")
    for node in timeline_nodes:
        for name, input_pin in (("PlayFromStart", True), ("Update", False), ("Finished", False)):
            pin = node.find_input_pin(name) if input_pin else node.find_output_pin(name)
            require(pin.is_valid() and pin.list_connected_pins(), "Actual Timeline link: " + name)
    require(not any(n.get_class().get_name().startswith("K2Node_Input")
                    for n in event_graph.list_all_nodes()), "Do not add a second input owner")
    require(event_graph.find_event_node("ReceivePuzzleResolved"), "Saved native Resolve override")
    gates = [n for n in calls(event_graph, "EqualEqual_NameName")
             if n.find_input_pin("B").get_pin_value() == DEFINITIONS[2][1]]
    require(len(gates) == 1, "Actual saved exact P03 PuzzleId gate")
    defaults = unreal.get_default_object(bp.generated_class())
    require(not any(defaults.get_editor_property(n)
                    for n in ("CueOwned", "Dropping", "Growing", "Completed", "Ended")),
            "No runtime cue ownership stored in authored defaults")
    return dict(graphs=graph_inventory(bp), timeline_count=len(timeline_nodes),
                completion_caption=caption.find_input_pin("Text").get_pin_value())


def inspect_definitions():
    result = []
    for package, puzzle_id, title, light_value, puppet_value in DEFINITIONS:
        definition = require(unreal.load_asset(package), "Saved Definition missing: " + package)
        require(str(definition.get_editor_property("puzzle_id")) == puzzle_id, "Saved PuzzleId differs")
        light = definition.get_editor_property("light_position")
        puppet = definition.get_editor_property("puppet_position")
        require(light.get_editor_property("enabled"), "Light condition must be authored enabled")
        exact_float(light.get_editor_property("target"), light_value, "Saved light target changed")
        exact_float(definition.get_editor_property("required_hold_seconds"), 1.25, "Saved hold time changed")
        exact_float(light.get_editor_property("enter_tolerance"), .045 if puppet_value is None else .05,
                    "Saved light enter tolerance changed")
        exact_float(light.get_editor_property("exit_tolerance"), .085 if puppet_value is None else .09,
                    "Saved light exit tolerance changed")
        pose = str(definition.get_editor_property("required_puppet_pose_id"))
        if puppet_value is None:
            require(not puppet.get_editor_property("enabled") and pose in ("None", ""),
                    "P01 must not require puppet movement/pose")
        else:
            require(puppet.get_editor_property("enabled") and pose == "P02_StrideReach", "Saved puppet condition changed")
            exact_float(puppet.get_editor_property("target"), puppet_value, "Saved puppet target changed")
            exact_float(puppet.get_editor_property("enter_tolerance"), .05, "Saved puppet enter tolerance changed")
            exact_float(puppet.get_editor_property("exit_tolerance"), .09, "Saved puppet exit tolerance changed")
        result.append(dict(path=package, puzzle_id=puzzle_id, title=title, light_target=light_value,
                           puppet_enabled=puppet.get_editor_property("enabled"),
                           puppet_target=puppet.get_editor_property("target"), pose=pose, hold_seconds=1.25))
    return result


def vector(value):
    return [value.x, value.y, value.z]


def actor_geometry(actor):
    rotation = actor.get_actor_rotation()
    return dict(name=actor.get_name(), label=actor.get_actor_label(), actor_class=path(actor.get_class()),
                location=vector(actor.get_actor_location()), scale=vector(actor.get_actor_scale3d()),
                rotation=[rotation.pitch, rotation.yaw, rotation.roll],
                tags=[str(x) for x in actor.get_editor_property("tags")])


def load_map(package):
    levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    editor = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
    # LevelEditorSubsystem.IsInPlayInEditor dereferences GUnrealEd, which is
    # absent in Python commandlets. The official GetGameWorld checks GEditor;
    # LoadLevel independently refuses PlayWorld/GIsPlayInEditorWorld as well.
    require(not editor.get_game_world(), "Refuse an existing PIE world")
    require(levels.load_level(package), "Cold saved map load: " + package)
    world = editor.get_editor_world()
    require(path(world) == package + "." + package.rsplit("/", 1)[1], "Exact requested World identity")
    api = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    actors = list(api.get_all_level_actors())
    labels = {}
    for actor in actors:
        label = actor.get_actor_label()
        require(label not in labels, "Ambiguous actor label, fail closed: " + label)
        labels[label] = actor
    return levels, world, api, labels


def inspect_map(package, expect_sequence=False):
    levels, world, api, labels = load_map(package)
    stage_label = "ThreeAct_StagePresentation" if expect_sequence else "M3_RuntimePresentation"
    stage = require(labels.get(stage_label), "Explicit saved presentation instance")
    expected_stage = DEST["stage"] if expect_sequence else SOURCES["stage"]
    require(path(stage.get_class()) == expected_stage + "." + expected_stage.rsplit("/", 1)[1] + "_C",
            "Presentation generated class identity")
    director = require(stage.get_puzzle_director(), "Explicit saved Director")
    light = require(labels.get("M2_LightRig_P02"), "Explicit same light")
    puppet = require(labels.get("M2_Puppet_P02_Controlled"), "Explicit same puppet")
    screen = require(labels.get("DEV_BackScreen"), "Explicit same screen")
    ground = require(labels.get("M3_RuntimeNarrativeGroundLine"), "Explicit accepted high ground")
    forest = require(labels.get("M3_RuntimeForest"), "Explicit saved 15-branch Forest")
    require(director.get_light_rig_actor() == light and director.get_puppet_actor() == puppet,
            "Director must use the explicitly identified old fixtures")
    exact_float(director.get_evaluation_frequency_hz(), 15, "Keep 15 Hz")
    for actor, component in ((light, "light_control"), (puppet, "puppet_control")):
        exact_float(actor.get_editor_property(component).get_editor_property("initial_normalized_value"),
                    .15, "Keep existing .15/.15 reset authoring")
    require(stage.get_editor_property("staff_projection_screen") == screen
            and stage.get_editor_property("DevReceiver") == screen.static_mesh_component
            and stage.get_editor_property("narrative_ground_line") == ground
            and stage.get_editor_property("DevGround") == ground
            and stage.get_forest_presentation_actor() == forest, "Exact native/Dev binding identities")
    exact_float(ground.get_actor_location().z, 70, "Keep accepted high narrative ground Z70")
    require(path(forest.get_class()) == FOREST + ".BP_DYForestPresentation_Dev_C"
            and len(forest.get_editor_property("branch_layout")) == 15
            and not forest.has_forest_session(), "Existing clean 15-branch Forest only")
    probe = labels.get("M3_StaffProjectionProbe_AB")
    if expect_sequence:
        require(not probe and not any(path(a.get_class()) == NATIVE + "DYStaffProjectionProbe"
                                     for a in labels.values()), "No diagnostic probe in new copy")
        entries = list(director.get_editor_property("act_sequence"))
        require(len(entries) == 3, "Exactly three explicitly authored sequence entries")
        for entry, (definition, _, title, _, _) in zip(entries, DEFINITIONS):
            require(path(entry.get_editor_property("definition")).split(".")[0] == definition
                    and str(entry.get_editor_property("act_title")) == title, "Exact ordered Definition/title")
        require(path(world.get_world_settings().get_editor_property("default_game_mode"))
                == DEST["mode"] + ".BP_DYThreeActGameMode_C", "Own new default GameMode")
    else:
        require(probe and path(probe.get_class()) == NATIVE + "DYStaffProjectionProbe"
                and "DY_M3GeometryOnly" in [str(t) for t in probe.get_editor_property("tags")],
                "Exact original diagnostic identity and authoring tag")
        require(probe.get_editor_property("light") == light and probe.get_editor_property("puppet") == puppet
                and probe.get_editor_property("screen_actor") == screen, "Original diagnostic bindings")
        require(not director.get_editor_property("act_sequence"), "Old single-act map must not become sequence")
    return dict(actors=[actor_geometry(a) for a in sorted(labels.values(), key=lambda a: a.get_actor_label())],
                director_name=director.get_name(), stage_name=stage.get_name(),
                fixture_geometry={name: actor_geometry(labels[name]) for name in (
                    "M2_LightRig_P02", "M2_Puppet_P02_Controlled", "DEV_BackScreen",
                    "M3_RuntimeNarrativeGroundLine", "M3_RuntimeGroundLineMarker", "M3_RuntimeForest")},
                ground_world=vector(ground.get_actor_location()), evaluation_hz=15,
                same_bindings=True, source_saved=False)


def read_approved_probe():
    filename = require(os.environ.get("DY_THREE_ACT_SOURCE_PROBE"), "Writing requires cold source_probe report path")
    with open(filename, "r", encoding="utf-8-sig") as stream:
        probe = json.load(stream)
    require(probe.get("success") and probe.get("phase") == "source_probe" and not probe.get("saved"),
            "Source probe must be successful, cold and non-mutating")
    require(probe.get("protected_before") == identities(), "Source package changed since cold source probe")
    return probe


def save(asset):
    package = path(asset).split(".")[0]
    require(package in ALLOWED_SAVES and package.startswith(ROOT + "/"), "Asset save outside exact whitelist")
    require(unreal.EditorAssetLibrary.save_loaded_asset(asset, only_if_is_dirty=False), "Save new asset " + package)
    REPORT["saved"].append(package)


def duplicate(source, destination):
    require(destination in ALLOWED_SAVES and not unreal.EditorAssetLibrary.does_asset_exist(destination),
            "Refuse existing/out-of-scope destination: " + destination)
    result = require(unreal.EditorAssetLibrary.duplicate_asset(source, destination), "Duplicate only new asset " + destination)
    require(path(result).split(".")[0] == destination, "Exact duplicated asset identity")
    return result


def add_call(editor, function_path, **inputs):
    node = require(editor.add_call_function_node(function_path), "Verified reflected function " + function_path)
    for key, value in inputs.items():
        if isinstance(value, unreal.BlueprintGraphPin):
            connect(value, node.find_input_pin(key))
        else:
            literal(node.find_input_pin(key), value)
    return node


def build_guidance(stage):
    # Private presentation helper, explicit PuzzleId, no secondary flow state.
    ed = BGE.create_and_edit_function_graph(stage, "ShowActGuidance")
    ed.set_function_is_private()
    puzzle = ed.add_graph_input_parameter("PuzzleId", BEL.get_basic_type_by_name("name"))
    execution = ed.find_graph_entry_pin()
    added = []
    captions = (
        "引日启幕 · 先按 E 操纵灯，用 A / D 发现灯与影的关系",
        "逐光成形 · 按 E 在灯与皮影之间切换，用 A / D 协同调整",
        "杖落成林 · 综合调整灯与皮影，影形稳定后等待真实落杖成林",
    )
    for (_, puzzle_id, _, _, _), caption in zip(DEFINITIONS, captions):
        equal = add_call(ed, MATH + "EqualEqual_NameName", A=puzzle, B=puzzle_id)
        branch = require(ed.add_branch_node(), "Official branch node")
        connect(execution, branch.find_execute_pin())
        connect(equal.find_result_pin(), branch.find_input_pin("Condition"))
        show = add_call(ed, "ShowCaption", Text=caption)
        connect(branch.find_output_pin("then"), show.find_execute_pin())
        execution = branch.find_output_pin("else")
        added.extend([equal, branch, show])
    neutral = add_call(ed, "ShowCaption", Text="依次复演三幕 · 操作沿用 E / A / D")
    connect(execution, neutral.find_execute_pin())
    ed.add_comment_to_nodes("Passive act-specific guidance; Director alone owns order and progress.", added + [neutral], 80)
    # Structural compilation makes the private helper resolvable to call nodes.
    compile_bp(stage)
    refresh = BGE.create_and_edit_function_graph(stage, "RefreshActGuidance")
    refresh.set_function_is_private()
    director = add_call(refresh, STAGE + "GetPuzzleDirector")
    valid = add_call(refresh, "/Script/Engine.KismetSystemLibrary.IsValid", Object=director.find_result_pin())
    branch = require(refresh.add_branch_node(), "Official branch")
    connect(refresh.find_graph_entry_pin(), branch.find_execute_pin())
    connect(valid.find_result_pin(), branch.find_input_pin("Condition"))
    current = add_call(refresh, DIR + "GetCurrentPuzzleId")
    connect(director.find_result_pin(), current.find_self_pin())
    guidance = add_call(refresh, "ShowActGuidance", PuzzleId=current.find_result_pin())
    connect(branch.find_output_pin("then"), guidance.find_execute_pin())
    compile_bp(stage)
    main = BGE.get_graph_editor(BEL.find_event_graph(stage))
    require(not main.find_event_node("ReceivePuzzleActivated"), "Do not replace an existing custom activation override")
    activated = require(BEL.add_event_override(stage, "ReceivePuzzleActivated", unreal.IntPoint()), "Native activation override")
    guidance = add_call(main, "ShowActGuidance", PuzzleId=activated.find_output_pin("PuzzleId"))
    connect(activated.find_then_pin(), guidance.find_execute_pin())
    # Replace ONLY the verified terminal initial caption, after successful create.
    beginnings = [n for n in calls(main, "ShowCaption")
                  if text_source(n.find_input_pin("Text")) == "调整灯与偶，让逐日影形稳定；沿用 E / A / D"]
    require(len(beginnings) == 1, "One exact old unconditional third-act startup caption")
    beginning = beginnings[0]
    previous = beginning.find_execute_pin().list_connected_pins()
    require(len(previous) == 1 and function_name(previous[0].get_owning_node()) == "AddToViewport"
            and not beginning.find_then_pin().list_connected_pins(), "Actual startup caption endpoint")
    require(beginning.find_execute_pin().break_pin_links(), "Disconnect old initial caption only")
    replacement = add_call(main, "RefreshActGuidance")
    connect(previous[0], replacement.find_execute_pin())
    main.remove_nodes([beginning])
    invalidated = [n for n in calls(main, "ShowCaption")
                   if text_source(n.find_input_pin("Text")) == "已复位 · 重新调整灯与偶"]
    require(len(invalidated) == 1, "One exact old invalidation caption")
    literal(invalidated[0].find_input_pin("Text"), "灯偶关系已重置")
    compile_bp(stage)


def patch_stage(stage, cue):
    inspect_stage(stage)
    old_cue_class = require(unreal.EditorAssetLibrary.load_blueprint_class(SOURCES["cue"]), "Immutable original Cue class")
    new_cue_class = cue.generated_class()
    # RetargetNodeClass is the UE5.8 official editor API, installed GraphEditor.h.
    # It reconstructs the function pins instead of writing MemberReference by hand.
    show = graph_editor(stage, "ShowCaption")
    setters = calls(show, "SetCueText")
    require(len(setters) == 1, "One actual immutable cue setter")
    main = BGE.get_graph_editor(BEL.find_event_graph(stage))
    # ChangeMemberVariableType in this installed engine only changes the author
    # description, leaving existing variable nodes/skeleton pins stale. Add a
    # correctly typed replacement and rebuild the six proven references through
    # the official graph API; retain every actual connection, then remove the
    # unused old member. There is still only one runtime Cue owner/reference.
    require(main.add_member_variable("ThreeActCueView", BEL.get_object_reference_type(new_cue_class)),
            "Create one correctly typed copied Cue reference")
    cue_nodes = []
    for graph in BEL.list_graphs(stage):
        ed = BGE.get_graph_editor(graph)
        for node in ed.list_all_nodes():
            if variable_name(node) == "CueView":
                links = [(str(pin.get_pin_name()), str(pin.get_pin_direction()), list(pin.list_connected_pins()))
                         for pin in node.list_all_pins()]
                require(not any(variable_name(other.get_owning_node()) == "CueView"
                                for _, _, targets in links for other in targets),
                        "Unexpected direct Cue-variable-to-Cue-variable link")
                cue_nodes.append((ed, node, links))
    require(len(cue_nodes) == 6, "Six cold-proven old Cue references")
    require(show.retarget_node_class(setters[0], old_cue_class, new_cue_class), "Retarget copied Cue setter to copied Cue class")
    NODE_EXPORT_CACHE.clear()  # Retarget changes the actual declaring class.
    main = BGE.get_graph_editor(BEL.find_event_graph(stage))
    creates = [n for n in main.list_all_nodes() if n.get_class().get_name() == "K2Node_CreateWidget"]
    require(len(creates) == 1, "One verified existing CreateWidget")
    literal(creates[0].find_input_pin("Class"), path(new_cue_class))
    for ed, node, links in cue_nodes:
        node_class = node.get_class().get_name()
        for pin in node.list_all_pins():
            if pin.list_connected_pins():
                require(pin.break_pin_links(), "Disconnect verified old Cue node")
        replacement = (ed.add_get_member_variable_node("ThreeActCueView")
                       if node_class == "K2Node_VariableGet"
                       else ed.add_set_member_variable_node("ThreeActCueView"))
        require(replacement, "Create exact new Cue get/set node")
        for name, direction, targets in links:
            name = "ThreeActCueView" if name == "CueView" else name
            rebuilt_pin = (replacement.find_input_pin(name) if "INPUT" in direction
                           else replacement.find_output_pin(name))
            require(rebuilt_pin.is_valid(), "Keep actual replacement pin " + name)
            for target in targets:
                connect(rebuilt_pin, target)
        ed.remove_nodes([node])
    require(main.remove_member_variable("CueView"), "Remove only unused copied old Cue member")
    compile_bp(stage)
    build_guidance(stage)
    editor, caption = inspect_complete_growth(stage)
    literal(caption.find_input_pin("Text"), "林影已成")
    token = editor.find_graph_entry_pin().get_owning_node().find_output_pin("Token")
    require(token.is_valid(), "Captured function-stack Token input")
    submit = add_call(editor, STAGE + "SubmitForestFinaleCompletion", Token=token)
    connect(caption.find_then_pin(), submit.find_execute_pin())
    require(not submit.find_then_pin().list_connected_pins(), "Completion must remain the final call")
    editor.add_comment_to_nodes("Existing real final growth -> local completion/caption -> native current-token proof. No writes after callback.", [caption, submit], 80)
    compile_bp(stage)
    REPORT["new_stage_graphs"] = inspect_stage(stage, patched=True)


def create():
    read_approved_probe()
    for destination in ALLOWED_SAVES:
        require(not unreal.EditorAssetLibrary.does_asset_exist(destination), "Refuse existing destination " + destination)
    inspect_definitions()
    require(unreal.load_asset(FONT), "Original licensed font missing")
    # Do NOT load either World in this process. Duplicate and save, then exit.
    assets = {key: duplicate(SOURCES[key], DEST[key]) for key in ("cue", "stage", "widget", "hud", "mode")}
    for key in ("cue", "widget", "hud", "mode"):
        compile_bp(assets[key])
    cue_cdo = unreal.get_default_object(assets["cue"].generated_class())
    cue_cdo.set_editor_property("CueText", unreal.Text("依次复演三幕"))
    patch_stage(assets["stage"], assets["cue"])
    unreal.get_default_object(assets["stage"].generated_class()).set_editor_property("dev_act_transition_seconds", 2.0)
    widget_cdo = unreal.get_default_object(assets["widget"].generated_class())
    require(widget_cdo.get_editor_property("chinese_font") == unreal.load_asset(FONT), "Reuse original registered font")
    widget_cdo.set_editor_property("act_title", unreal.Text("引日启幕"))
    unreal.get_default_object(assets["hud"].generated_class()).set_editor_property("widget_class", assets["widget"].generated_class())
    unreal.get_default_object(assets["mode"].generated_class()).set_editor_property("hud_class", assets["hud"].generated_class())
    for asset in assets.values():
        compile_bp(asset)
    for asset in assets.values():
        save(asset)
    world_copy = duplicate(SOURCE_MAP, MAP)
    save(world_copy)
    REPORT.update(success=True, needs_cold_configuration=True, formal_timing=False)


def configure_map():
    probe = read_approved_probe()
    stage_bp = require(unreal.load_asset(DEST["stage"]), "New copied Stage")
    inspect_stage(stage_bp, patched=True)
    _, world, api, labels = load_map(MAP)
    old_stage = require(labels.get("M3_RuntimePresentation"), "One copied source Stage")
    require(path(old_stage.get_class()) == SOURCES["stage"] + ".BP_DYP03RuntimePresentation_C", "Exact old copied class")
    director = old_stage.get_puzzle_director()
    # These values must match the cold source observation, not a guessed script.
    for label, expected in probe["source_map"]["fixture_geometry"].items():
        actual = actor_geometry(require(labels.get(label), "Copied fixture " + label))
        REPORT.setdefault("fixture_comparison", {})[label] = dict(actual=actual, expected=expected)
        require(actual == expected,
                "Copied fixture transform/class/tags changed: " + label)
    diagnostic = require(labels.get("M3_StaffProjectionProbe_AB"), "Copied diagnostic actor")
    require(path(diagnostic.get_class()) == NATIVE + "DYStaffProjectionProbe"
            and "DY_M3GeometryOnly" in [str(t) for t in diagnostic.get_editor_property("tags")],
            "Do not remove an unknown actor")
    native_bindings = {name: old_stage.get_editor_property(name) for name in (
        "puzzle_director", "stage_environment", "resolved_environment_state", "enable_staff_contact_presentation",
        "staff_projection_screen", "narrative_ground_line", "forest_presentation_actor", "DevReceiver", "DevGround")}
    new_stage = require(api.spawn_actor_from_class(stage_bp.generated_class(), old_stage.get_actor_location(),
                         old_stage.get_actor_rotation(), False), "New Stage instance only in copied map")
    new_stage.set_actor_label("ThreeAct_StagePresentation")
    new_stage.set_actor_scale3d(old_stage.get_actor_scale3d())
    new_stage.set_editor_properties(native_bindings)
    require(new_stage.get_editor_property("DevReceiver") == new_stage.get_editor_property("staff_projection_screen").static_mesh_component
            and new_stage.get_editor_property("DevGround") == new_stage.get_editor_property("narrative_ground_line"),
            "Keep native/Dev binding identity")
    entries = []
    for definition_path, _, title, _, _ in DEFINITIONS:
        entry = unreal.DYActSequenceEntry()
        entry.set_editor_properties(dict(definition=unreal.load_asset(definition_path), act_title=unreal.Text(title)))
        entries.append(entry)
    director.set_editor_property("act_sequence", entries)
    director.set_editor_property("puzzle_definition", unreal.load_asset(DEFINITIONS[0][0]))
    require(api.destroy_actor(old_stage), "Replace only copied explicitly identified old Stage")
    require(api.destroy_actor(diagnostic), "Remove only copied exact geometry diagnostic")
    mode = require(unreal.EditorAssetLibrary.load_blueprint_class(DEST["mode"]), "New GameMode class")
    world.get_world_settings().set_editor_property("default_game_mode", mode)
    levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    require(path(world) == MAP + ".LV_ThreeActDev", "Current new map identity before save")
    require(levels.save_current_level(), "Save only independent new map")
    REPORT["saved"].append(MAP)
    REPORT.update(success=True, input_changed=False, pov_changed=False, light_intensity_changed=False,
                  old_map_saved=False, definitions_saved=False, source_map_probe_used=True,
                  requires_cold_verify=True, formal_timing=False)


def verify():
    REPORT["definitions"] = inspect_definitions()
    stage = require(unreal.load_asset(DEST["stage"]), "Saved new Stage")
    REPORT["new_stage_graphs"] = inspect_stage(stage, patched=True)
    for key in ("cue", "widget", "hud", "mode"):
        compile_bp(require(unreal.load_asset(DEST[key]), "Saved new asset " + key))
    cue = unreal.load_asset(DEST["cue"])
    widget = unreal.load_asset(DEST["widget"])
    hud = unreal.load_asset(DEST["hud"])
    mode = unreal.load_asset(DEST["mode"])
    require(str(unreal.get_default_object(cue.generated_class()).get_editor_property("CueText"))
            == "依次复演三幕", "Cold copied Cue neutral CDO")
    widget_cdo = unreal.get_default_object(widget.generated_class())
    require(widget_cdo.get_editor_property("chinese_font") == unreal.load_asset(FONT)
            and str(widget_cdo.get_editor_property("act_title")) == "引日启幕",
            "Cold own first-act title and original font")
    require(unreal.get_default_object(hud.generated_class()).get_editor_property("widget_class")
            == widget.generated_class()
            and unreal.get_default_object(mode.generated_class()).get_editor_property("hud_class")
            == hud.generated_class(), "Cold explicit new mode -> HUD -> widget class chain")
    exact_float(unreal.get_default_object(stage.generated_class()).get_editor_property("dev_act_transition_seconds"),
                2.0, "Cold confirmed candidate transition delay")
    main = BGE.get_graph_editor(BEL.find_event_graph(stage))
    require(main.find_event_node("ReceivePuzzleActivated"), "Actual per-act guidance override")
    creates = [n for n in main.list_all_nodes() if n.get_class().get_name() == "K2Node_CreateWidget"]
    require(len(creates) == 1 and creates[0].find_input_pin("Class").get_pin_value() == path(cue.generated_class()),
            "Cold actual copied Cue CreateWidget class")
    setter = calls(graph_editor(stage, "ShowCaption"), "SetCueText")
    require(len(setter) == 1
            and node_metadata(setter[0])["references"]["FunctionReference"]["member_parent"]
            == path(cue.generated_class()), "Cold actual copied Cue setter declaring class")
    REPORT["new_map"] = inspect_map(MAP, expect_sequence=True)
    REPORT.update(success=True, cold_read_only=True, saved=[])


def refine_caption():
    read_approved_probe()
    filename = package_file(DEST["stage"])
    with open(filename, "rb") as stream:
        before_hash = hashlib.sha256(stream.read()).hexdigest().upper()
    require(before_hash == "4877F0C3FFED6E429417443C9EBE4A1BDCF86D661AD6F99FCA45AF6BF1B91C4C",
            "Caption refinement requires the exact cold-verified new Stage asset")
    stage = require(unreal.load_asset(DEST["stage"]), "Only new ThreeAct Stage")
    inspect_stage(stage, patched=True)
    _, caption = inspect_complete_growth(stage, patched=True)
    require(text_source(caption.find_input_pin("Text")) == "林影已成 · 正在确认复演结果",
            "Only the observed contradictory new caption may change")
    literal(caption.find_input_pin("Text"), "林影已成")
    compile_bp(stage)
    inspect_stage(stage, patched=True)
    save(stage)
    REPORT.update(success=True, previous_stage_sha256=before_hash,
                  change="New Stage final caption only; no gameplay or Timeline edits")


protected_before = None
report_writable = False
try:
    # Audit output is generated data, not a project source editor shortcut.
    saved_root = os.path.normcase(os.path.realpath(
        unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_saved_dir())))
    output_path = os.path.normcase(os.path.realpath(os.path.abspath(OUT)))
    require(os.path.commonpath([saved_root, output_path]) == saved_root,
            "Report must stay under the calling project's Saved directory")
    require(not os.path.exists(output_path), "Preserve prior evidence; choose a new report filename")
    report_writable = True
    protected_before = identities()
    REPORT["protected_before"] = protected_before
    if PHASE == "source_probe":
        REPORT["definitions"] = inspect_definitions()
        REPORT["source_stage_graphs"] = inspect_stage(require(unreal.load_asset(SOURCES["stage"]), "Source Stage"))
        REPORT["source_map"] = inspect_map(SOURCE_MAP)
        REPORT.update(success=True, cold_read_only=True)
    elif PHASE == "create":
        create()
    elif PHASE == "configure_map":
        configure_map()
    elif PHASE == "verify":
        verify()
    elif PHASE == "refine_caption":
        refine_caption()
    else:
        raise RuntimeError("Unknown explicit authoring phase: " + PHASE)
    REPORT["protected_after"] = identities()
    require(REPORT["protected_after"] == protected_before, "Original source package changed on disk")
except Exception:
    REPORT["success"] = False
    REPORT["error"] = traceback.format_exc()
    unreal.log_error("DY_THREE_ACT_AUTHOR " + REPORT["error"])
finally:
    if protected_before is not None:
        try:
            REPORT.setdefault("protected_after", identities())
        except Exception:
            REPORT["success"] = False
            REPORT["protected_after_error"] = traceback.format_exc()
    if report_writable:
        os.makedirs(os.path.dirname(os.path.abspath(OUT)), exist_ok=True)
        # Exclusive creation preserves the old report if a failed invocation reused it.
        with open(OUT, "x", encoding="utf-8") as stream:
            json.dump(REPORT, stream, ensure_ascii=False, indent=2)
    unreal.log("DY_THREE_ACT_AUTHOR_FINISHED " + str(REPORT["success"]))
