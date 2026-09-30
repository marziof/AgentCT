from pathlib import Path
import sys
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

from src.agentct.retrieval.semantic_scholar import search_semantic_scholar
from src.agentct.retrieval.openalex import search_openalex, reconstruct_abstract
from src.agentct.retrieval.europepmc import search_europepmc
from src.agentct.retrieval.mergesources import merge_sources

#claim = "Smoking tobacco is beneficial for your health."
#claim = "Smoking tobacco health impact."
claim = "Eating a diet rich in fruits and vegetables reduces the risk of developing cardiovascular diseases."
query = claim
max_sources = 10
from src.agentct.retrieval.fulltext import retrieve_fulltext

retrieved_sources = search_openalex(query, limit=max_sources)
europepmc_results = search_europepmc(query, limit=max_sources)
merged_sources = merge_sources(retrieved_sources, europepmc_results)

print("\n=== Full Text Retrieval (via consolidated retrieve_fulltext) ===")

# Test against your OpenAlex results
print("--- OpenAlex sources ---")
for i, source in enumerate(retrieved_sources, start=1):
    result = retrieve_fulltext(source)
    print(f"Source {i}: {source.get('title')}")
    print(f"  Format: {result.get('format')}")
    if result.get("fulltext"):
        print(f"  Length: {len(result['fulltext'])} chars")
        print(f"  Preview: {result['fulltext'][:200]}")
    else:
        print("  No full text retrieved.")
    print()

# Test against your Europe PMC results too, since those should reliably hit Route 1
print("--- Europe PMC sources ---")
for i, source in enumerate(europepmc_results, start=1):
    result = retrieve_fulltext(source)
    print(f"Source {i}: {source.get('title')}")
    print(f"  Format: {result.get('format')}")
    if result.get("fulltext"):
        print(f"  Length: {len(result['fulltext'])} chars")
        print(f"  Preview: {result['fulltext'][:200]}")
    else:
        print("  No full text retrieved.")
    print()

from src.agentct.retrieval.fulltext import parse_jats_xml
import requests
response = requests.get("https://www.ebi.ac.uk/europepmc/webservices/rest/PMC13235346/fullTextXML", timeout=15)
body_text = parse_jats_xml(response.text)
print(f"Length: {len(body_text)} characters")
print(body_text[:1000])


print("--- Merged sources ---")
for i, source in enumerate(merged_sources, start=1):
    print(f"Source {i}: {source.get('title')}")
    print(f"  pmcid: {source.get('pmcid')}")
    result = retrieve_fulltext(source)
    print(f"  Format: {result.get('format')}")
    if result.get("fulltext"):
        print(f"  Length: {len(result['fulltext'])} chars")
        print(f"  Preview: {result['fulltext'][:200]}")
    else:
        print("  No full text retrieved.")
    print()

