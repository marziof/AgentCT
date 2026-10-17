from langgraph.graph import StateGraph, END

from src.agentct.state import AgentState
from src.agentct.models.schemas import SourceOutput, SourceAssessments, KeywordExtraction, FinalReport
from src.agentct.utils.retry import invoke_with_retry

from src.agentct.config import llm

#structured_model = llm.with_structured_output(SourceAssessments)
#structured_model_with_keywords = llm.with_structured_output(KeywordExtraction)
structured_model_with_final_report = llm.with_structured_output(FinalReport, method="json_schema")

def return_report_node_prev(state: AgentState) -> dict:
    prompt = f"Based on the following assessments of the claim '{state.claim}':\n\n" \
             f"Source quality: {state.source_output}\n\n" \
             f"Evidence quality: {state.evidence_output}\n\n" \
             f"Argument quality: {state.arg_output}\n\n" \
             "Please provide a final report summarizing the key points and a clear conclusion."
    final_report_value = invoke_with_retry(structured_model_with_final_report, prompt)
    return {"final_report": final_report_value}


def _digest(state) -> str:
    lines = []
    so = state.source_output
    if so and so.source_assessments:
        sa = so.source_assessments
        stances = {s: sum(a.stance == s for a in sa) for s in {a.stance for a in sa}}
        lines.append(f"Sources: {len(sa)} assessed; stances {stances}; "
                     f"concordance {so.concordance_score:.2f}; support {so.overall_support:.2f}")
    else:
        lines.append("Sources: not assessed")

    ev = state.evidence_output
    if ev and ev.evidence_items:
        types = sorted({i.evidence_type for i in ev.evidence_items})
        lines.append(f"Evidence: {len(ev.evidence_items)} items ({', '.join(types)}); "
                     f"score {ev.overall_evidence_score:.2f}")
    else:
        lines.append("Evidence: not assessed")

    ar = state.arg_output
    if ar and ar.argument_items:
        concl = "; ".join(i.conclusion[:100] for i in ar.argument_items[:2])
        lines.append(f"Arguments: {len(ar.argument_items)} items; score "
                     f"{ar.overall_argument_score:.2f}; conclusions: {concl}")
    else:
        lines.append("Arguments: not assessed")
    return "\n".join(lines)

def return_report_node(state: AgentState) -> dict:
    errors = {
        name: err
        for name, err in {
            "source_assessment": state.source_assessment_error,
            "evidence_assessment": state.evidence_assessment_error,
            "argument_assessment": state.argument_assessment_error,
        }.items()
        if err
    }
    errors_text = f"\nAssessment errors:\n{errors}\n" if errors else ""

    prompt = f"""
        Evaluate the claim: {state.claim}

        Assessment summary:
        {_digest(state)}
        {errors_text}
        Instructions:
        - Do not invent missing assessments or scores.
        - Do not treat a failed assessment as a score of zero.
        - Do not claim that all sources were assessed unless the summary confirms it.
        - Do not claim unanimous agreement unless the successful assessments support that conclusion.
        - Distinguish between finding no supporting evidence and an assessment failing to complete.
        - Explicitly state important limitations caused by failed assessments.
        - Calibrate confidence to the available evidence and assessment coverage.
        """

    final_report_value = invoke_with_retry(structured_model_with_final_report, prompt)
    return {"final_report": final_report_value}