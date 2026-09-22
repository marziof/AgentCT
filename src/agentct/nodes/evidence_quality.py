from langgraph.graph import StateGraph, END

from src.agentct.state import AgentState
from src.agentct.models.schemas import SourceOutput, SourceAssessments, KeywordExtraction, FinalReport
from src.agentct.retrieval.openalex import search_openalex

from src.agentct.utils.scoring_sources import concordance_score, confidence_score
from src.agentct.utils.retry import invoke_with_retry

from src.agentct.config import llm

structured_model = llm.with_structured_output(SourceAssessments)
structured_model_with_keywords = llm.with_structured_output(KeywordExtraction)
structured_model_with_final_report = llm.with_structured_output(FinalReport)