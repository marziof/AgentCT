def merge_sources(
    openalex_results: list[dict],
    europepmc_results: list[dict],
) -> list[dict]:
    """Merge and deduplicate OpenAlex and Europe PMC results by DOI."""

    def normalize_doi(doi: str | None) -> str | None:
        if not doi:
            return None

        doi = doi.strip().lower()

        for prefix in (
            "https://doi.org/",
            "http://doi.org/",
            "doi:",
        ):
            if doi.startswith(prefix):
                doi = doi[len(prefix):]

        return doi or None

    def get_abstract(source: dict) -> str | dict | None:
        for key in (
            "abstract",
            "abstractText",
            "abstract_inverted_index",
            "content",
        ):
            value = source.get(key)

            if value:
                return value

        return None

    epmc_by_doi = {
        normalize_doi(source.get("doi")): source
        for source in europepmc_results
        if normalize_doi(source.get("doi"))
    }

    merged = []
    seen_dois = set()

    for source in openalex_results:
        doi = normalize_doi(source.get("doi"))
        merged_source = dict(source)

        if doi:
            seen_dois.add(doi)
            epmc_source = epmc_by_doi.get(doi)

            if epmc_source:
                # Preserve identifiers from Europe PMC.
                merged_source["pmcid"] = (
                    epmc_source.get("pmcid")
                    or merged_source.get("pmcid")
                )

                # Use the Europe PMC abstract if OpenAlex has none.
                if not get_abstract(merged_source):
                    abstract = get_abstract(epmc_source)

                    if abstract:
                        merged_source["content"] = (
                            abstract
                            if isinstance(abstract, str)
                            else ""
                        )
                        if isinstance(abstract, dict):
                            merged_source["abstract"] = abstract

        # Normalize any available abstract into content.
        if not merged_source.get("content", "").strip():
            abstract = get_abstract(merged_source)

            if isinstance(abstract, dict):
                merged_source["abstract"] = abstract
                merged_source["content"] = ""
            elif isinstance(abstract, str):
                merged_source["content"] = abstract

        merged.append(merged_source)

    for doi, epmc_source in epmc_by_doi.items():
        if doi not in seen_dois:
            merged_source = dict(epmc_source)
            abstract = get_abstract(merged_source)

            if isinstance(abstract, dict):
                merged_source["abstract"] = abstract
                merged_source["content"] = ""
            elif isinstance(abstract, str):
                merged_source["content"] = abstract

            merged.append(merged_source)

    return merged
