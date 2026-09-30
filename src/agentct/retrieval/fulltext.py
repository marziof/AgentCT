import requests
from pdfplumber import open as open_pdf
import io


def retrieve_fulltext(doc: dict) -> dict:
    """
    Retrieve full text for a source, trying multiple routes in order of reliability:
    1. Europe PMC REST API (via pmcid) — most reliable, avoids bot-blocking.
    2. OpenAlex's open_access.oa_url — often blocked by publisher sites, tried as a fallback.
    3. None — caller should fall back to abstract-only assessment.

    Args:
        doc (dict): A source dict, expected to optionally carry 'pmcid' and/or
                    'open_access' (as returned by search_openalex/search_europepmc).

    Returns:
        dict: doc merged with 'fulltext' (str | None) and 'format' (str | None).
    """

    # --- Route 1: Europe PMC REST API ---
    pmcid = doc.get("pmcid")
    if pmcid:
        xml_url = f"https://www.ebi.ac.uk/europepmc/webservices/rest/{pmcid}/fullTextXML"
        try:
            response = requests.get(xml_url, timeout=30)
            response.raise_for_status()
            text = parse_jats_xml(response.text)
            if text:
                return {**doc, "fulltext": text, "format": "europepmc_xml"}
        except Exception as e:
            print(f"Europe PMC fetch failed for {doc.get('title')}: {e}")

    # --- Route 2: OpenAlex open-access URL (PDF only; often blocked) ---
    oa_url = doc.get("open_access", {}).get("oa_url")
    if oa_url:
        try:
            headers = {"User-Agent": "Mozilla/5.0 (compatible; AgentCT/1.0; research tool)"}
            response = requests.get(oa_url, timeout=30, headers=headers)
            response.raise_for_status()

            content_type = response.headers.get("Content-Type", "")
            if "pdf" in content_type.lower():
                with open_pdf(io.BytesIO(response.content)) as pdf:
                    text = "\n".join(page.extract_text() or "" for page in pdf.pages)
                if text.strip():
                    return {**doc, "fulltext": text, "format": "pdf"}
        except Exception as e:
            print(f"OpenAlex oa_url fetch failed for {doc.get('title')}: {e}")

    # --- Route 3: no full text available ---
    return {**doc, "fulltext": None, "format": None}
    


import xml.etree.ElementTree as ET

def parse_jats_xml(xml_text: str) -> str:
    """
    Extract plain-text article body from Europe PMC's JATS XML format.

    Pulls paragraph text from <body>, skipping references and back-matter.

    Args:
        xml_text (str): Raw JATS XML string.

    Returns:
        str: Plain-text article body, or empty string on parse failure.
    """
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError as e:
        print(f"Failed to parse JATS XML: {e}")
        return ""

    body = root.find(".//body")
    if body is None:
        return ""

    paragraphs = [
        "".join(p.itertext()).strip()
        for p in body.iter("p")
        if "".join(p.itertext()).strip()
    ]

    return "\n\n".join(paragraphs)