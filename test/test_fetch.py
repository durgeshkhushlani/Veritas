from veritas.nodes.search import search_node
from veritas.nodes.fetch import fetch_and_read_node

search_result = search_node({"sub_queries": ["When was Google launched?"]})
fetch_result = fetch_and_read_node(search_result)

for s in fetch_result["sources"]:
    print(s["url"])
    print(s["content"][:200])
    print("---")
