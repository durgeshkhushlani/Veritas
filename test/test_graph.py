from veritas.graph import build_graph

app = build_graph()

for step in app.stream(
    {"question": "Which is the longest river in the world, the Nile or the Amazon?", "retry_count": 0},
    stream_mode="updates",
):
    for node_name, update in step.items():
        print(f"✔ {node_name} done", flush=True)
        if node_name == "fetch":
            for s in update["sources"]:
                c = s["content"]
                print(s["url"], "| length:", len(c), "| 6,695 at:", c.find("6,695"), "| 6,575 at:", c.find("6,575"), flush=True)
        if node_name == "check":
            print("   contradictions:", update["contradictions"], flush=True)