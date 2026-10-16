from veritas.nodes.search import search_node
from veritas.nodes.fetch import fetch_and_read_node
from veritas.nodes.contradiction import contradiction_check_node

state = {"sub_queries": ["Which is the longest river in the world, the Nile or the Amazon?"]}
state.update(search_node(state))
state.update(fetch_and_read_node(state))
print("sources:", [s["url"] for s in state["sources"]])

counts = [len(contradiction_check_node(state)["contradictions"]) for _ in range(10)]
print("flag counts over 10 runs:", counts)
print("empty runs:", counts.count(0), "/ 10")