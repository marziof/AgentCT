
from src.agentct.state import AgentState
from src.agentct.models.schemas import EvidenceOutput, EvidenceAssessments
from src.agentct.utils.retry import invoke_with_retry
from src.agentct.config import llm


LEVELS = {"low": 0.3, "medium": 0.6, "high": 0.9}

structured_model_evidence = llm.with_structured_output(EvidenceAssessments, method="json_schema")
def assess_evidence_node(state: AgentState) -> dict:
    '''
    Assess the quality of the evidence available for the claim based on the
    relevant passages retrieved. Return structured output according to the
    EvidenceOutput schema.
    '''

    if not state.relevant_passages:
        return {
            "evidence_output": EvidenceOutput(
                evidence_items=[],
                overall_evidence_score=0.0,
                overall_evidence_reasoning=(
                    "No relevant passages were retrieved, so the evidence "
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
        Assess the quality of the evidence available for this claim.

        CLAIM:
        {state.claim}

        PASSAGES:
        {passages_text}

        INSTRUCTIONS:

        Return one evidence item per distinct source that contains relevant
        evidence, combining all passages from the same source.

        Return at most 3 evidence items.

        For every evidence item, provide these fields according to the schema:

        - source_id: the exact source ID shown in the supplied passages.
        - evidence_type: the type of evidence, such as experimental,
        observational, review, or theoretical. Do not guess details that
        the passages do not establish.
        - finding: the main finding relevant to the claim.
        - relevance: explain how directly the evidence addresses the claim.
        - strengths: the main strengths of the evidence.
        - limitations: one sentence describing important limitations.
        - supporting_passages: a list of strings. Each string must identify
        a relevant supplied passage using its first 3 words followed by "...".
        - reliability: "low", "medium", or "high", based only on the study design the
        passages actually establish. low = narrative review, opinion, or description
        without data; medium = observational study, or a review of observational
        studies; high = randomized trial or meta-analysis of randomized trials.
        Do not rate above "medium" unless the passages establish the design.

        Use only information supported by the supplied passages.
        Do not invent study designs, findings, sample sizes, or source IDs.

        Assess evidence quality independently of whether the evidence supports
        or contradicts the claim. Consider relevance, methodological information
        actually provided, and limitations.

        Write overall_evidence_reasoning as at most 2 sentences summarizing the
        quality of the evidence. Do not output a numeric score.

        If no supplied passages contain evidence relevant to the claim,
        return an empty evidence_items list and explain why.
        """

    try:
        assessments = invoke_with_retry(structured_model_evidence, prompt)

        unexpected_ids = {str(i.source_id) for i in assessments.evidence_items} - valid_source_ids
        if unexpected_ids:
            raise ValueError(f"Unknown source IDs in evidence output: {unexpected_ids}")

        items = assessments.evidence_items[:3]
        for item in items:
            item.supporting_passages = item.supporting_passages[:3]

        score = sum(LEVELS[i.reliability] for i in items) / len(items) if items else 0.0

        evidence_output = EvidenceOutput(
            evidence_items=items,
            overall_evidence_score=score,
            overall_evidence_reasoning=assessments.overall_evidence_reasoning,
        )

        return {
            "evidence_output": evidence_output,
            "evidence_assessment_error": None,
        }

    except Exception as exc:
        # This is a failure fallback, not a genuine quality assessment.
        return {
            "evidence_output": EvidenceOutput(
                evidence_items=[],
                overall_evidence_score=0.0,
                overall_evidence_reasoning=(
                    "Evidence assessment failed. "
                    f"Error type: {type(exc).__name__}. "
                    "The score is a fallback, not an assessment "
                    "of evidence quality."
                ),
            ),
            "evidence_assessment_error": (
                f"{type(exc).__name__}: {exc}"
            ),
        }
