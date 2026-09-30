import requests

EMAIL = "marzioformica@gmail.com"

def check_unpaywall(doi: str, email: str = EMAIL) -> dict:
    """
    Check Unpaywall for an open-access copy of a work, given its DOI.

    Args:
        doi (str): The work's DOI (e.g. "10.1038/nature12373", no URL prefix).
        email (str): Contact email required by Unpaywall's API.

    Returns:
        dict: {"is_oa": bool, "pdf_url": str | None} — pdf_url is the best
        direct PDF link found, or None if unavailable.
    """
    if not doi:
        return {"is_oa": False, "pdf_url": None}

    url = f"https://api.unpaywall.org/v2/{doi}"
    params = {"email": email}

    try:
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        data = response.json()

        best_location = data.get("best_oa_location") or {}
        pdf_url = best_location.get("url_for_pdf")

        return {"is_oa": data.get("is_oa", False), "pdf_url": pdf_url}

    except Exception as e:
        print(f"Unpaywall check failed for DOI {doi}: {e}")
        return {"is_oa": False, "pdf_url": None}