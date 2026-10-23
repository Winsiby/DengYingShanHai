"""Separate diagnostic driver. NOT the human playable entry or physical-key proof.

Drives existing reflected parameter setters and waits actual world time/15 Hz.
Reset calls the same InteractionComponent semantic endpoint as native R, only
after genuine native focus/toggle acquired control. No direct success/token seam.
"""
import importlib.util
import os
import sys
import time
import traceback
import unreal

sys.dont_write_bytecode = True  # BEFORE compiling/importing the local player module.
spec = importlib.util.spec_from_file_location("dy_p03_playable",
    os.path.join(unreal.Paths.project_dir(), "Scripts", "Play-P03DevCandidate.py"))
play = importlib.util.module_from_spec(spec)
spec.loader.exec_module(play)


class Verify(play.Playable):
    def __init__(self):
        super().__init__()
        self.diagnostic = True
        self.test_phase = "startup"
        self.test_started = None
        self.safety_deadline = time.monotonic()+150
        self.reset_pose = None
        self.checks = []

    def checked(self, name, **evidence):
        self.checks.append(name)
        play.record("TestPassed", name=name, physical_keys=False, **evidence)

    def next_test(self, phase):
        self.test_phase, self.test_started = phase, self.now()

    def set_pair(self, light, puppet):
        self.refs["light_control"].set_normalized_value(light)
        self.refs["puppet_control"].set_normalized_value(puppet)

    def drive_diagnostic(self):
        play.base.require(time.monotonic() < self.safety_deadline, "Verification timeout")
        r = self.refs
        if self.test_started is None:
            self.next_test("startup")
        elapsed = self.now()-self.test_started
        result = r["director"].get_last_evaluation()
        interaction = unreal.GameplayStatics.get_player_pawn(r["world"], 0).get_interaction_component()
        if self.test_phase == "startup" and elapsed > 1:
            play.base.require(not result.resolve_count and not r["forest"].has_forest_session(), "Auto-answer startup")
            self.checked("UnsolvedStartup", initial_light=r["light_control"].get_normalized_value(),
                initial_puppet=r["puppet_control"].get_normalized_value())
            self.test_original_rotation = r["pc"].get_control_rotation()
            self.next_test("acquire_focus")
        elif self.test_phase == "acquire_focus":
            focused = interaction.get_focused_actor()
            if focused != r["light"]:
                view_location, _rotation = r["pc"].get_player_view_point()
                r["pc"].set_control_rotation(unreal.MathLibrary.find_look_at_rotation(view_location, r["light"].get_actor_location()))
                play.base.require(elapsed < 8, "Cannot acquire native lamp focus by diagnostic aiming")
                return
            play.base.require(interaction.toggle_control(), "Native semantic E cannot acquire focused light")
            play.base.require(interaction.get_active_controlled_actor() == r["light"], "Wrong active native control")
            r["pc"].set_control_rotation(self.test_original_rotation)  # Diagnostic only; player driver never does this.
            self.checked("NativeFocusAndSemanticE", diagnostic_aim_only=True, initial_spawn_focus_not_claimed=True)
            self.set_pair(.72, .1)
            self.next_test("light_only")
        elif self.test_phase == "light_only" and elapsed > 1.6:
            play.base.require(not result.resolve_count and not result.all_required_conditions_valid, "Light alone resolved")
            self.checked("LightOnlyRejected", world_elapsed=elapsed)
            self.set_pair(.1, .85)
            self.next_test("puppet_only")
        elif self.test_phase == "puppet_only" and elapsed > 1.6:
            play.base.require(not result.resolve_count and not result.all_required_conditions_valid, "Puppet alone resolved")
            self.checked("PuppetOnlyRejected", world_elapsed=elapsed)
            self.set_pair(.72, .85)
            self.next_test("partial_hold")
        elif self.test_phase == "partial_hold" and elapsed > .45:
            play.base.require(not result.resolve_count and 0 < result.hold_elapsed_seconds < 1.25, "No real partial hold")
            self.checked("PartialHold", measured_hold=result.hold_elapsed_seconds, required=1.25)
            self.set_pair(.5, .85)
            self.next_test("interrupt")
        elif self.test_phase == "interrupt" and elapsed > .25:
            play.base.require(not result.resolve_count and result.hold_elapsed_seconds == 0, "Interrupted hold retained time")
            self.checked("HoldInterrupted", measured_hold=result.hold_elapsed_seconds)
            self.set_pair(.72, .85)
            self.next_test("resolve_drop")
        elif self.test_phase == "resolve_drop" and self.state == "drop" and self.now()-r["clock"] > .7:
            play.base.require(result.resolve_count == 1 and not r["forest"].has_forest_session(), "Invalid drop authority")
            self.checked("RealTimedResolveBeforeDrop", hold=result.hold_elapsed_seconds,
                since_new_hold=self.now()-self.test_started, forest_absent=True)
            self.semantic_reset(interaction, "reset_drop")
        elif self.test_phase == "reset_drop" and self.state == "play":
            self.check_reset("DropResetCleanup")
            self.set_pair(.72, .85)
            self.next_test("resolve_growth")
        elif self.test_phase == "resolve_growth" and self.state == "growth" and self.now()-r["clock"] > 1:
            play.base.require(r["forest"].has_forest_session() and len(r["forest"].get_branch_mesh_components()) == 15,
                "No real growth resources")
            self.checked("ContactBeforeRealGrowth", resources=15)
            self.semantic_reset(interaction, "reset_growth")
        elif self.test_phase == "reset_growth" and self.state == "play":
            self.check_reset("GrowthResetCleanup")
            self.set_pair(.72, .85)
            self.next_test("final_attempt")
        elif self.test_phase == "final_attempt" and self.state == "complete":
            self.checked("ContinuousCompletion", attempts=self.completed_attempts, actual_branches=15)
            values = [r["light_control"].get_normalized_value(), r["puppet_control"].get_normalized_value()]
            interaction.apply_primary_axis(1, .2)
            play.base.require(values == [r["light_control"].get_normalized_value(), r["puppet_control"].get_normalized_value()],
                "Resolved disabled control moved scene")
            interaction.end_active_control()
            play.base.require(not interaction.is_controlling(), "Semantic E release failed")
            self.checked("ResolvedControlDisabledAndRelease", native_control_released=True)
            self.shot = play.OUT+"/ForestComplete.png"
            unreal.SystemLibrary.execute_console_command(r["world"],
                'HighResShot 1600x900 filename="%s"' % self.shot, r["pc"])
            self.next_test("capture")
        elif self.test_phase == "capture" and elapsed > .6 and os.path.exists(self.shot):
            play.base.require(str(r["hud_status"].get_text()) == "第三幕影形 · 成", "Release restored old P02 caption")
            self.checked("CurrentCaptionSurvivesSemanticERelease", actual_umg_text=True, visual_font_not_claimed=True)
            play.record("VerificationSummary", checks=self.checks, passed=len(self.checks), failed=0,
                physical_keys=False, package=False, screenshot=self.shot)
            self.stop_session()

    def semantic_reset(self, interaction, phase):
        play.base.require(interaction.get_active_controlled_actor() == self.refs["light"], "Native R has no active object")
        self.stale_token = self.refs["snapshot"].token
        interaction.reset_active_control()  # Same semantic route as HandleResetControlledInput.
        self.reset_pose = self.refs["staff"].get_relative_transform().rotation
        self.next_test(phase)

    def check_reset(self, name):
        r = self.refs
        play.base.require(r["staff"].get_relative_transform().rotation == self.reset_pose
            and r["staff"].get_relative_transform().translation == r["staff_base_location"]
            and not r["forest"].has_forest_session() and not r["forest"].get_branch_mesh_components()
            and not r["director"].is_resolved_token_current(self.stale_token)
            and not r["presentation"].try_accept_staff_contact(self.stale_token), "Semantic R cleanup invalid")
        self.checked(name, current_reset_rotation_preserved=True, translation_restored=True,
            stale_token_rejected=True, resources=0)


unreal.EditorPythonScripting.set_keep_python_script_alive(True)
session = Verify()
try:
    session.begin()
except Exception:
    session.error = traceback.format_exc()
    unreal.log_error("DY_P03_VERIFICATION_SETUP_FAILURE "+session.error)
    session.finish()
