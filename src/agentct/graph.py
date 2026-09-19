
from langgraph.graph import StateGraph, END

from src.agentct.state import AgentState
from src.agentct.models.schemas import SourceOutput, SourceAssessment, KeywordExtraction, FinalReport
from src.agentct.retrieval.openalex import search_openalex

from src.agentct.config import llm

structured_model = llm.with_structured_output(SourceOutput)
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
    
    key_words_response = structured_model_with_keywords.invoke(input=prompt)
    query = key_words_response.keywords
    print(f"Extracted key words: {query}")
    retrieved_docs = search_openalex(query, limit=3)
    return {"retrieved_docs": retrieved_docs}

def assess_source_node(state: AgentState) -> dict:
    # Placeholder for source assessment logic
    prompt = f"Please provide an assessment of the following claim: {state.claim} based on the following sources: {', '.join([doc['title'] for doc in state.retrieved_docs])}. " \
                "For each source, you should provide a stance with respect to the claim, " \
                "a benevolence score (0-1), benevolence reasoning, expertise score (0-1), expertise reasoning, " \
                "and then overall a concordance score (0-1) between expert sources, concordance reasoning, and overall confidence in the claim (0-1) (0 being that claim is not supported by the evidence), and overall confidence reasoning."
    structured_response = structured_model.invoke(input=prompt)
    source_output_value = structured_response
    return { "source_output": source_output_value }

def return_report_node(state: AgentState) -> dict:
    # Placeholder for returning the final report    
    prompt = f"Based on the source assessment in {state.source_output}, please provide a final report on the claim: {state.claim}. " \
                "Summarize the key points and provide a clear conclusion."
    final_report_value = structured_model_with_final_report.invoke(input=prompt)
    return {"final_report": final_report_value}


graph.add_node("retrieve_sources", retrieve_sources_node)
graph.add_node("source_assessment", assess_source_node)

graph.add_edge("retrieve_sources", "source_assessment")
graph.add_node("return_state", return_report_node)
graph.add_edge("source_assessment", "return_state")

graph.set_entry_point("retrieve_sources")
graph.add_edge("return_state", END)
compiled_graph = graph.compile()