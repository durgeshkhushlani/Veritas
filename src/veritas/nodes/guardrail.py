import os, json
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

GUARDRAIL_PROMPT = """You check whether a question can be answered on its own, with no earlier conversation.

A question is UNCLEAR only if it depends on something the user has not said, such as:
- a pronoun with nothing to point to ("Does it work for women?", "What did they say?")
- a reference to earlier context ("the second one", "as I mentioned")
- a missing subject ("How much does it cost?" with no product named)

A question is CLEAR if it can be searched as written, even if it is broad, odd or hard.

Return a JSON object:
{{"clear": true or false, "message": "if unclear, one short sentence asking the user to say what they mean; otherwise an empty string"}}

QUESTION: {question}
"""

def guardrail_node(state):
    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=GUARDRAIL_PROMPT.format(question=state["question"]),
        config=types.GenerateContentConfig(
            temperature=0,
            response_mime_type="application/json",
        ),
    )
    verdict = json.loads(response.text)

    if verdict["clear"]:
        return {"needs_clarification": False}

    return {"needs_clarification": True, "answer": verdict["message"]}