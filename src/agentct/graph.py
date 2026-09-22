
from langgraph.graph import StateGraph, END

from src.agentct.state import AgentState
from src.agentct.nodes.retrieval import retrieve_sources_node
from src.agentct.nodes.source_quality import assess_source_node
from src.agentct.nodes.aggregator import return_report_node

graph = StateGraph(AgentState)


graph.add_node("retrieve_sources", retrieve_sources_node)
graph.add_node("source_assessment", assess_source_node)

graph.add_edge("retrieve_sources", "source_assessment")
graph.add_node("return_state", return_report_node)
graph.add_edge("source_assessment", "return_state")

graph.set_entry_point("retrieve_sources")
graph.add_edge("return_state", END)
compiled_graph = graph.compile()