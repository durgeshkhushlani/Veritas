import json
from veritas.nodes.search import search_node
from veritas.nodes.fetch import fetch_and_read_node

state = {"sub_queries": ["Which is the longest river in the world, the Nile or the Amazon?"]}
state.update(search_node(state))
state.update(fetch_and_read_node(state))

with open("test/nile_sources.json", "w", encoding="utf-8") as f:
    json.dump(state["sources"], f, ensure_ascii=False)

print("saved", len(state["sources"]), "sources:")
for s in state["sources"]:
    print(" ", s["url"])