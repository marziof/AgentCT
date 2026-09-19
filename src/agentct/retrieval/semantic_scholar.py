
import requests

def search_semantic_scholar(query: str, limit: int = 5) -> list[dict]:
    """
    Search Semantic Scholar for papers related to the query.

    Args:
        query (str): The search query.
        limit (int): The maximum number of results to return.

    Returns:
        list[dict]: A list of dictionaries containing paper information.
    """
    url = "https://api.semanticscholar.org/graph/v1/paper/search"
    params = {
        "query": query,
        "limit": limit,
        "fields": "title,authors,year,venue,abstract,url"
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        return data.get("data", [])
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return []



EMAIL = "marzioformica@gmail.com"
    
def search_openalex(query: str, limit: int = 5, email: str =EMAIL) -> list[dict]:
    """
    Search OpenAlex for works related to the query.

    Args:
        query (str): The search query.
        limit (int): The maximum number of results to return.
        email (str): Contact email for OpenAlex's polite pool (faster, higher rate limits).

    Returns:
        list[dict]: A list of dictionaries containing work information.
    """
    url = "https://api.openalex.org/works"
    params = {
        "search": query,
        "per_page": limit,
        "mailto": email,
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        return data.get("results", [])
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return []