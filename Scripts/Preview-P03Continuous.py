"""Editor-only continuous Dev comparison; not a playable or packaged P03 finale.

Uses existing real Resolve/contact and the 15-branch diagnostic geometry. No
assets are saved. Temporary seconds affect only this process, not puzzle data.
"""
import importlib.util
import json
import math
import os
import sys
import time
import traceback
import unreal

sys.dont_write_bytecode = True
spec = importlib.util.spec_from_file_location("dy_continuous_refined_base",
    os.path.join(unreal.Paths.project_dir(), "Scripts", "Preview-P03BranchRefinement.py"))
refined = importlib.util.module_from_spec(spec)
spec.loader.exec_module(refined)
forest, base = refined.forest, refined.base
AUDIT = "C:/UEProjects/DengYingShanHai/Saved/Audit-2026-10-04-P03ContinuousPreview"
base.OUT = os.environ.get("DY_P03_CONTINUOUS_OUT", AUDIT + "/Run1")
base.require(os.path.commonpath((os.path.abspath(base.OUT), os.path.abspath(AUDIT)))
    == os.path.abspath(AUDIT), "Continuous evidence must stay inside its own audit")
# Labels for inherited branch diagnostics, not a static PHASES playback schedule.
forest.PHASES = (("Continuous", 0.0, 0.0, True),)


def preview_seconds(name, default, minimum, maximum):
    value = float(os.environ.get(name, str(default)))
    base.require(math.isfinite(value) and minimum <= value <= maximum,
        "Invalid bounded preview seconds: " + name)
    return value


def normalized_progress(elapsed, duration):
    """Elapsed-time progression, independent of the number of render callbacks."""
    if not math.isfinite(elapsed) or not math.isfinite(duration) or duration <= 0:
        raise ValueError("Progress needs finite elapsed time and positive duration")
    return max(0.0, min(1.0, elapsed / duration))


def record(event, **values):
    unreal.log("DY_CONTINUOUS_PREVIEW " + json.dumps(dict(event=event, **values), ensure_ascii=False))


class ContinuousPreview(refined.RefinedBranchPreview):
    def __init__(self):
        super().__init__()
        self.drop_seconds = preview_seconds("DY_P03_DROP_SECONDS", 2.0, .25, 30.0)
        self.growth_seconds = preview_seconds("DY_P03_GROWTH_SECONDS", 6.0, .25, 60.0)
        self.hold_seconds = preview_seconds("DY_P03_FINAL_HOLD_SECONDS", 6.0, 0.0, 30.0)
        self.motion_frames = {"drop": 0, "growth": 0}
        self.max_callback_gap = {"drop": 0.0, "growth": 0.0}
        self.max_progress_step = {"drop": 0.0, "growth": 0.0}
        self.phase_elapsed_end = {}
        self.phase_callback_last = None
        self.phase_started = None
        self.last_drop = self.last_growth = 0.0
        self.contact_count = 0
        self.shot_name = None

    def begin(self):
        base.require(not os.path.exists(base.OUT), "Refuse to overwrite existing continuous run")
        record("PreviewSettings", drop_seconds=self.drop_seconds, growth_seconds=self.growth_seconds,
            final_hold_seconds=self.hold_seconds, temporary_preview_values=True,
            approved_formal_seconds=False, changed_puzzle_parameters=False,
            automatic_fixture=True, editor_only=True, no_mid_motion_screenshot_pause=True)
        super().begin()

    def apply_sample(self):
        # Called by the existing begin_samples after it captures the live Resolve.
        self.index = 0
        self.apply_progress(0.0, 0.0)
        self.wait_frame = self.frame + 20  # Existing screenshot settle convention only.
        self.state = "continuous_start_render"

    def apply_progress(self, drop, growth, phase_elapsed=None):
        r = self.refs
        self.check_identity()
        base.require(0 <= self.last_drop <= drop <= 1 and 0 <= self.last_growth <= growth <= 1,
            "Continuous normalized progress regressed or exceeded endpoints")
        base.require(growth == 0 or drop == 1, "Growth began before the staff endpoint")
        r["staff"].set_world_location(r["start_location"] + r["displacement"] * drop, False, False)
        r["expected_staff_transform"] = r["staff"].get_world_transform()
        capture = self.check_identity()
        base.require(r["staff"].get_editor_property("relative_rotation") == r["relative_rotation"]
            and r["staff"].get_editor_property("relative_scale3d") == r["relative_scale"],
            "Continuous preview changed Staff rotation/scale")
        if r["contact"] is None:
            base.require(not r["presentation"].get_staff_contact_presentation_snapshot().has_contact,
                "Contact was consumed outside this diagnostic sequence")
            if drop == 1:
                base.require(r["presentation"].try_accept_staff_contact(r["snapshot"].token),
                    "Native contact refused the exact continuous endpoint")
                self.setup_root(r["presentation"].get_staff_contact_presentation_snapshot())
                self.contact_count += 1
                base.require(self.contact_count == 1, "Contact accepted more than once")
                base.require(not r["presentation"].try_accept_staff_contact(r["snapshot"].token),
                    "Native contact repeat was not rejected")
                record("ContactOnce", token=r["snapshot"].token.to_string(),
                    count=self.contact_count, duplicate_rejected=True, actual_A=True)
        else:
            base.require(base.close_vector(capture.staff.end_a_world, r["root"]),
                "Actual A/root moved after continuous contact")
        base.require(growth == 0 or r["contact"] is not None, "Tree appeared before accepted contact")
        visible = 0
        for index, (parent, child, begin, finish, thickness) in enumerate(refined.EDGES):
            actor = r["forest"][index]
            portion = max(0.0, min(1.0, (growth - begin) / (finish - begin)))
            if portion > 0:
                start, full_end = r["nodes"][parent], r["nodes"][child]
                end = start + (full_end - start) * portion
                # Same diagnostic nondegeneracy epsilon as inherited placement.
                portion = portion if (end - start).length() > .000001 else 0.0
            if portion == 0:
                actor.set_actor_hidden_in_game(True)
                actor.static_mesh_component.set_cast_shadow(False)
            else:
                self.place_branch(index, start, end, r["diameter"] * thickness, True)
                visible += 1
            r["forest_expected"][index] = (actor.get_actor_transform(), forest.hidden(actor),
                actor.static_mesh_component.get_editor_property("cast_shadow"))
        base.require(r["director"].get_resolved_puzzle_snapshot().is_resolved,
            "Cosmetic sequence revoked the authoritative success")
        self.check_identity()
        r["probe"].refresh_projection()
        self.last_drop, self.last_growth = drop, growth
        record("MotionFrame", frame=self.frame, phase=self.state, monotonic_seconds=time.monotonic(),
            drop=drop, growth=growth, phase_elapsed_seconds=phase_elapsed,
            actual_staff_a=base.xyz(capture.staff.end_a_world),
            shadow_a=base.xyz(capture.end_a.world_position), visible_branches=visible,
            contact_accepted=r["contact"] is not None, contact_count=self.contact_count,
            puzzle_remains_resolved=True, actual_pie=True)

    def request_shot(self, name):
        self.shot_name = name
        self.shot = base.OUT + "/" + name + ".png"
        base.require(not os.path.exists(self.shot), "Refuse existing screenshot: " + self.shot)
        unreal.SystemLibrary.execute_console_command(self.refs["world"],
            'HighResShot 1600x900 filename="%s"' % self.shot, self.refs["pc"])

    def continuous_tick(self):
        self.check_identity()
        now = time.monotonic()
        if self.state == "continuous_start_render" and self.frame >= self.wait_frame:
            self.request_shot("01-Start")
            self.state = "continuous_start_shot"
        elif self.state == "continuous_start_shot" and os.path.exists(self.shot) and os.path.getsize(self.shot) > 1024:
            record("Screenshot", name=self.shot_name, path=self.shot, motion_paused_for_capture=False,
                actual_pie=True, ui_included=False)
            self.phase_started = now
            self.phase_callback_last = now
            self.state = "continuous_drop"
            record("MotionStarted", token=self.refs["snapshot"].token.to_string())
        elif self.state == "continuous_drop":
            self.motion_frames["drop"] += 1
            elapsed = now - self.phase_started
            drop = normalized_progress(elapsed, self.drop_seconds)
            self.max_callback_gap["drop"] = max(self.max_callback_gap["drop"], now - self.phase_callback_last)
            self.max_progress_step["drop"] = max(self.max_progress_step["drop"], drop - self.last_drop)
            self.phase_callback_last = now
            self.apply_progress(drop, 0.0, elapsed)
            if drop == 1:
                self.phase_elapsed_end["drop"] = elapsed
                self.phase_started = time.monotonic()
                self.phase_callback_last = self.phase_started
                self.state = "continuous_growth"
        elif self.state == "continuous_growth":
            self.motion_frames["growth"] += 1
            elapsed = now - self.phase_started
            growth = normalized_progress(elapsed, self.growth_seconds)
            self.max_callback_gap["growth"] = max(self.max_callback_gap["growth"], now - self.phase_callback_last)
            self.max_progress_step["growth"] = max(self.max_progress_step["growth"], growth - self.last_growth)
            self.phase_callback_last = now
            self.apply_progress(1.0, growth, elapsed)
            if growth == 1:
                self.phase_elapsed_end["growth"] = elapsed
                record("MotionCompleted", token=self.refs["snapshot"].token.to_string(),
                    drop=1.0, growth=1.0, contact_count=self.contact_count,
                    callback_counts=self.motion_frames, max_callback_gap_seconds=self.max_callback_gap,
                    max_normalized_step=self.max_progress_step, phase_elapsed_end_seconds=self.phase_elapsed_end,
                    continuous_elapsed_based=True,
                    formal_animation=False, packaged=False, user_visual_acceptance=False)
                self.wait_frame = self.frame + 20
                self.state = "continuous_end_render"
        elif self.state == "continuous_end_render" and self.frame >= self.wait_frame:
            self.request_shot("02-ForestComplete")
            self.state = "continuous_end_shot"
        elif self.state == "continuous_end_shot" and os.path.exists(self.shot) and os.path.getsize(self.shot) > 1024:
            record("Screenshot", name=self.shot_name, path=self.shot, motion_paused_for_capture=False,
                actual_pie=True, ui_included=False)
            self.phase_started = now
            self.state = "continuous_hold"
        elif self.state == "continuous_hold" and now - self.phase_started >= self.hold_seconds:
            record("PreviewEnded", diagnostic_restore_only=True, finale_finished=False,
                game_restart_implemented=False, skip_implemented=False)
            self.restore_and_end()

    def tick(self, delta):
        if not self.state.startswith("continuous_"):
            super().tick(delta)
            return
        try:
            self.frame += 1
            base.require(time.monotonic() < self.deadline, "Continuous diagnostic exceeded safety limit")
            self.continuous_tick()
        except Exception:
            if self.error is None:
                self.cleanup_deadline = time.monotonic() + 30  # Cleanup safety, not animation tempo.
            self.error = traceback.format_exc()
            unreal.log_error("DY_CONTINUOUS_PREVIEW_FAILURE " + self.error)
            if self.editor.get_game_world():
                try:
                    self.restore_and_end()
                except Exception:
                    self.refs = None
                    self.levels.editor_request_end_play()
                    self.state = "wait_end"
            else:
                self.refs = None
                self.finish()


if __name__ == "__main__":
    unreal.EditorPythonScripting.set_keep_python_script_alive(True)
    preview = None
    try:
        preview = ContinuousPreview()
        preview.begin()
    except Exception:
        failure = traceback.format_exc()
        unreal.log_error("DY_CONTINUOUS_PREVIEW_SETUP_FAILURE " + failure)
        if preview is not None:
            preview.error = failure
            preview.finish()
        else:
            unreal.EditorPythonScripting.set_keep_python_script_alive(False)
