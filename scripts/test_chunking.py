from pathlib import Path
import sys
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

from src.agentct.retrieval.openalex import search_openalex, reconstruct_abstract
from src.agentct.retrieval.europepmc import search_europepmc
from src.agentct.retrieval.mergesources import merge_sources
from src.agentct.retrieval.fulltext import retrieve_fulltext
from src.agentct.retrieval.chunking import chunk_text


#claim = "Smoking tobacco is beneficial for your health."
#claim = "Smoking tobacco health impact."
claim = "Eating a diet rich in fruits and vegetables reduces the risk of developing cardiovascular diseases."
query = claim
max_sources = 3

retrieved_sources = search_openalex(query, limit=max_sources)
europepmc_results = search_europepmc(query, limit=max_sources)
merged_sources = merge_sources(retrieved_sources, europepmc_results)

print("\n=== Full Text Retrieval (via consolidated retrieve_fulltext) ===")
chunked_sources = []
for i, source in enumerate(europepmc_results, start=1):
    result = retrieve_fulltext(source)
    print(f"Source {i}: {source.get('title')}")
    chunked = chunk_text(result.get("fulltext", ""), source_id=source.get("pmcid"))
    chunked_sources.append({
        "source": source,
        "fulltext": result.get("fulltext"),
        "chunks": chunked
    })

from src.agentct.retrieval.embeddings import embed_chunks, embed_claim, model

all_chunks = []
for chunked_source in chunked_sources:
    all_chunks.extend(chunked_source["chunks"])

embedded_chunks = embed_chunks(all_chunks, model)
embedded_claim = embed_claim(claim, model)

print("Nb of chunks embedded:", len(embedded_chunks))
print("Claim embedding shape:", embedded_claim.shape)
print("First chunk embedding shape:", embedded_chunks[0]["embedding"].shape)
print("First chunk source_id:", embedded_chunks[0]["source_id"])


from src.agentct.retrieval.embeddings import retrieve_relevant_passages

top_passages = retrieve_relevant_passages(embedded_claim, embedded_chunks, top_k=5)

print("\n=== Top Relevant Passages ===")
for i, passage in enumerate(top_passages, start=1):
    print(f"{i}. Similarity: {passage['similarity']:.3f} | Source: {passage['source_id']}")
    print(f"   {passage['text'][:200]}")
    print()