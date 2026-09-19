from pathlib import Path
import sys
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

from src.agentct.retrieval.semantic_scholar import search_semantic_scholar
from src.agentct.retrieval.openalex import search_openalex, reconstruct_abstract

#claim = "Smoking tobacco is beneficial for your health."
claim = "Smoking tobacco health impact."
query = claim
max_sources = 1
retrieved_sources = search_openalex(query, max_sources)

print("=== Retrieved Sources ===")
for i, source in enumerate(retrieved_sources, start=1):
    print(f"Source {i}: {source.get('title', 'No title')}")
    print(f"URL: {source.get('id', 'No URL')}")
    print(f"Abstract: {source.get('abstract', 'No abstract')}")
    print(source.get('abstract_inverted_index'))
    print()

print("=== Reconstructed Abstract ===")
print(reconstruct_abstract(retrieved_sources[0]["abstract_inverted_index"]))
