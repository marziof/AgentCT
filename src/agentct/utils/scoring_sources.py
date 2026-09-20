"""
Calculate the concordance between expert sources.
Function to be called after assessing each source, to complete the source criterion.
"""
from pathlib import Path
import sys
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

from typing import List

from src.agentct.models.schemas import SourceAssessments, SourceAssessment



def concordance_score(sources: SourceAssessments) -> float:
    """
    Calculate the concordance score between expert sources.

    Args:
        sources (list): A list of source assessments, each containing a stance and an expertise score.

    Returns:
        float: The concordance score (0-1) between expert sources.
    """
    expert_sources = [s for s in sources if s.expertise_score > 0.5]  # Consider sources with expertise score > 0.5 as experts
    if not expert_sources:
        return 0.0  # No expert sources to compare

    stances = [s.stance for s in expert_sources]
    # concordance as proportion of expert sources that agree on the stance
    max_stance_count = max(stances.count("support"), stances.count("oppose"))
    concordance = max_stance_count / len(expert_sources)
    return concordance


def confidence_score(sources: SourceAssessments) -> float:
    """
    Calculate the overall confidence score in a claim based on the concordance, benevolence, and expertise scores of sources.

    Args:
        sources (list): A list of source assessments, each containing a stance and an expertise score.
        concordance (float): The concordance score (0-1) between expert sources.

    Returns:
        float: The overall confidence score (0-1) in the claim.
    """
    def stance_value(source: SourceAssessment) -> float:
        if source.stance == "support":
            return 1.0
        elif source.stance == "oppose":
            return 0.0
        else:
            return 0.5

    def weight(source: SourceAssessment) -> float:
        return source.benevolence_score * source.expertise_score

    # overall confidence in claim is high if benevolent and expert sources agree that it is true, low if they agree on the opposite, and mid if they disagree
    weighted_stance = sum(stance_value(s) * weight(s) for s in sources) / sum(weight(s) for s in sources)
    return weighted_stance