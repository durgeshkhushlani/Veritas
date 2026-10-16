from veritas.nodes.search import search_node
from veritas.nodes.fetch import fetch_and_read_node
from veritas.nodes.contradiction import contradiction_check_node

state = {"sub_queries": ["Which is the longest river in the world, the Nile or the Amazon?"]}
state.update(search_node(state))
state.update(fetch_and_read_node(state))

print("sources fetched:", [s["url"] for s in state["sources"]])

all_flags = contradiction_check_node(state)["contradictions"]
print("ALL SOURCES ->", len(all_flags), "flagged")

pair = [s for s in state["sources"] if "nationalgeographic" in s["url"] or "atlas.co" in s["url"]]
pair_flags = contradiction_check_node({"sources": pair})["contradictions"]
print("PAIR ONLY (", len(pair), "sources ) ->", len(pair_flags), "flagged")