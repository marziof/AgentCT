from langgraph.graph import StateGraph, END

from src.agentct.state import AgentState
from src.agentct.models.schemas import SourceOutput, SourceAssessments, KeywordExtraction, FinalReport
from src.agentct.retrieval.openalex import search_openalex
from src.agentct.utils.retry import invoke_with_retry

from src.agentct.config import llm

structured_model = llm.with_structured_output(SourceAssessments)
structured_model_with_keywords = llm.with_structured_output(KeywordExtraction)
structured_model_with_final_report = llm.with_structured_output(FinalReport)


def retrieve_sources_node(state: AgentState) -> dict:
    # use few shot prompting to extract key words from the claim and use them to query OpenAlex for relevant sources

    prompt = f"Please extract the key words for the following claim: {state.claim}. " \
             "The words should be neutral in tone and relevant to the claim.\n" \
             "Here are a few examples of key words to be extracted from input claims:\n" \
             "example 1: Smoking is good for your health. -> keywords: smoking, health, impact\n" \
             "example 2: Is eating meat beneficial for your health? -> keywords: eating meat, health, impact\n" \
             "example 3: Are vaccines safe and effective? -> keywords: vaccines, safety, effectiveness\n"
    
    key_words_response = invoke_with_retry(structured_model_with_keywords, prompt)
    query = key_words_response.keywords
    print(f"Extracted key words: {query}")
    retrieved_docs = search_openalex(query, limit=5)
    return {"retrieved_docs": retrieved_docs}