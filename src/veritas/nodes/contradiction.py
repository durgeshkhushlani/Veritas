import os, json 
from dotenv import load_dotenv
from google import genai

load_dotenv()
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

CONTRADICTION_PROMPT = """You are fact-checking a set of sources about the same question. 
Read the source below. Identify any factual claims that DIRECTLY CONTRADICT each other (different dates, different numbers, opposing conclusions). Minor differences in phrasing or emphasis are NOT contradictions.

If there are no real contradictions, return an empty array.

Return ONLY a JSON array of objects, no markdown fences. Each object: 
{{"claim_a": "...", "source_a": "url", "claim_b": "...", "source_b": "url"}}


SOURCES: 
{sources}
"""

def strip_fences(raw):
    raw = raw.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    return raw.strip()


def contradiction_check_node(state):
    sources = state["sources"]

    formatted = "\n\n".join(
        f"[{s['url']}]\n{s['content'][:1500]}" for s in sources
    )

    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=CONTRADICTION_PROMPT.format(sources=formatted),
    )
    contradictions = json.loads(strip_fences(response.text))
    return {"contradictions": contradictions}