import requests

def search_europepmc(query: str, limit: int = 5) -> list[dict]:
    """
    Search Europe PMC for open-access, full-text-available works matching the query.

    Returns dicts shaped consistently with search_openalex's output, plus a
    'fulltext_url' field pointing to a directly fetchable full-text copy.

    Args:
        query (str): The search query.
        limit (int): Maximum number of results to return.

    Returns:
        list[dict]: Works with title, content (abstract), url, doi, authors, fulltext_url.
    """
    search_url = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
    params = {
        "query": f"{query} AND OPEN_ACCESS:Y AND HAS_FT:Y",
        "format": "json",
        "pageSize": limit,
        "resultType": "core",
    }

    try:
        response = requests.get(search_url, params=params, timeout=15)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        print(f"Europe PMC search failed: {e}")
        return []

    results = data.get("resultList", {}).get("result", [])
    formatted_results = []

    for r in results:
        fulltext_urls = r.get("fullTextUrlList", {}).get("fullTextUrl", [])
        # Prefer an XML full-text link (usually Europe PMC's own, cleanest to parse)
        xml_url = next((u["url"] for u in fulltext_urls if u.get("documentStyle") == "xml"), None)
        #fallback_url = fulltext_urls[0]["url"] if fulltext_urls else None
        # Prefer Europe PMC's own hosted copy (avoids publisher bot-blocking)
        epmc_url = next(
            (u["url"] for u in fulltext_urls
            if u.get("site") == "Europe_PMC" and u.get("documentStyle") == "html"),
            None
        )
        fallback_url = fulltext_urls[0]["url"] if fulltext_urls else None
        pmcid = r.get("pmcid")
        fulltext_url = f"https://www.ebi.ac.uk/europepmc/webservices/rest/{pmcid}/fullTextXML" if pmcid else None

        formatted_results.append({
            "title": r.get("title", "No title"),
            "content": r.get("abstractText", ""),
            "url": f"https://europepmc.org/article/{r.get('source')}/{r.get('id')}",
            "pmcid": r.get("pmcid"), 
            "doi": r.get("doi"),
            "authors": r.get("authorString", "").split(", ") if r.get("authorString") else [],
            "fulltext_url": fulltext_url,  # epmc_url or fallback_url,
        })

    return formatted_results

def check_europepmc(doi: str) -> dict:
    """
    Check Europe PMC for a self-hosted full-text copy of a work, given its DOI.

    Europe PMC hosts full text directly for a large fraction of biomedical/
    life-science literature, avoiding the publisher-site bot-blocking that
    affects raw OpenAlex/Unpaywall PDF links.

    Args:
        doi (str): The work's DOI (bare, e.g. "10.1038/nature12373").

    Returns:
        dict: {"has_fulltext": bool, "fulltext_url": str | None, "format": str | None}
    """
    if not doi:
        return {"has_fulltext": False, "fulltext_url": None, "format": None}

    search_url = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
    params = {
        "query": f"DOI:{doi}",
        "format": "json",
    }

    try:
        response = requests.get(search_url, params=params, timeout=15)
        response.raise_for_status()
        data = response.json()

        results = data.get("resultList", {}).get("result", [])
        if not results:
            return {"has_fulltext": False, "fulltext_url": None, "format": None}

        record = results[0]

        if record.get("hasTextMinedTerms") == "N" and record.get("isOpenAccess") != "Y":
            return {"has_fulltext": False, "fulltext_url": None, "format": None}

        # Fetch the full-text-availability info for this record
        source = record.get("source")
        pmcid_or_id = record.get("pmcid") or record.get("id")

        if not pmcid_or_id or record.get("isOpenAccess") != "Y":
            return {"has_fulltext": False, "fulltext_url": None, "format": None}

        fulltext_url = f"https://www.ebi.ac.uk/europepmc/webservices/rest/{source}/{pmcid_or_id}/fullTextXML"
        return {"has_fulltext": True, "fulltext_url": fulltext_url, "format": "xml"}

    except Exception as e:
        print(f"Europe PMC check failed for DOI {doi}: {e}")
        return {"has_fulltext": False, "fulltext_url": None, "format": None}