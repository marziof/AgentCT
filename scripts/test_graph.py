from pathlib import Path
import sys
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

from src.agentct.graph import graph, compiled_graph
from src.agentct.state import AgentState


examples = ["Smoking tobacco is beneficial for your health.", 
            "Eating a diet rich in fruits and vegetables reduces the risk of developing cardiovascular diseases.",
            "Moderate alcohol consumption is good for cardiovascular health.",
            "Climate change is primarily caused by human activities.",
            "Vaccines are safe and effective in preventing infectious diseases.",
            "The use of genetically modified organisms (GMOs) in agriculture is safe for human consumption."]   
print("=== Example test claims ===")
for i, example in enumerate(examples, start=1):
    print(f"{i}. {example}")

claim = input("Enter a claim to test: ")  # Example: "Moderate alcohol consumption is good for cardiovascular health."
#claim = "Moderate alcohol consumption is good for cardiovascular health." #"Smoking tobacco is beneficial for your health."
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

print("\n=== RETRIEVAL STATS ===")
print(result.get("retrieval_stats", "MISSING retrieval_stats"))

print("\n=== RELEVANT PASSAGES ===")
passages = result.get("relevant_passages", [])
print(f"Passages returned: {len(passages)}")

for i, passage in enumerate(passages, start=1):
    print(f"\nPassage {i}")
    print(f"  source_id: {passage.get('source_id')}")
    print(f"  text_basis: {passage.get('text_basis', 'MISSING')}")
    print(f"  text preview: {passage.get('text', '')[:200]!r}")

# print("=== Full result ===")
# print(result)

# print source output (example for one source, then concordance and support scores)
print("\n=== source_output ===")
source_output = result.get("source_output")
if source_output:
    for i, src in enumerate(source_output.source_assessments, start=1):
        print(f"{i}. {src.source[:60]} | {src.stance} | B={src.benevolence_score} E={src.expertise_score}")
    print(f"\nConcordance: {source_output.concordance_score} — {source_output.concordance_reasoning}")
    print(f"Support: {source_output.overall_support} — {source_output.overall_support_reasoning}")


print("\n=== evidence_output ===")
evidence_output = result.get("evidence_output")
if evidence_output:
    for i, item in enumerate(evidence_output.evidence_items, start=1):
        if i==1:  # Only print the first evidence item for brevity
            print(f"Evidence {i}: {item.source_id}")
            print(f"  Relevance: {item.relevance}")
            print(f"  Strengths: {item.strengths}")
            print(f"  Limitations: {item.limitations}")
    print(f"\nOverall Evidence Score: {evidence_output.overall_evidence_score} — {evidence_output.overall_evidence_reasoning}")


print("\n=== arg_output ===")
arg_output = result.get("arg_output")
if arg_output:
    for i, item in enumerate(arg_output.argument_items, start=1):
        if i==1:  # Only print the first argument item for brevity
            print(f"Argument {i}: {item.source_id}")
            print(f"  Premises: {item.premises}")
            print(f"  Conclusion: {item.conclusion}")
            print(f"  Assumptions: {item.assumptions}")
            print(f"  Counterarguments: {item.counterarguments}")
            print(f"  Weaknesses: {item.weaknesses}")
            print(f"  Supporting Passages: {item.supporting_passages}")
    print(f"\nOverall Argument Score: {arg_output.overall_argument_score} — {arg_output.overall_argument_reasoning}")


print("\n=== final_report ===")
final_report = result.get("final_report")
if final_report:
    print(final_report.conclusion)
    print(f"Confidence: {final_report.confidence}")
    print(final_report.key_reasoning)