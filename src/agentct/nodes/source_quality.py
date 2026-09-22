from langgraph.graph import StateGraph, END

from src.agentct.state import AgentState
from src.agentct.models.schemas import SourceOutput, SourceAssessments, KeywordExtraction, FinalReport
from src.agentct.utils.scoring_sources import concordance_score, confidence_score
from src.agentct.utils.retry import invoke_with_retry

from src.agentct.config import llm

structured_model = llm.with_structured_output(SourceAssessments)
structured_model_with_keywords = llm.with_structured_output(KeywordExtraction)
structured_model_with_final_report = llm.with_structured_output(FinalReport)

def assess_source_node(state: AgentState) -> dict:
    # Placeholder for source assessment logic
    prompt = f"Please provide an assessment of the following claim: {state.claim} based on the following sources: {', '.join([doc['title'] for doc in state.retrieved_docs])}. " \
            "For each source, you should provide a stance (support or oppose) with respect to the claim, " \
            "a benevolence score (in range 0-1) that reflects the source's benevolence (0 if the source may have private interests, 1 if the source is completely objective), as well as benevolence reasoning explaining the score, " \
            "an expertise score (in range 0-1) that reflects the source's expertise SPECIFICALLY IN THE SUBJECT MATTER OF THE CLAIM " \
            "(0 if the source's field is unrelated or only tangentially related to the claim, even if it is authoritative in its own field; 1 if the source is a recognized expert directly in the claim's specific subject area), as well as expertise reasoning that explicitly addresses how relevant the source's domain is to this specific claim. " \
            "If a source discusses a related but different topic (e.g. general health or a different intervention) rather than the claim's specific subject, its expertise score should be low regardless of its general credibility."

    structured_response = invoke_with_retry(structured_model, prompt)
    source_assessments = structured_response.source_assessments
    concordance = concordance_score(source_assessments)
    confidence = confidence_score(source_assessments)
    concordance_reasoning = "expert sources agree on the stance" if concordance == 1.0 else "experts mostly agree" if concordance > 0.5 else "experts are divided" 
    confidence_reasoning = "sources support the claim" if confidence == 1.0 else "sources mostly support the claim" if confidence > 0.5 else "sources oppose the claim"
    #confidence_reasoning = #llm.invoke(input=f"Please provide a brief reasoning for the overall confidence score of {confidence} based on the source assessments: {source_assessments}.").content
    source_output_value = SourceOutput(
        source_assessments=source_assessments,
        concordance_score=concordance,
        concordance_reasoning=concordance_reasoning,
        overall_confidence=confidence, 
        overall_confidence_reasoning=confidence_reasoning
    )
    return { "source_output": source_output_value }