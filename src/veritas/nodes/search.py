import os 
from dotenv import load_dotenv
from tavily import TavilyClient

load_dotenv()

tavily = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])

def search_node(state):
    sub_queries = state["sub_queries"]

    # fewer sub-queries = fewer sources per query

    max_results_per_query = 5 if  len(sub_queries) == 1 else 2

    all_results = []

    for query in sub_queries: 
        response = tavily.search(query=query, max_results=max_results_per_query)
        all_results.extend(response["results"])

    return {"search_results": all_results}


