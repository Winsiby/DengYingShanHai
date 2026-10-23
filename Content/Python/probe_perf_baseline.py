import unreal, json, os

OUT = r"D:\灯影山海\Saved\Audit-2026-10-23-Performance"
os.makedirs(OUT, exist_ok=True)
res = {"ok": False, "errors": [], "assets": {}, "actors": [], "map": ""}

try:
    AR = unreal.AssetRegistryHelpers.get_asset_registry()

    def list_dir(path):
        out = []
        try:
            for a in AR.get_assets_by_path(path, recursive=True):
                out.append(str(a.package_name))
        except Exception as ex:
            res["errors"].append("list %s: %s" % (path, ex))
        return sorted(out)

    for p in ["/Game/DengYingShanHai/Puppets",
              "/Game/DengYingShanHai/Dev/KuafuAppearance",
              "/Game/DengYingShanHai/Stage/ArtMainline"]:
        res["assets"][p] = list_dir(p)

    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    res["map"] = world.get_name() if world else "none"

    wanted = ("DYPuzzleDirector", "DYStagePresentation", "DYForestPresentationActor",
              "DYPuppetActor", "CameraActor", "DYStageAudioPresentationActor", "CineCameraActor")
    props_of = ["bFourActCampaign", "bEnableStaffContactPresentation",
                "bEnableFiveStateDevEnvironment", "bEnablePlayerAlignmentFeedback",
                "bAutoStartOnBeginPlay", "bShowDevelopmentDebug",
                "ForestPresentationActor", "ChapterTitleMaterials"]
    for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors():
        cls = a.get_class().get_name()
        if cls not in wanted:
            continue
        loc = a.get_actor_location()
        rot = a.get_actor_rotation()
        info = {"label": a.get_actor_label(), "class": cls,
                "loc": [round(loc.x, 2), round(loc.y, 2), round(loc.z, 2)],
                "rot": [round(rot.pitch, 2), round(rot.yaw, 2), round(rot.roll, 2)],
                "props": {}}
        for name in props_of:
            try:
                v = a.get_editor_property(name)
                if isinstance(v, unreal.Object):
                    info["props"][name] = v.get_name()
                elif isinstance(v, (list, unreal.Array)):
                    info["props"][name] = "array(%d)" % len(v)
                else:
                    info["props"][name] = v
            except Exception:
                pass
        res["actors"].append(info)
    res["ok"] = True
except Exception as ex:
    res["errors"].append("top: %s" % ex)
finally:
    with open(os.path.join(OUT, "probe.json"), "w", encoding="utf-8") as f:
        json.dump(res, f, ensure_ascii=False, indent=2)
    print("DONE probe ok=%s errors=%d" % (res["ok"], len(res["errors"])))
    unreal.SystemLibrary.quit_editor()
