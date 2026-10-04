from langgraph.graph import StateGraph, END

from src.agentct.state import AgentState
from src.agentct.models.schemas import ArgOutput

from src.agentct.utils.retry import invoke_with_retry

from src.agentct.config import llm


# placeholder function to assess the quality of arguments based on the retrieved passages

structured_model_argument = llm.with_structured_output(ArgOutput)


def assess_argument_node(state: AgentState) -> dict:
    if not state.relevant_passages:
        return {
            "arg_output": ArgOutput(
                argument_items=[],
                overall_argument_score=0.0,
                overall_argument_reasoning=(
                    "No relevant passages were retrieved, so the argument "
                    "could not be assessed."
                ),
            )
        }

    passages_text = "\n\n".join(
        f"[Source: {p['source_id']}]\n{p['text']}"
        for p in state.relevant_passages
    )
    prompt = (
        f"Please provide an assessment of the arguments for the following claim: "
        f"{state.claim} based on the following passages:\n\n"
        f"{passages_text}\n\n"

        "For each distinct source represented in the passages, you should provide "
        "an argument item with a source_id identifying the source, "
        
        "premises describing the main claims or propositions from the source "
        "that are used to support its conclusion, "
        
        "a conclusion describing the main conclusion reached by the source "
        "that is relevant to the claim, "
        
        "assumptions describing important assumptions underlying the reasoning "
        "from the premises to the conclusion, "
        
        "counterarguments describing relevant alternative explanations, objections, "
        "or competing interpretations, "
        
        "weaknesses describing the main weaknesses or gaps in the reasoning "
        "(1 sentence), "
        
        "and supporting_passages identifying the most relevant passage from that "
        "source using only its first 3 words followed by '...'. "
        
        "You should then provide an overall_argument_score in the range 0-1 "
        "reflecting the overall quality of the reasoning across the sources, "
        "as well as overall_argument_reasoning explaining the score. "
        
        "Evaluate the quality of the reasoning, not whether the source agrees "
        "with the claim. Do not invent arguments that are not supported by the "
        "provided passages. Multiple passages from the same source must be treated "
        "as belonging to one source, not as independent arguments."
    )

    argument_output = invoke_with_retry(
        structured_model_argument,
        prompt
    )

    return {"arg_output": argument_output}