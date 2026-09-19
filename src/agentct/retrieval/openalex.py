import requests




EMAIL = "marzioformica@gmail.com"
    
def search_openalex(query: str, limit: int = 5, email: str = EMAIL) -> list[dict]:
    """
    Search OpenAlex for works related to the query.

    Args:
        query (str): The search query.
        limit (int): The maximum number of results to return.
        email (str): Contact email for OpenAlex's polite pool (faster, higher rate limits).

    Returns:
        list[dict]: A list of dicts with 'title', 'content' (abstract), and 'url' keys.
    """
    url = "https://api.openalex.org/works"
    params = {
        "search": query,
        "per_page": limit,
        "mailto": email,
    }
    response = requests.get(url, params=params)
    if response.status_code != 200:
        print(f"Error: {response.status_code} - {response.text}")
        return []

    data = response.json()
    raw_results = data.get("results", [])

    formatted_results = []
    for result in raw_results:
        abstract = reconstruct_abstract(result.get("abstract_inverted_index", {}))
        formatted_results.append({
            "title": result.get("title", "No title"),
            "content": abstract,
            "url": result.get("id", "No URL"),
        })

    return formatted_results



def reconstruct_abstract(inverted_index: dict) -> str:
    """
    Reconstructs the original text from an inverted index.

    Args:
        inverted_index (dict): The inverted index where keys are words and values are lists of positions.

    Returns:
        str: The reconstructed text.
    """
    if not inverted_index:
        return ""

    max_position = max(pos for positions in inverted_index.values() for pos in positions)
    words = [""] * (max_position + 1)
    for word, positions in inverted_index.items():
        for pos in positions:
            words[pos] = word

    # Join the words to form the reconstructed text
    return " ".join(words)