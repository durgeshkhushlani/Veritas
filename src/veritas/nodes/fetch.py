import trafilatura
import requests
from concurrent.futures import ThreadPoolExecutor

HEADERS = {"User-Agent": "Mozilla/5.0 (Veritas research bot)"}
TIMEOUT = (5, 10) # (connect, read) seconds

def _fetch_one(result):
    url = result["url"]
    try:
        resp= requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        resp.raise_for_status()
    except requests.RequestException as e:
        print(f"SKIPPED (fetch failed): {url} -> {type(e).__name__}", flush=True)
        return None

    text = trafilatura.extract(resp.text)
    if not text:
        print(f"SKIPPED (no extractable content): {url}", flush=True)
        return None

    return {"url": url, "title": result.get("title", ""), "content": text}
  
def fetch_and_read_node(state):
    existing = state.get("sources", [])
    seen = {s["url"] for s in existing}

    unique = []
    for r in state["search_results"]:
        if r["url"] not in seen:
            seen.add(r["url"])
            unique.append(r)

    with ThreadPoolExecutor(max_workers=5) as pool:
        fetched = list(pool.map(_fetch_one, unique))

    return {"sources": existing + [s for s in fetched if s]}