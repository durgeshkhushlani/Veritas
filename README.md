# Veritas

Veritas is a multi-agent research assistant that answers questions by searching the web, reading real source pages, and cross-verifying claims across multiple sources before writing a final answer, with every claim traced back to a numbered citation. Built with LangGraph.

## How it works

```
question → planner → search → fetch → check ─┬─ conflict & retries left → refine → search
                                              └─ otherwise → writer → cited answer
```

- **planner:** splits a question into 1-3 focused search queries (a simple fact stays one query)
- **search:** Tavily web search
- **fetch:** downloads pages in parallel with timeouts, skips dead or blocked links, accumulates sources across retries
- **check:** an LLM flags sources that give conflicting values or opposite answers
- **refine:** on a conflict, writes new queries aimed at the disagreement (max 2 retries)
- **writer:** answers using only the numbered sources, citing every claim as `[n]`, and states disagreements openly

## Status

- [x] Core pipeline: planner, search, fetch, contradiction check, refine loop, writer
- [x] Retry cap verified (stops after 2 retries)
- [ ] Guardrail for unresolved references ("it", "they")
- [ ] Streamlit UI with clickable citations
- [ ] Faithfulness evaluation harness

## Out of scope (v1)

- Multi-turn conversations (planned for v1.1)
- Non-English queries
- PDF or image input

## Setup

```bash
uv sync
```

Create a `.env` file:

```
GEMINI_API_KEY=your-key
TAVILY_API_KEY=your-key
```

Run the graph:

```bash
uv run python test/test_graph.py
```

## Known issues

Failures found while building, with causes and fixes, are logged in [FAILURES.md](FAILURES.md).