import trafilatura

def fetch_and_read_node(state):
    search_results = state["search_results"]
    sources = []

    for result in search_results: 
        url = result["url"]
        downloaded = trafilatura.fetch_url(url)

        if downloaded is None: 
            print(f"SKIPPED (fetch failed): {url}")
            continue

        text = trafilatura.extract(downloaded)

        if not text:
            print(f"SKIPPED (no extractable content): {url}")
            continue

        sources.append({
            "url": url, 
            "title": result.get("title", ""),
            "content": text
        })

    return {"sources": sources}
