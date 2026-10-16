import json
from veritas.nodes.contradiction import contradiction_check_node

with open("test/nile_sources.json", encoding="utf-8") as f:
    sources = json.load(f)

print("sources:", [s["url"] for s in sources])

counts = [len(contradiction_check_node({"sources": sources})["contradictions"]) for _ in range(10)]
print("flag counts over 10 runs:", counts)
print("empty runs:", counts.count(0), "/ 10")