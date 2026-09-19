
from langgraph.graph import StateGraph, END

from src.agentct.state import AgentState
from src.agentct.models.schemas import SourceOutput, SourceAssessment

graph = StateGraph(AgentState)

def assess_source_node(state: AgentState) -> dict:
    # Placeholder for source assessment logic
    # Here you would implement the logic to assess the sources based on the claim and retrieved documents
    # For now, we will just return the state as is
    source_assessments = [
        SourceAssessment(
            source="doc1",
            stance="against",
            benevolence_score=0.9,
            benevolence_reasoning="No clear evidence of malevolence.",
            expertise_score=0.8,
            expertise_reasoning="The source has expertise but is not definitive."
        ), 
        SourceAssessment(
                    source="doc2",
                    stance="against",
                    benevolence_score=0.9,
                    benevolence_reasoning="No clear evidence of benevolence or malevolence.",
                    expertise_score=0.9,
                    expertise_reasoning="The source has expertise."
        )
    ]
    source_output_value = SourceOutput(
        sources=source_assessments,
        concordance_score=1.0,
        concordance_reasoning="",
        overall_confidence=0.0,
        overall_confidence_reasoning="Claim is not supported by the evidence."
    )
    return { "source_output": source_output_value }

def return_report_node(state: AgentState) -> dict:
    # Placeholder for returning the final report    
    final_report_value = "Final report: The claim should not be trusted as it is not supported by the evidence from sources."
    return {"final_report": final_report_value}

graph.add_node("source_assessment", assess_source_node)
graph.add_node("return_state", return_report_node)
graph.add_edge("source_assessment", "return_state")

graph.set_entry_point("source_assessment")
graph.add_edge("return_state", END)
compiled_graph = graph.compile()