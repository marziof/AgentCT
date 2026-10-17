
from src.agentct.state import AgentState
from src.agentct.models.schemas import ArgOutput
from src.agentct.utils.retry import invoke_with_retry
from src.agentct.config import llm


structured_model_argument = llm.with_structured_output(ArgOutput, method="json_schema")


def assess_argument_node(state: AgentState) -> dict:
    '''
    Assess the quality of the reasoning in the supplied passages in relation
    to the claim. Return structured output according to the ArgOutput schema.
    '''

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
    
    MAX_PASSAGES = 6
    MAX_CHARS_PER_PASSAGE = 2500

    passages = state.relevant_passages[:MAX_PASSAGES]

    passages_text = "\n\n".join(
        f"[Source ID: {p['source_id']}]\n"
        f"{p['text'][:MAX_CHARS_PER_PASSAGE]}"
        for p in passages
    )


    valid_source_ids = {
        str(p["source_id"])
        for p in state.relevant_passages
        if p.get("source_id") is not None
    }

    prompt = f"""
        Assess the quality of the reasoning in the supplied passages in relation
        to this claim.

        CLAIM:
        {state.claim}

        PASSAGES:
        {passages_text}

        INSTRUCTIONS:

        Return one argument item per distinct source containing a relevant
        argument. Combine multiple passages from the same source into one item.

        Return at most 3 argument items.

        For every argument item, provide these fields according to the schema:

        - 'source_id': the exact source ID shown in the supplied passages.
        - 'premises': a list of up to 3 propositions used to support the conclusion.
        - 'conclusion': the main conclusion relevant to the claim.
        - 'assumptions': a list of up to 3 important assumptions underlying
        the reasoning from premises to conclusion.
        - 'counterarguments': a list of up to 3 relevant objections, alternative
        explanations, or competing interpretations.
        - 'weaknesses': list of at most 3 strings describing the main reasoning weaknesses or gaps (1 sentence for each).
        - 'supporting_passages': a list of strings (at most 3). Each string must identify
        a relevant supplied passage using its first 3 words followed by "...". 

        Use only information supported by the supplied passages.
        Do not invent premises, conclusions, or source IDs.
        If a list category is unsupported, return an empty list.

        Evaluate reasoning quality, not whether the source agrees with the claim.
        Do not treat multiple passages from the same source as independent arguments.

        Set overall_argument_score between 0.0 and 1.0 and explain the score
        in 'overall_argument_reasoning'.

        If no relevant arguments are present, return an empty argument_items
        list and explain why.
        """

    try:
        arg_output = invoke_with_retry(
            structured_model_argument,
            prompt,
        )

        unexpected_ids = {
            str(item.source_id)
            for item in arg_output.argument_items
        } - valid_source_ids

        if unexpected_ids:
            raise ValueError(
                f"Unknown source IDs in argument output: {unexpected_ids}"
            )

        arg_output.argument_items = arg_output.argument_items[:3]
        for item in arg_output.argument_items:
            item.supporting_passages = item.supporting_passages[:3]

        return {
            "arg_output": arg_output,
            "argument_assessment_error": None,
        }


    except Exception as exc:
        return {
            "arg_output": ArgOutput(
                argument_items=[],
                overall_argument_score=0.0,
                overall_argument_reasoning=(
                    "Argument assessment failed. "
                    f"Error type: {type(exc).__name__}. "
                    "The score is a fallback, not a genuine "
                    "assessment of argument quality."
                ),
            ),
            "argument_assessment_error": (
                f"{type(exc).__name__}: {exc}"
            ),
        }
