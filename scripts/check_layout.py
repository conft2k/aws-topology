#!/usr/bin/env python3
"""Check an SVG diagram for layout defects that only show up in a render.

    python scripts/check_layout.py draft.svg

Reports, and exits with status 1 on any of them:
  LINE OVER TEXT   a connector or container border crosses a label
  LINE OVER ICON   a connector or container border crosses an icon or badge
  TEXT OVERLAP     two labels overlap, or a label overlaps an icon
  TEXT TOO CLOSE   two labels side by side are less than 4px apart (a label and its
                   sub-caption stack 16px apart and are not checked)
  TEXT AT BORDER   a label is closer than 8px to a container border (a bold header
                   label: 4px)
  OFF CANVAS       a label runs past the edge of the viewBox
  LINE NEAR TEXT   a connector skims a node or header label (< 4px) without crossing it
  BADGE NEAR ICON  a group badge (e.g. an ASG's) is within 8px of a node icon
  TEXT NEAR ICON   a label is within 8px of a node icon it doesn't label (a header
                   label: 6px, so nodes start at subnet.y + 28 or lower)
  HEADER CLEARANCE a container title (or its CIDR line) has a nested box's top border
                   < 8px below it (nested boxes start at container.y + 30, + 46 with a CIDR)
  SMALL TEXT       a label is smaller than 12px
  SERVICE AS TEXT  a connector label names an AWS service or resource that has an
                   official icon in the bundle — draw it as an icon node instead
                   (labels centered under an icon are node labels and are skipped)
  SHORT ARROW      the segment carrying an arrowhead is shorter than 20px (a head
                   stuck on a bend or trunk junction)
  LINE HUGS BORDER a connector runs alongside (or on top of) a container border less
                   than 12px from it for more than 20px
  TITLE OFFSET     a container title not on its box's header row (baseline box.y + 18;
                   the 15px AWS Cloud title + 22)
  OUTSIDE CLOUD    a Direct Connect location, Internet or Site-to-Site VPN icon inside the
                   AWS Cloud box (drafts only: needs bundle: refs)
  CIDR IN TITLE    a container title that carries its CIDR (the CIDR is its own line)
  CIDR OFF HEADER  a bare CIDR label neither right under a container title nor a
                   node's sub-caption
  CIDR COLOR       a CIDR line under a title that isn't squid ink #232F3E
  GLYPH STEP       a label numbers steps with circled digits (①) — draw the legend's
                   numbers as the diagram's step badges instead

Anything covered by a white mask rect drawn later (the IGW/VGW on the VPC border)
is not reported, nor is a small junction dot (circle, r ≤ 6) sitting on its own line. Text widths are estimated (0.55 × font-size per Latin character,
1.0 × per Hangul/CJK character, arrow or circled digit), so a hit within a pixel or two is worth a look in
the render rather than a blind fix. Only translate() transforms are understood,
which is all the skill's diagrams use.
"""
import math
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import find_icon  # noqa: E402  (same directory; reuses the icon search and aliases)

NS = "{http://www.w3.org/2000/svg}"
MIN_FONT = 12
WHITE = {"#fff", "#ffffff", "white"}


def num(v, default=0.0):
    try:
        return float(v)
    except (TypeError, ValueError):
        return default


def translate(el):
    m = re.search(r"translate\(\s*([-\d.]+)[ ,]*([-\d.]*)\s*\)", el.get("transform", ""))
    return (num(m.group(1)), num(m.group(2))) if m else (0.0, 0.0)


def text_width(s, fs):
    w = 0.0
    for c in s:
        # Hangul, CJK, and the arrows / circled digits / symbols (U+2190–U+2BFF) that CJK
        # fonts draw full-width ("→", "①").
        wide = ("ᄀ" <= c <= "ᇿ" or "\u2190" <= c <= "\u2bff" or "　" <= c <= "鿿"
                or "가" <= c <= "힣")
        w += fs * (1.0 if wide else 0.55)
    return w


def shrink(b, d=1.0):
    x0, y0, x1, y1 = b
    return (x0 + d, y0 + d, x1 - d, y1 - d)


def boxes_overlap(a, b):
    return a[0] < b[2] and b[0] < a[2] and a[1] < b[3] and b[1] < a[3]


def contains(outer, inner, tol=1.0):
    return (outer[0] - tol <= inner[0] and outer[1] - tol <= inner[1]
            and inner[2] <= outer[2] + tol and inner[3] <= outer[3] + tol)


def seg_hits_box(p, q, b):
    """Liang–Barsky: does segment p→q pass through the interior of box b?"""
    x0, y0, x1, y1 = b
    dx, dy = q[0] - p[0], q[1] - p[1]
    t0, t1 = 0.0, 1.0
    for pk, qk in ((-dx, p[0] - x0), (dx, x1 - p[0]), (-dy, p[1] - y0), (dy, y1 - p[1])):
        if pk == 0:
            if qk <= 0:
                return False
        else:
            t = qk / pk
            if pk < 0:
                t0 = max(t0, t)
            else:
                t1 = min(t1, t)
            if t0 >= t1:
                return False
    return True


def collect(svg_root):
    texts, segs, masks, icons = [], [], [], []
    canvas = svg_root.get("viewBox", "0 0 0 0").split()
    cw, ch = num(canvas[2]), num(canvas[3])
    order = 0

    def walk(el, ox, oy):
        nonlocal order
        dx, dy = translate(el)
        ox, oy = ox + dx, oy + dy
        tag = el.tag.replace(NS, "")
        order += 1
        if tag == "defs" or tag == "marker":
            return
        if tag == "text":
            s = "".join(el.itertext()).strip()
            if s:
                fs = num(el.get("font-size"), 16)
                x, y = num(el.get("x")) + ox, num(el.get("y")) + oy
                w = text_width(s, fs)
                anchor = el.get("text-anchor", "start")
                x0 = x - w / 2 if anchor == "middle" else x - w if anchor == "end" else x
                texts.append({"s": s, "fs": fs, "box": (x0, y - 0.75 * fs, x0 + w, y + 0.25 * fs), "o": order,
                              "fill": el.get("fill", "").lower(),
                              "cx": x0 + w / 2, "y": y,
                              "header": el.get("font-weight", "") in ("600", "700", "bold")})
                texts[-1]["title"] = texts[-1]["header"] and fs >= 14
        elif tag in ("line", "polyline"):
            if tag == "line":
                pts = [(num(el.get("x1")) + ox, num(el.get("y1")) + oy),
                       (num(el.get("x2")) + ox, num(el.get("y2")) + oy)]
            else:
                pts = [num(v) for v in re.split(r"[ ,]+", el.get("points", "").strip()) if v]
                pts = [(pts[i] + ox, pts[i + 1] + oy) for i in range(0, len(pts) - 1, 2)]
            new = [{"p": p, "q": q, "kind": "connector", "o": order} for p, q in zip(pts, pts[1:])]
            # The segment an arrowhead sits on (last for marker-end, first for marker-start).
            if new and el.get("marker-end"):
                new[-1]["head"] = True
            if new and el.get("marker-start"):
                new[0]["head"] = True
            segs.extend(new)
        elif tag == "rect":
            x, y = num(el.get("x")) + ox, num(el.get("y")) + oy
            w, h = num(el.get("width")), num(el.get("height"))
            stroke = el.get("stroke", "none").lower()
            fill = el.get("fill", "#000").lower()
            if stroke != "none":
                c = [(x, y), (x + w, y), (x + w, y + h), (x, y + h)]
                for p, q in zip(c, c[1:] + c[:1]):
                    segs.append({"p": p, "q": q, "kind": "border", "o": order})
            elif fill in WHITE and not (w >= cw and h >= ch):
                masks.append({"box": (x, y, x + w, y + h), "o": order})
        elif tag == "image":
            x, y = num(el.get("x")) + ox, num(el.get("y")) + oy
            href = el.get("href") or el.get("{http://www.w3.org/1999/xlink}href") or ""
            icons.append({"box": (x, y, x + num(el.get("width")), y + num(el.get("height"))),
                          "o": order, "badge": "group/" in href[:40],
                          "ref": href[len("bundle:"):] if href.startswith("bundle:") else ""})
        elif tag == "circle":
            cx, cy, r = num(el.get("cx")) + ox, num(el.get("cy")) + oy, num(el.get("r"))
            # r <= 6: a junction dot drawn on a connector on purpose (e.g. segment membership)
            icons.append({"box": (cx - r, cy - r, cx + r, cy + r), "o": order, "badge": True,
                          "dot": (cx, cy) if r <= 6 else None})
        for child in el:
            walk(child, ox, oy)

    walk(svg_root, 0.0, 0.0)
    return texts, segs, masks, icons, (cw, ch)


# A connector label is any text whose box comes within this distance of a connector.
LABEL_REACH = 14
# A label closer than this to a container border reads as touching it.
BORDER_CLEAR = 4
# Node labels, captions and connector labels keep this much room from any border.
LABEL_CLEAR = 8
# A connector passing a node or header label keeps at least this much room.
LINE_CLEAR = 4
# Group badges and labels keep this much room from node icons that aren't theirs.
ICON_CLEAR = 8
HEADER_ICON_CLEAR = 6
# Two labels keep at least this much room between them.
TEXT_GAP = 4
# A header label (bold) needs this much room above the next box below it.
HEADER_CLEAR = 8
# The segment carrying an arrowhead is at least this long (an 8px head plus a 12px shaft), so the arrow reads as a line
# into the node, not a head stuck on a bend or junction.
MIN_ARROW = 20
# A connector running alongside a container border keeps at least this much room from it
# (a trunk squeezed into a corridor reads as part of the border).
HUG_CLEAR = 12
# Circled digits (①–⑳, ❶–➓): a step legend repeats the diagram's badges instead.
CIRCLED = re.compile("[\u2460-\u2473\u2776-\u2793]")
# A label that is nothing but a CIDR. A container's CIDR is its own line right under the
# container's title (same x, 16px lower); a bare one elsewhere is allowed only as the
# sub-caption of a node (single-icon VPC, customer gateway).
BARE_CIDR = re.compile(r"^\d{1,3}(\.\d{1,3}){3}/\d{1,2}$")
CIDR_IN = re.compile(r"\d{1,3}(\.\d{1,3}){3}/\d{1,2}")
CIDR_COLOR = "#232f3e"
# Things that are not in AWS: they sit between the on-premises group and the AWS Cloud box,
# never inside it (a Direct Connect location is a colocation facility, the Internet is the
# Internet, and a Site-to-Site VPN's IPsec runs over it). Checked on drafts (bundle: refs).
OUTSIDE_CLOUD = ("service/AWS-Direct-Connect", "resource/Internet", "service/AWS-Site-to-Site-VPN")
ICON_SETS = ("service", "resource")


def official_icon(phrase):
    """The bundle icon a phrase names exactly (score ≥ 95), or None."""
    if len(find_icon.norm(phrase)) < 3:
        return None
    for score, ref in find_icon.search(phrase, k=3):
        if score >= 95 and ref.split("/", 1)[0] in ICON_SETS:
            return ref
    return None


def services_in_label(s):
    parts = re.split(r"\s+·\s+|[(),→⇄↔]|\s+-\s+", s)
    return [(p.strip(), ref) for p in parts if p.strip() for ref in [official_icon(p.strip())] if ref]


def is_node_label(t, icons):
    """A label (or its sub-caption) centered under an icon names that node, not a connector."""
    for i in icons:
        x0, y0, x1, y1 = i["box"]
        if not i["badge"] and abs(t["cx"] - (x0 + x1) / 2) <= 3 and y1 < t["y"] <= y1 + 44:
            return True
    return False


def expand(b, d):
    return (b[0] - d, b[1] - d, b[2] + d, b[3] + d)


def through(dot, s):
    """Does segment s pass through point dot (a junction dot sits on its line)?"""
    (x1, y1), (x2, y2) = s["p"], s["q"]
    cx, cy = dot
    length = ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5 or 1.0
    dist = abs((x2 - x1) * (y1 - cy) - (x1 - cx) * (y2 - y1)) / length
    return dist < 1.0


def masked(box, after, masks):
    return any(m["o"] > after and contains(m["box"], box) for m in masks)


def container_rects(root):
    """Bordered rects (containers) with translate offsets applied."""
    out = []
    def walk(el, ox, oy):
        dx, dy = translate(el)
        ox, oy = ox + dx, oy + dy
        if (el.tag.replace(NS, "") == "rect" and el.get("stroke", "none").lower() != "none"
                and el.get("fill", "none").lower() == "none"):
            out.append((num(el.get("x")) + ox, num(el.get("y")) + oy, num(el.get("width")), num(el.get("height"))))
        for c in el:
            walk(c, ox, oy)
    walk(root, 0, 0)
    return out


def check(path):
    root = ET.parse(path).getroot()
    texts, segs, masks, icons, (cw, ch) = collect(root)
    issues = []
    # A container title sits in its box's header row: x = box.x + 32 (with a badge) or
    # + 12 (label only), baseline box.y + 18. A title that drifted when content was moved
    # reads as belonging to nothing.
    rects = container_rects(root)
    clouds = [r for r in rects for i in icons
              if i.get("ref", "").startswith("group/AWS-Cloud-logo") and abs(i["box"][0] - r[0]) <= 1
              and abs(i["box"][1] - r[1]) <= 1]
    for i in icons:
        if i.get("ref") in OUTSIDE_CLOUD:
            x0, y0, x1, y1 = i["box"]
            for r in clouds:
                if r[0] <= x0 and x1 <= r[0] + r[2] and r[1] <= y0 and y1 <= r[1] + r[3]:
                    issues.append(f"OUTSIDE CLOUD   {i['ref']} at ({x0:g},{y0:g}) is inside the AWS Cloud box — "
                                  "it isn't in AWS; place it between the on-premises group and the Cloud")
                    break
    for t in texts:
        if not (t["title"] and t["fs"] in (14, 15)):
            continue
        base = 22 if t["fs"] == 15 else 18
        owners = [r for r in rects if any(abs(t["box"][0] - (r[0] + off)) <= 1 for off in (42, 32, 12))
                  and r[1] < t["y"] < r[1] + r[3]]
        if owners:
            r = max(owners, key=lambda r: r[1])
            if abs(t["y"] - (r[1] + base)) > 1:
                issues.append(f"TITLE OFFSET    {t['s']!r} sits {t['y'] - r[1]:g}px below its box top "
                              f"— a container title's baseline is box.y + {base}")
    for s in segs:
        if s.get("head"):
            (x1, y1), (x2, y2) = s["p"], s["q"]
            if 0 < math.hypot(x2 - x1, y2 - y1) < MIN_ARROW:
                issues.append(f"SHORT ARROW     {fmt(s)} is under {MIN_ARROW}px — widen the gap so the arrow "
                              "has a visible shaft")
    for s in segs:
        if s["kind"] != "connector":
            continue
        (x1, y1), (x2, y2) = s["p"], s["q"]
        for b in segs:
            if b["kind"] != "border":
                continue
            (bx1, by1), (bx2, by2) = b["p"], b["q"]
            if abs(x1 - x2) < 0.5 and abs(bx1 - bx2) < 0.5:      # both vertical
                d, lo, hi = abs(x1 - bx1), max(min(y1, y2), min(by1, by2)), min(max(y1, y2), max(by1, by2))
            elif abs(y1 - y2) < 0.5 and abs(by1 - by2) < 0.5:    # both horizontal
                d, lo, hi = abs(y1 - by1), max(min(x1, x2), min(bx1, bx2)), min(max(x1, x2), max(bx1, bx2))
            else:
                continue
            if d < HUG_CLEAR and hi - lo > 20 and not masked((min(x1, bx1), lo, max(x1, bx1) + 0.1, hi), s["o"], masks):
                where = "on top of" if d == 0 else f"{d:g}px from"
                issues.append(f"LINE HUGS BORDER {fmt(s)} runs {where} the border {fmt(b)} — "
                              f"keep {HUG_CLEAR}px or more")
                break
    for t in texts:
        if t["title"] and CIDR_IN.search(t["s"]):
            issues.append(f"CIDR IN TITLE   {t['s']!r} — put the CIDR on its own 12px {CIDR_COLOR.upper()} line "
                          "under the title (same x, baseline 16px lower)")
        if BARE_CIDR.match(t["s"]) and not is_node_label(t, icons):
            titles = [h for h in texts if h["title"] and h is not t]
            under = any(abs(h["box"][0] - t["box"][0]) <= 1 and 14 <= t["y"] - h["y"] <= 18 for h in titles)
            if not under:
                near = min(titles, key=lambda h: abs(h["box"][0] - t["box"][0]) + abs(t["y"] - h["y"] - 16),
                           default=None)
                if near and abs(near["box"][0] - t["box"][0]) <= 8 and 8 <= t["y"] - near["y"] <= 24:
                    issues.append(f"CIDR OFF HEADER {t['s']!r} is {t['box'][0] - near['box'][0]:+g}px off "
                                  f"the x of {near['s']!r} and {t['y'] - near['y']:g}px below it — "
                                  "same x as the title, baseline 16px lower")
                else:
                    issues.append(f"CIDR OFF HEADER {t['s']!r} floats inside a box — put it right under its "
                                  "container's title and move whatever crosses the header instead")
            elif not t["fill"]:
                issues.append(f"CIDR COLOR      {t['s']!r} has no fill attribute (inherits) — set "
                              f'fill="{CIDR_COLOR.upper()}"')
            elif t["fill"] != CIDR_COLOR:
                issues.append(f"CIDR COLOR      {t['s']!r} under a title is {CIDR_COLOR.upper()} (squid ink), "
                              f"not {t['fill'].upper()}")
        if CIRCLED.search(t["s"]):
            issues.append(f"GLYPH STEP      {t['s']!r} uses circled digits; draw step badges instead")
        x0, y0, x1, y1 = t["box"]
        if cw and ch and (x0 < 0 or y0 < 0 or x1 > cw or y1 > ch):
            issues.append(f"OFF CANVAS      {t['s']!r} runs past the {cw:g} × {ch:g} canvas")
        if t["fs"] < MIN_FONT:
            issues.append(f"SMALL TEXT      {t['fs']:g}px  {t['s']!r}")
        b = shrink(t["box"])
        for s in segs:
            if seg_hits_box(s["p"], s["q"], b) and not masked(t["box"], s["o"], masks):
                issues.append(f"LINE OVER TEXT  {s['kind']} {fmt(s)} crosses {t['s']!r}")
                break
        else:
            if t["title"]:
                x0, _, x1, y1 = t["box"]
                cidr = next((c for c in texts if BARE_CIDR.match(c["s"]) and abs(c["box"][0] - x0) <= 1
                             and 14 <= c["y"] - t["y"] <= 18), None)
                if cidr:
                    y1 = cidr["box"][3]
                below = (x0, y1, x1, y1 + HEADER_CLEAR)
                hit = next((s for s in segs if s["kind"] == "border" and s["p"][1] == s["q"][1]
                            and seg_hits_box(s["p"], s["q"], below)), None)
                if hit:
                    start = 46 if cidr else 30
                    issues.append(f"HEADER CLEARANCE {t['s']!r} has a box border {fmt(hit)} less than "
                                  f"{HEADER_CLEAR}px below it{' (under its CIDR line)' if cidr else ''} — "
                                  f"start nested boxes at container.y + {start}")
                    continue
            # A title sits at a fixed distance from its own container's border; every
            # other label (node, caption, connector label, legend row) keeps the full 8px.
            clear = BORDER_CLEAR if t["title"] else LABEL_CLEAR
            near = expand(t["box"], clear)
            for s in segs:
                if (s["kind"] == "border" and seg_hits_box(s["p"], s["q"], near)
                        and not masked(t["box"], s["o"], masks)):
                    issues.append(f"TEXT AT BORDER  {t['s']!r} is within {clear}px of the border "
                                  f"{fmt(s)} — give it room")
                    break
    connectors = [s for s in segs if s["kind"] == "connector"]
    for t in texts:
        # Node and header labels aren't connector labels, so a line skimming them is a
        # near miss, not a label sitting on its own line.
        if not (t["header"] or is_node_label(t, icons)):
            continue
        b = expand(t["box"], LINE_CLEAR)
        for s in connectors:
            if seg_hits_box(s["p"], s["q"], b) and not seg_hits_box(s["p"], s["q"], shrink(t["box"])) \
                    and not masked(t["box"], s["o"], masks):
                issues.append(f"LINE NEAR TEXT  connector {fmt(s)} passes within {LINE_CLEAR}px of {t['s']!r}")
                break
    for t in texts:
        near = expand(t["box"], LABEL_REACH)
        if not is_node_label(t, icons) and any(seg_hits_box(s["p"], s["q"], near) for s in connectors):
            for phrase, ref in services_in_label(t["s"]):
                issues.append(f"SERVICE AS TEXT {phrase!r} in connector label {t['s']!r} has an "
                              f"official icon ({ref}) — draw it as a node")
    for i in icons:
        b = shrink(i["box"], 2.0)
        for s in segs:
            if i.get("dot") and through(i["dot"], s):
                continue
            if seg_hits_box(s["p"], s["q"], b) and not masked(i["box"], s["o"], masks):
                what = "badge" if i["badge"] else "icon"
                issues.append(f"LINE OVER ICON  {s['kind']} {fmt(s)} crosses the {what} at "
                              f"({i['box'][0]:g},{i['box'][1]:g})")
                break
    nodes = [i for i in icons if not i["badge"]]
    for g in (i for i in icons if i["badge"] and not i.get("dot") and i["box"][2] - i["box"][0] > 21):
        for n in nodes:
            if boxes_overlap(expand(g["box"], ICON_CLEAR), n["box"]) and not boxes_overlap(g["box"], n["box"]):
                issues.append(f"BADGE NEAR ICON group badge at ({g['box'][0]:g},{g['box'][1]:g}) is within "
                              f"{ICON_CLEAR}px of the icon at ({n['box'][0]:g},{n['box'][1]:g})")
                break
    for t in texts:
        # A header sits in its container's header row, so the first icon below it only
        # needs HEADER_ICON_CLEAR; every other label keeps ICON_CLEAR from icons it
        # doesn't label.
        clear = HEADER_ICON_CLEAR if t["title"] else ICON_CLEAR
        for n in nodes:
            x0, y0, x1, y1 = n["box"]
            own = abs(t["cx"] - (x0 + x1) / 2) <= 3 and y1 < t["y"] <= y1 + 44
            if not own and boxes_overlap(expand(t["box"], clear), n["box"]) \
                    and not boxes_overlap(shrink(t["box"]), shrink(n["box"], 2.0)):
                issues.append(f"TEXT NEAR ICON  {t['s']!r} is within {clear}px of the icon at "
                              f"({x0:g},{y0:g})")
                break
    for a_i, a in enumerate(texts):
        for b in texts[a_i + 1:]:
            if boxes_overlap(shrink(a["box"]), shrink(b["box"])):
                issues.append(f"TEXT OVERLAP    {a['s']!r} and {b['s']!r}")
            elif (min(a["box"][3], b["box"][3]) - max(a["box"][1], b["box"][1]) > 0  # side by side
                  and boxes_overlap(expand(a["box"], TEXT_GAP), b["box"])):
                issues.append(f"TEXT TOO CLOSE  {a['s']!r} and {b['s']!r} are less than {TEXT_GAP}px apart")
        for i in icons:
            if not i["badge"] and boxes_overlap(shrink(a["box"]), shrink(i["box"], 2.0)):
                issues.append(f"TEXT OVERLAP    {a['s']!r} overlaps the icon at ({i['box'][0]:g},{i['box'][1]:g})")
    return issues


def fmt(s):
    (x1, y1), (x2, y2) = s["p"], s["q"]
    return f"({x1:g},{y1:g})→({x2:g},{y2:g})"


def main():
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(1)
    issues = check(sys.argv[1])
    for line in issues:
        print(line)
    if issues:
        sys.exit(f"{len(issues)} layout issue(s); move the label, line or container and re-run.")
    print("Layout OK")


if __name__ == "__main__":
    main()
