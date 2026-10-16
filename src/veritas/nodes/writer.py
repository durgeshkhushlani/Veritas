import os 
from dotenv import load_dotenv 
from google import genai 

load_dotenv()
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

WRITER_PROMPT = """Answer the question using ONLY the numbered sources below. 

Rules: 
-Cite every factual claim with its source number in square bracket like [1] or [2][3].
-Do not state anything that is not support by the sources. 
-If the sources contradict each other, say so explicitlyy and attribute each version to its source. 
-If the sources do not contain the answer, say you could not find it. 
-Be concise. Use Markdown. 
-Only flag claims that give different values for the SAME quantity. Do not flag differing opinions, history of a debate, or different measurement methods unless the values conflict

QUESTION: {question}

SOURCES:
{sources}

KNOWN CONTRADICTIONS:
{contradictions}
"""

def writer_node(state):
    sources = state["sources"]

    formatted_sources = "\n\n".join(
        f"[{i}] {s['title']} ({s['url']})\n{s['content'][:3000]}"
        for i, s in enumerate(sources, start=1)
    )

    contradictions = state.get("all_contradictions") or "None found."

    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=WRITER_PROMPT.format(
            question=state["question"],
            sources= formatted_sources,
            contradictions=contradictions,
        ),
    )

    return {"answer": response.text.strip()}
