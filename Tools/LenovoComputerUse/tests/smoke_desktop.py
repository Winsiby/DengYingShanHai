"""End-to-end test against a disposable window, never a user's open document."""
from __future__ import annotations

import argparse
import base64
import ctypes as C
from ctypes import wintypes as W
import json
import os
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins/lenovo-computer-use"
sys.path.insert(0, str(PLUGIN))
from server import ComputerUseServer


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", type=Path, required=True)
    args = parser.parse_args()
    args.data_dir.mkdir(parents=True, exist_ok=True)
    state_path = args.data_dir / "smoke-state.json"
    ps = Path(os.environ.get("SystemRoot", r"C:\Windows")) / "System32/WindowsPowerShell/v1.0/powershell.exe"
    process = subprocess.Popen([str(ps), "-NoProfile", "-File", str(ROOT / "tests/SmokeWindow.ps1"),
                                "-StatePath", str(state_path)], creationflags=subprocess.CREATE_NO_WINDOW)
    server = ComputerUseServer(args.data_dir)
    passed = []

    def call(name, **kw):
        result = server.call(name, kw)
        if result["isError"]:
            raise AssertionError(name + ": " + result["content"][0]["text"])
        return result

    def state():
        for _ in range(30):
            try:
                return json.loads(state_path.read_text(encoding="utf-8-sig"))
            except (FileNotFoundError, json.JSONDecodeError, PermissionError):
                time.sleep(0.03)
        raise AssertionError("Test window state is unavailable")

    def observe():
        return call("observe_window", window_id=wid)

    def input_args(result):
        return {"window_id": wid, "snapshot_id": result["structuredContent"]["snapshot_id"]}

    def point(result, node):
        data = result["structuredContent"]
        rect, n = data["capture_rect"], node["rect"]
        return {"x": round((n["left"] + n["width"] / 2 - rect["left"]) * data["image_width"] / (rect["right"] - rect["left"])),
                "y": round((n["top"] + n["height"] / 2 - rect["top"]) * data["image_height"] / (rect["bottom"] - rect["top"]))}

    try:
        for _ in range(80):
            windows = call("list_windows")["structuredContent"]["windows"]
            matches = [w for w in windows if w["pid"] == process.pid and w["title"] == "Lenovo Computer Use Test"]
            if matches:
                break
            if process.poll() is not None:
                raise AssertionError("Test window process exited")
            time.sleep(0.1)
        else:
            raise AssertionError("No test window appeared")
        wid = matches[0]["window_id"]
        passed.append("allowed window enumeration and process identity")
        call("focus_window", window_id=wid)
        time.sleep(0.4)
        tree = call("ui_tree", window_id=wid)["structuredContent"]["nodes"]
        (args.data_dir / "smoke-ui-tree.json").write_text(json.dumps(tree, ensure_ascii=False, indent=2), encoding="utf-8")
        obs = observe()
        (args.data_dir / "smoke-before.png").write_bytes(base64.b64decode(next(c["data"] for c in obs["content"] if c["type"] == "image")))
        nodes = {n["name"]: n for n in tree}
        button_node = nodes["Click test"]
        # Some WinForms providers expose unnamed Pane proxies rather than
        # AccessibleName/Edit. Select the two unique regions in our own fixture.
        text_candidates = [n for n in tree if n["depth"] == 1 and not n["name"]
                           and n["rect"]["top"] < button_node["rect"]["top"]
                           and n["rect"]["height"] > 100]
        panel_candidates = [n for n in tree if n["depth"] == 1 and not n["name"]
                            and n["rect"]["left"] > button_node["rect"]["left"]
                            and n["rect"]["top"] >= button_node["rect"]["top"]]
        assert len(text_candidates) == len(panel_candidates) == 1, tree
        text_node, panel_node = text_candidates[0], panel_candidates[0]
        passed.append("UI Automation exposes correct test controls")
        obs = observe()
        image = next(c for c in obs["content"] if c["type"] == "image")
        png = base64.b64decode(image["data"])
        assert png.startswith(b"\x89PNG\r\n\x1a\n")
        (args.data_dir / "smoke-before.png").write_bytes(png)
        passed.append("foreground screenshot and PNG encoding")
        call("click", **input_args(obs), **point(obs, text_node))
        obs = observe()
        message = "灯影山海：专属桌面插件测试成功！🌳"
        call("type_text", **input_args(obs), text=message)
        time.sleep(0.2)
        assert state()["text"] == message, state()
        passed.append("Unicode Chinese and emoji input reaches the actual textbox")
        obs = observe()
        call("press_key", **input_args(obs), keys=["CTRL", "A"])
        obs = observe()
        call("press_key", **input_args(obs), keys=["RIGHT"])
        obs = observe()
        call("click", **input_args(obs), **point(obs, button_node))
        time.sleep(0.15)
        assert state()["clicks"] == 1, state()
        passed.append("keyboard chord, navigation key and click")
        # An action consumes its screenshot; replay cannot produce a second click.
        replay = server.call("click", {**input_args(obs), **point(obs, button_node)})
        assert replay["isError"] and state()["clicks"] == 1
        passed.append("snapshot replay rejected")
        obs = observe()
        center = point(obs, panel_node)
        call("drag", **input_args(obs), **center, end_x=center["x"] + 70,
             end_y=center["y"] + 25, duration_ms=300)
        time.sleep(0.1)
        data = obs["structuredContent"]
        capture = data["capture_rect"]
        physical_distance = (70 * (capture["right"] - capture["left"]) / data["image_width"]
                             + 25 * (capture["bottom"] - capture["top"]) / data["image_height"])
        expected_logical_distance = physical_distance * state()["panel_width"] / panel_node["rect"]["width"]
        assert abs(state()["drag_pixels"] - expected_logical_distance) <= 3, state()
        passed.append("drag executes and releases the mouse")
        obs = observe()
        call("scroll", **input_args(obs), **point(obs, panel_node), steps=2)
        time.sleep(0.15)
        assert state()["scrolls"] == 2, state()
        passed.append("wheel reaches the intended panel")
        # Reject changes to geometry while a screenshot is outstanding.
        obs = observe()
        hwnd = int(wid.split(":")[0])
        user = C.WinDLL("user32", use_last_error=True)
        user.SetWindowPos.argtypes = [W.HWND, W.HWND, C.c_int, C.c_int, C.c_int, C.c_int, W.UINT]
        user.SetWindowPos.restype = W.BOOL
        rect = obs["structuredContent"]["window"]["rect"]
        user.SetWindowPos(hwnd, None, rect["left"]+20, rect["top"]+10, 0, 0, 0x0001 | 0x0004)
        moved = server.call("click", {**input_args(obs), **point(obs, button_node)})
        assert moved["isError"] and "moved/resized" in moved["content"][0]["text"]
        passed.append("moved-window input rejected")
        # Minimized/nonforeground targets must not receive keyboard input.
        obs = observe()
        server.desktop.user.ShowWindow(hwnd, 6)
        lost = server.call("type_text", {**input_args(obs), "text": "SHOULD_NOT_APPEAR"})
        assert lost["isError"] and "foreground" in lost["content"][0]["text"]
        assert state()["text"] == message
        passed.append("lost-focus/minimized input rejected")
        call("focus_window", window_id=wid)
        obs = observe()
        # Exercise expiry without sleeping for the full timeout.
        server.desktop.snapshots[obs["structuredContent"]["snapshot_id"]]["created"] -= 61
        expired = server.call("press_key", {**input_args(obs), "keys": ["ENTER"]})
        assert expired["isError"] and "expired" in expired["content"][0]["text"]
        passed.append("expired observation rejected")
        obs = observe()
        (args.data_dir / "smoke-after.png").write_bytes(base64.b64decode(next(c["data"] for c in obs["content"] if c["type"] == "image")))
        # Use a separate data directory to keep the real control state untouched.
        stopped = ComputerUseServer(args.data_dir / "stop-test")
        stopped.call("stop", {})
        blocked = stopped.call("focus_window", {"window_id": wid})
        assert blocked["isError"] and "STOPPED" in blocked["content"][0]["text"]
        passed.append("persistent STOP blocks focus/input")
        summary = {"passed": len(passed), "checks": passed, "test_pid": process.pid,
                   "text_verified": True, "third_party_windows_modified": False}
        (args.data_dir / "smoke-results.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
        print(json.dumps(summary, ensure_ascii=False))
    finally:
        # This child was created solely by this test; do not close unrelated apps.
        process.terminate()
        process.wait(timeout=5)


if __name__ == "__main__":
    main()
