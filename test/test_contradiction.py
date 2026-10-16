from veritas.nodes.contradiction import contradiction_check_node

def src(url, text):
    return {"url": url, "title": url, "content": text}

CASES = [
    ("should flag: different dates", True, [
        src("a", "Google was launched in 1998."),
        src("b", "Google was launched in 2001.")]),
    ("should flag: opposite answers", True, [
        src("a", "The Nile is the longest river, at 6,650 km."),
        src("b", "The Amazon is the longest river, at 6,800 km.")]),
    ("should NOT flag: agreement", False, [
        src("a", "Google was founded in 1998 by Page and Brin."),
        src("b", "Larry Page and Sergey Brin launched Google in 1998.")]),
    ("should NOT flag: same fact, different wording", False, [
        src("a", "Mount Everest is 8,849 metres tall."),
        src("b", "Everest stands about 8,849 m high.")]),
    ("should flag: same quantity, different values", True, [
        src("a", "The Nile is about 6,650 km long."),
        src("b", "The Nile is about 6,853 km long.")]),
    ("should NOT flag: mentions a debate, no conflicting values", False, [
        src("a", "Geographers have long debated which river is longest."),
        src("b", "Measuring river length depends on where you place the source.")]),
    ("should flag: real nile/amazon conflict", True, [
        src("a", "The Amazon is 4,225 miles (6,800 kilometers) long. The Nile stretches 4,160 miles (6,695 kilometers)."),
        src("b", "1. Nile River – 6,650 km ... 2. Amazon River – 6,575 km")]),
]

passed = 0
for name, expected, sources in CASES:
    got = bool(contradiction_check_node({"sources": sources})["contradictions"])
    ok = got == expected
    passed += ok
    print("PASS" if ok else "FAIL", "-", name)
print(f"{passed}/{len(CASES)} passed")