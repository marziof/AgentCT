
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


graph = StateGraph(AgentState)

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
    retrieved_docs = search_openalex(query, limit=3)
    return {"retrieved_docs": retrieved_docs}

def assess_source_node(state: AgentState) -> dict:
    # Placeholder for source assessment logic
    prompt = f"Please provide an assessment of the following claim: {state.claim} based on the following sources: {', '.join([doc['title'] for doc in state.retrieved_docs])}. " \
                "For each source, you should provide a stance (support or oppose) with respect to the claim, " \
                "a benevolence score (0-1) that reflects the source's benevolence, as well as benevolence reasoning explaining the score, " \
                "an expertise score (0-1) that reflects the source's expertise, as well as expertise reasoning. "

    structured_response = invoke_with_retry(structured_model, prompt)
    source_assessments = structured_response.source_assessments
    concordance = concordance_score(source_assessments)
    confidence = confidence_score(source_assessments)
    concordance_reasoning = "expert sources agree on the stance" if concordance == 1.0 else "expert sources disagree on the stance"
    confidence_reasoning = "sources support the claim" if confidence == 1.0 else "sources oppose the claim"
    #confidence_reasoning = #llm.invoke(input=f"Please provide a brief reasoning for the overall confidence score of {confidence} based on the source assessments: {source_assessments}.").content
    source_output_value = SourceOutput(
        source_assessments=source_assessments,
        concordance_score=concordance,
        concordance_reasoning=concordance_reasoning,
        overall_confidence=confidence, 
        overall_confidence_reasoning=confidence_reasoning
    )
    return { "source_output": source_output_value }

def return_report_node(state: AgentState) -> dict:
    # Placeholder for returning the final report    
    prompt = f"Based on the source assessment in {state.source_output}, please provide a final report on the claim: {state.claim}. " \
                "Summarize the key points and provide a clear conclusion."
    final_report_value = invoke_with_retry(structured_model_with_final_report, prompt)
    return {"final_report": final_report_value}


graph.add_node("retrieve_sources", retrieve_sources_node)
graph.add_node("source_assessment", assess_source_node)

graph.add_edge("retrieve_sources", "source_assessment")
graph.add_node("return_state", return_report_node)
graph.add_edge("source_assessment", "return_state")

graph.set_entry_point("retrieve_sources")
graph.add_edge("return_state", END)
compiled_graph = graph.compile()