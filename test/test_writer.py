from veritas.nodes.search import search_node
from veritas.nodes.fetch import fetch_and_read_node
from veritas.nodes.writer import writer_node

state = {"question": "When was Google launched?", "sub_queries": ["When was Google launched?"]}
state.update(search_node(state))
state.update(fetch_and_read_node(state))
state["contradictions"] = []



print(writer_node(state)["answer"])


print("\n--- SOURCES ---")
for i, s in enumerate(state["sources"], start=1):
    print(f"[{i}] {s['title']}\n    {s['url']}")
