"""Author ONLY new Dev runtime assets using UE's official graph editor.

Python never drives the playable cue. Refuse existing destinations; do not save
the source map, old forest, old widgets, defaults, config, or other dirty assets.
Temporary 2/6 second linear timings and candidate answers are not formal tuning.
"""
import json
import os
import traceback
import unreal

ROOT = "/Game/DengYingShanHai/Dev/M3/Runtime"
MAP = "/Game/DengYingShanHai/Dev/M3/Maps/LV_M3RuntimeCandidate"
SOURCE = "/Game/DengYingShanHai/Dev/M3/Maps/LV_M3GeometryProbe"
FOREST = "/Game/DengYingShanHai/Dev/M3/Forest/BP_DYForestPresentation_Dev"
FONT = "/Game/DengYingShanHai/Dev/M2/UI/FF_DYSourceHanSansSC_Font"
PUZZLE = "P03_DevPlayableCandidate"
OUT = os.environ.get("DY_P03_RUNTIME_AUTHOR_OUT", unreal.Paths.project_saved_dir()
    + "Audit-2026-10-06-P03RuntimeWiring/Author-Run1.json")
REPORT = {"success": False, "error": None, "saved": [], "map": MAP}
BEL = unreal.BlueprintEditorLibrary
BGE = unreal.BlueprintGraphEditor
NATIVE = "/Script/DengYingShanHai."
MATH = "/Script/Engine.KismetMathLibrary."
STAGE = NATIVE + "DYStagePresentation."
DIR = NATIVE + "DYPuzzleDirector."
COMP = "/Script/Engine.SceneComponent."


def require(value, why):
    if not value:
        raise RuntimeError(why)
    return value


def connect(source, target):
    require(source.is_valid() and target.is_valid(), "Missing pin")
    require(source.try_create_connection(target), "Pin link failed: "
        + str(source.get_pin_name()) + " -> " + str(target.get_pin_name()))


def literal(pin, value):
    require(pin.is_valid() and pin.set_pin_value(str(value)), "Invalid literal: " + str(value))


def compile_bp(bp):
    require(BEL.compile_blueprint(bp), "Compile failed: " + bp.get_path_name())
    for graph in BEL.list_graphs(bp):
        ed = BGE.get_graph_editor(graph)
        require(not ed.list_nodes_with_errors(), "Graph errors: " + graph.get_path_name())


def make_bp(name, parent, widget=False):
    factory = unreal.WidgetBlueprintFactory() if widget else unreal.BlueprintFactory()
    factory.set_editor_property("parent_class", parent)
    bp = require(unreal.AssetToolsHelpers.get_asset_tools().create_asset(name, ROOT,
        unreal.WidgetBlueprint if widget else unreal.Blueprint, factory), "Create " + name)
    compile_bp(bp)
    return bp


def save(asset):
    path = asset.get_path_name().split(".")[0]
    require(path.startswith(ROOT + "/"), "Save outside runtime whitelist")
    require(unreal.EditorAssetLibrary.save_loaded_asset(asset, only_if_is_dirty=False), "Save " + path)
    REPORT["saved"].append(path)


def struct_type(name, module="DengYingShanHai"):
    return BEL.get_struct_type(require(unreal.load_object(None, "/Script/" + module + "." + name), "Struct " + name))


def object_type(cls):
    return BEL.get_object_reference_type(cls if isinstance(cls, unreal.Class) else cls.static_class())


class Graph:
    def __init__(self, bp, graph):
        self.bp, self.ed = bp, BGE.get_graph_editor(graph)
        self.nodes = []

    def place(self, node):
        require(node, "Cannot author graph node")
        node.set_node_pos(unreal.IntPoint((len(self.nodes) % 5) * 480,
            (len(self.nodes) // 5) * 220))
        self.nodes.append(node)
        return node

    def call(self, path, target=None, **args):
        n = self.place(self.ed.add_call_function_node(path))
        if target is not None:
            connect(target, n.find_self_pin())
        for name, value in args.items():
            if isinstance(value, unreal.BlueprintGraphPin):
                connect(value, n.find_input_pin(name))
            else:
                literal(n.find_input_pin(name), value)
        return n

    def result(self, path, target=None, **args):
        return self.call(path, target, **args).find_result_pin()

    def get(self, name, target=None, class_path=""):
        n = self.place(self.ed.add_get_member_variable_node(name, class_path))
        if target is not None:
            connect(target, n.find_self_pin())
        return n.find_result_pin()

    def set(self, exec_pin, name, value):
        n = self.place(self.ed.add_set_member_variable_node(name))
        connect(exec_pin, n.find_execute_pin())
        if isinstance(value, unreal.BlueprintGraphPin):
            connect(value, n.find_input_pin(name))
        else:
            literal(n.find_input_pin(name), value)
        return n.find_then_pin()

    def exec(self, start, node):
        connect(start, node.find_execute_pin())
        return node.find_then_pin() if node.get_class().get_name() != "K2Node_FunctionResult" else None

    def branch(self, start, condition):
        n = self.place(self.ed.add_branch_node())
        connect(start, n.find_execute_pin())
        connect(condition, n.find_input_pin("Condition"))
        return n.find_output_pin("then"), n.find_output_pin("else")

    def break_struct(self, name, value):
        actions = [str(a) for a in self.ed.list_available_nodes([])
            if str(a).split("|")[-1] == "Break" + name]
        require(len(actions) == 1, "Actual break action " + name + ": " + repr(actions))
        n = self.place(self.ed.create_node_from_name(actions[0], unreal.Vector2D(), []))
        inputs = [p for p in n.list_all_pins()
            if p.get_pin_direction() == unreal.EdGraphPinDirection.EGPD_INPUT]
        require(len(inputs) == 1, "Break input shape " + name)
        connect(value, inputs[0])
        return {str(p.get_pin_name()): p for p in n.list_all_pins()
            if p.get_pin_direction() == unreal.EdGraphPinDirection.EGPD_OUTPUT}

    def bool_all(self, *pins):
        answer = pins[0]
        for pin in pins[1:]:
            answer = self.result(MATH + "BooleanAND", A=answer, B=pin)
        return answer

    def not_(self, pin):
        return self.result(MATH + "Not_PreBool", A=pin)

    def guid_eq(self, a, b):
        return self.result("/Script/Engine.KismetGuidLibrary.EqualEqual_GuidGuid", A=a, B=b)

    def valid(self, obj):
        return self.result("/Script/Engine.KismetSystemLibrary.IsValid", Object=obj)

    def same_vector(self, a, b):
        return self.result(MATH + "EqualExactly_VectorVector", A=a, B=b)

    def same_transform(self, a, b):
        return self.result(MATH + "NearlyEqual_TransformTransform", A=a, B=b,
            LocationTolerance="0.00000001", RotationTolerance="0.00000001", Scale3DTolerance="0.00000001")

    def transform_parts(self, value):
        node = self.call(MATH + "BreakTransform", InTransform=value)
        return {name: node.find_output_pin(name) for name in ("Location", "Rotation", "Scale")}

    def own_call(self, name, **args):
        # The official editor resolves current SkeletonGeneratedClass members.
        return self.call(name, **args)

    def finish(self, text):
        self.ed.add_comment_to_nodes(text, self.nodes, 80)


def member(bp, name, pin_type):
    require(BEL.add_member_variable(bp, name, pin_type), "Member " + name)
    BEL.set_blueprint_variable_instance_editable(bp, name, False)
    BEL.set_blueprint_variable_expose_on_spawn(bp, name, False)
    BEL.set_blueprint_variable_category(bp, name, unreal.Text("Dev runtime cue"))


def function(bp, name, args=(), output=None, pure=False):
    editor = BGE.create_and_edit_function_graph(bp, name)
    values = {key: editor.add_graph_input_parameter(key, typ) for key, typ in args}
    ret = editor.add_graph_output_parameter("Result", output) if output else None
    if pure:
        editor.set_is_pure_function(True)
    editor.set_function_is_private()
    return Graph(bp, editor.get_graph()), values, ret


def event(bp, name):
    graph = Graph(bp, BEL.find_event_graph(bp))
    node = graph.place(BEL.add_event_override(bp, name, unreal.IntPoint()))
    return graph, node


def make_cue():
    # OnPaint is a public UE override; only renders stored text using the existing
    # embedded OFL font. No protected WidgetTree writes, Tick, input or discovery.
    bp = make_bp("WBP_DYP03RuntimeCue", unreal.UserWidget, True)
    member(bp, "CueText", BEL.get_basic_type_by_name("text"))
    compile_bp(bp)
    graph = Graph(bp, BEL.add_function_override(bp, "OnPaint"))
    entry = graph.ed.find_graph_entry_pin()
    draw = graph.call("/Script/UMG.WidgetBlueprintLibrary.DrawTextFormatted",
        Context=entry.get_owning_node().find_output_pin("Context"), Text=graph.get("CueText"),
        Position="(X=20,Y=64)", Font=FONT + ".FF_DYSourceHanSansSC_Font", FontSize=22,
        Tint="(R=0.93,G=0.89,B=0.80,A=1)")
    graph.exec(entry, draw)
    graph.exec(draw.find_then_pin(), graph.place(graph.ed.add_return_node()))
    graph.finish("Passive caption only. No puzzle reads, input, timers, or progress computation.")
    setter, inputs, _ = function(bp, "SetCueText", [("Text", BEL.get_basic_type_by_name("text"))])
    setter.ed.set_function_is_public()
    setter.set(setter.ed.find_graph_entry_pin(), "CueText", inputs["Text"])
    compile_bp(bp)
    defaults = unreal.get_default_object(bp.generated_class())
    defaults.set_editor_property("CueText", unreal.Text("杖落成林 · Dev候选"))
    defaults.set_editor_property("tick_frequency", unreal.WidgetTickFrequency.NEVER)
    defaults.set_editor_property("visibility", unreal.SlateVisibility.HIT_TEST_INVISIBLE)
    return bp


def build_presentation(cue):
    bp = make_bp("BP_DYP03RuntimePresentation", unreal.DYStagePresentation)
    bool_type = BEL.get_basic_type_by_name("bool")
    guid = struct_type("Guid", "CoreUObject")
    vector = struct_type("Vector", "CoreUObject")
    for name in ("CueOwned", "Dropping", "Growing", "Completed", "Ended"):
        member(bp, name, bool_type)
    for name in ("CueToken", "UsedToken"):
        member(bp, name, guid)
    member(bp, "ResolvedStart", struct_type("DYStageResolvedPresentationSnapshot"))
    member(bp, "BaseStaffLocation", vector)
    member(bp, "StaffRef", object_type(unreal.StaticMeshComponent))
    member(bp, "DevReceiver", object_type(unreal.StaticMeshComponent))
    member(bp, "DevGround", object_type(unreal.Actor))
    # Explicit new-map authoring bindings, not runtime world scans. The creator
    # and verifier check identity with native Screen/Ground configuration.
    for name in ("DevReceiver", "DevGround"):
        BEL.set_blueprint_variable_instance_editable(bp, name, True)
    member(bp, "CueView", object_type(cue.generated_class()))
    compile_bp(bp)
    declarations = {
        "ShowCaption": function(bp, "ShowCaption", [("Text", BEL.get_basic_type_by_name("text"))]),
        "OwnsToken": function(bp, "OwnsToken", [("Token", guid)], bool_type, True),
        "SceneUnchanged": function(bp, "SceneUnchanged", [("Token", guid)], bool_type, True),
        "ReleaseCue": function(bp, "ReleaseCue", [("Token", guid)]),
        "ApplyDrop": function(bp, "ApplyDrop", [("Token", guid), ("Progress", BEL.get_basic_type_by_name("real"))]),
        "AcceptContact": function(bp, "AcceptContact", [("Token", guid)]),
        "ApplyGrowth": function(bp, "ApplyGrowth", [("Token", guid), ("Progress", BEL.get_basic_type_by_name("real"))]),
        "CompleteGrowth": function(bp, "CompleteGrowth", [("Token", guid)]),
    }
    compile_bp(bp)
    main = Graph(bp, BEL.find_event_graph(bp))
    timeline_action = [str(a) for a in main.ed.list_available_nodes([])
        if str(a) == "|添加时间轴……"]
    require(len(timeline_action) == 1, "Verified localized Timeline action unavailable")
    timelines = []
    for length in (2.0, 6.0):
        previous = {t.get_path_name() for t in unreal.ObjectIterator(unreal.TimelineTemplate)}
        node = main.place(main.ed.create_node_from_name(timeline_action[0], unreal.Vector2D(), []))
        templates = [t for t in unreal.ObjectIterator(unreal.TimelineTemplate)
            if t.get_path_name() not in previous and t.get_outer() == bp.generated_class()]
        require(len(templates) == 1, "One new native Timeline template")
        template = templates[0]
        require(template.get_name().endswith("_Template"), "UE template naming contract")
        name = template.get_name()[:-len("_Template")]
        for key, value in (("TimelineLength", length), ("LengthMode", unreal.TimelineLengthMode.TL_TIMELINE_LENGTH),
                           ("bAutoPlay", False), ("bLoop", False), ("bIgnoreTimeDilation", False)):
            template.set_editor_property(key, value)
        timelines.append((node, name, length))
    compile_bp(bp)
    drop, growth = timelines

    g, p, ret = declarations["OwnsToken"]
    director = g.result(STAGE + "GetPuzzleDirector")
    condition = g.bool_all(g.get("CueOwned"), g.not_(g.get("Ended")), g.valid(director),
        g.guid_eq(g.get("CueToken"), p["Token"]))
    yes, no = g.branch(g.ed.find_graph_entry_pin(), condition)
    g.exec(no, g.place(g.ed.add_return_node()))
    connect(g.result(DIR + "IsResolvedTokenCurrent", director, Token=p["Token"]), ret.find_input_pin("Result"))
    g.exec(yes, ret)

    g, p, ret = declarations["SceneUnchanged"]
    director = g.result(STAGE + "GetPuzzleDirector")
    light = g.result(DIR + "GetLightRigActor", director)
    puppet = g.result(DIR + "GetPuppetActor", director)
    yes, no = g.branch(g.ed.find_graph_entry_pin(), g.bool_all(
        g.own_call("OwnsToken", Token=p["Token"]).find_result_pin(),
        g.valid(g.get("StaffRef")), g.valid(g.get("DevReceiver")), g.valid(g.get("DevGround"))))
    g.exec(no, g.place(g.ed.add_return_node()))
    yes, no = g.branch(yes, g.bool_all(g.valid(light), g.valid(puppet)))
    g.exec(no, g.place(g.ed.add_return_node()))
    start = g.break_struct("DYStageResolvedPresentationSnapshot", g.get("ResolvedStart"))
    old = g.break_struct("DYStaffProjectionCapture", start["Projection"])
    old_staff = g.break_struct("DYStaffGeometrySnapshot", old["Staff"])
    capture = g.result(NATIVE + "DYStaffProjectionLibrary.CaptureStaffProjection",
        Light=light, Puppet=puppet, Screen=g.get("DevReceiver"))
    now = g.break_struct("DYStaffProjectionCapture", capture)
    a = g.transform_parts(g.result(COMP + "K2_GetComponentToWorld", g.get("StaffRef")))
    b = g.transform_parts(old_staff["ComponentTransform"])
    roots = []
    for actor, key in ((light, "Light"), (puppet, "Puppet")):
        snapshot = g.break_struct("DYControlSnapshot", start[key])
        roots.append(g.same_transform(g.result("/Script/Engine.Actor.GetTransform", actor), snapshot["WorldTransform"]))
    ground = g.break_struct("DYNarrativeGroundLineSnapshot", start["GroundLine"])
    condition = g.bool_all(g.own_call("OwnsToken", Token=p["Token"]).find_result_pin(), now["bHasGeometry"], *roots,
        g.same_transform(now["ScreenTransform"], old["ScreenTransform"]),
        g.same_vector(now["EmitterWorld"], old["EmitterWorld"]),
        g.same_vector(now["ScreenLocalMin"], old["ScreenLocalMin"]),
        g.same_vector(now["ScreenLocalMax"], old["ScreenLocalMax"]),
        g.same_vector(g.result("/Script/Engine.Actor.K2_GetActorLocation", g.get("DevGround")), ground["WorldAnchor"]),
        g.result(MATH + "EqualEqual_RotatorRotator", A=a["Rotation"], B=b["Rotation"], ErrorTolerance="0.00000001"),
        g.same_vector(a["Scale"], b["Scale"]))
    connect(condition, ret.find_input_pin("Result"))
    g.exec(yes, ret)

    g, p, _ = declarations["ShowCaption"]
    yes, _ = g.branch(g.ed.find_graph_entry_pin(), g.valid(g.get("CueView")))
    setter = require(unreal.find_object(cue.generated_class(), "SetCueText"), "Compiled widget setter")
    g.exec(yes, g.call(setter.get_path_name(), g.get("CueView"), Text=p["Text"]))

    g, p, _ = declarations["ReleaseCue"]
    yes, _ = g.branch(g.ed.find_graph_entry_pin(), g.bool_all(g.get("CueOwned"), g.guid_eq(g.get("CueToken"), p["Token"])))
    for key in ("CueOwned", "Dropping", "Growing", "Completed"):
        yes = g.set(yes, key, "false")
    for _, name, _ in timelines:
        yes = g.exec(yes, g.call("/Script/Engine.TimelineComponent.Stop", g.get(name)))
    yes = g.exec(yes, g.call(STAGE + "ClearForestPresentation", Token=p["Token"]))
    yes, _ = g.branch(yes, g.bool_all(g.not_(g.get("CueOwned")), g.valid(g.get("StaffRef"))))
    g.exec(yes, g.call(COMP + "K2_SetRelativeLocation", g.get("StaffRef"), NewLocation=g.get("BaseStaffLocation"), bSweep="false", bTeleport="false"))
    g.finish("Old-token cleanup clears local ownership BEFORE callbacks; restores translation only, never current native pose.")

    def fail(g, start, token):
        tail = g.exec(start, g.own_call("ReleaseCue", Token=token))
        tail, _ = g.branch(tail, g.not_(g.get("CueOwned")))
        g.exec(tail, g.own_call("ShowCaption", Text="Dev 表现中止 · 使用当前操纵对象 R 复位"))

    g, p, _ = declarations["ApplyDrop"]
    yes, no = g.branch(g.ed.find_graph_entry_pin(), g.bool_all(g.get("Dropping"), g.own_call("SceneUnchanged", Token=p["Token"]).find_result_pin()))
    fail(g, no, p["Token"])
    sample = g.result(NATIVE + "DYStaffDropLibrary.SampleStaffDrop", Resolved=g.get("ResolvedStart"), NormalizedProgress=p["Progress"])
    fields = g.break_struct("DYStaffDropSample", sample)
    yes, no = g.branch(yes, g.result(MATH + "EqualEqual_ByteByte", A=fields["Status"], B=unreal.DYStaffDropStatus.VALID.value))
    fail(g, no, p["Token"])
    location = g.transform_parts(fields["StaffWorldTransform"])["Location"]
    g.exec(yes, g.call(COMP + "K2_SetWorldLocation", g.get("StaffRef"), NewLocation=location, bSweep="false", bTeleport="false"))
    g.finish("Pure normalized sample from the actual Resolve; only Staff translation is written. No puzzle scoring, Tick scan or POV changes.")

    g, p, _ = declarations["AcceptContact"]
    yes, no = g.branch(g.ed.find_graph_entry_pin(), g.bool_all(g.get("Dropping"), g.own_call("SceneUnchanged", Token=p["Token"]).find_result_pin()))
    fail(g, no, p["Token"])
    accept = g.call(STAGE + "TryAcceptStaffContact", Token=p["Token"])
    yes = g.exec(yes, accept)
    contact = g.break_struct("DYStaffContactPresentationSnapshot", g.result(STAGE + "GetStaffContactPresentationSnapshot"))
    yes, no = g.branch(yes, g.bool_all(accept.find_result_pin(), contact["bHasContact"],
        g.guid_eq(contact["Token"], p["Token"]), g.own_call("OwnsToken", Token=p["Token"]).find_result_pin()))
    fail(g, no, p["Token"])
    begin = g.call(STAGE + "BeginForestPresentation", Token=p["Token"])
    yes = g.exec(yes, begin)
    yes, no = g.branch(yes, g.bool_all(begin.find_result_pin(), g.own_call("OwnsToken", Token=p["Token"]).find_result_pin()))
    fail(g, no, p["Token"])
    forest = g.result(STAGE + "GetForestPresentationActor")
    components = g.result(NATIVE + "DYForestPresentationActor.GetBranchMeshComponents", forest)
    count = g.result("/Script/Engine.KismetArrayLibrary.Array_Length", TargetArray=components)
    yes, no = g.branch(yes, g.result(MATH + "EqualEqual_IntInt", A=count, B=15))
    fail(g, no, p["Token"])
    first = g.call("/Script/Engine.KismetArrayLibrary.Array_Get", TargetArray=components, Index=0).find_output_pin("Item")
    bounds = g.call("/Script/Engine.StaticMeshComponent.GetLocalBounds", first)
    director = g.result(STAGE + "GetPuzzleDirector")
    puppet = g.result(DIR + "GetPuppetActor", director)
    args = {"Contact": g.result(STAGE + "GetStaffContactPresentationSnapshot"),
        "BranchDefinitions": g.get("BranchLayout", forest, NATIVE + "DYForestPresentationActor"),
        "MeshMin": bounds.find_output_pin("Min"), "MeshMax": bounds.find_output_pin("Max"), "PaddingFraction": ".02"}
    for name in ("Torso", "Head"):
        body = g.get(name, puppet, NATIVE + "DYPuppetActor")
        box = g.call("/Script/Engine.StaticMeshComponent.GetLocalBounds", body)
        args.update({name + "Min": box.find_output_pin("Min"), name + "Max": box.find_output_pin("Max"),
            name + "Transform": g.result(COMP + "K2_GetComponentToWorld", body)})
    preflight = g.break_struct("DYForestPreflightResult", g.result(NATIVE + "DYForestPreflightLibrary.CheckForestSilhouette", **args))
    yes, no = g.branch(yes, g.bool_all(g.result(MATH + "EqualEqual_ByteByte", A=preflight["Status"], B=unreal.DYForestPreflightStatus.VALID.value),
        g.own_call("OwnsToken", Token=p["Token"]).find_result_pin()))
    fail(g, no, p["Token"])
    yes = g.set(yes, "Dropping", "false")
    yes = g.set(yes, "Growing", "true")
    yes = g.exec(yes, g.own_call("ShowCaption", Text="杖尖已触地 · 同一点生长真实林影"))
    # Function graphs cannot host Timeline controls; call an event whose guard
    # reads the same current ownership. The Timeline still belongs to Blueprint.
    growth_event = main.place(main.ed.add_custom_event_node("StartGrowthTimeline"))
    gate, _ = main.branch(growth_event.find_then_pin(), main.bool_all(main.get("Growing"),
        main.own_call("OwnsToken", Token=main.get("CueToken")).find_result_pin()))
    connect(gate, growth[0].find_input_pin("PlayFromStart"))
    compile_bp(bp)
    g.exec(yes, g.own_call("StartGrowthTimeline"))
    g.finish("Real A contact -> recheck the old function-stack Token -> native hidden p0 -> full 15-branch/16-corner preflight -> growth.")

    g, p, _ = declarations["ApplyGrowth"]
    yes, no = g.branch(g.ed.find_graph_entry_pin(), g.bool_all(g.get("Growing"), g.own_call("SceneUnchanged", Token=p["Token"]).find_result_pin()))
    fail(g, no, p["Token"])
    apply = g.call(STAGE + "SetForestNormalizedGrowth", Token=p["Token"], Progress=p["Progress"])
    yes = g.exec(yes, apply)
    _, no = g.branch(yes, apply.find_result_pin())
    fail(g, no, p["Token"])

    g, p, _ = declarations["CompleteGrowth"]
    yes, _ = g.branch(g.ed.find_graph_entry_pin(), g.bool_all(g.get("Growing"), g.own_call("OwnsToken", Token=p["Token"]).find_result_pin()))
    apply = g.call(STAGE + "SetForestNormalizedGrowth", Token=p["Token"], Progress=1)
    yes = g.exec(yes, apply)
    yes, no = g.branch(yes, g.bool_all(apply.find_result_pin(), g.own_call("OwnsToken", Token=p["Token"]).find_result_pin()))
    fail(g, no, p["Token"])
    yes = g.set(yes, "Growing", "false")
    yes = g.set(yes, "Completed", "true")
    g.exec(yes, g.own_call("ShowCaption", Text="Dev 演出完成 · 成林保持；当前操纵对象 R 可复位"))
    g.finish("Keep the real forest under current identity. NOT FinishFinale, ForestComplete environment, Skip or whole-game Restart.")
    compile_bp(bp)

    for (timeline, name, length), update, finished in ((drop, "ApplyDrop", "AcceptContact"),
            (growth, "ApplyGrowth", "CompleteGrowth")):
        position = main.result("/Script/Engine.TimelineComponent.GetPlaybackPosition", main.get(name))
        duration = main.result("/Script/Engine.TimelineComponent.GetTimelineLength", main.get(name))
        alpha = main.result(MATH + "Divide_DoubleDouble", A=position, B=duration)
        main.exec(timeline.find_output_pin("Update"), main.own_call(update, Token=main.get("CueToken"), Progress=alpha))
        main.exec(timeline.find_output_pin("Finished"), main.own_call(finished, Token=main.get("CueToken")))
    main.finish("Dev-only linear timelines, fixed-length 2/6 seconds; world time, no autoplay, loop or ignored dilation. Not formal timing.")

    g, ev = event(bp, "ReceivePuzzleResolved")
    snapshot = g.result(STAGE + "GetResolvedStaffPresentationSnapshot")
    fields = g.break_struct("DYStageResolvedPresentationSnapshot", snapshot)
    director = g.result(STAGE + "GetPuzzleDirector")
    condition = g.bool_all(g.not_(g.get("Ended")), g.not_(g.get("CueOwned")), fields["bHasSnapshot"],
        g.result(DIR + "IsResolvedTokenCurrent", director, Token=fields["Token"]),
        g.not_(g.guid_eq(fields["Token"], g.get("UsedToken"))),
        g.result(MATH + "EqualEqual_NameName", A=fields["PuzzleId"], B=PUZZLE))
    yes, _ = g.branch(ev.find_then_pin(), condition)
    puppet = g.result(DIR + "GetPuppetActor", director)
    staff = g.get("Staff", puppet, NATIVE + "DYPuppetActor")
    sample = g.break_struct("DYStaffDropSample", g.result(NATIVE + "DYStaffDropLibrary.SampleStaffDrop", Resolved=snapshot, NormalizedProgress=0))
    yes, _ = g.branch(yes, g.bool_all(g.valid(staff), g.valid(g.get("DevReceiver")), g.valid(g.get("DevGround")),
        g.result(MATH + "EqualEqual_ByteByte", A=sample["Status"], B=unreal.DYStaffDropStatus.VALID.value)))
    for name, val in (("ResolvedStart", snapshot), ("CueToken", fields["Token"]), ("UsedToken", fields["Token"]),
            ("StaffRef", staff), ("BaseStaffLocation", g.transform_parts(g.result(COMP + "GetRelativeTransform", staff))["Location"]),
            ("CueOwned", "true"), ("Dropping", "true"), ("Growing", "false"), ("Completed", "false")):
        yes = g.set(yes, name, val)
    yes, no = g.branch(yes, g.own_call("SceneUnchanged", Token=g.get("CueToken")).find_result_pin())
    fail(g, no, g.get("CueToken"))
    yes = g.exec(yes, g.own_call("ShowCaption", Text="影形已稳 · 杖尖正落向幕上地线"))
    connect(yes, drop[0].find_input_pin("PlayFromStart"))
    g.finish("Accept ONLY the original live native capture. Same UsedToken never restarts; late synchronization cannot invent geometry.")

    g, ev = event(bp, "ReceiveStaffPresentationInvalidated")
    yes = g.exec(ev.find_then_pin(), g.own_call("ReleaseCue", Token=ev.find_output_pin("Token")))
    yes, _ = g.branch(yes, g.not_(g.get("CueOwned")))
    g.exec(yes, g.own_call("ShowCaption", Text="已复位 · 重新调整灯与偶"))
    g.finish("Real Director invalidation handles drop, growth AND completed holding. Late old identities do not stop a new cue.")

    g, ev = event(bp, "ReceiveBeginPlay")
    actions = [str(a) for a in g.ed.list_available_nodes([]) if "创建控件" in str(a) or "CreateWidget" in str(a)]
    require(len(actions) == 1, "Verified Create Widget action")
    create = g.place(g.ed.create_node_from_name(actions[0], unreal.Vector2D(), []))
    literal(create.find_input_pin("Class"), cue.generated_class().get_path_name())
    pc = g.result("/Script/Engine.GameplayStatics.GetPlayerController", PlayerIndex=0)
    connect(pc, create.find_input_pin("OwningPlayer"))
    yes, _ = g.branch(ev.find_then_pin(), g.valid(pc))
    yes = g.exec(yes, create)
    yes = g.set(yes, "CueView", create.find_result_pin())
    yes = g.exec(yes, g.call("/Script/UMG.UserWidget.AddToViewport", g.get("CueView"), ZOrder=1))
    g.exec(yes, g.own_call("ShowCaption", Text="调整灯与偶，让逐日影形稳定；沿用 E / A / D"))

    g, ev = event(bp, "ReceiveEndPlay")
    yes = g.set(ev.find_then_pin(), "Ended", "true")
    yes = g.exec(yes, g.own_call("ReleaseCue", Token=g.get("CueToken")))
    yes, _ = g.branch(yes, g.valid(g.get("CueView")))
    g.exec(yes, g.call("/Script/UMG.Widget.RemoveFromParent", g.get("CueView")))
    compile_bp(bp)
    REPORT["timelines"] = [{"variable": n, "seconds": sec, "linear": True, "autoplay": False,
        "loop": False, "world_time": True} for _, n, sec in timelines]
    REPORT["presentation_graphs"] = [str(g.get_name()) for g in BEL.list_graphs(bp)]
    return bp


def main():
    names = ("BP_DYP03RuntimePresentation", "DA_P03RuntimeCandidate", "WBP_DYP03RuntimeHUD",
        "BP_DYP03RuntimeHUD", "BP_DYP03RuntimeGameMode", "WBP_DYP03RuntimeCue")
    for path in [ROOT + "/" + name for name in names] + [MAP]:
        require(not unreal.EditorAssetLibrary.does_asset_exist(path), "Refuse existing destination " + path)
    require(unreal.load_asset(FONT), "Existing embedded project font missing")
    require(unreal.EditorAssetLibrary.does_asset_exist(SOURCE), "Source map missing")
    forest_class = require(unreal.EditorAssetLibrary.load_blueprint_class(FOREST), "Saved 15-branch forest missing")
    forest_cdo = unreal.get_default_object(forest_class)
    require(len(forest_cdo.get_editor_property("branch_layout")) == 15 and not forest_cdo.has_forest_session(), "Bad forest authoring defaults")
    cue = make_cue()
    presentation_bp = build_presentation(cue)
    # Asset authoring ONLY. The player entry never creates or mutates a Definition.
    data_factory = unreal.DataAssetFactory()
    data_factory.set_editor_property("data_asset_class", unreal.DYPuzzleDefinition)
    definition = require(unreal.AssetToolsHelpers.get_asset_tools().create_asset("DA_P03RuntimeCandidate", ROOT,
        unreal.DYPuzzleDefinition, data_factory), "Definition asset factory")
    definition.set_editor_property("puzzle_id", PUZZLE)
    definition.set_editor_property("display_name", "杖落成林 · Dev候选")
    for field, target in (("light_position", .72), ("puppet_position", .85)):
        value = unreal.DYTargetRange()
        value.set_editor_properties(dict(enabled=True, target=target, enter_tolerance=.05, exit_tolerance=.09))
        definition.set_editor_property(field, value)
    definition.set_editor_property("required_puppet_pose_id", "P02_StrideReach")
    definition.set_editor_property("required_hold_seconds", 1.25)
    hud_widget = make_bp("WBP_DYP03RuntimeHUD", unreal.DYInteractionHUDWidget, True)
    cdo = unreal.get_default_object(hud_widget.generated_class())
    cdo.set_editor_properties(dict(chinese_font=unreal.load_asset(FONT), act_title=unreal.Text("第三幕影形"),
        body_font_size=22, tick_frequency=unreal.WidgetTickFrequency.NEVER))
    hud = make_bp("BP_DYP03RuntimeHUD", unreal.DYInteractionHUD)
    unreal.get_default_object(hud.generated_class()).set_editor_property("widget_class", hud_widget.generated_class())
    mode = make_bp("BP_DYP03RuntimeGameMode", unreal.DYStageGameMode)
    unreal.get_default_object(mode.generated_class()).set_editor_property("hud_class", hud.generated_class())
    # No asset is saved until all executable graphs compile.
    for asset in (cue, presentation_bp, definition, hud_widget, hud, mode):
        save(asset)
    duplicate_map()
    # A cold second author process loads/configures the saved copy. Loading a
    # newly duplicated standalone World in the same process trips UE's world
    # leak check. Do not remove KEEPFLAGS or modify the engine to bypass it.
    REPORT.update(success=True, phase="assets_and_map_copy", needs_cold_configuration=True)


def duplicate_map():
    require(not unreal.EditorAssetLibrary.does_asset_exist(MAP), "Refuse existing map copy")
    duplicate = require(unreal.EditorAssetLibrary.duplicate_asset(SOURCE, MAP), "Duplicate new map only")
    require(duplicate.get_path_name() == MAP + ".LV_M3RuntimeCandidate", "Exact new World")
    require(unreal.EditorAssetLibrary.save_loaded_asset(duplicate, only_if_is_dirty=False), "Save duplicated new World")
    REPORT["saved"].append(MAP)


def configure_map():
    presentation_bp = require(unreal.load_asset(ROOT + "/BP_DYP03RuntimePresentation"), "Runtime BP")
    definition = require(unreal.load_asset(ROOT + "/DA_P03RuntimeCandidate"), "Runtime Definition")
    mode = require(unreal.load_asset(ROOT + "/BP_DYP03RuntimeGameMode"), "Runtime mode")
    forest_class = require(unreal.EditorAssetLibrary.load_blueprint_class(FOREST), "Existing saved forest")
    levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    actors_api = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    require(levels.load_level(MAP), "Load new map")
    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    require(world.get_path_name() == MAP + ".LV_M3RuntimeCandidate", "Unexpected map; refuse save")
    actors = list(actors_api.get_all_level_actors())
    by_label = {a.get_actor_label(): a for a in actors}
    light = require(by_label.get("M2_LightRig_P02"), "Existing light")
    puppet = require(by_label.get("M2_Puppet_P02_Controlled"), "Existing puppet")
    screen = require(by_label.get("DEV_BackScreen"), "Existing receiver")
    old_stage = require(by_label.get("M2_StagePresentation"), "Existing presentation")
    director = require(old_stage.get_editor_property("puzzle_director"), "Existing Director")
    require(director.get_evaluation_frequency_hz() == 15, "Keep 15 Hz")
    # Only explicit old temporary fixtures, in the NEW map, may be removed.
    removable = {"DEV_UnsavedNarrativeGroundLine", "DEV_UnsavedGroundLineMarker", "DEV_UnsavedP03PlayableForest"}
    for actor in actors:
        if actor.get_actor_label() in removable:
            require(actors_api.destroy_actor(actor), "Remove copied temporary fixture")
    projection = unreal.DYStaffProjectionLibrary.capture_staff_projection(light, puppet, screen.static_mesh_component)
    require(projection.has_geometry, "Actual map receiver geometry")
    lo, hi = projection.screen_local_min, projection.screen_local_max
    emitter_local = unreal.MathLibrary.inverse_transform_location(projection.screen_transform, projection.emitter_world)
    face = lo.x if emitter_local.x < lo.x else hi.x
    anchor = unreal.MathLibrary.transform_location(projection.screen_transform,
        unreal.Vector(face, (lo.y + hi.y) * .5, lo.z + (hi.z - lo.z) * .15))
    require(unreal.DYStaffContactLibrary.capture_narrative_ground_line(projection, anchor).is_valid, "Accepted high ground")
    ground = require(actors_api.spawn_actor_from_class(unreal.TargetPoint, anchor, unreal.Rotator(), False), "New ground anchor")
    ground.set_actor_label("M3_RuntimeNarrativeGroundLine")
    marker = require(actors_api.spawn_actor_from_class(unreal.StaticMeshActor, unreal.Vector(), unreal.Rotator(), False), "New ground marker")
    marker.set_actor_label("M3_RuntimeGroundLineMarker")
    mesh = marker.static_mesh_component
    mesh.set_static_mesh(unreal.load_asset("/Engine/BasicShapes/Cube"))
    mesh.set_mobility(unreal.ComponentMobility.MOVABLE)
    mesh.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
    mesh.set_editor_property("cast_shadow", False)
    normal = unreal.MathLibrary.transform_direction(projection.screen_transform,
        unreal.Vector(-1 if emitter_local.x < lo.x else 1, 0, 0))
    marker.set_actor_location(anchor + normal * .2, False, False)
    marker.set_actor_rotation(screen.get_actor_rotation(), False)
    scale = screen.get_actor_scale3d()
    marker.set_actor_scale3d(unreal.Vector(.002, abs(scale.y) * (hi.y-lo.y) / 100, .02))
    forest = require(actors_api.spawn_actor_from_class(forest_class, unreal.Vector(), unreal.Rotator(), False), "New saved forest instance")
    forest.set_actor_label("M3_RuntimeForest")
    stage = require(actors_api.spawn_actor_from_class(presentation_bp.generated_class(), unreal.Vector(), unreal.Rotator(), False), "New runtime presentation")
    stage.set_actor_label("M3_RuntimePresentation")
    stage.set_editor_properties(dict(puzzle_director=director, stage_environment=old_stage.get_stage_environment(),
        resolved_environment_state=old_stage.get_resolved_environment_state(), enable_staff_contact_presentation=True,
        staff_projection_screen=screen, narrative_ground_line=ground, forest_presentation_actor=forest,
        DevReceiver=screen.static_mesh_component, DevGround=ground))
    require(actors_api.destroy_actor(old_stage), "Replace copied old presentation in new map")
    director.set_editor_property("puzzle_definition", definition)
    require(stage.get_editor_property("DevReceiver") == stage.get_editor_property("staff_projection_screen").static_mesh_component
        and stage.get_editor_property("DevGround") == stage.get_editor_property("narrative_ground_line"), "Read-only Dev binding identity")
    world.get_world_settings().set_editor_property("default_game_mode", mode.generated_class())
    require(levels.save_current_level(), "Save new map only")
    REPORT["saved"].append(MAP)
    REPORT.update(success=True, phase="map_configured", auto_answer=False, evaluation_hz=15, inputs_changed=False, pov_changed=False,
        source_saved=False, forest_authoring_saved=False, formal_tuning=False, python_runtime_dependency=False,
        actual_ground_world=[anchor.x, anchor.y, anchor.z], graph_compile=True)


try:
    phase = os.environ.get("DY_P03_RUNTIME_AUTHOR_PHASE", "create")
    if phase == "duplicate_map":
        duplicate_map()
        REPORT.update(success=True, phase="map_copy_only", needs_cold_configuration=True)
    elif phase == "configure_map":
        configure_map()
    elif phase == "create":
        main()
    else:
        raise RuntimeError("Unknown author phase")
except Exception:
    REPORT["error"] = traceback.format_exc()
    unreal.log_error("DY_P03_RUNTIME_AUTHOR " + REPORT["error"])
finally:
    with open(OUT, "w", encoding="utf-8") as stream:
        json.dump(REPORT, stream, ensure_ascii=False, indent=2)
    unreal.log("DY_P03_RUNTIME_AUTHOR_FINISHED " + str(REPORT["success"]))
