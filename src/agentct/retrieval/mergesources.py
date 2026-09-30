
def merge_sources(openalex_results: list[dict], europepmc_results: list[dict]) -> list[dict]:
    """
    Merge and deduplicate sources from OpenAlex and Europe PMC by DOI.

    When a paper appears in both, keeps OpenAlex's richer metadata
    (authors, affiliations) but adds Europe PMC's pmcid for full-text access.

    Args:
        openalex_results (list[dict]): Results from search_openalex.
        europepmc_results (list[dict]): Results from search_europepmc.

    Returns:
        list[dict]: Deduplicated, merged source list.
    """
    def normalize_doi(doi: str | None) -> str | None:
        if not doi:
            return None
        return doi.replace("https://doi.org/", "").strip().lower()

    epmc_by_doi = {
        normalize_doi(r.get("doi")): r
        for r in europepmc_results
        if normalize_doi(r.get("doi"))
    }

    merged = []
    seen_dois = set()

    for source in openalex_results:
        doi = normalize_doi(source.get("doi"))
        merged_source = dict(source)

        if doi and doi in epmc_by_doi:
            merged_source["pmcid"] = epmc_by_doi[doi].get("pmcid")
            seen_dois.add(doi)

        merged.append(merged_source)

    # Add Europe PMC-only results not already covered
    for doi, epmc_source in epmc_by_doi.items():
        if doi not in seen_dois:
            merged.append(epmc_source)

    return merged