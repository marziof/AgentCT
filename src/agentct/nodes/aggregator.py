from langgraph.graph import StateGraph, END

from src.agentct.state import AgentState
from src.agentct.models.schemas import SourceOutput, SourceAssessments, KeywordExtraction, FinalReport
from src.agentct.utils.retry import invoke_with_retry

from src.agentct.config import llm

structured_model = llm.with_structured_output(SourceAssessments)
structured_model_with_keywords = llm.with_structured_output(KeywordExtraction)
structured_model_with_final_report = llm.with_structured_output(FinalReport)

def return_report_node(state: AgentState) -> dict:
    # Placeholder for returning the final report    
    prompt = f"Based on the source assessment in {state.source_output}, please provide a final report on the claim: {state.claim}. " \
                "Summarize the key points and provide a clear conclusion in 2-3 sentences."
    final_report_value = invoke_with_retry(structured_model_with_final_report, prompt)
    return {"final_report": final_report_value}