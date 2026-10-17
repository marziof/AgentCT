from langgraph.graph import StateGraph, END

from src.agentct.state import AgentState
from src.agentct.models.schemas import SourceOutput, SourceAssessments, KeywordExtraction, FinalReport
from src.agentct.utils.scoring_sources import concordance_score, support_score
from src.agentct.utils.retry import invoke_with_retry

from src.agentct.config import llm

structured_model = llm.with_structured_output(SourceAssessments, method="json_schema")
# structured_model_with_keywords = llm.with_structured_output(KeywordExtraction)
# structured_model_with_final_report = llm.with_structured_output(FinalReport)

def assess_source_node(state: AgentState) -> dict:
    # Placeholder for source assessment logic
    docs = state.retrieved_docs#[:6]   # stopgap until ranking exists upstream
    if not docs:
        return {"source_output": None}   # handle explicitly, see note below

    sources_text = "\n\n".join(
        f"[{i}] {d.get('title')}\n"
        f"Authors: {', '.join(d.get('authors', [])[:3])}\n"
        f"Abstract: {(d.get('content') or '')[:600]}"
        for i, d in enumerate(docs, 1)
    )
    prompt = (
        f"Assess the following claim: {state.claim}\n\n"
        f"SOURCES:\n{sources_text}\n\n"
        "For each source, provide: a stance (support or oppose) toward the claim; "
        "a benevolence score (0-1; 0 if the source may have private interests, 1 if "
        "completely objective) with reasoning; an expertise score (0-1) specifically "
        "in the subject matter of the claim (low if the source's field is unrelated or "
        "only tangential, even if authoritative elsewhere) with reasoning. "
        "Keep each reasoning field to one short sentence. "
        "In the `source` field, copy the source's title exactly as given."
    )
    structured_response = invoke_with_retry(structured_model, prompt)
    source_assessments = structured_response.source_assessments
    # Calculate the concordance and support scores
    concordance = concordance_score(source_assessments)
    support = support_score(source_assessments)
    concordance_reasoning = "expert sources agree on the stance" if concordance == 1.0 else "experts mostly agree" if concordance > 0.5 else "experts are divided" 
    support_reasoning = "sources support the claim" if support == 1.0 else "sources mostly support the claim" if support > 0.5 else "sources oppose the claim"
    #confidence_reasoning = #llm.invoke(input=f"Please provide a brief reasoning for the overall confidence score of {confidence} based on the source assessments: {source_assessments}.").content
    source_output_value = SourceOutput(
        source_assessments=source_assessments,
        concordance_score=concordance,
        concordance_reasoning=concordance_reasoning,
        overall_support=support, 
        overall_support_reasoning=support_reasoning
    )
    return { "source_output": source_output_value }