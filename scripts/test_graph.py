from pathlib import Path
import sys
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

from src.agentct.graph import graph, compiled_graph
from src.agentct.state import AgentState

claim = "Eating meat is good for your health." #"Smoking tobacco is beneficial for your health."
# retrieved_docs = [
#     {"title": "The Grey Hoodie Project: Big Tobacco, Big Tech, and the Threat on Academic Integrity", "content": "This source discusses the influence of big tobacco and big tech on academic integrity."},
#     {"title": "Spatial, temporal, and demographic patterns in prevalence of smoking tobacco use and attributable disease burden in 204 countries and territories, 1990–2019: a systematic analysis from the Global Burden of Disease Study 2019", "content": "This source provides a systematic analysis of smoking tobacco use and its health impacts across various countries and demographics."},
#     {"title": "A 1950s cigarette advertisement claiming that doctors preferred a particular cigarette brand.", "content": "This source is a historical advertisement from the 1950s that claims doctors preferred a specific cigarette brand."}
# ]

initial_state = AgentState(
    claim=claim,
    retrieved_docs=[],
    source_output=None,
    plausibility_output=None,
    arg_output=None,
    evidence_output=None,
    meta_output=None,
    final_report=None
)

result = compiled_graph.invoke(initial_state)

# print("=== Full result ===")
# print(result)

print("\n=== source_output ===")
source_output = result.get("source_output")
if source_output:
    for i, src in enumerate(source_output.source_assessments, start=1):
        print(f"Source {i}: {src.source}")
        print(f"  Stance: {src.stance}")
        print(f"  Benevolence: {src.benevolence_score} — {src.benevolence_reasoning}")
        print(f"  Expertise: {src.expertise_score} — {src.expertise_reasoning}")
    print(f"\nConcordance: {source_output.concordance_score} — {source_output.concordance_reasoning}")
    print(f"Overall confidence: {source_output.overall_confidence} — {source_output.overall_confidence_reasoning}")

print("\n=== final_report ===")
final_report = result.get("final_report")
if final_report:
    print(final_report.conclusion)
    print(f"Confidence: {final_report.confidence}")
    print(final_report.key_reasoning)