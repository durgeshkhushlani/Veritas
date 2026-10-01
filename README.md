# Veritas

Veritas is a multi-agent research assistant that answers questions by searching the web, reading real source pages, and cross-verifying claims across multiple sources before writing a final answer — every claim traced back to its citation. Built with LangGraph for orchestration.

## Features (v1)

- Answers general, open-domain questions (no topic restriction)
- Decomposes each question into focused sub-queries before searching
- Retrieves and reads up to 5 sources per question
- Cross-checks claims across sources and flags contradictions, re-searching when needed
- Produces a cited, markdown-formatted answer rendered on a Streamlit UI
- Evaluated for faithfulness — verifies every claim in the answer traces back to a source
- Guardrail for ambiguous questions (unresolved references like "it" / "they") with a clarification prompt instead of a blind answer

