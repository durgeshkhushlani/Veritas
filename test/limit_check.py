import veritas.nodes.contradiction as c
from veritas.nodes.search import search_node
from veritas.nodes.fetch import fetch_and_read_node

state = {"sub_queries": ["Which is the longest river in the world, the Nile or the Amazon?"]}
state.update(search_node(state))
state.update(fetch_and_read_node(state))
print("sources:", [s["url"] for s in state["sources"]])

for limit in [1500, 3000, 30000]:
    c.CHAR_LIMIT = limit
    counts = [len(c.contradiction_check_node(state)["contradictions"]) for _ in range(5)]
    print(f"limit {limit}: {counts}  (empty: {counts.count(0)}/5)")