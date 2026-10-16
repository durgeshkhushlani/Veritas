from veritas.faithfulness import judge_faithfulness

def src(url, text):
    return {"url": url, "title": url, "content": text}

S1 = src("a", "Google was founded in September 1998 by Larry Page and Sergey Brin.")
S2 = src("b", "The Amazon River discharges more water than any other river.")

CASES = [
    ("supported claim", "Google was founded in 1998 [1].", [S1], {"supported"}),
    ("wrong fact", "Google was founded in 2001 [1].", [S1], {"unsupported"}),
    ("wrong source cited", "Google was founded in 1998 [2].", [S1, S2], {"unsupported"}),
    ("no citation", "Google was founded in 1998.", [S1], {"uncited"}),
    ("half and half", "Google was founded in 1998 [1]. It was founded by three people [1].", [S1], {"supported", "unsupported"}),
]

passed = 0
for name, answer, sources, expected in CASES:
    result = judge_faithfulness(answer, sources)
    got = {c["verdict"] for c in result["claims"]}
    ok = got == expected
    passed += ok
    print("PASS" if ok else "FAIL", "-", name, "| score:", result["score"], "| verdicts:", got)
    print("      raw:", result["claims"])
print(f"{passed}/{len(CASES)} passed")