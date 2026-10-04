from langgraph.graph import StateGraph, END

from src.agentct.state import AgentState
from src.agentct.models.schemas import SourceOutput, SourceAssessments, KeywordExtraction, FinalReport
from src.agentct.utils.retry import invoke_with_retry

from src.agentct.config import llm

structured_model = llm.with_structured_output(SourceAssessments)
structured_model_with_keywords = llm.with_structured_output(KeywordExtraction)
structured_model_with_final_report = llm.with_structured_output(FinalReport)

def return_report_node(state: AgentState) -> dict:
    prompt = f"Based on the following assessments of the claim '{state.claim}':\n\n" \
             f"Source quality: {state.source_output}\n\n" \
             f"Evidence quality: {state.evidence_output}\n\n" \
             f"Argument quality: {state.arg_output}\n\n" \
             "Please provide a final report summarizing the key points and a clear conclusion."
    final_report_value = invoke_with_retry(structured_model_with_final_report, prompt)
    return {"final_report": final_report_value}