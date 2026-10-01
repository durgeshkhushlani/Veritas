import os, json 
from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

PLANNER_PROMPT = """You are a research planning assistant. 

Given a user's question, decide if it needs to be broken into mulitple search angles or its already a single , atomic question.

Rules: 
- if the question asks about ONE simple fact (a date, a name, a number), return it as a single sub-query, unchanged.
- if the question has multiple distinct angles (cause, effects, comparisons, pros/cons), breaak it into 2-3 focused sub-queries.
- Each sub-query should be a good web search query, not a full sentence. 

Return ONLY a JSON array of strings. No markdown fences.

Question: {question}

"""

def strip_fences(raw):
    raw = raw.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw=raw[4:]
    return raw.strip()

def planner_node(state):
    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=PLANNER_PROMPT.format(question=state["question"]),
    )

    sub_queries = json.loads(strip_fences(response.text))
    return {"sub_queries": sub_queries}


