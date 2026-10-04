from langgraph.graph import StateGraph, END

from src.agentct.state import AgentState
from src.agentct.models.schemas import EvidenceOutput

from src.agentct.utils.retry import invoke_with_retry

from src.agentct.config import llm

structured_model_evidence = llm.with_structured_output(EvidenceOutput)

def assess_evidence_node(state: AgentState) -> dict:
    if not state.relevant_passages:
        return {
            "evidence_output": EvidenceOutput(
                evidence_items=[],
                overall_evidence_score=0.0,
                overall_evidence_reasoning=(
                    "No relevant passages were retrieved, so the evidence "
                    "could not be assessed."
                ),
            )
        }

    passages_text = "\n\n".join(
        f"[Source: {p['source_id']}]\n{p['text']}"
        for p in state.relevant_passages
    )

    prompt = (
        f"Please provide an assessment of the evidence for the following claim: "
        f"{state.claim} based on the following passages:\n\n"
        f"{passages_text}\n\n"
        
        "For each distinct source represented in the passages, you should provide "
        "an evidence item with a source_id identifying the source, "
        "an evidence_type describing the type of evidence "
        "(experimental, observational, review, theoretical, etc.), "
        "a finding describing the main finding from that source relevant to the claim, "
        "a relevance assessment explaining how directly the evidence addresses the claim, "
        "strengths explaining the main strengths of the evidence, "
        "limitations explaining important limitations of the evidence (1 sentence), "
        "and supporting_passages (just the first 3 words followed by '...') identifying the passages from that source that support"
        "the assessment. "
        
        "You should then provide an overall_evidence_score in the range 0-1 "
        "reflecting the overall quality of the available evidence, "
        "as well as overall_evidence_reasoning explaining the score. "
        
        "Multiple passages from the same source must be treated as evidence from "
        "one source, not as independent sources."
    )

    evidence_output = invoke_with_retry(
        structured_model_evidence,
        prompt
    )

    return {"evidence_output": evidence_output}