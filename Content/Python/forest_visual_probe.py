import unreal, json, os, time
def write(p, o):
    with open(p, "w", encoding="utf-8") as f:
        json.dump(o, f, ensure_ascii=False, indent=1)

OUT = r"D:/灯影山海/Saved/Audit-2026-10-23-Performance"
report = {"ok": False, "errors": [], "actors": [], "calls": [], "shots": []}
write(os.path.join(OUT, "forest-visual-probe.json"), report)
try:
    les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    les.load_level("/Game/DengYingShanHai/Maps/L_DY_Main")
    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    actors = eas.get_all_level_actors()
    keys = ("forest", "screen", "proscen", "lightrig", "spot", "lamp", "m3_", "puppet", "director", "seat")
    for a in actors:
        label = str(a.get_actor_label())
        cls = str(a.get_class().get_name())
        if any(k in label.lower() for k in keys) or any(k in cls.lower() for k in keys):
            try:
                loc = a.get_actor_location()
                mn, mx = a.get_actor_bounds(False)
                report["actors"].append({"label": label, "class": cls,
                    "loc": [round(loc.x,1), round(loc.y,1), round(loc.z,1)],
                    "min": [round(mn.x,1), round(mn.y,1), round(mn.z,1)],
                    "max": [round(mx.x,1), round(mx.y,1), round(mx.z,1)]})
            except Exception as e:
                report["errors"].append("bounds " + label + ": " + str(e))
    forest = None
    for a in actors:
        if str(a.get_actor_label()) == "M3_RuntimeForest":
            forest = a
            break
    report["forest_found"] = forest is not None
    cam = eas.spawn_actor_from_class(unreal.CameraActor, unreal.Vector(-980, -80, 250), unreal.Rotator(0, 0, 0))
    cam.set_actor_label("TMP_ForestCam")
    cam.set_actor_rotation(unreal.Rotator(0.0, 0.0, 0.0), False)
    c = cam.get_component_by_class(unreal.CameraComponent)
    c.set_editor_property("field_of_view", 62.0)
    if forest is not None:
        report["forest_methods"] = [n for n in dir(forest) if "forest" in n.lower() or "growth" in n.lower() or "clear" in n.lower()]
        for g, tag in ((0.0, "0"), (0.55, "055"), (1.0, "1")):
            try:
                forest.set_forest_normalized_growth(g)
                report["calls"].append({"growth": g, "ok": True})
                time.sleep(0.8)
                shot = os.path.join(OUT, "ForestProbe-%s.png" % tag)
                unreal.AutomationLibrary.take_high_res_screenshot(1280, 800, shot, camera=cam, mask=False)
                for _ in range(160):
                    if os.path.exists(shot) and os.path.getsize(shot) > 20000:
                        break
                    time.sleep(0.25)
                report["shots"].append({"path": shot, "size": os.path.getsize(shot) if os.path.exists(shot) else 0})
            except Exception as e:
                report["calls"].append({"growth": g, "ok": False, "error": str(e)})
    report["ok"] = forest is not None
except Exception as e:
    report["errors"].append("FATAL " + str(e))
finally:
    write(os.path.join(OUT, "forest-visual-probe.json"), report)
    print("FOREST_PROBE " + json.dumps(report, ensure_ascii=False)[:1200])
    unreal.SystemLibrary.quit_editor()
