import requests
import xml.etree.ElementTree as ET


def retrieve_fulltext(doc: dict) -> dict:
    """
    Retrieve full text for an OpenAlex work.

    Prefers GROBID TEI XML because it preserves document structure.
    Falls back to PDF if TEI XML is unavailable.

    Returns the document metadata plus extracted full text.
    """

    content_urls = doc.get("content_urls", {})

    # Prefer structured GROBID XML
    xml_url = content_urls.get("grobid_xml")

    if xml_url:
        response = requests.get(xml_url, timeout=30)
        response.raise_for_status()

        root = ET.fromstring(response.content)

        # Extract all textual content from the TEI document
        text = " ".join(
            element.text.strip()
            for element in root.iter()
            if element.text and element.text.strip()
        )

        return {
            **doc,
            "fulltext": text,
            "format": "grobid_xml",
        }

    # Fall back to PDF
    pdf_url = content_urls.get("pdf")

    if pdf_url:
        response = requests.get(pdf_url, timeout=30)
        response.raise_for_status()

        return {
            **doc,
            "fulltext_bytes": response.content,
            "format": "pdf",
        }

    return {
        **doc,
        "fulltext": None,
        "format": None,
    }