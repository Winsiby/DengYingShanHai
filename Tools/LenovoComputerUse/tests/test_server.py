from __future__ import annotations

import base64
import importlib.util
import json
from pathlib import Path
import struct
import subprocess
import sys
import tempfile
import unittest
import zlib

PLUGIN = Path(__file__).resolve().parents[1] / "plugins/lenovo-computer-use"
sys.path.insert(0, str(PLUGIN))
from desktop import DesktopError, bgra_to_png, image_point
from server import ComputerUseServer, TOOLS, validate


class NoDesktop:
    """Invalid requests must fail without touching native APIs."""
    def __init__(self, *_):
        raise AssertionError("Unexpected desktop access")


class ProtocolTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.server = ComputerUseServer(Path(self.tmp.name), NoDesktop)

    def tearDown(self):
        self.tmp.cleanup()

    def request(self, method, params=None):
        return self.server.dispatch({"jsonrpc": "2.0", "id": 4, "method": method, "params": params or {}})

    def test_initialization_and_tool_discovery(self):
        result = self.request("initialize", {"protocolVersion": "2025-11-25"})["result"]
        self.assertEqual(result["protocolVersion"], "2025-11-25")
        self.assertEqual(result["capabilities"], {"tools": {"listChanged": False}})
        self.assertEqual(len(self.request("tools/list")["result"]["tools"]), 11)

    def test_notifications_have_no_response(self):
        self.assertIsNone(self.server.dispatch({"jsonrpc": "2.0", "method": "notifications/initialized"}))

    def test_bad_requests_and_unknown_methods(self):
        self.assertEqual(self.server.dispatch([])["error"]["code"], -32600)
        self.assertEqual(self.request("unknown")["error"]["code"], -32601)
        self.assertEqual(self.request("tools/call", {"name": []})["error"]["code"], -32602)

    def test_rejects_unknown_argument_and_boolean_coordinate(self):
        result = self.server.call("click", {"window_id": "3:4", "snapshot_id": "a" * 32,
                                            "x": True, "y": 5})
        self.assertTrue(result["isError"])
        self.assertIn("integer", result["content"][0]["text"])
        self.assertTrue(self.server.call("status", {"secret": "no"})["isError"])

    def test_bounded_keyboard_and_drag_requests(self):
        args = {"window_id": "3:4", "snapshot_id": "a" * 32, "keys": ["W"], "hold_ms": 999999}
        self.assertTrue(self.server.call("press_key", args)["isError"])
        args["hold_ms"] = 100
        args["keys"] = ["CTRL", "CTRL"]
        self.assertTrue(self.server.call("press_key", args)["isError"])

    def test_stop_survives_new_server_instance(self):
        self.assertFalse(self.server.call("stop", {})["isError"])
        other = ComputerUseServer(Path(self.tmp.name), NoDesktop)
        self.assertTrue(other.call("status", {})["structuredContent"]["stopped"])

    def test_audit_does_not_record_typed_content(self):
        private_text = "私人测试文字abc123"
        self.server.audit("type_text", {"text": private_text}, True)
        data = (Path(self.tmp.name) / "audit.jsonl").read_text(encoding="utf-8")
        self.assertNotIn(private_text, data)
        self.assertEqual(json.loads(data)["text_length"], len(private_text))

    def test_actual_stdio_transport_unicode_and_parse_error(self):
        messages = "\n".join([
            '{bad JSON}',
            json.dumps({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2025-06-18"}}),
            json.dumps({"jsonrpc": "2.0", "method": "notifications/initialized"}),
            json.dumps({"jsonrpc": "2.0", "id": 2, "method": "tools/call", "params": {"name": "status", "arguments": {}}}),
        ]) + "\n"
        completed = subprocess.run([sys.executable, str(PLUGIN / "server.py"), "--data-dir", self.tmp.name],
                                   input=messages, text=True, encoding="utf-8", capture_output=True, timeout=10)
        self.assertEqual(completed.returncode, 0, completed.stderr)
        responses = [json.loads(line) for line in completed.stdout.splitlines()]
        self.assertEqual(len(responses), 3)
        self.assertEqual(responses[0]["error"]["code"], -32700)
        self.assertEqual(responses[2]["result"]["structuredContent"]["name"], "Lenovo Computer Use")


class ImageTests(unittest.TestCase):
    def test_negative_monitor_and_scaled_coordinates(self):
        rect = {"left": -1920, "top": 100, "right": 0, "bottom": 1180}
        self.assertEqual(image_point(rect, 960, 540, 480, 270), (-960, 640))
        for x, y in ((960, 0), (-1, 1), (0, 540)):
            with self.assertRaises(DesktopError):
                image_point(rect, 960, 540, x, y)

    def test_png_has_correct_size_channels_and_crc(self):
        png = bgra_to_png(2, 1, bytes([0, 0, 255, 0, 255, 0, 0, 0]))
        self.assertEqual(png[:8], b"\x89PNG\r\n\x1a\n")
        index, idat = 8, b""
        while index < len(png):
            size = struct.unpack(">I", png[index:index+4])[0]
            kind, data = png[index+4:index+8], png[index+8:index+8+size]
            crc = struct.unpack(">I", png[index+8+size:index+12+size])[0]
            self.assertEqual(crc, zlib.crc32(kind + data))
            if kind == b"IHDR":
                self.assertEqual(struct.unpack(">II", data[:8]), (2, 1))
            if kind == b"IDAT":
                idat += data
            index += 12 + size
        self.assertEqual(zlib.decompress(idat), b"\x00\xff\x00\x00\x00\x00\xff")


if __name__ == "__main__":
    unittest.main()
