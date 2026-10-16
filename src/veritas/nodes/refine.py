import os, json
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

REFINE_PROMPT = """Web sources disagreed on a question. Write 2 NEW search queries
likely to find authoritative sources (official surveys, scientific papers,
encyclopedias) that could settle the disagreement. Do not repeat the previous queries.

QUESTION: {question}
PREVIOUS QUERIES: {previous}
DISAGREEMENTS: {contradictions}

Return a JSON array of strings."""

def refine_node(state):
    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=REFINE_PROMPT.format(
            question=state["question"],
            previous=state["sub_queries"],
            contradictions=json.dumps(state["contradictions"]),
        ),
        config=types.GenerateContentConfig(
            temperature=0, response_mime_type="application/json"
        ),
    )
    return {
        "sub_queries": json.loads(response.text),
        "retry_count": state.get("retry_count", 0) + 1,
    }