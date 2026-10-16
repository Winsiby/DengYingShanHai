"""UNSAVED Editor-only playable candidate. Never set the player's answer.

Director remains the 15 Hz puzzle authority. This isolated presentation adapter
is deliberately not shipped: it supplies temporary cue time to existing native
contact/forest APIs. The separate verifier may drive parameters; this file cannot.
No map/asset save, camera override, input binding, staged lock, or invented token.
"""
import importlib.util
import json
import os
import sys
import time
import traceback
import unreal

sys.dont_write_bytecode = True
spec = importlib.util.spec_from_file_location("dy_p03_drop_fixture",
    os.path.join(unreal.Paths.project_dir(), "Scripts", "Preview-P03StaffDrop.py"))
base = importlib.util.module_from_spec(spec)
spec.loader.exec_module(base)
AUDIT = "C:/UEProjects/DengYingShanHai/Saved/Audit-2026-10-05-P03PlayableCandidate"
OUT = os.environ.get("DY_P03_PLAYABLE_OUT", AUDIT + "/ManualRun")
base.require(os.path.commonpath((os.path.abspath(OUT), os.path.abspath(AUDIT)))
    == os.path.abspath(AUDIT), "Output must stay in playable audit")
base.OUT, base.CANDIDATES = OUT, (("High", .15),)
BP_PATH = "/Game/DengYingShanHai/Dev/M3/Forest/BP_DYForestPresentation_Dev"
PUZZLE_ID = "P03_DevPlayableCandidate"


def put(obj, field, value):
    obj.set_editor_property(field, value, notify_mode=unreal.PropertyAccessChangeNotifyMode.NEVER)


def record(event, **values):
    data = dict(event=event, **values)
    unreal.log("DY_P03_PLAYABLE " + json.dumps(data, ensure_ascii=False))
    with open(OUT + "/Events.jsonl", "a", encoding="utf-8") as stream:
        stream.write(json.dumps(data, ensure_ascii=False) + "\n")


def rows(layout):
    return [(int(b.parent_index), b.start_screen_offset.x, b.start_screen_offset.y,
        b.end_screen_offset.x, b.end_screen_offset.y, b.diameter_world,
        b.growth_begin, b.growth_end) for b in layout]


def corners(lo, hi):
    return [unreal.Vector(x, y, z) for x in (lo.x, hi.x)
        for y in (lo.y, hi.y) for z in (lo.z, hi.z)]


class Playable(base.Preview):
    def __init__(self):
        super().__init__()
        self.deadline = time.monotonic() + 90  # Setup only. NO player time limit.
        self.forest_ref_saved = False
        self.definition = None
        self.cue = None
        self.completed_attempts = 0
        self.finished = False
        self.diagnostic = False
        self.last_feedback = None

    def prepare_temporary_actors(self):
        self.old_forest = self.presentation.get_editor_property("forest_presentation_actor")
        self.forest_ref_saved = True
        cls = base.require(unreal.EditorAssetLibrary.load_blueprint_class(BP_PATH), "Missing saved Dev forest")
        self.cdo = unreal.get_default_object(cls)
        self.cdo_rows = rows(self.cdo.get_editor_property("branch_layout"))
        self.cdo_mesh = self.cdo.get_editor_property("branch_mesh")
        self.cdo_material = self.cdo.get_editor_property("branch_material")
        base.require(len(self.cdo_rows) == 15 and not self.cdo.has_forest_session()
            and not self.cdo.get_branch_mesh_components(), "Bad saved forest defaults")
        actor = base.require(self.actors.spawn_actor_from_class(cls,
            unreal.Vector(), unreal.Rotator(), False), "Cannot spawn unsaved forest instance")
        self.temporary_actors.append(actor)
        actor.set_actor_label("DEV_UnsavedP03PlayableForest")
        put(self.presentation, "forest_presentation_actor", actor)
        self.forest_name = actor.get_name()

    def start_fixture(self, world, pc):
        presentation = self.pie_actor(world, self.presentation_name)
        director = presentation.get_editor_property("puzzle_director")
        base.require(director and director.get_evaluation_frequency_hz() == 15, "Missing existing 15 Hz Director")
        light, puppet = director.get_light_rig_actor(), director.get_puppet_actor()
        forest = self.pie_actor(world, self.forest_name)
        base.require(presentation.get_editor_property("forest_presentation_actor") == forest, "Wrong PIE forest")
        self.refs = dict(world=world, pc=pc, presentation=presentation, director=director,
            light=light, puppet=puppet, forest=forest,
            screen=presentation.get_editor_property("staff_projection_screen"),
            ground=presentation.get_editor_property("narrative_ground_line"),
            light_control=light.get_editor_property("light_control"),
            puppet_control=puppet.get_editor_property("puppet_control"),
            staff=puppet.get_editor_property("staff"),
            original_definition=director.get_editor_property("puzzle_definition"))
        r = self.refs
        initial = [r["light_control"].get_normalized_value(), r["puppet_control"].get_normalized_value()]
        self.definition = unreal.DYPuzzleDefinition()
        base.require(self.definition.get_outer().get_path_name() == "/Engine/Transient", "Definition must be unsaved")
        put(self.definition, "puzzle_id", PUZZLE_ID)
        put(self.definition, "display_name", "杖落成林 · Dev候选")
        for field, target in (("light_position", .72), ("puppet_position", .85)):
            value = unreal.DYTargetRange()
            for key, data in (("enabled", True), ("target", target), ("enter_tolerance", .05), ("exit_tolerance", .09)):
                put(value, key, data)
            put(self.definition, field, value)
        put(self.definition, "required_puppet_pose_id", "P02_StrideReach")
        put(self.definition, "required_hold_seconds", 1.25)
        put(director, "puzzle_definition", self.definition)
        director.start_current_puzzle()  # DOES NOT reset or set control parameters.
        base.require(initial == [r["light_control"].get_normalized_value(), r["puppet_control"].get_normalized_value()]
            and not director.get_resolved_puzzle_snapshot().is_resolved, "Startup moved answers or resolved")
        r["staff_base_location"] = r["staff"].get_relative_transform().translation
        self.install_cue()
        self.state = "play"
        self.show_cue("调整灯与偶，让逐日影形稳定；沿用 E / A / D")
        if not self.diagnostic:
            # Capture only the current PIE viewport, after its HUD is ready.
            # This is Slate/input routing, NOT a mapping/context or POV change.
            unreal.WidgetLibrary.set_input_mode_game_only(pc, True)
            unreal.WidgetLibrary.set_focus_to_game_viewport()
        record("Ready", initial_values=initial, target_light=.72, target_puppet=.85,
            enter=.05, exit=.09, hold=1.25, pose="P02_StrideReach", evaluation_hz=15,
            drop=2, growth=6, auto_answer=False, editor_only=True, verification_driver=self.diagnostic,
            viewport_focus_requested=not self.diagnostic,
            input_mode="unchanged_diagnostic" if self.diagnostic else "game_only")

    def install_cue(self):
        # Instance-only native UMG tree. Never alter the Widget Blueprint CDO.
        # One bootstrap lookup via public UMG API; no HUD private-field bypass
        # and no recurring world/widget discovery in the cue loop.
        views = unreal.WidgetLibrary.get_all_widgets_of_class(
            self.refs["world"], unreal.DYInteractionHUDWidget, True)
        base.require(len(views) == 1, "Expected one current-world Chinese HUD")
        view = views[0]
        # Blueprint duplication chooses the actual tree name. Discover once by
        # explicit native canvas label + owner, never guess a tree name/graph.
        roots = [obj for obj in unreal.ObjectIterator(unreal.CanvasPanel)
            if obj.get_name() == "DYRoot" and obj.get_outer().get_outer() == view]
        base.require(len(roots) == 1, "Expected one native current-HUD canvas")
        root, tree = roots[0], roots[0].get_outer()
        title = base.require(unreal.find_object(tree, "DYActTitle"), "Missing native HUD title")
        # ActTitle is EditDefaultsOnly: never mutate its CDO to customize a run.
        # Override only the current native text element AFTER actual Resolve.
        self.refs["hud_status"] = base.require(unreal.find_object(tree, "DYStatus"), "Missing native status text")
        title.set_text(unreal.Text("杖落成林 · Dev候选"))
        self.cue = unreal.TextBlock(outer=tree, name="DYDevP03Cue")
        self.cue.set_font(title.get_editor_property("font"))
        self.cue.set_color_and_opacity(title.get_editor_property("color_and_opacity"))
        self.cue.set_visibility(unreal.SlateVisibility.HIT_TEST_INVISIBLE)
        slot = root.add_child_to_canvas(self.cue)
        slot.set_anchors(unreal.Anchors(unreal.Vector2D(.5, 0), unreal.Vector2D(.5, 0)))
        slot.set_alignment(unreal.Vector2D(.5, 0))
        slot.set_position(unreal.Vector2D(0, 64))
        slot.set_auto_size(True)

    def show_cue(self, text):
        if self.cue:
            self.cue.set_text(unreal.Text(text))

    def now(self):
        return unreal.GameplayStatics.get_time_seconds(self.refs["world"])

    def capture(self):
        r = self.refs
        return unreal.DYStaffProjectionLibrary.capture_staff_projection(r["light"], r["puppet"], r["screen"].static_mesh_component)

    def begin_drop(self, snapshot):
        r = self.refs
        base.require(snapshot.has_snapshot and snapshot.projection.has_geometry and snapshot.ground_line.is_valid,
            "Resolve lacks real Staff geometry")
        a = snapshot.projection.end_a
        base.require(a.status == unreal.DYStaffProjectionStatus.ON_SCREEN
            and a.screen_local_position.z > snapshot.ground_line.screen_local_z, "A must start on screen above Z70")
        staff = r["staff"].get_world_transform()
        base.require(staff == snapshot.projection.staff.component_transform, "Resolve-to-drop substituted pose")
        shadow_goal = unreal.MathLibrary.transform_location(snapshot.projection.screen_transform,
            unreal.Vector(a.screen_local_position.x, a.screen_local_position.y, snapshot.ground_line.screen_local_z))
        goal_a = snapshot.projection.emitter_world + (shadow_goal - snapshot.projection.emitter_world) / a.ray_parameter
        r.update(snapshot=snapshot, staff_start=staff, displacement=goal_a-snapshot.projection.staff.end_a_world,
            light_transform=r["light"].get_actor_transform(), puppet_transform=r["puppet"].get_actor_transform(),
            ground_transform=r["ground"].get_actor_transform(), clock=self.now())
        base.require(not r["forest"].has_forest_session(), "Forest appeared before contact")
        self.state = "drop"
        r["hud_status"].set_text(unreal.Text("第三幕影形 · 成"))
        self.show_cue("影形已稳 · 杖尖正落向幕上地线")
        record("DropStarted", token=snapshot.token.to_string(), light=r["light_control"].get_normalized_value(),
            puppet=r["puppet_control"].get_normalized_value(), pose=str(r["puppet_control"].get_pose_id()),
            start_a=base.xyz(snapshot.projection.staff.end_a_world), displacement=base.xyz(r["displacement"]),
            ground_screen_local_z=snapshot.ground_line.screen_local_z,
            ground_world=base.xyz(snapshot.ground_line.world_anchor), actual_resolve=True)

    def check_scene(self):
        r = self.refs
        base.require(r["director"].is_resolved_token_current(r["snapshot"].token), "Stale presentation identity")
        p = self.capture()
        base.require(r["light"].get_actor_transform() == r["light_transform"]
            and r["puppet"].get_actor_transform() == r["puppet_transform"]
            and p.screen_transform == r["snapshot"].projection.screen_transform
            and base.close_vector(p.emitter_world, r["snapshot"].projection.emitter_world)
            and r["ground"].get_actor_transform() == r["ground_transform"], "Resolved causal scene changed")
        current = r["staff"].get_world_transform()
        base.require(current.rotation == r["staff_start"].rotation and current.scale3d == r["staff_start"].scale3d,
            "Staff rotation/scale changed")

    def preflight(self, contact):
        r = self.refs
        components = r["forest"].get_branch_mesh_components()
        base.require(len(components) == 15 and all(not c.is_visible() and not c.get_editor_property("cast_shadow")
            for c in components), "Premature forest visibility")
        lo, hi = components[0].get_local_bounds()
        final = unreal.DYForestGeometryLibrary.sample_forest_geometry(contact,
            r["forest"].get_editor_property("branch_layout"), 1.0, lo, hi)
        base.require(final.status == unreal.DYForestGeometryStatus.VALID, "Full saved forest outside receiver")
        projected = []
        p = contact.projection
        for field in ("torso", "head"):
            component = r["puppet"].get_editor_property(field)
            for corner in corners(*component.get_local_bounds()):
                q = unreal.DYStaffProjectionLibrary.project_point_to_screen(p.emitter_world,
                    unreal.MathLibrary.transform_location(component.get_world_transform(), corner),
                    p.screen_transform, p.screen_local_min, p.screen_local_max)
                base.require(q.status == unreal.DYStaffProjectionStatus.ON_SCREEN, "Silhouette outside receiver")
                projected.append(q.screen_local_position)
        dy = (p.screen_local_max.y-p.screen_local_min.y)*.02
        dz = (p.screen_local_max.z-p.screen_local_min.z)*.02
        gap = (min(q.y for q in projected)-dy, max(q.y for q in projected)+dy, min(q.z for q in projected)-dz)
        base.require(all(not b.visible or b.projected_max.x < gap[0] or b.projected_min.x > gap[1]
            or b.projected_max.y < gap[2] for b in final.branches), "Saved branches overlap protected silhouette")
        r["final_geometry"] = final
        record("Preflight", branches=15, full_bounds_valid=True, torso_head_gap_clear=True, no_pixel_mask_claim=True)

    def advance_cue(self):
        r = self.refs
        token = r["snapshot"].token
        if not r["director"].is_resolved_token_current(token):
            # Existing native R may have refreshed rotation already: restore only
            # the translation owned by this adapter, NEVER overwrite current pose.
            r["staff"].set_relative_location(r["staff_base_location"], False, False)
            base.require(not r["forest"].has_forest_session() and not r["forest"].get_branch_mesh_components(),
                "Native invalidation leaked forest")
            del r["snapshot"]
            self.state = "play"
            self.show_cue("已复位 · 重新调整灯与偶")
            record("Invalidated", stale_contact_rejected=not r["presentation"].try_accept_staff_contact(token),
                resources_released=True, staff_translation_restored=True, current_pose_preserved=True)
            return
        self.check_scene()
        # Native interaction refresh can rewrite the old P02 default caption
        # after E release. Correct only a changed cosmetic text during a current
        # resolved cue; no core feedback/state/input ownership is replaced.
        if str(r["hud_status"].get_text()) != "第三幕影形 · 成":
            r["hud_status"].set_text(unreal.Text("第三幕影形 · 成"))
        if self.state == "drop":
            progress = min(1.0, max(0.0, (self.now()-r["clock"])/2.0))
            r["staff"].set_world_location(r["staff_start"].translation+r["displacement"]*progress, False, False)
            if progress < 1:
                base.require(not r["forest"].has_forest_session(), "Forest started during drop")
                return
            base.require(r["presentation"].try_accept_staff_contact(token), "Actual A contact rejected")
            contact = r["presentation"].get_staff_contact_presentation_snapshot()
            base.require(r["director"].is_resolved_token_current(token) and contact.has_contact
                and contact.token.to_string() == token.to_string(), "Contact callback invalidated cue")
            base.require(not r["presentation"].try_accept_staff_contact(token), "Repeated contact accepted")
            base.require(r["presentation"].begin_forest_presentation(token), "Native forest authorization failed")
            self.preflight(contact)
            base.require(not r["presentation"].begin_forest_presentation(token), "Duplicate forest allowed")
            r["contact_staff"] = r["staff"].get_world_transform()
            drop_elapsed = self.now()-r["clock"]
            r["clock"] = self.now()
            self.state = "growth"
            self.show_cue("杖尖已触地 · 同一点生长真实林影")
            record("Contact", token=token.to_string(), contact_world=base.xyz(contact.contact_world_position),
                drop_elapsed=drop_elapsed, real_a_contact=True, duplicate_rejected=True)
        elif self.state == "growth":
            base.require(r["staff"].get_world_transform() == r["contact_staff"], "Contact Staff moved")
            progress = min(1.0, max(0.0, (self.now()-r["clock"])/6.0))
            base.require(r["presentation"].set_forest_normalized_growth(token, progress), "Native growth rejected")
            if progress == 1:
                actual = r["forest"].get_branch_mesh_components()
                base.require(len(actual) == 15, "Missing real branches")
                for component, branch in zip(actual, r["final_geometry"].branches):
                    base.require(component.is_visible() == branch.visible
                        and component.get_editor_property("cast_shadow") == branch.visible
                        and (not branch.visible or component.get_world_transform() == branch.mesh_world_transform),
                        "Actual native branch mismatch")
                self.completed_attempts += 1
                self.state = "complete"
                self.show_cue("Dev 演出完成 · 成林保持；当前操纵对象 R 可复位")
                record("ForestComplete", token=token.to_string(), branches_verified=15,
                    attempts=self.completed_attempts, formal_ending=False)

    def drive_diagnostic(self):
        """Empty in player entry; only the separate verifier overrides this."""
        pass

    def stop_session(self):
        r = self.refs
        if r:
            if "snapshot" in r and r["forest"].has_forest_session():
                r["presentation"].clear_forest_presentation(r["snapshot"].token)
            r["staff"].set_relative_location(r["staff_base_location"], False, False)
            put(r["director"], "puzzle_definition", r["original_definition"])
            r["director"].reset_current_puzzle()  # Cleanup, NOT a new player restart rule.
            base.require(not r["forest"].has_forest_session() and not r["forest"].get_branch_mesh_components(), "Cleanup leaked")
        self.refs, self.cue = None, None
        self.levels.editor_request_end_play()
        self.state = "wait_end"

    def finish(self):
        if self.finished:
            return
        self.finished = True
        defaults_restored = False
        try:
            if self.forest_ref_saved:
                put(self.presentation, "forest_presentation_actor", self.old_forest)
            if hasattr(self, "cdo"):
                base.require(rows(self.cdo.get_editor_property("branch_layout")) == self.cdo_rows
                    and self.cdo.get_editor_property("branch_mesh") == self.cdo_mesh
                    and self.cdo.get_editor_property("branch_material") == self.cdo_material
                    and not self.cdo.has_forest_session() and not self.cdo.get_branch_mesh_components(), "CDO contaminated")
            defaults_restored = True
        except Exception:
            self.error = (self.error or "") + traceback.format_exc()
        super().finish()
        if not self.diagnostic:
            # The reusable preview cleanup clears KeepPythonScriptAlive. UE's
            # -ExecutePythonScript runner interprets that as QUIT_EDITOR on the
            # next tick, even without our own QUIT. Keep only its close guard;
            # the preview callback/temporary actors were already unregistered.
            unreal.EditorPythonScripting.set_keep_python_script_alive(True)
        self.state = "finished"
        with open(OUT + "/Result.json", "w", encoding="utf-8") as stream:
            json.dump(dict(error=self.error, completed_attempts=self.completed_attempts,
                diagnostic=self.diagnostic, editor_only=True, package_tested=False,
                physical_keys_verified=False, no_saved_assets=True,
                editor_retained=not self.diagnostic), stream, ensure_ascii=False, indent=2)
        record("Finished", error=self.error, attempts=self.completed_attempts, defaults_restored=defaults_restored,
            no_asset_save=True, package_tested=False, editor_retained=not self.diagnostic)
        if self.diagnostic:
            unreal.SystemLibrary.execute_console_command(None, "QUIT_EDITOR")
        else:
            unreal.log("DY_P03_PLAYABLE_STOPPED: temporary session cleaned up; Editor retained. Close WITHOUT saving before relaunching.")

    def tick(self, _delta):
        try:
            self.frame += 1
            if self.state in ("setup", "wait_pie"):
                base.require(time.monotonic() < self.deadline, "Setup timed out")
            if self.state == "wait_pie":
                world = self.editor.get_game_world()
                if world:
                    pc = unreal.GameplayStatics.get_player_controller(world, 0)
                    if pc and unreal.GameplayStatics.get_player_pawn(world, 0):
                        self.start_fixture(world, pc)
            elif self.state == "wait_end":
                if not self.editor.get_game_world() and not self.levels.is_in_play_in_editor():
                    self.finish()
            elif self.refs:
                if not self.editor.get_game_world() or not self.levels.is_in_play_in_editor():
                    self.refs, self.cue = None, None  # Discard destroyed PIE wrappers.
                    self.finish()
                    return
                self.drive_diagnostic()
                if not self.refs:
                    return
                if self.state == "play":
                    result = self.refs["director"].get_last_evaluation()
                    feedback = str(result.feedback)
                    if feedback != self.last_feedback:
                        record("Feedback", feedback=feedback, hold=result.hold_elapsed_seconds,
                            resolve_count=result.resolve_count, all_valid=result.all_required_conditions_valid)
                        self.last_feedback = feedback
                    snapshot = self.refs["presentation"].get_resolved_staff_presentation_snapshot()
                    if snapshot.has_snapshot:
                        self.begin_drop(snapshot)
                elif self.state in ("drop", "growth", "complete"):
                    self.advance_cue()
        except Exception:
            self.error = traceback.format_exc()
            unreal.log_error("DY_P03_PLAYABLE_FAILURE " + self.error)
            if self.refs and self.editor.get_game_world():
                try:
                    self.stop_session()
                except Exception:
                    self.refs, self.cue = None, None
                    self.levels.editor_request_end_play()
                    self.state = "wait_end"
            else:
                self.finish()


if __name__ == "__main__":
    unreal.EditorPythonScripting.set_keep_python_script_alive(True)
    session = Playable()
    try:
        session.begin()
    except Exception:
        session.error = traceback.format_exc()
        unreal.log_error("DY_P03_PLAYABLE_SETUP_FAILURE " + session.error)
        session.finish()
