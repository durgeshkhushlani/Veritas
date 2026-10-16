import os, json 
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
CHAR_LIMIT = 3000


CONTRADICTION_PROMPT = """You are fact-checking several sources that answer the same question.

Find places where two sources CONFLICT:
- they give different values for the same quantity (dates, numbers, lengths), or
- they give opposite answers to the same question (e.g. one says A is longer, another says B is longer).

Do NOT flag sources that agree, rewordings of the same fact, or a source that only mentions that a debate exists.

If there are no conflicts, return an empty array.

Return ONLY a JSON array of objects. Each object:
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
        f"[{s['url']}]\n{s['content'][:CHAR_LIMIT]}" for s in sources
    )

    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=CONTRADICTION_PROMPT.format(sources=formatted),
        config=types.GenerateContentConfig(
            temperature=0,
            response_mime_type="application/json",
        ),
    )
    contradictions = json.loads(strip_fences(response.text))

    previous = state.get("all_contradictions", [])
    seen = {(c["claim_a"], c["claim_b"]) for c in previous}
    new = [c for c in contradictions if (c["claim_a"], c["claim_b"]) not in seen]

    return {
        "contradictions": contradictions,
        "all_contradictions": previous + new,
    }