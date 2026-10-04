
from langgraph.graph import StateGraph, END

from src.agentct.state import AgentState
from src.agentct.nodes.retrieval import  search_sources_node, retrieve_passages_node
from src.agentct.nodes.source_quality import assess_source_node
from src.agentct.nodes.evidence_quality import assess_evidence_node
from src.agentct.nodes.argument_quality import assess_argument_node
from src.agentct.nodes.aggregator import return_report_node

graph = StateGraph(AgentState)


graph.add_node("retrieve_sources", search_sources_node)
graph.add_node("retrieve_passages", retrieve_passages_node)
graph.add_node("source_assessment", assess_source_node)
graph.add_node("evidence_assessment", assess_evidence_node)
graph.add_node("argument_assessment", assess_argument_node)
graph.add_node("return_state", return_report_node)


graph.add_edge("retrieve_sources", "retrieve_passages")
graph.add_edge("retrieve_sources", "source_assessment")
graph.add_edge("retrieve_passages", "evidence_assessment")
graph.add_edge("retrieve_passages", "argument_assessment")
graph.add_edge("source_assessment", "return_state")
graph.add_edge("evidence_assessment", "return_state")
graph.add_edge("argument_assessment", "return_state")

graph.set_entry_point("retrieve_sources")
graph.add_edge("return_state", END)
compiled_graph = graph.compile()