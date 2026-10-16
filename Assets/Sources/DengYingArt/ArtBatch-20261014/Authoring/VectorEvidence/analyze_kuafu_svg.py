"""Read-only path geometry evidence from the public-domain Kuafu SVG.

SVG diagnostic files retain original paths. They are not finished puppet parts:
the source consists of engraved ink, not watertight anatomical silhouettes.
"""

from __future__ import annotations

import hashlib
import json
import math
import re
import xml.etree.ElementTree as ET
from pathlib import Path

SOURCE = Path(r"D:\灯影山海\Saved\SourceReadiness-20261014\Kuafu\Run2\Kuafu-auto-vector.svg")
OUT = Path(__file__).resolve().parent
NS = "{http://www.w3.org/2000/svg}"
TOKEN = re.compile(r"[A-Za-z]|[-+]?(?:\d*\.\d+|\d+\.?\d*)(?:[eE][-+]?\d+)?")


def cubic(p0, p1, p2, p3, t):
    s = 1.0 - t
    return s**3 * p0 + 3.0 * s * s * t * p1 + 3.0 * s * t * t * p2 + t**3 * p3


def extrema(p0, p1, p2, p3):
    a = -p0 + 3 * p1 - 3 * p2 + p3
    b = 2 * (p0 - 2 * p1 + p2)
    c = p1 - p0
    if abs(a) < 1e-12:
        return [-c / b] if abs(b) > 1e-12 else []
    discriminant = b * b - 4 * a * c
    if discriminant < 0:
        return []
    root = math.sqrt(discriminant)
    return [(-b + root) / (2 * a), (-b - root) / (2 * a)]


def parse_path(d):
    tokens = TOKEN.findall(d)
    commands = {x for x in tokens if x.isalpha()}
    assert commands <= set("MmLlHhVvCcZz"), commands
    points = []
    runs = []
    curves = []
    x = y = start_x = start_y = 0.0
    i = 0
    command = None
    while i < len(tokens):
        if tokens[i].isalpha():
            command = tokens[i]
            i += 1
        assert command is not None
        absolute = command.isupper()
        code = command.upper()
        if code == "Z":
            points.append((start_x, start_y))
            runs[-1].append((start_x, start_y))
            x, y = start_x, start_y
            command = None
            continue
        count = {"M": 2, "L": 2, "H": 1, "V": 1, "C": 6}[code]
        values = list(map(float, tokens[i : i + count]))
        assert len(values) == count
        i += count
        if code in ("M", "L"):
            nx, ny = values
            if not absolute:
                nx += x
                ny += y
            if code == "M":
                start_x, start_y = nx, ny
                runs.append([])
                command = "L" if absolute else "l"
            x, y = nx, ny
            points.append((x, y))
            runs[-1].append((x, y))
        elif code in ("H", "V"):
            if code == "H":
                x = values[0] if absolute else x + values[0]
            else:
                y = values[0] if absolute else y + values[0]
            points.append((x, y))
            runs[-1].append((x, y))
        elif code == "C":
            x1, y1, x2, y2, x3, y3 = values
            if not absolute:
                x1, y1, x2, y2, x3, y3 = x1 + x, y1 + y, x2 + x, y2 + y, x3 + x, y3 + y
            curves.append(((x, y), (x1, y1), (x2, y2), (x3, y3)))
            for t in [0.0, 1.0] + extrema(x, x1, x2, x3) + extrema(y, y1, y2, y3):
                if 0 <= t <= 1:
                    points.append((cubic(x, x1, x2, x3, t), cubic(y, y1, y2, y3, t)))
            for sample in range(1, 9):
                t = sample / 8
                runs[-1].append((cubic(x, x1, x2, x3, t), cubic(y, y1, y2, y3, t)))
            x, y = x3, y3
    assert runs and points
    # Original group transforms raw units into original image pixels.
    converted = [(a * 0.1, 2488 - b * 0.1) for a, b in points]
    bbox = [min(a for a, b in converted), min(b for a, b in converted), max(a for a, b in converted), max(b for a, b in converted)]
    flat_runs = [[(a * 0.1, 2488 - b * 0.1) for a, b in run] for run in runs]
    ink_area = abs(sum(sum(a[0] * b[1] - b[0] * a[1] for a, b in zip(run, run[1:] + run[:1])) * 0.5 for run in flat_runs))
    return bbox, flat_runs, ink_area, commands


def point_in_polygon(point, polygon):
    x, y = point
    inside = False
    for (ax, ay), (bx, by) in zip(polygon, polygon[1:] + polygon[:1]):
        if (ay > y) != (by > y) and x < (bx - ax) * (y - ay) / (by - ay) + ax:
            inside = not inside
    return inside


REGIONS = {
    "title": [(1490, 80), (1660, 80), (1660, 645), (1490, 645)],
    "sun": [(150, 440), (650, 440), (650, 930), (150, 930)],
    "head": [(998, 1142), (1040, 1137), (1150, 1160), (1190, 1225), (1168, 1295), (1080, 1320), (1000, 1290), (974, 1215)],
    "ear_snake_upper": [(995, 1030), (1080, 1030), (1080, 1130), (1180, 1130), (1265, 1090), (1265, 1178), (1140, 1180), (1060, 1150), (1010, 1100)],
    "ear_snake_side": [(895, 1170), (1005, 1115), (1020, 1150), (1145, 1180), (1180, 1210), (1230, 1215), (1280, 1255), (1250, 1298), (1165, 1270), (1120, 1220), (1000, 1180), (920, 1220)],
    "front_hand_snake": [(617, 1195), (675, 1220), (736, 1280), (745, 1340), (870, 1395), (930, 1445), (975, 1545), (920, 1545), (875, 1445), (720, 1400), (676, 1350), (680, 1285)],
    "back_hand_snake": [(1030, 1350), (1110, 1305), (1200, 1330), (1325, 1320), (1360, 1360), (1340, 1415), (1350, 1435), (1440, 1430), (1460, 1475), (1385, 1475), (1315, 1440), (1280, 1395), (1165, 1375)],
    "torso_cloth": [(961, 1260), (1120, 1295), (1210, 1220), (1325, 1260), (1310, 1350), (1220, 1410), (1240, 1510), (1400, 1470), (1320, 1605), (1265, 1740), (1220, 1780), (1120, 1740), (1080, 1700), (1000, 1720), (905, 1740), (874, 1670), (881, 1600), (976, 1565)],
    "front_arm": [(957, 1260), (991, 1300), (962, 1462), (907, 1463), (880, 1400), (820, 1440), (747, 1440), (735, 1350), (822, 1368), (865, 1350), (907, 1350)],
    "back_arm": [(1285, 1260), (1330, 1290), (1390, 1370), (1380, 1410), (1320, 1420), (1250, 1380), (1200, 1410), (1130, 1370), (1130, 1330), (1185, 1310), (1225, 1350)],
    "front_leg": [(884, 1655), (958, 1640), (992, 1690), (981, 1775), (976, 1822), (995, 1860), (994, 1890), (987, 1900), (933, 1900), (875, 1918), (828, 1890), (885, 1850), (932, 1825), (916, 1740), (885, 1690)],
    "back_leg": [(1320, 1730), (1370, 1760), (1445, 1810), (1495, 1820), (1530, 1850), (1516, 1965), (1450, 1970), (1460, 1905), (1455, 1845), (1405, 1840), (1325, 1805), (1290, 1780)],
}

JOINTS = {
    "neck": [1090, 1300],
    "front_shoulder": [977, 1305],
    "front_elbow": [919, 1412],
    "front_wrist": [816, 1395],
    "back_shoulder": [1273, 1295],
    "back_elbow": [1335, 1375],
    "back_wrist": [1190, 1368],
    "pelvis": [1164, 1610],
    "front_hip": [1047, 1615],
    "front_knee": [927, 1655],
    "front_ankle": [947, 1825],
    "back_hip": [1240, 1618],
    "back_knee": [1313, 1780],
    "back_ankle": [1467, 1840],
}


def main():
    raw = SOURCE.read_bytes()
    root = ET.fromstring(raw)
    group = root.find(NS + "g")
    assert group is not None and group.attrib["transform"] == "translate(0.000000,2488.000000) scale(0.100000,-0.100000)"
    originals = root.findall(".//" + NS + "path")
    assert len(originals) == 1067
    records = []
    all_commands = set()
    total_outer = total_inner = 0
    for index, item in enumerate(originals):
        bbox, runs, area, commands = parse_path(item.attrib["d"])
        all_commands |= commands
        center = [(bbox[0] + bbox[2]) * 0.5, (bbox[1] + bbox[3]) * 0.5]
        vertices = [point for run in runs for point in run]
        loop_areas = [sum(a[0] * b[1] - b[0] * a[1] for a, b in zip(run, run[1:] + run[:1])) * 0.5 for run in runs]
        outer_count = sum(a < -0.01 for a in loop_areas)
        inner_count = sum(a > 0.01 for a in loop_areas)
        assert outer_count == 1 and outer_count + inner_count == len(runs), (index, loop_areas)
        total_outer += outer_count
        total_inner += inner_count
        region_fractions = {name: sum(point_in_polygon(point, poly) for point in vertices) / len(vertices) for name, poly in REGIONS.items()}
        labels = [name for name, fraction in region_fractions.items() if fraction >= 0.75]
        records.append({"path_index": index, "bbox_px": [round(v, 3) for v in bbox], "center_px": [round(v, 3) for v in center], "approx_ink_area_px2": round(area, 3), "subpath_count": len(runs), "ink_outer_contour_count": outer_count, "ink_inner_contour_count": inner_count, "sample_count": len(vertices), "region_candidates": labels, "region_coverage": {k: round(v, 4) for k, v in region_fractions.items() if v > 0}})
    # Basic parser checks ensure relative and absolute cubic coordinates agree.
    box_a, *_ = parse_path("M10 10 c10 0 20 10 30 10 l0 10 z")
    box_b, *_ = parse_path("M10 10 C20 10 30 20 40 20 L40 30 Z")
    assert box_a == box_b
    assert point_in_polygon([5, 5], [[0, 0], [10, 0], [10, 10], [0, 10]])
    assert not point_in_polygon([15, 5], [[0, 0], [10, 0], [10, 10], [0, 10]])
    evidence = {"source": str(SOURCE), "source_sha256": hashlib.sha256(raw).hexdigest().upper(), "viewbox_px": [0, 0, 1682, 2488], "path_count": len(records), "commands": sorted(all_commands), "ink_contour_topology": {"outer_contours": total_outer, "inner_contours": total_inner, "definition": "Signed flattened path contours after the original y-flip: each of all 1067 paths has exactly one clockwise outer ink contour; positive contours are inner cut-outs. This describes engraved ink connectivity, not anatomical connectivity."}, "coordinate_system": "Original PNG/SVG pixels: x right, y down. Bounds use analytic cubic extrema, sampled membership is diagnostic only.", "segmentation_status": "Semantic regions are visual tracing guides, not authoritative anatomical masks; no watertight silhouette was invented.", "joint_status": "Observed bend/attachment coordinate candidates from the source figure, not hidden anatomical assertions.", "regions_px": REGIONS, "joint_candidates_px": JOINTS, "largest_ink_paths": sorted(records, key=lambda r: r["approx_ink_area_px2"], reverse=True)[:30], "paths": records}
    (OUT / "PATH_GEOMETRY.json").write_text(json.dumps(evidence, ensure_ascii=False, indent=2), encoding="utf-8")
    original_body = "\n".join(f'<path id="source-path-{index}" d="{item.attrib["d"]}"/>' for index, item in enumerate(originals))
    colours = ["#b33b44", "#efbd33", "#31657e", "#cc79a7", "#dd6633", "#009e73", "#7c55aa", "#69a8d0", "#805922", "#e1771a", "#4466aa", "#64a266"]
    overlay = []
    for (name, polygon), color in zip(REGIONS.items(), colours):
        pts = " ".join(f"{x},{y}" for x, y in polygon)
        overlay.append(f'<polygon points="{pts}" fill="{color}" fill-opacity="0.13" stroke="{color}" stroke-width="3"/>')
        overlay.append(f'<text x="{polygon[0][0]}" y="{polygon[0][1]-6}" fill="{color}" font-size="17">{name}</text>')
    for name, (x, y) in JOINTS.items():
        overlay.append(f'<circle cx="{x}" cy="{y}" r="8" fill="#00aaaa" stroke="#fff" stroke-width="2"/>')
        overlay.append(f'<text x="{x+10}" y="{y+5}" fill="#006666" font-size="16">{name}</text>')
    diagnostic = f'<svg xmlns="http://www.w3.org/2000/svg" width="1682" height="2488" viewBox="0 0 1682 2488"><rect width="1682" height="2488" fill="white"/><g transform="{group.attrib["transform"]}" fill="black" stroke="none">{original_body}</g>{"".join(overlay)}</svg>'
    (OUT / "REGIONS_AND_JOINTS.svg").write_text(diagnostic, encoding="utf-8")
    # Each diagnostic region retains originals. clipPath is explicitly unsuitable
    # for importing as the model silhouette because clipped ink is not body mass.
    summary = []
    for name, polygon in REGIONS.items():
        selected = [r for r in records if name in r["region_candidates"]]
        mixed = [r for r in records if 0.05 < r["region_coverage"].get(name, 0) < 0.75]
        bbox = [min(p[0] for p in polygon), min(p[1] for p in polygon), max(p[0] for p in polygon), max(p[1] for p in polygon)]
        pts = " ".join(f"{x},{y}" for x, y in polygon)
        region_svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{bbox[0]-10} {bbox[1]-10} {bbox[2]-bbox[0]+20} {bbox[3]-bbox[1]+20}"><defs><clipPath id="region"><polygon points="{pts}"/></clipPath></defs><g clip-path="url(#region)"><g transform="{group.attrib["transform"]}" fill="black">{original_body}</g></g><polygon points="{pts}" fill="none" stroke="#00aaaa" stroke-width="1"/></svg>'
        (OUT / f"ink_region_{name}.svg").write_text(region_svg, encoding="utf-8")
        summary.append({"region": name, "guide_bbox_px": bbox, "mostly_inside_paths": [r["path_index"] for r in selected], "boundary_mixed_paths": [r["path_index"] for r in mixed], "counts": {"inside": len(selected), "mixed": len(mixed)}})
    (OUT / "REGION_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"status": "PASS-READONLY-SVG-EVIDENCE", "paths": len(records), "ink_contour_topology": evidence["ink_contour_topology"], "source_sha256": evidence["source_sha256"], "regions": [{"region": r["region"], **r["counts"]} for r in summary], "largest_paths": [{k: r[k] for k in ("path_index", "bbox_px", "approx_ink_area_px2", "region_candidates")} for r in evidence["largest_ink_paths"][:15]]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
