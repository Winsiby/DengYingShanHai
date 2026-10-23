"""Editor-only, unsaved PIE composition samples. NOT the P03 animation.

Launch in a separate full Editor with -ExecutePythonScript, never -game/NullRHI.
No save_asset/save_level, authored Definition edits, runtime API or input changes.
Candidate heights and normalized displacement are comparisons, not approved tuning.
"""
import json
import os
import time
import traceback
import unreal

MAP = "/Game/DengYingShanHai/Dev/M3/Maps/LV_M3GeometryProbe"
OUT = "C:/UEProjects/DengYingShanHai/Saved/Audit-2026-10-04-P03DropPreview/VisibilityRefinement"
# The earlier 5% candidate projected below the backstage floor and hid the tip.
# Compare a 10% candidate instead; both remain unapproved composition samples.
CANDIDATES = (("High", 0.15), ("Low", 0.10))
PROGRESS = (0.0, 0.5, 1.0)


def require(value, message):
    if not value:
        raise RuntimeError(message)
    return value


def record(event, **values):
    unreal.log("DY_DROP_PREVIEW " + json.dumps(dict(event=event, **values), ensure_ascii=False))


def xyz(value):
    return [float(value.x), float(value.y), float(value.z)]


def close_vector(left, right):
    return all(abs(a - b) < 0.000001 for a, b in zip(xyz(left), xyz(right)))


class Preview:
    def __init__(self):
        self.levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
        self.editor = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
        self.actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
        self.handle = None
        self.refs = None
        self.state = "setup"
        self.candidate = 0
        self.index = 0
        self.error = None
        self.deadline = time.monotonic() + 240.0  # Diagnostic safety only, not animation time.
        self.cleanup_deadline = None
        self.frame = 0
        self.wait_frame = 0
        self.temporary_actors = []
        self.original = None

    def begin(self):
        os.makedirs(OUT, exist_ok=True)  # Generated screenshots only, never game content.
        require(not self.levels.is_in_play_in_editor(), "Refuse an already-running PIE session")
        require(self.levels.load_level(MAP), "Cannot load independent Dev/M3 fixture")
        editor_world = self.editor.get_editor_world()
        require(editor_world and MAP in editor_world.get_path_name(), "Unexpected editor world")
        by_label = {a.get_actor_label(): a for a in self.actors.get_all_level_actors()}
        self.presentation = require(by_label.get("M2_StagePresentation"), "Missing explicit presentation")
        self.probe_name = require(by_label.get("M3_StaffProjectionProbe_AB"), "Missing probe").get_name()
        self.screen = by_label["DEV_BackScreen"]
        self.original = (
            self.presentation.get_editor_property("enable_staff_contact_presentation"),
            self.presentation.get_editor_property("staff_projection_screen"),
            self.presentation.get_editor_property("narrative_ground_line"),
        )
        self.presentation_name = self.presentation.get_name()
        initial = unreal.DYStaffProjectionLibrary.capture_staff_projection(
            by_label["M2_LightRig_P02"], by_label["M2_Puppet_P02_Controlled"],
            self.screen.static_mesh_component)
        require(initial.has_geometry, "Native editor geometry invalid")
        self.initial_geometry = initial
        self.ground = require(self.actors.spawn_actor_from_class(
            unreal.TargetPoint, unreal.Vector(), unreal.Rotator(), False), "Cannot create transient anchor")
        self.ground.set_actor_label("DEV_UnsavedNarrativeGroundLine")
        self.temporary_actors.append(self.ground)
        self.marker = require(self.actors.spawn_actor_from_class(
            unreal.StaticMeshActor, unreal.Vector(), unreal.Rotator(), False), "Cannot create transient line")
        self.marker.set_actor_label("DEV_UnsavedGroundLineMarker")
        self.temporary_actors.append(self.marker)
        mesh = self.marker.static_mesh_component
        mesh.set_static_mesh(unreal.load_asset("/Engine/BasicShapes/Cube"))
        mesh.set_mobility(unreal.ComponentMobility.MOVABLE)
        mesh.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
        mesh.set_editor_property("cast_shadow", False)
        self.presentation.set_editor_property("enable_staff_contact_presentation", True)
        self.presentation.set_editor_property("staff_projection_screen", self.screen)
        self.presentation.set_editor_property("narrative_ground_line", self.ground)
        self.prepare_temporary_actors()
        self.handle = unreal.register_slate_post_tick_callback(self.tick)
        self.request_variant()

    def prepare_temporary_actors(self):
        """Optional unsaved Editor fixtures, created before PIE copies exist."""
        pass

    def screenshot_name(self):
        return "%s-%03d" % (CANDIDATES[self.candidate][0], PROGRESS[self.index] * 100)

    def request_variant(self):
        name, fraction = CANDIDATES[self.candidate]
        capture = self.initial_geometry
        lower, upper = capture.screen_local_min, capture.screen_local_max
        emitter_local = unreal.MathLibrary.inverse_transform_location(capture.screen_transform, capture.emitter_world)
        face = lower.x if emitter_local.x < lower.x else upper.x
        local_z = lower.z + (upper.z - lower.z) * fraction
        anchor = unreal.MathLibrary.transform_location(capture.screen_transform,
            unreal.Vector(face, (lower.y + upper.y) * 0.5, local_z))
        require(unreal.DYStaffContactLibrary.capture_narrative_ground_line(capture, anchor).is_valid,
            "Candidate anchor invalid according to native library")
        self.ground.set_actor_location(anchor, False, False)
        # Visual line has its own thin offset. Its actor is NOT the native contact anchor.
        normal = unreal.MathLibrary.transform_direction(capture.screen_transform,
            unreal.Vector(-1 if emitter_local.x < lower.x else 1, 0, 0))
        self.marker.set_actor_location(anchor + normal * 0.2, False, False)
        self.marker.set_actor_rotation(self.screen.get_actor_rotation(), False)
        screen_scale = self.screen.get_actor_scale3d()
        self.marker.set_actor_scale3d(unreal.Vector(0.002, abs(screen_scale.y)*(upper.y-lower.y)/100.0, 0.02))
        record("Candidate", name=name, bottom_fraction=fraction, anchor_world=xyz(anchor), formal_approved=False)
        self.index = 0
        self.refs = None
        self.levels.editor_request_begin_play()
        self.state = "wait_pie"

    def pie_actor(self, world, name):
        path = world.get_path_name() + ":PersistentLevel." + name
        return require(unreal.find_object(None, path), "Missing explicit PIE copy: " + path)

    def start_fixture(self, world, pc):
        presentation = self.pie_actor(world, self.presentation_name)
        director = presentation.get_puzzle_director()
        light, puppet = director.get_light_rig_actor(), director.get_puppet_actor()
        require(light and puppet, "Missing actual Director actors")
        definition = director.get_editor_property("puzzle_definition")
        require(str(definition.puzzle_id) == "P02_ChaseForm", "Fixture is not accepted P02")
        require(director.get_evaluation_frequency_hz() == 15.0, "Sampling frequency changed")
        light.get_editor_property("light_control").set_normalized_value(definition.light_position.target)
        puppet.get_editor_property("puppet_control").set_normalized_value(definition.puppet_position.target)
        self.refs = dict(world=world, pc=pc, presentation=presentation, director=director,
            light=light, puppet=puppet, screen=presentation.get_editor_property("staff_projection_screen"),
            ground=presentation.get_editor_property("narrative_ground_line"),
            probe=self.pie_actor(world, self.probe_name))
        record("Fixture", puzzle=str(definition.puzzle_id), light_target=definition.light_position.target,
            puppet_target=definition.puppet_position.target, existing_hold=definition.required_hold_seconds,
            evaluation_hz=15, invented_p03_parameters=False)
        self.state = "wait_resolve"

    def capture(self):
        r = self.refs
        return unreal.DYStaffProjectionLibrary.capture_staff_projection(r["light"], r["puppet"],
            r["screen"].static_mesh_component)

    def check_identity(self):
        r = self.refs
        require(r["director"].is_resolved_token_current(r["snapshot"].token), "Resolved Token no longer current")
        require(r["light"].get_actor_transform() == r["light_transform"], "Light root changed")
        require(r["puppet"].get_actor_transform() == r["puppet_transform"], "Puppet root changed")
        current = self.capture()
        require(current.screen_transform == r["snapshot"].projection.screen_transform, "Receiver changed")
        require(close_vector(current.emitter_world, r["snapshot"].projection.emitter_world), "Emitter changed")
        require(close_vector(r["ground"].get_actor_location(), r["snapshot"].ground_line.world_anchor), "Ground anchor changed")
        if "expected_staff_transform" in r:
            require(current.staff.component_transform == r["expected_staff_transform"], "Staff changed after the recorded static sample")
        location, rotation = r["pc"].get_player_view_point()
        require(close_vector(location, r["pov_location"]) and rotation == r["pov_rotation"], "POV changed between static samples")
        return current

    def begin_samples(self, snapshot):
        r = self.refs
        require(snapshot.projection.has_geometry and snapshot.ground_line.is_valid, "No live geometry snapshot")
        require(snapshot.projection.end_a.status == unreal.DYStaffProjectionStatus.ON_SCREEN, "Initial A not on screen")
        staff = r["puppet"].get_editor_property("staff")
        require(staff.get_name() == "Staff", "Wrong component")
        require(staff.get_world_transform() == snapshot.projection.staff.component_transform,
            "Staff changed after actual Resolve; cannot substitute a later pose")
        location, rotation = r["pc"].get_player_view_point()
        r.update(snapshot=snapshot, staff=staff, relative=staff.get_relative_transform(),
            relative_rotation=staff.get_editor_property("relative_rotation"), relative_scale=staff.get_editor_property("relative_scale3d"),
            light_transform=r["light"].get_actor_transform(), puppet_transform=r["puppet"].get_actor_transform(),
            pov_location=location, pov_rotation=rotation)
        initial = snapshot.projection
        projected = initial.end_a.screen_local_position
        require(projected.z > snapshot.ground_line.screen_local_z, "Candidate must be below initial A")
        target_shadow = unreal.MathLibrary.transform_location(initial.screen_transform,
            unreal.Vector(projected.x, projected.y, snapshot.ground_line.screen_local_z))
        target_a = initial.emitter_world + (target_shadow - initial.emitter_world) / initial.end_a.ray_parameter
        r["displacement"] = target_a - initial.staff.end_a_world
        r["start_location"] = unreal.MathLibrary.transform_location(initial.staff.component_transform, unreal.Vector())
        record("Resolved", candidate=CANDIDATES[self.candidate][0], token=snapshot.token.to_string(),
            staff_a=xyz(initial.staff.end_a_world), shadow_a=xyz(initial.end_a.world_position),
            goal_shadow=xyz(target_shadow), displacement=xyz(r["displacement"]), pov=xyz(location),
            fov=unreal.GameplayStatics.get_player_camera_manager(r["world"], 0).get_fov_angle())
        self.apply_sample()

    def apply_sample(self):
        r = self.refs
        self.check_identity()
        progress = PROGRESS[self.index]
        r["staff"].set_world_location(r["start_location"] + r["displacement"] * progress, False, False)
        r["expected_staff_transform"] = r["staff"].get_world_transform()
        capture = self.check_identity()
        require(r["staff"].get_editor_property("relative_rotation") == r["relative_rotation"], "Staff rotation changed")
        require(r["staff"].get_editor_property("relative_scale3d") == r["relative_scale"], "Staff scale changed")
        accepted = r["presentation"].try_accept_staff_contact(r["snapshot"].token)
        require(accepted == (progress == 1.0), "Native contact result differs from sample endpoint")
        require(r["director"].get_resolved_puzzle_snapshot().is_resolved, "Cosmetic sample revoked puzzle success")
        if progress == 1.0:
            require(not r["presentation"].try_accept_staff_contact(r["snapshot"].token), "Contact repeated")
        r["probe"].refresh_projection()
        record("Sample", candidate=CANDIDATES[self.candidate][0], progress=progress,
            shadow_a=xyz(capture.end_a.world_position), staff_a=xyz(capture.staff.end_a_world),
            native_contact=accepted, actual_component=True, puzzle_remains_resolved=True)
        self.wait_frame = self.frame + 20  # Render settle frames, not animation duration.
        self.state = "wait_render"

    def restore_and_end(self):
        r = self.refs
        if r and "relative" in r and unreal.SystemLibrary.is_valid(r["staff"]):
            r["staff"].set_relative_transform(r["relative"], False, False)
            require(r["staff"].get_relative_transform() == r["relative"], "Full Staff transform not restored")
            if not self.error:
                token = r["snapshot"].token
                r["director"].reset_current_puzzle()  # Diagnostic cleanup; NOT a new R/restart policy.
                require(not r["presentation"].try_accept_staff_contact(token), "Stale Token accepted after cleanup")
                record("Cleanup", candidate=CANDIDATES[self.candidate][0], full_staff_restored=True, stale_token_rejected=True)
        self.refs = None  # No access to PIE wrappers after request_end_play.
        self.levels.editor_request_end_play()
        self.state = "wait_end"

    def finish(self):
        try:
            if self.original:
                for field, value in zip(("enable_staff_contact_presentation", "staff_projection_screen", "narrative_ground_line"), self.original):
                    self.presentation.set_editor_property(field, value)
            for actor in self.temporary_actors:
                if unreal.SystemLibrary.is_valid(actor):
                    self.actors.destroy_actor(actor)
            self.temporary_actors = []
        except Exception:
            self.error = (self.error or "") + "\nCleanup: " + traceback.format_exc()
            unreal.log_error(self.error)
        finally:
            record("Failed" if self.error else "Completed", saved_assets=False, formal_animation=False, error=self.error)
            try:
                if self.handle is not None:
                    unreal.unregister_slate_post_tick_callback(self.handle)
            finally:
                self.handle = None
                unreal.EditorPythonScripting.set_keep_python_script_alive(False)

    def tick(self, _delta):
        try:
            self.frame += 1
            if self.error and self.cleanup_deadline and time.monotonic() >= self.cleanup_deadline:
                self.finish()
                return
            if not self.error:
                require(time.monotonic() < self.deadline, "Diagnostic session exceeded bounded runtime")
            if self.state == "wait_pie":
                world = self.editor.get_game_world()
                if world:
                    pc = unreal.GameplayStatics.get_player_controller(world, 0)
                    if pc and unreal.GameplayStatics.get_player_pawn(world, 0):
                        self.start_fixture(world, pc)
            elif self.state == "wait_resolve":
                snapshot = self.refs["presentation"].get_resolved_staff_presentation_snapshot()
                if snapshot.has_snapshot:
                    self.begin_samples(snapshot)
            elif self.state == "wait_render" and self.frame >= self.wait_frame:
                self.check_identity()
                name = self.screenshot_name()
                self.shot = OUT + "/" + name + ".png"
                require(not os.path.exists(self.shot), "Refuse to overwrite existing preview: " + self.shot)
                unreal.SystemLibrary.execute_console_command(self.refs["world"],
                    'HighResShot 1600x900 filename="%s"' % self.shot, self.refs["pc"])
                self.state = "wait_shot"
            elif self.state == "wait_shot" and os.path.exists(self.shot) and os.path.getsize(self.shot) > 1024:
                self.check_identity()
                record("Screenshot", path=self.shot, actual_pie=True, ui_included=False)
                self.index += 1
                if self.index < len(PROGRESS):
                    self.apply_sample()
                else:
                    self.restore_and_end()
            elif self.state == "wait_end" and not self.editor.get_game_world() and not self.levels.is_in_play_in_editor():
                self.candidate += 1
                if self.error or self.candidate >= len(CANDIDATES):
                    self.finish()
                else:
                    self.request_variant()
        except Exception:
            failure = traceback.format_exc()
            if self.error is None:
                self.cleanup_deadline = time.monotonic() + 30
            self.error = failure
            unreal.log_error("DY_DROP_PREVIEW_FAILURE " + self.error)
            if self.state == "wait_end":
                self.finish()
            elif self.editor.get_game_world():
                try:
                    self.restore_and_end()
                except Exception:
                    self.refs = None
                    self.levels.editor_request_end_play()
                    self.state = "wait_end"
            else:
                self.finish()


if __name__ == "__main__":
    unreal.EditorPythonScripting.set_keep_python_script_alive(True)
    _preview = Preview()
    try:
        _preview.begin()
    except Exception:
        _preview.error = traceback.format_exc()
        unreal.log_error("DY_DROP_PREVIEW_SETUP_FAILURE " + _preview.error)
        _preview.finish()
