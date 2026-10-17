"""
schemas.py
Schemas for the AgentCT models.
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Literal



"""
For sources:
"""

class SourceAssessment(BaseModel):
    source: str = Field(description="The source's title, copied exactly as given")
    stance: str = Field(description="'support' or 'oppose' toward the claim")
    benevolence_score: float = Field(description="Number between 0 and 1 only, no text")
    benevolence_reasoning: str = Field(description="One short sentence")
    expertise_score: float = Field(description="Number between 0 and 1 only, no text")
    expertise_reasoning: str = Field(description="One short sentence")

class SourceAssessments(BaseModel):
    source_assessments: list[SourceAssessment]

class SourceOutput(BaseModel):
    source_assessments: list[SourceAssessment]
    concordance_score: float
    concordance_reasoning: str
    overall_support: float
    overall_support_reasoning: str


"""
For Plausibility:
"""
class PlausibilityOutput(BaseModel):
    plausibility_score: float
    plausibility_reasoning: str



class StrictOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")


"""
For Evidence:
"""
class EvidenceItem(StrictOutput):
    source_id: str
    evidence_type: str
    finding: str
    relevance: str
    strengths: str
    limitations: str
    reliability: Literal["low", "medium", "high"]
    supporting_passages: list[str] = Field(
        default_factory=list,
        description="At most 3 items, each a short quote or label from the supplied passages",
    )

class EvidenceAssessments(StrictOutput):      # bind the LLM to this
    evidence_items: list[EvidenceItem] = Field(default_factory=list, description="At most 3 items")
    overall_evidence_reasoning: str

class EvidenceOutput(StrictOutput):           # what goes in state
    evidence_items: list[EvidenceItem]
    overall_evidence_score: float = Field(ge=0.0, le=1.0)
    overall_evidence_reasoning: str

# class EvidenceOutput(StrictOutput):
#     evidence_items: list[EvidenceItem] = Field(
#         default_factory=list,
#         description="At most 3 short sentences or labels",
#     )
#     overall_evidence_score: float = Field(ge=0.0, le=1.0)
#     overall_evidence_reasoning: str

"""
For Arguments:
"""

class ArgumentItem(BaseModel):
    source_id: str
    premises: list[str]
    conclusion: str
    assumptions: list[str]
    counterarguments: list[str]
    weaknesses: list[str] = Field(default_factory=list)
    supporting_passages: list[str] = Field(
        default_factory=list,
        description="At most 3 short quotes or labels",
    )


class ArgOutput(StrictOutput):
    argument_items: list[ArgumentItem] = Field(max_length=3)
    overall_argument_score: float = Field(ge=0.0, le=1.0)
    overall_argument_reasoning: str


"""
For Metacognition:
"""
class MetaOutput(BaseModel):
    metacognition_score: float
    metacognition_reasoning: str


"""
For Keywords extraction:
"""
class KeywordExtraction(BaseModel):
    """
    keywords: str = Field(description="Comma-separated keywords only, no labels or extra text")
    """
    keywords: str


"""
For Final report:
"""
class FinalReport(BaseModel):
    """
    keywords: str = Field(description="Comma-separated keywords only, no labels or extra text")
    """
    conclusion: str
    confidence: float
    key_reasoning: str