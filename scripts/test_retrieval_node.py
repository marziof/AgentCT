from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

from src.agentct.retrieval.openalex import search_openalex
from src.agentct.retrieval.europepmc import search_europepmc
from src.agentct.retrieval.mergesources import merge_sources
from src.agentct.retrieval.fulltext import retrieve_fulltext
from src.agentct.retrieval.chunking import chunk_text
from src.agentct.retrieval.embeddings import (
    embed_chunks,
    embed_claim,
    model,
    retrieve_relevant_passages,
)
from src.agentct.nodes.retrieval import retrieve_passages_node
from src.agentct.state import AgentState


CLAIM = (
    "Vaccines are safe and effective in preventing infectious diseases."
)


def inspect_source(stage: str, source: dict) -> None:
    """Print abstract-related fields for one source."""
    print(f"\n--- {stage} ---")
    print("Title:", source.get("title"))
    print("URL:", source.get("url"))
    print("OpenAlex ID:", source.get("openalex_id"))
    print("PMCID:", source.get("pmcid"))
    print("DOI:", source.get("doi"))

    for key in (
        "abstract",
        "abstractText",
        "abstract_inverted_index",
        "content",
    ):
        value = source.get(key)
        if isinstance(value, str):
            length = len(value)
        elif isinstance(value, dict):
            length = len(value)
        else:
            length = "N/A"

        print(
            f"{key}: type={type(value).__name__}, "
            f"length={length}, preview={repr(value)[:300]}"
        )


def main() -> None:
    print("=== CLAIM ===")
    print(CLAIM)

    # 1. Search each provider separately.
    print("\n=== OPENALEX SEARCH ===")
    openalex_sources = search_openalex(CLAIM, limit=10)
    print("Sources returned:", len(openalex_sources))

    for source in openalex_sources:
        inspect_source("OpenAlex raw result", source)

    print("\n=== EUROPE PMC SEARCH ===")
    europepmc_sources = search_europepmc(CLAIM, limit=10)
    print("Sources returned:", len(europepmc_sources))

    for source in europepmc_sources:
        inspect_source("Europe PMC raw result", source)

    # 2. Merge results and inspect whether content is preserved.
    print("\n=== MERGE SOURCES ===")
    merged_sources = merge_sources(openalex_sources, europepmc_sources)
    print("Merged sources:", len(merged_sources))

    for source in merged_sources:
        inspect_source("Merged result", source)

    # 3. Test passage retrieval in isolation.
    print("\n=== RETRIEVE PASSAGES NODE ===")
    state = AgentState(
        claim=CLAIM,
        retrieved_docs=merged_sources,
    )

    result = retrieve_passages_node(state)

    print("\n=== RETRIEVAL STATS ===")
    print(result.get("retrieval_stats"))

    print("\n=== RELEVANT PASSAGES ===")
    passages = result.get("relevant_passages", [])
    print("Passages returned:", len(passages))

    for i, passage in enumerate(passages, start=1):
        print(f"\nPassage {i}")
        print("Source ID:", passage.get("source_id"))
        print("Text basis:", passage.get("text_basis"))
        print("Text preview:", repr(passage.get("text", "")[:300]))


if __name__ == "__main__":
    main()