
from langgraph.graph import StateGraph, END

from src.agentct.state import AgentState
from src.agentct.models.schemas import SourceOutput, SourceAssessment

from src.agentct.config import llm

structured_model = llm.with_structured_output(SourceOutput)


graph = StateGraph(AgentState)

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
    final_report_value = llm.invoke(input=prompt).content[0]
    return {"final_report": final_report_value}

graph.add_node("source_assessment", assess_source_node)
graph.add_node("return_state", return_report_node)
graph.add_edge("source_assessment", "return_state")

graph.set_entry_point("source_assessment")
graph.add_edge("return_state", END)
compiled_graph = graph.compile()