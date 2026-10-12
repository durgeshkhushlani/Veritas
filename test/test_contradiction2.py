from veritas.nodes.contradiction import contradiction_check_node

fake_sources = [
    {"url": "https://a.com", "title": "A", "content": "Google was launched in 1998 by Larry Page and Sergey Brin."},
    {"url": "https://b.com", "title": "B", "content": "Google was launched in 2001 by Larry Page and Sergey Brin."},
]

print(contradiction_check_node({"sources": fake_sources}))