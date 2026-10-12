from veritas.nodes.search import search_node
from veritas.nodes.fetch import fetch_and_read_node
from veritas.nodes.contradiction import contradiction_check_node

search_result = search_node({"sub_queries": ["When was Google launched"]})
fetch_result = fetch_and_read_node(search_result)
contradiction_result = contradiction_check_node(fetch_result)

print(contradiction_result["contradictions"])