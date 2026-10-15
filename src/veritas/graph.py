from langgraph.graph import StateGraph, START, END
from veritas.state import ResearchState
from veritas.nodes.planner import planner_node
from veritas.nodes.search import search_node
from veritas.nodes.fetch import fetch_and_read_node
from veritas.nodes.contradiction import contradiction_check_node
from veritas.nodes.writer import writer_node

MAX_RETRIES = 2

def bump_retry(state):
    return {"retry_count": state.get("retry_count", 0) + 1}

def route_after_check(state):
    if state["contradictions"] and state.get("retry_count", 0) < MAX_RETRIES:
        return "retry"
    return "write"

def build_graph(): 
    g = StateGraph(ResearchState)

    g.add_node("planner", planner_node)
    g.add_node("search", search_node)
    g.add_node("fetch", fetch_and_read_node)
    g.add_node("check", contradiction_check_node)
    g.add_node("bump_retry", bump_retry)
    g.add_node("writer", writer_node)

    g.add_edge(START, "planner")
    g.add_edge("planner", "search")
    g.add_edge("search", "fetch")
    g.add_edge("fetch", "check")
    g.add_conditional_edges(
        "check", route_after_check, {"retry": "bump_retry", "write": "writer"}
    )
    g.add_edge("bump_retry", "search")
    g.add_edge("writer", END)

    return g.compile()
