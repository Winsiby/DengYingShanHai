"""Read-only cold graph/map audit + separate bounded PIE verification driver.

Only this diagnostic may set test input values. Blueprint owns all drop/growth
time and Staff writes. Never save assets/levels, alter Definition, input or POV.
Not a player launcher and not independent packaged-build evidence.
"""
import json
import os
import time
import traceback
import unreal

ROOT = "/Game/DengYingShanHai/Dev/M3/Runtime"
MAP = "/Game/DengYingShanHai/Dev/M3/Maps/LV_M3RuntimeCandidate"
OUT = os.environ.get("DY_P03_RUNTIME_VERIFY_OUT", unreal.Paths.project_saved_dir()
    + "Audit-2026-10-06-P03RuntimeWiring/Runtime-Verify-Run1.json")
RESULT = dict(success=False, error=None, saved=False, editor_only=True,
    driver_sets_test_inputs=True, python_drives_cue=False, checkpoints=[])


def require(value, why):
    if not value:
        raise RuntimeError(why)
    return value


def check(name, **values):
    RESULT["checkpoints"].append(dict(name=name, **values))
    unreal.log("DY_P03_RUNTIME_VERIFY " + json.dumps(RESULT["checkpoints"][-1], ensure_ascii=False))


def cold_audit():
    bp = require(unreal.load_asset(ROOT + "/BP_DYP03RuntimePresentation"), "Saved runtime BP")
    require(unreal.BlueprintEditorLibrary.compile_blueprint(bp), "Cold blueprint compile")
    nodes = []
    for graph in unreal.BlueprintEditorLibrary.list_graphs(bp):
        editor = unreal.BlueprintGraphEditor.get_graph_editor(graph)
        require(not editor.list_nodes_with_errors(), "Cold graph errors")
        nodes.extend(editor.list_all_nodes())
    timelines = [n for n in nodes if n.get_class().get_name() == "K2Node_Timeline"]
    require(len(timelines) == 2, "Two authored Timelines")
    for tl in timelines:
        for pin in ("PlayFromStart", "Update", "Finished"):
            p = tl.find_input_pin(pin) if pin == "PlayFromStart" else tl.find_output_pin(pin)
            require(p.list_connected_pins(), "Real connected Timeline " + pin)
    require(not any(n.get_class().get_name().startswith("K2Node_Input") for n in nodes), "No new input nodes")
    check("ColdExecutableGraphs", timelines=2, checked_real_links=True, graph_count=len(unreal.BlueprintEditorLibrary.list_graphs(bp)))
    cls = bp.generated_class()
    defaults = unreal.get_default_object(cls)
    require(not any(defaults.get_editor_property(n) for n in ("CueOwned", "Dropping", "Growing", "Completed", "Ended")), "No authored session in CDO")
    levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    require(not levels.is_in_play_in_editor(), "No existing PIE")
    require(levels.load_level(MAP), "Cold new map")
    actors = {a.get_actor_label(): a for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()}
    stage = require(actors.get("M3_RuntimePresentation"), "Runtime presentation map instance")
    director = stage.get_puzzle_director()
    definition = director.get_editor_property("puzzle_definition")
    require(str(definition.puzzle_id) == "P03_DevPlayableCandidate" and director.get_evaluation_frequency_hz() == 15, "Saved 15 Hz candidate")
    require(stage.get_editor_property("DevReceiver") == stage.get_editor_property("staff_projection_screen").static_mesh_component
        and stage.get_editor_property("DevGround") == stage.get_editor_property("narrative_ground_line"), "Explicit scene binding identity")
    forest = stage.get_forest_presentation_actor()
    require(forest and len(forest.get_editor_property("branch_layout")) == 15 and not forest.has_forest_session(), "Actual saved forest ref and clean defaults")
    check("ColdMapBindings", candidate=str(definition.puzzle_id), hz=15, branches=15,
        ground_world=list((stage.get_editor_property("DevGround").get_actor_location().x,
            stage.get_editor_property("DevGround").get_actor_location().y,
            stage.get_editor_property("DevGround").get_actor_location().z)))
    return levels, stage.get_name()


class Verify:
    def __init__(self, levels, name):
        self.levels, self.name = levels, name
        self.editor = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
        self.deadline = time.monotonic() + 60
        self.state = "wait_pie"
        self.refs = None
        self.handle = unreal.register_slate_post_tick_callback(self.tick)
        levels.editor_request_begin_play()

    def finish(self, success):
        RESULT["success"] = success
        if self.handle is not None:
            unreal.unregister_slate_post_tick_callback(self.handle)
            self.handle = None
        with open(OUT, "w", encoding="utf-8") as stream:
            json.dump(RESULT, stream, ensure_ascii=False, indent=2)
        self.refs = None
        unreal.EditorPythonScripting.set_keep_python_script_alive(False)
        unreal.SystemLibrary.quit_editor()

    def reset(self, phase):
        r = self.refs
        old = r["stage"].get_editor_property("CueToken")
        r["director"].reset_current_puzzle()
        require(not r["stage"].get_editor_property("CueOwned") and not r["forest"].has_forest_session(), "Reset leaked ownership/session")
        require(not r["forest"].get_branch_mesh_components(), "Reset leaked branches")
        require(r["staff"].get_relative_transform().translation == r["base_location"], "Owner-relative translation not restored")
        # Reset's current native rotation/scale must stay intact; no whole TF restore.
        require(not r["director"].is_resolved_token_current(old) and not r["stage"].try_accept_staff_contact(old), "Old identity accepted")
        check("ResetDuring" + phase, resources_released=True, translation_restored=True, old_token_rejected=True)
        r["light_control"].set_normalized_value(.72)
        r["puppet_control"].set_normalized_value(.85)
        r["baseline_pose"] = r["staff"].get_relative_transform()

    def tick(self, delta):
        try:
            require(time.monotonic() < self.deadline, "Bounded diagnostic timed out")
            if self.state == "wait_pie":
                world = self.editor.get_game_world()
                if not world:
                    return
                stage = unreal.find_object(None, world.get_path_name() + ":PersistentLevel." + self.name)
                if not stage or not stage.get_puzzle_director():
                    return
                director = stage.get_puzzle_director()
                light, puppet = director.get_light_rig_actor(), director.get_puppet_actor()
                staff = puppet.get_editor_property("staff")
                forest = stage.get_forest_presentation_actor()
                self.refs = dict(world=world, stage=stage, director=director, forest=forest, staff=staff,
                    light_control=light.get_editor_property("light_control"), puppet_control=puppet.get_editor_property("puppet_control"),
                    base_location=staff.get_relative_transform().translation)
                r = self.refs
                require(not director.get_resolved_puzzle_snapshot().is_resolved and not stage.get_editor_property("CueOwned")
                    and not forest.has_forest_session(), "Startup automatically answered/animated")
                check("UnsolvedStartup", actual_light=r["light_control"].get_normalized_value(),
                    actual_puppet=r["puppet_control"].get_normalized_value(), auto_answer=False)
                r["light_control"].set_normalized_value(.72)
                r["puppet_control"].set_normalized_value(.85)
                r["baseline_pose"] = staff.get_relative_transform()
                self.state = "drop_reset"
                return
            r = self.refs
            if self.state == "wait_end":
                if not self.editor.get_game_world() and not self.levels.is_in_play_in_editor():
                    self.finish(RESULT["error"] is None)
                return
            stage, forest = r["stage"], r["forest"]
            if self.state == "drop_reset" and stage.get_editor_property("Dropping"):
                snap = stage.get_resolved_staff_presentation_snapshot()
                r["snapshot"] = snap
                require(snap.has_snapshot and stage.get_editor_property("CueOwned") and not forest.has_forest_session(), "Actual live drop ownership")
                old_used = stage.get_editor_property("UsedToken")
                r["director"].get_last_evaluation()  # Diagnostic read only.
                stage.synchronize_from_director()
                after_used, after_cue = stage.get_editor_property("UsedToken"), stage.get_editor_property("CueToken")
                check("SynchronizationIdentity", before=old_used.to_string(), used_after=after_used.to_string(), cue_after=after_cue.to_string())
                require(after_used.to_string() == old_used.to_string() and after_cue.to_string() == old_used.to_string(), "Duplicate synchronization replaced cue")
                self.reset("Drop")
                self.state = "growth_reset"
            elif self.state == "growth_reset" and stage.get_editor_property("Growing"):
                contact = stage.get_staff_contact_presentation_snapshot()
                require(contact.has_contact and forest.has_forest_session() and len(forest.get_branch_mesh_components()) == 15, "Real accepted A before growth")
                check("ActualContactBeforeGrowth", contact_token=contact.token.to_string(), real_branches=15)
                self.reset("Growth")
                self.state = "complete_reset"
            elif self.state == "complete_reset" and stage.get_editor_property("Completed"):
                require(not stage.get_editor_property("Growing") and stage.get_editor_property("CueOwned")
                    and forest.has_forest_session(), "Complete holding did not retain current session")
                components = forest.get_branch_mesh_components()
                final = forest.get_forest_geometry_sample()
                require(len(components) == len(final.branches) == 15 and final.status == unreal.DYForestGeometryStatus.VALID, "Final complete geometry")
                measurements = []
                for index, (component, branch) in enumerate(zip(components, final.branches)):
                    actual, expected = component.get_world_transform(), branch.mesh_world_transform
                    vector = lambda value: [value.x, value.y, value.z]
                    quaternion = lambda value: [value.x, value.y, value.z, value.w]
                    measurements.append(dict(index=index, visible=component.is_visible(),
                        casts_shadow=component.get_editor_property("cast_shadow"),
                        expected_visible=branch.visible, portion=branch.portion,
                        actual_translation=vector(actual.translation), expected_translation=vector(expected.translation),
                        actual_scale=vector(actual.scale3d), expected_scale=vector(expected.scale3d),
                        actual_rotation=quaternion(actual.rotation), expected_rotation=quaternion(expected.rotation)))
                check("ActualFinalComponentValues", measurements=measurements,
                    purpose="Raw observations; not a relaxation of C++ transform epsilon")
                for component, branch in zip(components, final.branches):
                    require(branch.visible and abs(branch.portion - 1.0) <= 1.e-8, "Every final branch fully visible and expanded")
                    require(component.is_visible() == branch.visible and component.get_editor_property("cast_shadow") == branch.visible
                        and (not branch.visible or component.get_world_transform() == branch.mesh_world_transform), "Actual branch differs from native geometry")
                check("BlueprintTimelineComplete", fifteen_real_branches=True, python_time_or_staff_writes=False, formal_ending=False)
                self.reset("CompletedHolding")
                self.levels.editor_request_end_play()
                self.state = "wait_end"
        except Exception:
            RESULT["error"] = traceback.format_exc()
            unreal.log_error("DY_P03_RUNTIME_VERIFY " + RESULT["error"])
            if self.editor.get_game_world():
                self.refs = None
                self.levels.editor_request_end_play()
                self.state = "wait_end"
                self.deadline = time.monotonic() + 20
            else:
                self.finish(False)


try:
    levels, name = cold_audit()
    unreal.EditorPythonScripting.set_keep_python_script_alive(True)
    session = Verify(levels, name)
except Exception:
    RESULT["error"] = traceback.format_exc()
    unreal.log_error("DY_P03_RUNTIME_VERIFY " + RESULT["error"])
    with open(OUT, "w", encoding="utf-8") as stream:
        json.dump(RESULT, stream, ensure_ascii=False, indent=2)
