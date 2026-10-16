from veritas.graph import build_graph
from veritas.faithfulness import judge_faithfulness

QUESTION = "When was Google launched?"

app = build_graph()
result = app.invoke({"question": QUESTION, "retry_count": 0})

print("ANSWER:\n", result["answer"], "\n")

report = judge_faithfulness(result["answer"], result["sources"])

for c in report["claims"]:
    print(f"{c['verdict']:12} {c['claim']}")
print("\nFAITHFULNESS SCORE:", report["score"])