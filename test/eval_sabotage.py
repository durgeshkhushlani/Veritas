from veritas.graph import build_graph
from veritas.faithfulness import judge_faithfulness

app = build_graph()
result = app.invoke({"question": "When was Google launched?", "retry_count": 0})
answer, sources = result["answer"], result["sources"]

good = judge_faithfulness(answer, sources)
print("REAL answer score:", good["score"])

bad_answer = answer.replace("1998", "2003")
bad = judge_faithfulness(bad_answer, sources)
print("SABOTAGED answer score:", bad["score"])
for c in bad["claims"]:
    print(f"{c['verdict']:12} {c['claim']}")