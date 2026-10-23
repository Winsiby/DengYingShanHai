"""Independent Windows desktop adapter. Uses only Python's standard library.

All image coordinates refer to the returned PNG, not desktop logical pixels.
No OpenAI desktop-control binaries or private APIs are used.
"""
from __future__ import annotations

import base64
import ctypes as C
from ctypes import wintypes as W
import json
import os
from pathlib import Path
import struct
import subprocess
import time
import uuid
import zlib


class DesktopError(RuntimeError):
    pass


def png_chunk(kind: bytes, data: bytes) -> bytes:
    return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data))


def bgra_to_png(width: int, height: int, pixels: bytes) -> bytes:
    """Encode a top-down 32-bit DIB; discard undefined GDI alpha."""
    if len(pixels) != width * height * 4:
        raise DesktopError("Invalid bitmap size")
    rows = bytearray()
    for y in range(height):
        row = pixels[y * width * 4:(y + 1) * width * 4]
        rgb = bytearray(width * 3)
        rgb[0::3], rgb[1::3], rgb[2::3] = row[2::4], row[1::4], row[0::4]
        rows.append(0)
        rows.extend(rgb)
    return (b"\x89PNG\r\n\x1a\n"
            + png_chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
            + png_chunk(b"IDAT", zlib.compress(rows, 6)) + png_chunk(b"IEND", b""))


def image_point(rect: dict, width: int, height: int, x: int, y: int) -> tuple[int, int]:
    if not (0 <= x < width and 0 <= y < height):
        raise DesktopError("Point is outside the observed image")
    return (rect["left"] + int(x * (rect["right"] - rect["left"]) / width),
            rect["top"] + int(y * (rect["bottom"] - rect["top"]) / height))


class MOUSEINPUT(C.Structure):
    _fields_ = [("dx", W.LONG), ("dy", W.LONG), ("mouseData", W.DWORD),
                ("dwFlags", W.DWORD), ("time", W.DWORD), ("dwExtraInfo", C.c_size_t)]


class KEYBDINPUT(C.Structure):
    _fields_ = [("wVk", W.WORD), ("wScan", W.WORD), ("dwFlags", W.DWORD),
                ("time", W.DWORD), ("dwExtraInfo", C.c_size_t)]


class HARDWAREINPUT(C.Structure):
    _fields_ = [("uMsg", W.DWORD), ("wParamL", W.WORD), ("wParamH", W.WORD)]


class INPUTUNION(C.Union):
    _fields_ = [("mi", MOUSEINPUT), ("ki", KEYBDINPUT), ("hi", HARDWAREINPUT)]


class INPUT(C.Structure):
    _anonymous_ = ("u",)
    _fields_ = [("type", W.DWORD), ("u", INPUTUNION)]


class BITMAPINFOHEADER(C.Structure):
    _fields_ = [("biSize", W.DWORD), ("biWidth", W.LONG), ("biHeight", W.LONG),
                ("biPlanes", W.WORD), ("biBitCount", W.WORD), ("biCompression", W.DWORD),
                ("biSizeImage", W.DWORD), ("biXPelsPerMeter", W.LONG), ("biYPelsPerMeter", W.LONG),
                ("biClrUsed", W.DWORD), ("biClrImportant", W.DWORD)]


KEYS = {"CTRL": 0x11, "ALT": 0x12, "SHIFT": 0x10, "ENTER": 0x0D,
        "TAB": 0x09, "ESC": 0x1B, "ESCAPE": 0x1B, "SPACE": 0x20,
        "BACKSPACE": 0x08, "DELETE": 0x2E, "HOME": 0x24, "END": 0x23,
        "LEFT": 0x25, "UP": 0x26, "RIGHT": 0x27, "DOWN": 0x28,
        "PAGEUP": 0x21, "PAGEDOWN": 0x22}
KEYS.update({f"F{i}": 0x6F + i for i in range(1, 13)})
KEYS.update({c: ord(c) for c in "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"})


class WindowsDesktop:
    def __init__(self, policy: dict, data_dir: Path):
        if os.name != "nt":
            raise DesktopError("Lenovo Computer Use requires Windows 10/11")
        self.policy, self.data_dir = policy, data_dir
        self.snapshots: dict[str, dict] = {}
        self.user = C.WinDLL("user32", use_last_error=True)
        self.gdi = C.WinDLL("gdi32", use_last_error=True)
        self.kernel = C.WinDLL("kernel32", use_last_error=True)
        self.callback_type = C.WINFUNCTYPE(W.BOOL, W.HWND, W.LPARAM)
        self._signatures()
        # PER_MONITOR_AWARE_V2 prevents 125%/150% DPI coordinate virtualization.
        if not self.user.SetProcessDpiAwarenessContext(C.c_void_p(-4)):
            # Already initialized hosts can set the calling thread instead.
            if not self.user.SetThreadDpiAwarenessContext(C.c_void_p(-4)):
                raise DesktopError("Cannot establish physical-pixel DPI coordinates")

    def _signatures(self):
        def sig(dll, name, args, result):
            fn = getattr(dll, name)
            fn.argtypes, fn.restype = args, result
        u, g, k = self.user, self.gdi, self.kernel
        for name in ("IsWindow", "IsWindowVisible", "IsIconic", "SetForegroundWindow"):
            sig(u, name, [W.HWND], W.BOOL)
        sig(u, "GetForegroundWindow", [], W.HWND)
        sig(u, "EnumWindows", [self.callback_type, W.LPARAM], W.BOOL)
        sig(u, "GetWindowThreadProcessId", [W.HWND, C.POINTER(W.DWORD)], W.DWORD)
        sig(u, "GetWindowTextLengthW", [W.HWND], C.c_int)
        sig(u, "GetWindowTextW", [W.HWND, W.LPWSTR, C.c_int], C.c_int)
        sig(u, "GetWindowRect", [W.HWND, C.POINTER(W.RECT)], W.BOOL)
        sig(u, "GetAncestor", [W.HWND, W.UINT], W.HWND)
        sig(u, "GetLastActivePopup", [W.HWND], W.HWND)
        sig(u, "WindowFromPoint", [W.POINT], W.HWND)
        sig(u, "SetCursorPos", [C.c_int, C.c_int], W.BOOL)
        sig(u, "GetAsyncKeyState", [C.c_int], W.SHORT)
        sig(u, "GetSystemMetrics", [C.c_int], C.c_int)
        sig(u, "ShowWindow", [W.HWND, C.c_int], W.BOOL)
        sig(u, "SendInput", [W.UINT, C.POINTER(INPUT), C.c_int], W.UINT)
        sig(u, "SetProcessDpiAwarenessContext", [C.c_void_p], W.BOOL)
        sig(u, "SetThreadDpiAwarenessContext", [C.c_void_p], C.c_void_p)
        sig(u, "GetDC", [W.HWND], W.HDC)
        sig(u, "ReleaseDC", [W.HWND, W.HDC], C.c_int)
        sig(k, "OpenProcess", [W.DWORD, W.BOOL, W.DWORD], W.HANDLE)
        sig(k, "QueryFullProcessImageNameW", [W.HANDLE, W.DWORD, W.LPWSTR, C.POINTER(W.DWORD)], W.BOOL)
        sig(k, "CloseHandle", [W.HANDLE], W.BOOL)
        sig(g, "CreateCompatibleDC", [W.HDC], W.HDC)
        sig(g, "DeleteDC", [W.HDC], W.BOOL)
        sig(g, "CreateDIBSection", [W.HDC, C.POINTER(BITMAPINFOHEADER), W.UINT,
                                   C.POINTER(C.c_void_p), W.HANDLE, W.DWORD], W.HBITMAP)
        sig(g, "SelectObject", [W.HDC, W.HANDLE], W.HANDLE)
        sig(g, "DeleteObject", [W.HANDLE], W.BOOL)
        sig(g, "SetStretchBltMode", [W.HDC, C.c_int], C.c_int)
        sig(g, "StretchBlt", [W.HDC, C.c_int, C.c_int, C.c_int, C.c_int,
                              W.HDC, C.c_int, C.c_int, C.c_int, C.c_int, W.DWORD], W.BOOL)
        sig(g, "GdiFlush", [], W.BOOL)

    def check_stop(self):
        hotkey = all(self.user.GetAsyncKeyState(vk) & 0x8000 for vk in (0x11, 0x12, 0x13))
        if hotkey:
            self.data_dir.mkdir(parents=True, exist_ok=True)
            (self.data_dir / "STOP").touch()
        if hotkey or (self.data_dir / "STOP").exists():
            raise DesktopError("STOPPED: use Resume-Control.cmd yourself to resume")

    def _process_path(self, pid: int) -> str:
        handle = self.kernel.OpenProcess(0x1000, False, pid)
        if not handle:
            return ""
        try:
            size, buffer = W.DWORD(32768), C.create_unicode_buffer(32768)
            return buffer.value if self.kernel.QueryFullProcessImageNameW(handle, 0, buffer, C.byref(size)) else ""
        finally:
            self.kernel.CloseHandle(handle)

    def allowed(self, window: dict) -> bool:
        for rule in self.policy["allowed_apps"]:
            if window["process"].casefold() != rule["process"].casefold():
                continue
            if rule.get("path") and os.path.normcase(window["path"]) != os.path.normcase(rule["path"]):
                continue
            if rule.get("title") and window["title"] != rule["title"]:
                continue
            return True
        return False

    def _info(self, hwnd: int) -> dict:
        if not self.user.IsWindow(hwnd):
            raise DesktopError("Window has closed; list windows again")
        pid = W.DWORD()
        self.user.GetWindowThreadProcessId(hwnd, C.byref(pid))
        title = C.create_unicode_buffer(self.user.GetWindowTextLengthW(hwnd) + 1)
        self.user.GetWindowTextW(hwnd, title, len(title))
        rect = W.RECT()
        if not self.user.GetWindowRect(hwnd, C.byref(rect)):
            raise DesktopError("Cannot read window geometry")
        path = self._process_path(pid.value)
        return {"window_id": f"{hwnd}:{pid.value}", "pid": pid.value,
                "process": path.rsplit("\\", 1)[-1], "path": path, "title": title.value,
                "rect": {"left": rect.left, "top": rect.top, "right": rect.right, "bottom": rect.bottom},
                "minimized": bool(self.user.IsIconic(hwnd)),
                "foreground": self.user.GetForegroundWindow() == hwnd}

    def list_windows(self) -> dict:
        windows = []
        @self.callback_type
        def visit(hwnd, _):
            if self.user.IsWindowVisible(hwnd):
                try:
                    info = self._info(hwnd)
                    if info["title"] and self.allowed(info):
                        windows.append(info)
                except DesktopError:
                    pass
            return True
        if not self.user.EnumWindows(visit, 0):
            raise DesktopError("Cannot enumerate this interactive desktop")
        return {"windows": windows, "scope": "configured allowed applications only"}

    def target(self, window_id: str, foreground=False) -> tuple[int, dict]:
        try:
            hwnd, pid = map(int, window_id.split(":"))
        except (ValueError, AttributeError):
            raise DesktopError("Invalid window_id; use list_windows") from None
        info = self._info(hwnd)
        if info["pid"] != pid:
            raise DesktopError("Window identity changed; list windows again")
        if not self.allowed(info):
            raise DesktopError("Application is not allowed by policy.json")
        if not self.user.IsWindowVisible(hwnd):
            raise DesktopError("Target window is hidden")
        if foreground:
            self.check_stop()
            if info["minimized"] or not info["foreground"]:
                raise DesktopError("Target is not foreground; focus_window then observe again")
            popup = self.user.GetLastActivePopup(hwnd)
            if popup != hwnd and self.user.IsWindowVisible(popup):
                raise DesktopError("A modal/popup is blocking the target; select its own window_id")
        return hwnd, info

    def focus_window(self, window_id: str) -> dict:
        self.check_stop()
        hwnd, info = self.target(window_id)
        if info["minimized"]:
            self.user.ShowWindow(hwnd, 9)
        self.user.SetForegroundWindow(hwnd)
        time.sleep(0.15)
        _, info = self.target(window_id, foreground=True)
        return info

    def _capture(self, rect: dict, width: int, height: int) -> bytes:
        screen = self.user.GetDC(None)
        dc = self.gdi.CreateCompatibleDC(screen)
        bitmap, previous = None, None
        try:
            if not screen or not dc:
                raise DesktopError("Screen capture is unavailable on this desktop")
            header = BITMAPINFOHEADER(C.sizeof(BITMAPINFOHEADER), width, -height, 1, 32, 0, 0, 0, 0, 0, 0)
            bits = C.c_void_p()
            bitmap = self.gdi.CreateDIBSection(screen, C.byref(header), 0, C.byref(bits), None, 0)
            if not bitmap or not bits:
                raise DesktopError("Cannot allocate screenshot bitmap")
            previous = self.gdi.SelectObject(dc, bitmap)
            self.gdi.SetStretchBltMode(dc, 4)
            if not self.gdi.StretchBlt(dc, 0, 0, width, height, screen, rect["left"], rect["top"],
                                       rect["right"] - rect["left"], rect["bottom"] - rect["top"], 0x00CC0020):
                raise DesktopError("Screenshot failed")
            self.gdi.GdiFlush()
            return bgra_to_png(width, height, C.string_at(bits, width * height * 4))
        finally:
            if previous:
                self.gdi.SelectObject(dc, previous)
            if bitmap:
                self.gdi.DeleteObject(bitmap)
            if dc:
                self.gdi.DeleteDC(dc)
            if screen:
                self.user.ReleaseDC(None, screen)

    def observe_window(self, window_id: str) -> dict:
        _, info = self.target(window_id, foreground=True)
        rect = info["rect"]
        vx, vy = self.user.GetSystemMetrics(76), self.user.GetSystemMetrics(77)
        vr, vb = vx + self.user.GetSystemMetrics(78), vy + self.user.GetSystemMetrics(79)
        # Invisible resize borders of maximized windows can extend outside monitors.
        rect = {"left": max(rect["left"], vx), "top": max(rect["top"], vy),
                "right": min(rect["right"], vr), "bottom": min(rect["bottom"], vb)}
        w, h = rect["right"] - rect["left"], rect["bottom"] - rect["top"]
        if w <= 0 or h <= 0 or w > 16384 or h > 16384:
            raise DesktopError("Window is outside the usable desktop")
        scale = min(1.0, self.policy["max_image_dimension"] / max(w, h))
        width, height = max(1, round(w * scale)), max(1, round(h * scale))
        image = self._capture(rect, width, height)
        _, current = self.target(window_id, foreground=True)
        if current["rect"] != info["rect"]:
            raise DesktopError("Window moved during screenshot; retry observe_window")
        snapshot_id = uuid.uuid4().hex
        self.snapshots = {key: s for key, s in self.snapshots.items()
                          if time.monotonic() - s["created"] <= self.policy["snapshot_ttl_seconds"]}
        self.snapshots[snapshot_id] = {"window_id": window_id, "window_rect": info["rect"],
                                      "capture_rect": rect, "width": width, "height": height,
                                      "created": time.monotonic()}
        return {"window": info, "snapshot_id": snapshot_id, "capture_rect": rect,
                "image_width": width, "image_height": height,
                "coordinate_system": "pixels in this PNG; top-left is (0, 0)",
                "expires_in_seconds": self.policy["snapshot_ttl_seconds"],
                "png_base64": base64.b64encode(image).decode("ascii")}

    def _snapshot(self, window_id: str, snapshot_id: str) -> tuple[int, dict]:
        hwnd, info = self.target(window_id, foreground=True)
        snapshot = self.snapshots.get(snapshot_id)
        if not snapshot or snapshot["window_id"] != window_id:
            raise DesktopError("Unknown snapshot; observe this window in this server session first")
        if time.monotonic() - snapshot["created"] > self.policy["snapshot_ttl_seconds"]:
            raise DesktopError("Snapshot expired; observe_window again")
        if info["rect"] != snapshot["window_rect"]:
            raise DesktopError("Window moved/resized; observe_window again")
        return hwnd, snapshot

    def _point(self, hwnd: int, snapshot: dict, x: int, y: int) -> tuple[int, int]:
        point = image_point(snapshot["capture_rect"], snapshot["width"], snapshot["height"], x, y)
        actual = self.user.WindowFromPoint(W.POINT(*point))
        if self.user.GetAncestor(actual, 2) != hwnd:
            raise DesktopError("Point is covered by another window; inspect the desktop again")
        return point

    def _send(self, events: list[INPUT]):
        array = (INPUT * len(events))(*events)
        if self.user.SendInput(len(array), array, C.sizeof(INPUT)) != len(array):
            raise DesktopError("Windows rejected input (possibly elevation/UIPI); no privilege bypass is attempted")

    @staticmethod
    def _mouse(flags: int, data=0) -> INPUT:
        return INPUT(type=0, mi=MOUSEINPUT(0, 0, data & 0xFFFFFFFF, flags, 0, 0))

    @staticmethod
    def _key(vk: int, up=False, unicode=False) -> INPUT:
        return INPUT(type=1, ki=KEYBDINPUT(0 if unicode else vk, vk if unicode else 0,
                                         (2 if up else 0) | (4 if unicode else 0), 0, 0))

    def _check_physical_modifiers(self):
        if any(self.user.GetAsyncKeyState(vk) & 0x8000 for vk in (0x10, 0x11, 0x12, 0x5B, 0x5C)):
            raise DesktopError("Release held Shift/Ctrl/Alt/Windows keys before automation")

    def click(self, window_id: str, snapshot_id: str, x: int, y: int, button="left", count=1) -> dict:
        hwnd, snapshot = self._snapshot(window_id, snapshot_id)
        self._check_physical_modifiers()
        point = self._point(hwnd, snapshot, x, y)
        if not self.user.SetCursorPos(*point):
            raise DesktopError("Cannot move pointer")
        down, up = {"left": (2, 4), "right": (8, 16)}[button]
        for _ in range(count):
            self._snapshot(window_id, snapshot_id)
            self._point(hwnd, snapshot, x, y)
            self._send([self._mouse(down), self._mouse(up)])
            time.sleep(0.06)
        return {"clicked": True, "point": [x, y], "button": button, "count": count}

    def type_text(self, window_id: str, snapshot_id: str, text: str) -> dict:
        self._snapshot(window_id, snapshot_id)
        self._check_physical_modifiers()
        # No clipboard replacement. UTF-16 surrogate pairs support Chinese/emoji.
        encoded = text.encode("utf-16-le")
        units = struct.unpack("<" + "H" * (len(encoded) // 2), encoded)
        for start in range(0, len(units), 16):
            self._snapshot(window_id, snapshot_id)
            events = [event for unit in units[start:start + 16]
                      for event in (self._key(unit, unicode=True), self._key(unit, up=True, unicode=True))]
            self._send(events)
            time.sleep(0.01)
        return {"typed_characters": len(text), "submitted": False}

    def press_key(self, window_id: str, snapshot_id: str, keys: list[str], hold_ms=0) -> dict:
        self._snapshot(window_id, snapshot_id)
        self._check_physical_modifiers()
        codes = [KEYS[key.upper()] for key in keys]
        pressed = []
        try:
            for code in codes:
                self._snapshot(window_id, snapshot_id)
                self._send([self._key(code)])
                pressed.append(code)
            until = time.monotonic() + hold_ms / 1000
            while time.monotonic() < until:
                self._snapshot(window_id, snapshot_id)
                time.sleep(0.02)
        finally:
            if pressed:
                self._send([self._key(code, up=True) for code in reversed(pressed)])
        return {"pressed": keys, "hold_ms": hold_ms}

    def scroll(self, window_id: str, snapshot_id: str, x: int, y: int, steps: int) -> dict:
        hwnd, snapshot = self._snapshot(window_id, snapshot_id)
        self._check_physical_modifiers()
        point = self._point(hwnd, snapshot, x, y)
        if not self.user.SetCursorPos(*point):
            raise DesktopError("Cannot move pointer")
        self._snapshot(window_id, snapshot_id)
        self._send([self._mouse(0x0800, steps * 120)])
        return {"scrolled_steps": steps, "positive_direction": "up"}

    def drag(self, window_id: str, snapshot_id: str, x: int, y: int, end_x: int, end_y: int,
             duration_ms=500) -> dict:
        hwnd, snapshot = self._snapshot(window_id, snapshot_id)
        self._check_physical_modifiers()
        first = self._point(hwnd, snapshot, x, y)
        self._point(hwnd, snapshot, end_x, end_y)
        if not self.user.SetCursorPos(*first):
            raise DesktopError("Cannot move pointer")
        self._send([self._mouse(2)])
        try:
            steps = max(2, duration_ms // 20)
            for i in range(1, steps + 1):
                self._snapshot(window_id, snapshot_id)
                px = round(x + (end_x - x) * i / steps)
                py = round(y + (end_y - y) * i / steps)
                point = self._point(hwnd, snapshot, px, py)
                if not self.user.SetCursorPos(*point):
                    raise DesktopError("Cannot move pointer")
                time.sleep(duration_ms / steps / 1000)
        finally:
            self._send([self._mouse(4)])
        return {"dragged": True, "start": [x, y], "end": [end_x, end_y]}

    def ui_tree(self, window_id: str) -> dict:
        hwnd, info = self.target(window_id)
        request = {"hwnd": hwnd, "pid": info["pid"]}
        ps = Path(os.environ.get("SystemRoot", r"C:\Windows")) / "System32/WindowsPowerShell/v1.0/powershell.exe"
        script = Path(__file__).with_name("ui_tree.ps1")
        try:
            completed = subprocess.run([str(ps), "-NoProfile", "-NonInteractive", "-File", str(script)],
                                       input=json.dumps(request), capture_output=True, encoding="utf-8",
                                       timeout=12, creationflags=subprocess.CREATE_NO_WINDOW)
        except subprocess.TimeoutExpired:
            raise DesktopError("UI Automation provider timed out; use the screenshot instead") from None
        if completed.returncode:
            raise DesktopError("UI Automation unavailable: " + completed.stderr.strip()[:400])
        result = json.loads(completed.stdout.lstrip("\ufeff"))
        self.target(window_id)
        return result
