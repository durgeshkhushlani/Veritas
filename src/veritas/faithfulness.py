import os, re, json
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

CHAR_LIMIT = 3000  # same text the writer saw

JUDGE_PROMPT = """You are checking whether an answer is faithful to its numbered sources.

You are checking whether an answer is faithful to its numbered sources.

Split the ANSWER into ATOMIC claims: each claim states exactly ONE fact, such as one
date, one number, or one name. If a sentence contains several facts, make one claim
per fact. Every sentence of the answer must be covered, including the first one.
Copy each claim from the answer as written, INCLUDING the [n] citation markers
that apply to it. Do not add citation markers that are not in the answer.

For each claim, judge it ONLY against the source(s) named by its [n] markers,
never against your own knowledge:
- "supported": the cited source clearly states this
- "partial": the cited source states only part of it, or something close
- "unsupported": the cited source does not say this, or says something different

If a claim has no [n] marker, give it the verdict "unsupported".

Return a JSON array. Each item:
{{"claim": "Google was founded in 1998 [1].", "verdict": "supported"}}

ANSWER:
{answer}

SOURCES:
{sources}
"""


def judge_faithfulness(answer, sources):
    formatted = "\n\n".join(
        f"[{i}] {s['url']}\n{s['content'][:CHAR_LIMIT]}"
        for i, s in enumerate(sources, start=1)
    )
    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=JUDGE_PROMPT.format(answer=answer, sources=formatted),
        config=types.GenerateContentConfig(
            temperature=0,
            response_mime_type="application/json",
        ),
    )
    claims = json.loads(response.text)

    for c in claims:
        c["cited"] = [int(n) for n in re.findall(r"\[(\d+)\]", c["claim"])]
        if not c["cited"]:
            c["verdict"] = "uncited"

    supported = sum(1 for c in claims if c["verdict"] == "supported")
    score = supported / len(claims) if claims else None
    return {"score": score, "claims": claims}