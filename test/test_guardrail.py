from veritas.nodes.guardrail import guardrail_node

CASES = [
    ("Does it work the same way for women?", True),
    ("What did they say about that?", True),
    ("How much does it cost?", True),
    ("When was Google launched?", False),
    ("What are the health benefits of intermittent fasting?", False),
    ("Which is the longest river, the Nile or the Amazon?", False),
    ("Why is the sky blue?", False),
]

passed = 0
for question, expect_unclear in CASES:
    result = guardrail_node({"question": question})
    got_unclear = result["needs_clarification"]
    ok = got_unclear == expect_unclear
    passed += ok
    print("PASS" if ok else "FAIL", "-", question)
    if got_unclear:
        print("      asks:", result["answer"])
print(f"{passed}/{len(CASES)} passed")