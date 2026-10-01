from veritas.nodes.search import search_node

result = search_node({"sub_queries": ["When was Google launched?"]})

for r in result["search_results"]:
    print(r["title"], "-", r["content"])


