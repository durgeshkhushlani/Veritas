import streamlit.components.v1 as components

GREEN, ORANGE, GREY = "#22c55e", "#f59e0b", "#374151"
EDGE_ON, EDGE_OFF = "#22c55e", "#4b5563"

NODES = ["guardrail", "planner", "search", "fetch", "check", "refine", "writer", "stop"]

# the node that runs after each one (check is left out: it can go two ways)
NEXT = {"guardrail": "planner", "planner": "search", "search": "fetch",
        "fetch": "check", "refine": "search"}

GRAPH_HEIGHT = 335
W, H = 96, 40  # node size

POS = {
    "guardrail": (10, 20), "planner": (150, 20), "search": (290, 20), "fetch": (430, 20),
    "refine": (290, 145), "check": (430, 145),
    "stop": (290, 270), "writer": (430, 270),
}
LABELS = {"stop": "end"}
DECISIONS = {"guardrail", "check"}


def _top(n):    x, y = POS[n]; return (x + W / 2, y)
def _bottom(n): x, y = POS[n]; return (x + W / 2, y + H)
def _left(n):   x, y = POS[n]; return (x, y + H / 2)
def _right(n):  x, y = POS[n]; return (x + W, y + H / 2)


def _line(p, q):
    return f"M{p[0]} {p[1]} L{q[0]} {q[1]}"


# (from, to, path, dashed, label, label_x, label_y, label_anchor)
EDGES = [
    ("guardrail", "planner", _line(_right("guardrail"), _left("planner")), False, "clear", 128, 34, "middle"),
    ("planner", "search", _line(_right("planner"), _left("search")), False, "", 0, 0, "middle"),
    ("search", "fetch", _line(_right("search"), _left("fetch")), False, "", 0, 0, "middle"),
    ("fetch", "check", _line(_bottom("fetch"), _top("check")), False, "", 0, 0, "middle"),
    ("check", "refine", _line(_left("check"), _right("refine")), False, "conflict", 408, 159, "middle"),
    ("check", "writer", _line(_bottom("check"), _top("writer")), False, "no conflict", 470, 232, "end"),
    ("writer", "stop", _line(_left("writer"), _right("stop")), False, "", 0, 0, "middle"),
    ("refine", "search", _line(_top("refine"), _bottom("search")), True, "retry", 330, 108, "end"),
    ("guardrail", "stop", "M58 60 V290 H284", True, "unclear", 66, 175, "start"),
]


def _edge_on(a, b, done, running):
    if (a, b) == ("guardrail", "stop"):
        return "stop" in done and "writer" not in done
    return a in done and (b in done or b == running)


def _svg(done, running):
    parts = [
        '<svg viewBox="0 0 536 320" width="100%" xmlns="http://www.w3.org/2000/svg">',
        "<defs>",
        f'<marker id="on" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0 L10 5 L0 10 z" fill="{EDGE_ON}"/></marker>',
        f'<marker id="off" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0 L10 5 L0 10 z" fill="{EDGE_OFF}"/></marker>',
        "</defs>",
    ]
    for a, b, path, dashed, label, lx, ly, anchor in EDGES:
        on = _edge_on(a, b, done, running)
        color = EDGE_ON if on else EDGE_OFF
        dash = ' stroke-dasharray="5 4"' if dashed else ""
        marker = "on" if on else "off"
        parts.append(
            f'<path d="{path}" fill="none" stroke="{color}" stroke-width="2"{dash} marker-end="url(#{marker})"/>'
        )
        if label:
            parts.append(
                f'<text x="{lx}" y="{ly}" fill="#9ca3af" font-size="10" text-anchor="{anchor}">{label}</text>'
            )
    for n in NODES:
        x, y = POS[n]
        if n == running:
            fill, cls = ORANGE, ' class="pulse"'
        elif n in done:
            fill, cls = GREEN, ""
        else:
            fill, cls = GREY, ""
        stroke = ' stroke="#c7d2fe" stroke-width="1.5"' if n in DECISIONS else ""
        parts.append(f'<g{cls}>')
        parts.append(f'<rect x="{x}" y="{y}" width="{W}" height="{H}" rx="11" fill="{fill}"{stroke}/>')
        parts.append(
            f'<text x="{x + W / 2}" y="{y + H / 2 + 5}" fill="#fff" font-size="13" '
            f'font-weight="600" text-anchor="middle">{LABELS.get(n, n)}</text>'
        )
        parts.append("</g>")
    parts.append("</svg>")
    return "".join(parts)


STYLE = (
    "<style>"
    "body{margin:0;background:transparent;font-family:Inter,system-ui,Arial,sans-serif;}"
    "@keyframes pulse{0%,100%{opacity:1}50%{opacity:.6}}"
    ".pulse{animation:pulse 1.1s ease-in-out infinite}"
    "</style>"
)


def legend_html():
    return f"""
<div class="legend">
<div><span class="dot" style="background:{GREEN}"></span>Finished</div>
<div><span class="dot" style="background:{ORANGE}"></span>Running next</div>
<div><span class="dot" style="background:{GREY}"></span>Not reached</div>
</div>
"""


def show_graph(box, done, running):
    html = STYLE + _svg(done, running)
    with box.container():
        components.html(html, height=GRAPH_HEIGHT)