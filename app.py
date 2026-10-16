import base64
import re
import streamlit as st
from veritas.graph import build_graph
from veritas.faithfulness import judge_faithfulness
from veritas.pipelines_view import show_graph, legend_html, NEXT

st.set_page_config(page_title="Veritas", page_icon="🔎", layout="wide")

st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Sora:wght@500;600;700;800&display=swap');

#MainMenu, footer {visibility: hidden;}
.block-container {padding-top: 4.5rem; max-width: 1300px;}

.stApp, .stApp p, .stApp label, .stApp input, .stApp button, .stApp li {
    font-family: 'Inter', sans-serif;
}
.stApp h1, .stApp h2, .stApp h3, .stApp h4 {
    font-family: 'Sora', sans-serif; letter-spacing: -0.3px;
}

.title {
    font-family: 'Sora', sans-serif;
    font-size: 2.2rem; font-weight: 800; letter-spacing: 0.22em; margin: 0;
    text-transform: uppercase;
    background: linear-gradient(90deg, #93c5fd 0%, #a78bfa 50%, #f0abfc 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    filter: drop-shadow(0 0 22px rgba(167,139,250,0.45));
}
.tagline {
    color: #9ca3af; margin: 0.3rem 0 1.2rem 0; font-size: 1rem;
}
.panel-title {
    font-family: 'Sora', sans-serif; font-weight: 600; font-size: 0.8rem;
    letter-spacing: 0.18em; text-transform: uppercase; color: #a5b4fc;
    margin: 0 0 0.8rem 0;
}
.legend {display: flex; gap: 18px; flex-wrap: wrap; margin: 0 0 6px 0;
         color: #9ca3af; font-size: 0.82rem;}
.legend span.dot {display: inline-block; width: 10px; height: 10px;
                  border-radius: 50%; margin-right: 6px;}

div[data-testid="stTextInput"] input {
    border-radius: 14px; padding: 0.8rem 1.1rem; font-size: 1.05rem;
}
div.stButton > button {
    border-radius: 14px; padding: 0.6rem 1.9rem; font-weight: 600;
    font-family: 'Sora', sans-serif; letter-spacing: 0.3px; width: 100%;
    background: linear-gradient(90deg, #3b82f6, #8b5cf6);
    color: white; border: none;
    box-shadow: 0 6px 22px rgba(99,102,241,0.35);
}
div.stButton > button:hover {filter: brightness(1.12); color: white;}
div[data-testid="stMetricValue"] {font-family: 'Sora', sans-serif;}
</style>
""",
    unsafe_allow_html=True,
)

PANEL_HEIGHT = 560

def link_citations(text, sources):
    def repl(m):
        i = int(m.group(1))
        if 1 <= i <= len(sources):
            return f"[[{i}]]({sources[i - 1]['url']})"
        return m.group(0)
    return re.sub(r"\[(\d+)\]", repl, text)


if "started" not in st.session_state:
    st.session_state.started = False

if not st.session_state.started:
    with open("assets/bg_small.jpg", "rb") as f:
        bg = base64.b64encode(f.read()).decode()

    st.markdown(
        f"""
<style>
.stApp {{
    background:
        linear-gradient(rgba(10,12,20,0.55), rgba(10,12,20,0.85)),
        url("data:image/jpeg;base64,{bg}") center / cover no-repeat fixed;
}}
.hero {{text-align: center; padding-top: 18vh;}}
.hero .title {{font-size: 5.2rem; letter-spacing: 0.28em;}}
.hero .tagline {{font-size: 1.25rem; margin-bottom: 1.2rem;}}
.chips {{display: flex; gap: 10px; justify-content: center; flex-wrap: wrap; margin: 1.2rem 0 2.2rem 0;}}
.chips span {{padding: 7px 16px; border-radius: 999px; font-size: 0.85rem; color: #c7d2fe;
             border: 1px solid rgba(165,180,252,0.35); background: rgba(99,102,241,0.14);
             backdrop-filter: blur(6px);}}
</style>
<div class="hero">
<p class="title">Veritas</p>
<p class="tagline">A research assistant that checks its sources before it answers.</p>
<div class="chips">
<span>LangGraph</span><span>Multi-agent</span><span>Cross-verified sources</span>
<span>Cited answers</span><span>Self-correcting retries</span>
</div>
</div>
""",
        unsafe_allow_html=True,
    )

    _, btn, _ = st.columns([2, 1, 2])
    with btn:
        if st.button("Continue →", use_container_width=True):
            st.session_state.started = True
            st.rerun()
    st.stop()

with open("assets/bg2.jpg", "rb") as f:
    bg2 = base64.b64encode(f.read()).decode()

st.markdown(
    f"""
<style>
.stApp {{
    background:
        linear-gradient(rgba(10,12,20,0.78), rgba(10,12,20,0.9)),
        url("data:image/jpeg;base64,{bg2}") center / cover no-repeat fixed;
}}
div[data-testid="stVerticalBlockBorderWrapper"] {{
    background: rgba(10,12,20,0.55);
    backdrop-filter: blur(8px);
    border-radius: 16px;
}}
</style>
""",
    unsafe_allow_html=True,
)

# ---------- header + question row ----------
st.markdown('<p class="title">Veritas</p>', unsafe_allow_html=True)
st.markdown(
    '<p class="tagline">Ask a question. Veritas searches, reads, and cross-checks '
    "the sources before it answers.</p>",
    unsafe_allow_html=True,
)

q_col, b_col = st.columns([6, 1], gap="small")
with q_col:
    question = st.text_input(
        "Question", placeholder="e.g. When was Google launched?",
        label_visibility="collapsed",
    )
with b_col:
    run = st.button("Search")

st.write("")

# ---------- two equal halves ----------
left, right = st.columns(2, gap="large")

with left:
    with st.container(border=True, height=PANEL_HEIGHT):
        st.markdown('<p class="panel-title">Answer</p>', unsafe_allow_html=True)
        answer_box = st.empty()
        answer_box.caption("The answer will appear here.")
        st.write("")
        score_box = st.empty()
        extras_box = st.empty()

with right:
    with st.container(border=True, height=PANEL_HEIGHT):
        st.markdown('<p class="panel-title">Pipeline</p>', unsafe_allow_html=True)
        st.markdown(legend_html(), unsafe_allow_html=True)  
        graph_box = st.empty()
        status_box = st.empty()
        show_graph(graph_box, set(), None)

# ---------- run ----------
if run and question:
    app = build_graph()
    done = set()
    needs_clarification = False
    sources = []
    final_answer = ""
    show_graph(graph_box, done, "guardrail")
    
    for step in app.stream(
        {"question": question, "retry_count": 0},
        stream_mode="updates",
    ):
        for node_name, update in step.items():
            done.add(node_name)
            if update.get("needs_clarification"):
                needs_clarification = True
            if node_name == "fetch":
                sources = update["sources"]
            if "answer" in update:
                final_answer = update["answer"]
                answer_box.markdown(link_citations(final_answer, sources))

            if node_name == "writer" or needs_clarification:
                done.add("stop")
                running = None
            else:
                running = NEXT.get(node_name)
            show_graph(graph_box, done, running)
            
    if needs_clarification:
        status_box.warning("Needs clarification")
    else:
        status_box.success("Done")
        if final_answer and sources:
            score_box.caption("Checking the answer against its sources...")
            report = judge_faithfulness(final_answer, sources)

            with score_box.container():
                if report["score"] is None:
                    st.caption("Faithfulness: no claims to check")
                else:
                    st.metric("Faithfulness", f"{report['score']:.0%}")

            icons = {"supported": "✅", "partial": "🟡", "unsupported": "❌", "uncited": "⚪"}
            with extras_box.container():
                with st.expander("Sources"):
                    for i, s in enumerate(sources, start=1):
                        st.markdown(f"{i}. [{s['title'] or s['url']}]({s['url']})")
                with st.expander("Claim by claim"):
                    for c in report["claims"]:
                        st.markdown(f"{icons.get(c['verdict'], '•')} {c['claim']}")