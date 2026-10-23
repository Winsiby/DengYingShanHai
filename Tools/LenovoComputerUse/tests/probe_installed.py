"""Verify the installed manifest's actual stdio launch, handshake and tools.

Optional --workbuddy captures an allowed real app without typing/clicking.
"""
from __future__ import annotations

import argparse
import base64
import json
from pathlib import Path
import subprocess
import sys
import time


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--workbuddy", action="store_true")
    args = parser.parse_args()
    config = json.loads(args.manifest.read_text(encoding="utf-8"))["mcpServers"]["lenovo_desktop"]
    process = subprocess.Popen([config["command"], *config["args"]], stdin=subprocess.PIPE,
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                               encoding="utf-8", bufsize=1)
    rid = 0
    def rpc(method, params=None):
        nonlocal rid
        rid += 1
        process.stdin.write(json.dumps({"jsonrpc": "2.0", "id": rid, "method": method,
                                       "params": params or {}}) + "\n")
        process.stdin.flush()
        response = json.loads(process.stdout.readline())
        assert response.get("id") == rid, response
        assert "error" not in response, response
        return response["result"]
    def call(name, arguments=None):
        result = rpc("tools/call", {"name": name, "arguments": arguments or {}})
        assert not result.get("isError"), result
        return result

    restored_minimized = False
    try:
        initialized = rpc("initialize", {"protocolVersion": "2025-11-25", "capabilities": {},
                                         "clientInfo": {"name": "lenovo-install-probe", "version": "1.0"}})
        process.stdin.write(json.dumps({"jsonrpc": "2.0", "method": "notifications/initialized"}) + "\n")
        process.stdin.flush()
        tools = rpc("tools/list")["tools"]
        status = call("status")["structuredContent"]
        windows = call("list_windows")["structuredContent"]["windows"]
        summary = {"manifest": str(args.manifest.resolve()), "protocol": initialized["protocolVersion"],
                   "server_name": initialized["serverInfo"]["name"], "tool_count": len(tools),
                   "tools": [t["name"] for t in tools], "stopped": status["stopped"],
                   "workbuddy_found": any(w["process"].casefold() == "workbuddy.exe" for w in windows),
                   "workbuddy_observed": False, "messages_submitted": False}
        args.output_dir.mkdir(parents=True, exist_ok=True)
        if args.workbuddy:
            matches = [w for w in windows if w["process"].casefold() == "workbuddy.exe" and w["title"] == "WorkBuddy"]
            assert len(matches) == 1, "Expected exactly one WorkBuddy main window"
            window = matches[0]
            call("focus_window", {"window_id": window["window_id"]})
            time.sleep(0.5)
            observed = call("observe_window", {"window_id": window["window_id"]})
            image = next(c for c in observed["content"] if c["type"] == "image")
            (args.output_dir / "workbuddy-observed.png").write_bytes(base64.b64decode(image["data"]))
            summary["workbuddy_observed"] = True
            summary["workbuddy_capture"] = observed["structuredContent"]
            # Restore only minimization, if this inspection temporarily restored it.
            if window["minimized"]:
                import ctypes
                from ctypes import wintypes
                user = ctypes.WinDLL("user32", use_last_error=True)
                user.ShowWindow.argtypes = [wintypes.HWND, ctypes.c_int]
                user.ShowWindow.restype = wintypes.BOOL
                user.ShowWindow(int(window["window_id"].split(":")[0]), 6)
                restored_minimized = True
        summary["original_minimized_state_restored"] = restored_minimized
        (args.output_dir / "installed-probe.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
        print(json.dumps({k:v for k,v in summary.items() if k != "workbuddy_capture"}, ensure_ascii=False))
    finally:
        process.stdin.close()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.terminate()
            process.wait(timeout=5)


if __name__ == "__main__":
    main()
