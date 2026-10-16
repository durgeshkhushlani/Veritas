import streamlit as st
from veritas.graph import build_graph

st.set_page_config(page_title="Veritas", page_icon="🔎", layout="wide")

st.markdown(
    """
<style>
#MainMenu, footer {visibility: hidden;}
.block-container {padding-top: 2.5rem; max-width: 1300px;}

.title {
    font-size: 3rem; font-weight: 800; letter-spacing: -1px; margin: 0;
    background: linear-gradient(90deg, #60a5fa, #a78bfa);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}
.tagline {color: #9ca3af; margin: 0 0 1.5rem 0; font-size: 1.05rem;}

.legend {display: flex; gap: 18px; flex-wrap: wrap; margin: 4px 0 10px 0;
         color: #9ca3af; font-size: 0.85rem;}
.legend span.dot {display: inline-block; width: 10px; height: 10px;
                  border-radius: 50%; margin-right: 6px;}

div[data-testid="stTextInput"] input {
    border-radius: 12px; padding: 0.8rem 1rem; font-size: 1.05rem;
}
div.stButton > button {
    border-radius: 12px; padding: 0.55rem 1.8rem; font-weight: 600;
    background: linear-gradient(90deg, #3b82f6, #8b5cf6);
    color: white; border: none;
}
div.stButton > button:hover {filter: brightness(1.12); color: white;}
</style>
""",
    unsafe_allow_html=True,
)

NODES = ["guardrail", "planner", "search", "fetch", "check", "refine", "writer", "stop"]
EDGES = [
    ("guardrail", "planner", "clear"),
    ("guardrail", "stop", "unclear"),
    ("planner", "search", ""),
    ("search", "fetch", ""),
    ("fetch", "check", ""),
    ("check", "writer", "no conflict"),
    ("check", "refine", "conflict"),
    ("refine", "search", "retry"),
    ("writer", "stop", ""),
]
# the node that runs after each one (check is left out: it can go two ways)
NEXT = {"guardrail": "planner", "planner": "search", "search": "fetch",
        "fetch": "check", "refine": "search"}

GREEN, ORANGE, GREY = "#22c55e", "#f59e0b", "#374151"


def graph_dot(done, running):
    lines = [
        "digraph G {",
        'bgcolor="transparent";',
        "rankdir=TB; nodesep=0.45; ranksep=0.45;",
        'node [shape=box, style="rounded,filled", fontname="Helvetica", '
        'fontsize=13, fontcolor="white", penwidth=0, margin="0.25,0.12"];',
        'edge [color="#6b7280", fontcolor="#9ca3af", fontname="Helvetica", fontsize=11];',
    ]
    for n in NODES:
        if n == running:
            color = ORANGE
        elif n in done:
            color = GREEN
        else:
            color = GREY
        label = "end" if n == "stop" else n
        lines.append(f'{n} [label="{label}", fillcolor="{color}"];')
    for a, b, label in EDGES:
        lines.append(f'{a} -> {b} [label="{label}"];')
    lines.append("}")
    return "\n".join(lines)


st.markdown('<p class="title">Veritas</p>', unsafe_allow_html=True)
st.markdown(
    '<p class="tagline">Ask a question. Veritas searches, reads, and cross-checks '
    "the sources before it answers.</p>",
    unsafe_allow_html=True,
)

left, right = st.columns([1, 1], gap="large")

with left:
    question = st.text_input(
        "Question", placeholder="e.g. When was Google launched?",
        label_visibility="collapsed",
    )
    run = st.button("Search")
    with st.container(border=True):
        answer_box = st.empty()
        answer_box.caption("The answer will appear here.")

with right:
    st.markdown("#### Pipeline")
    st.markdown(
        f"""
<div class="legend">
<div><span class="dot" style="background:{GREEN}"></span>Finished</div>
<div><span class="dot" style="background:{ORANGE}"></span>Running next</div>
<div><span class="dot" style="background:{GREY}"></span>Not reached</div>
</div>
""",
        unsafe_allow_html=True,
    )
    graph_box = st.empty()
    status_box = st.empty()
    graph_box.graphviz_chart(graph_dot(set(), None))

if run and question:
    app = build_graph()
    done = set()
    needs_clarification = False
    graph_box.graphviz_chart(graph_dot(done, "guardrail"))

    for step in app.stream(
        {"question": question, "retry_count": 0},
        stream_mode="updates",
    ):
        for node_name, update in step.items():
            done.add(node_name)
            if update.get("needs_clarification"):
                needs_clarification = True
            if "answer" in update:
                answer_box.markdown(update["answer"])

            if node_name == "writer" or needs_clarification:
                done.add("stop")
                running = None
            else:
                running = NEXT.get(node_name)
            graph_box.graphviz_chart(graph_dot(done, running))

    if needs_clarification:
        status_box.warning("Needs clarification")
    else:
        status_box.success("Done")