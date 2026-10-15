from veritas.graph import build_graph

app = build_graph()

for step in app.stream(
    {"question": "When was Google launched?", "retry_count": 0},
    stream_mode="updates",
):
    for node_name, update in step.items():
        print(f"done {node_name} done -> keys: {list(update.keys())}", flush=True)