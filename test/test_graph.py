from veritas.graph import build_graph

app = build_graph()

for step in app.stream(
    {"question": "Which is the longest river in the world, the Nile or the Amazon?", "retry_count": 0},
    stream_mode="updates",
):
    for node_name, update in step.items():
        if node_name == "refine":
            print(f"\n>>> RETRY {update['retry_count']} <<<  new queries: {update['sub_queries']}", flush=True)
        elif node_name == "fetch":
            print(f"✔ fetch done -> {len(update['sources'])} sources total", flush=True)
        elif node_name == "check":
            print(f"✔ check done -> {len(update['contradictions'])} contradictions", flush=True)
        elif node_name == "writer":
            print("✔ writer done\n")
            print(update["answer"])
        else:
            print(f"✔ {node_name} done", flush=True)