from typing import TypedDict

class ResearchState(TypedDict):
    question: str
    sub_queries: list[str]
    search_results: list[dict]
    source: list[dict]
    contradictions: list[dict]
    retry_count: int
    answer: str
    faithfulness_score: float


