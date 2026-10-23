"""Visible, unsaved Editor diagnostic of the EXISTING M3 runtime map.

Only public control setters and Director reset are driven by this script.
The saved Blueprint Timelines own Staff movement, real contact and tree growth.
No physical key injection, authored data changes, asset saves or camera changes.
"""
import json
import os
import sys
import time
import traceback
import unreal

sys.dont_write_bytecode = True
MAP = "/Game/DengYingShanHai/Dev/M3/Maps/LV_M3RuntimeCandidate"
AUDIT = os.path.realpath(os.path.join(unreal.Paths.project_saved_dir(), "Audit-2026-10-09-M3VisibleAutoTest"))
OUT = os.environ.get("DY_P03_VISIBLE_TEST_OUT", "")
if not OUT:
    raise RuntimeError("Launch with Start-M3AutoTest.cmd; a fresh run output directory is required.")
OUT = os.path.realpath(OUT)
if os.path.commonpath((AUDIT, OUT)) != AUDIT or OUT == AUDIT:
    raise RuntimeError("Visible test output must be a new child of its own audit directory.")
if os.path.exists(os.path.join(OUT, "Events.jsonl")):
    raise RuntimeError("Preserve existing run evidence; choose a new run.")
os.makedirs(OUT, exist_ok=True)


def require(condition, message):
    if not condition:
        raise RuntimeError(message)
    return condition


def vector(value):
    return [float(value.x), float(value.y), float(value.z)]


def record(event, **values):
    item = dict(event=event, utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), **values)
    unreal.log("DY_M3_VISIBLE_TEST " + json.dumps(item, ensure_ascii=False))
    with open(os.path.join(OUT, "Events.jsonl"), "a", encoding="utf-8") as stream:
        stream.write(json.dumps(item, ensure_ascii=False) + "\n")


class VisibleTest:
    def __init__(self):
        self.levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
        self.editor = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
        self.actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
        self.refs = None
        self.overlay = None
        self.handle = None
        self.state = "wait_pie"
        self.phase_time = 0.0
        self.attempt = 1
        self.checks = []
        self.shots = []
        self.completed = 0
        self.error = None
        self.result_written = False
        self.last_ui = -1.0
        self.last_observation = None
        self.seen_drop = False
        self.seen_contact = False
        self.startup_deadline = time.monotonic() + 120.0
        self.test_deadline = None

    def begin(self):
        require(not self.levels.is_in_play_in_editor(), "Existing PIE session: leave it untouched.")
        require(self.levels.load_level(MAP), "Cannot load saved runtime Dev map.")
        stages = [a for a in self.actors.get_all_level_actors() if a.get_actor_label() == "M3_RuntimePresentation"]
        require(len(stages) == 1, "Expected one explicitly authored M3_RuntimePresentation.")
        stage = stages[0]
        require(stage.get_class().get_name() == "BP_DYP03RuntimePresentation_C", "Wrong runtime presentation class.")
        self.stage_name = stage.get_name()
        definition = stage.get_puzzle_director().get_editor_property("puzzle_definition")
        require(str(definition.puzzle_id) == "P03_DevPlayableCandidate", "Wrong saved candidate Definition.")
        for field, target in (("light_position", .72), ("puppet_position", .85)):
            bounds = definition.get_editor_property(field)
            require(bounds.enabled and abs(bounds.target-target) < 1.e-8
                and abs(bounds.enter_tolerance-.05) < 1.e-8 and abs(bounds.exit_tolerance-.09) < 1.e-8,
                "Existing candidate bounds differ; do not rewrite them.")
        require(abs(definition.required_hold_seconds-1.25) < 1.e-8
            and str(definition.required_puppet_pose_id) == "P02_StrideReach", "Unexpected saved hold or pose.")
        self.targets = (definition.light_position.target, definition.puppet_position.target)
        record("Preflight", map=MAP, editor_only=True, package_tested=False,
            driver_sets_test_inputs=True, python_drives_cue=False, physical_keys_verified=False,
            saved_assets=False, target_light=self.targets[0], target_puppet=self.targets[1], hold=1.25)
        self.handle = unreal.register_slate_post_tick_callback(self.tick)
        self.levels.editor_request_begin_play()

    def now(self):
        return unreal.GameplayStatics.get_time_seconds(self.refs["world"])

    def change(self, state):
        self.state = state
        self.phase_time = self.now()
        record("Step", state=state, attempt=self.attempt, world_seconds=self.phase_time)

    def passed(self, name, **values):
        self.checks.append(dict(name=name, attempt=self.attempt, **values))
        record("CheckPassed", **self.checks[-1])

    def attach(self):
        world = self.editor.get_game_world()
        if not world:
            return False
        stage = unreal.find_object(None, world.get_path_name() + ":PersistentLevel." + self.stage_name)
        pc = unreal.GameplayStatics.get_player_controller(world, 0)
        if not stage or not pc or not unreal.GameplayStatics.get_player_pawn(world, 0):
            return False
        views = unreal.WidgetLibrary.get_all_widgets_of_class(world, unreal.DYInteractionHUDWidget, True)
        if not views:
            return False
        require(len(views) == 1, "Expected one current-world HUD.")
        roots = [obj for obj in unreal.ObjectIterator(unreal.CanvasPanel)
            if obj.get_name() == "DYRoot" and obj.get_outer().get_outer() == views[0]]
        if not roots:
            return False
        require(len(roots) == 1, "Ambiguous current-HUD root.")
        root, tree = roots[0], roots[0].get_outer()
        title = unreal.find_object(tree, "DYActTitle")
        if not title:
            return False
        director = stage.get_puzzle_director()
        light, puppet = director.get_light_rig_actor(), director.get_puppet_actor()
        forest = stage.get_forest_presentation_actor()
        require(light and puppet and forest and director.get_evaluation_frequency_hz() == 15.0,
            "Missing configured runtime actors or changed sampling rate.")
        staff = puppet.get_editor_property("staff")
        self.refs = dict(world=world, pc=pc, stage=stage, director=director, forest=forest, staff=staff,
            light=light.get_editor_property("light_control"), puppet=puppet.get_editor_property("puppet_control"),
            base_location=staff.get_relative_transform().translation)
        r = self.refs
        self.initial = (r["light"].get_normalized_value(), r["puppet"].get_normalized_value())
        require(not director.get_resolved_puzzle_snapshot().is_resolved and not forest.has_forest_session(),
            "Session startup is already answered or growing.")
        require(abs(self.initial[0]-.15) < 1.e-8 and abs(self.initial[1]-.15) < 1.e-8,
            "Unexpected authored reset baseline; preserve it for review.")
        self.overlay = unreal.TextBlock(outer=tree, name="DYDevP03VisibleTest")
        self.overlay.set_font(title.get_editor_property("font"))
        self.overlay.set_color_and_opacity(title.get_editor_property("color_and_opacity"))
        self.overlay.set_visibility(unreal.SlateVisibility.HIT_TEST_INVISIBLE)
        slot = root.add_child_to_canvas(self.overlay)
        slot.set_anchors(unreal.Anchors(unreal.Vector2D(0, 0), unreal.Vector2D(0, 0)))
        slot.set_alignment(unreal.Vector2D(0, 0))
        slot.set_position(unreal.Vector2D(24, 112))
        slot.set_auto_size(True)
        unreal.WidgetLibrary.set_input_mode_game_only(pc, True)
        unreal.WidgetLibrary.set_focus_to_game_viewport()
        self.test_deadline = time.monotonic() + 180.0
        self.passed("UnsolvedStartup", light=self.initial[0], puppet=self.initial[1], hz=15)
        self.change("countdown")
        record("Ready", map=world.get_path_name(), visible_pie_requested=True, physical_keys_verified=False)
        return True

    def screenshot(self, name):
        path = os.path.join(OUT, name + ".png").replace("\\", "/")
        require(not os.path.exists(path), "Refuse screenshot overwrite.")
        unreal.SystemLibrary.execute_console_command(self.refs["world"], 'Shot SHOWUI filename="%s" -nosuffix' % path,
            self.refs["pc"])
        self.shots.append(path)
        record("ScreenshotRequested", path=path, includes_ui=True)

    def ramp(self, component, start, target, duration):
        # Resolve freezes the real scene: stop test writes immediately once it occurs.
        if self.refs["director"].get_resolved_puzzle_snapshot().is_resolved:
            self.change("watch_cue")
            return False
        portion = min(1.0, max(0.0, (self.now()-self.phase_time)/duration))
        component.set_normalized_value(start+(target-start)*portion)
        return portion >= 1.0

    def observe(self):
        r = self.refs
        result = r["director"].get_last_evaluation()
        contact = r["stage"].get_staff_contact_presentation_snapshot()
        flags = tuple(bool(r["stage"].get_editor_property(name)) for name in ("Dropping", "Growing", "Completed"))
        signature = (str(result.state), str(result.feedback), flags, bool(contact.has_contact))
        if signature != self.last_observation:
            record("ActualState", attempt=self.attempt, world_seconds=self.now(), state=str(result.state),
                feedback=str(result.feedback), hold=result.hold_elapsed_seconds,
                light=r["light"].get_normalized_value(), puppet=r["puppet"].get_normalized_value(),
                pose=str(r["puppet"].get_pose_id()), dropping=flags[0], growing=flags[1], completed=flags[2],
                actual_contact=bool(contact.has_contact), branches=len(r["forest"].get_branch_mesh_components()))
            self.last_observation = signature
        if flags[0]:
            require(not r["forest"].has_forest_session() and not contact.has_contact,
                "Forest/contact appeared while Staff was still dropping.")
            if not self.seen_drop:
                self.seen_drop = True
                self.passed("NativeDropBeforeContact", actual_staff_relative=vector(r["staff"].get_relative_transform().translation))
        if flags[1] or flags[2]:
            require(contact.has_contact and r["director"].is_resolved_token_current(contact.token)
                and r["forest"].has_forest_session(), "Growth bypassed real current A-end contact.")
            if not self.seen_contact:
                self.seen_contact = True
                self.passed("NativeContactBeforeGrowth", token=contact.token.to_string(), branches=len(r["forest"].get_branch_mesh_components()))
        return result, flags

    def check_complete(self):
        r = self.refs
        sample = r["forest"].get_forest_geometry_sample()
        components = r["forest"].get_branch_mesh_components()
        require(self.seen_drop and self.seen_contact, "Continuous drop/contact observations were missed.")
        require(sample.status == unreal.DYForestGeometryStatus.VALID and len(components) == len(sample.branches) == 15,
            "Missing valid final 15-branch geometry.")
        for component, branch in zip(components, sample.branches):
            require(branch.visible and abs(branch.portion-1.0) <= 1.e-8 and component.is_visible()
                and component.get_editor_property("cast_shadow"), "Final branch is not expanded, visible and shadow casting.")
        self.completed += 1
        self.completed_token = r["director"].get_resolved_puzzle_snapshot().token
        if self.attempt == 2:
            require(self.completed_token.to_string() != self.old_token.to_string(), "Replay reused invalidated identity.")
        self.passed("BlueprintContinuousForestComplete", fifteen_branches=True, native_timeline=True,
            token=self.completed_token.to_string(), physical_keys_verified=False)

    def reset(self):
        r = self.refs
        self.old_token = self.completed_token
        r["director"].reset_current_puzzle()
        require(not r["director"].is_resolved_token_current(self.old_token)
            and not r["stage"].get_editor_property("CueOwned")
            and not r["stage"].get_editor_property("Dropping")
            and not r["stage"].get_editor_property("Growing")
            and not r["forest"].has_forest_session() and not r["forest"].get_branch_mesh_components(),
            "Completed reset retained old authority or resources.")
        require(r["staff"].get_relative_transform().translation == r["base_location"],
            "Native reset did not restore owner-relative Staff translation.")
        require(abs(r["light"].get_normalized_value()-self.initial[0]) < 1.e-8
            and abs(r["puppet"].get_normalized_value()-self.initial[1]) < 1.e-8,
            "Reset did not restore authored controls.")
        self.passed("CompletedResetCleanup", old_token_rejected=True, branches_released=True,
            translation_restored=True, reset_route="Director public API; physical R not tested")
        self.seen_drop = self.seen_contact = False
        self.change("reset_pause")

    def update_ui(self, result, flags):
        if self.now()-self.last_ui < .15:
            return
        self.last_ui = self.now()
        descriptions = {
            "countdown": "即将开始，请观看灯、皮影和幕上影子",
            "light_ramp": "缓慢调整灯：目标 0.720",
            "light_only": "灯已到位，皮影未到位：检查不会提前成功",
            "puppet_ramp": "缓慢调整皮影：目标 0.850",
            "watch_cue": "等待真实判定与演出",
            "complete_pause": "第一次成林完成，停留后自动复位",
            "reset_pause": "已复位：旧枝形清除，准备第二遍",
            "final_capture": "两次成林与复位检查通过，正在保存画面",
            "done": "自动测试通过：画面保留，可正常关闭编辑器",
            "failed": "自动测试中止，请查看日志中的具体原因",
        }
        state = "调整影形"
        if flags[0]:
            state = "正在落杖：A 端尚未接触地线"
        elif flags[1]:
            state = "A 端已接触：真实投影枝形正在生长"
        elif flags[2]:
            state = "成林完成"
        elif result.all_required_conditions_valid:
            state = "保持此刻：松开调整，等保持计时完成"
        text = ("脚本自动测试 · 第%d遍 · Editor Dev\n%s\n"
            "实际值：灯 %.3f　皮影 %.3f\n保持 %.2f / %.2f 秒\n%s") % (
            self.attempt, descriptions.get(self.state, self.state),
            self.refs["light"].get_normalized_value(), self.refs["puppet"].get_normalized_value(),
            result.hold_elapsed_seconds, result.hold_required_seconds, state)
        if self.state == "countdown":
            text += "\n%d 秒后自动开始" % max(0, int(8-(self.now()-self.phase_time))+1)
        self.overlay.set_text(unreal.Text(text))

    def write_result(self, status):
        if self.result_written:
            return
        self.result_written = True
        result = dict(status=status, error=self.error, checks=self.checks, completed_attempts=self.completed,
            screenshots=self.shots, editor_only=True, package_tested=False, physical_keys_verified=False,
            driver_sets_test_inputs=True, python_drives_cue=False, saved_assets=False, editor_retained=True)
        with open(os.path.join(OUT, "Result.json"), "w", encoding="utf-8") as stream:
            json.dump(result, stream, ensure_ascii=False, indent=2)
        record("Result", status=status, error=self.error, completed_attempts=self.completed,
            passed_checks=len(self.checks), physical_keys_verified=False, editor_retained=True)

    def dispose(self):
        # The world has ended: do not call methods on its destroyed UObject wrappers.
        self.refs = self.overlay = None
        if self.handle is not None:
            unreal.unregister_slate_post_tick_callback(self.handle)
            self.handle = None
        # -ExecutePythonScript runner would close Editor on False; user owns close.
        record("SessionStopped", result_preserved=self.result_written, editor_retained=True)

    def tick(self, _delta):
        try:
            if self.refs and (not self.editor.get_game_world() or not self.levels.is_in_play_in_editor()):
                self.write_result("CANCELED")
                self.dispose()
                return
            if self.state == "wait_pie":
                require(time.monotonic() < self.startup_deadline, "PIE/HUD startup timed out.")
                self.attach()
                return
            if self.state in ("done", "failed"):
                return  # Retain the final picture; only lifetime cleanup continues.
            require(time.monotonic() < self.test_deadline, "Visible test exceeded bounded diagnostic duration.")
            result, flags = self.observe()
            elapsed = self.now()-self.phase_time
            self.update_ui(result, flags)
            r = self.refs
            if self.state == "countdown" and elapsed >= 8.0:
                self.screenshot("01-Initial")
                self.change("light_ramp")
            elif self.state == "light_ramp" and self.ramp(r["light"], self.initial[0], self.targets[0], 4.0):
                self.change("light_only")
            elif self.state == "light_only" and elapsed >= 3.0:
                require(not result.resolve_count and not result.all_required_conditions_valid
                    and result.hold_elapsed_seconds == 0.0, "Lamp alone incorrectly resolved.")
                self.passed("LampAloneRejected", waited_world_seconds=elapsed)
                self.change("puppet_ramp")
            elif self.state == "puppet_ramp" and self.ramp(r["puppet"], self.initial[1], self.targets[1], 5.0):
                self.change("watch_cue")
            elif self.state == "watch_cue" and flags[2]:
                require(result.resolve_count == 1 and result.hold_elapsed_seconds >= 1.25,
                    "Native completion did not use one timed Resolve.")
                self.check_complete()
                self.change("complete_pause" if self.attempt == 1 else "final_capture")
            elif self.state == "complete_pause":
                if elapsed >= .5 and not any("02-FirstForest" in path for path in self.shots):
                    self.screenshot("02-FirstForest")
                if elapsed >= 4.0:
                    self.reset()
            elif self.state == "reset_pause":
                if elapsed >= .5 and not any("03-Reset" in path for path in self.shots):
                    self.screenshot("03-Reset")
                if elapsed >= 3.0:
                    self.attempt = 2
                    self.change("light_ramp")
            elif self.state == "final_capture":
                if elapsed >= .5 and not any("04-FinalForest" in path for path in self.shots):
                    self.screenshot("04-FinalForest")
                if elapsed >= 1.5 and self.shots and all(os.path.exists(path) for path in self.shots):
                    self.change("done")
                    self.last_ui = -1.0
                    self.update_ui(result, flags)
                    self.write_result("PASS")
        except Exception:
            self.error = traceback.format_exc()
            unreal.log_error("DY_M3_VISIBLE_TEST " + self.error)
            self.state = "failed"
            if self.refs and self.overlay and self.editor.get_game_world():
                self.overlay.set_text(unreal.Text("脚本自动测试中止\n请查看本次 Result.json 和 Session.log\n画面保留，编辑器可正常关闭"))
            self.write_result("FAIL")
            if not self.refs:
                self.dispose()


unreal.EditorPythonScripting.set_keep_python_script_alive(True)
session = VisibleTest()
try:
    session.begin()
except Exception:
    session.error = traceback.format_exc()
    unreal.log_error("DY_M3_VISIBLE_TEST_SETUP " + session.error)
    session.write_result("FAIL")
    session.dispose()
