"""
schemas.py
Schemas for the AgentCT models.
"""

from pydantic import BaseModel


"""
For sources:
"""
class SourceAssessment(BaseModel):
    source: str
    stance: str
    benevolence_score: float
    benevolence_reasoning: str
    expertise_score: float
    expertise_reasoning: str

class SourceAssessments(BaseModel):
    source_assessments: list[SourceAssessment]

class SourceOutput(BaseModel):
    source_assessments: list[SourceAssessment]
    concordance_score: float
    concordance_reasoning: str
    overall_confidence: float
    overall_confidence_reasoning: str


"""
For Plausibility:
"""
class PlausibilityOutput(BaseModel):
    plausibility_score: float
    plausibility_reasoning: str

"""
For Evidence:
"""
class EvidenceItem(BaseModel):
    source_id: str
    evidence_type: str
    finding: str
    relevance: str
    strengths: str
    limitations: str
    supporting_passages: list[str]

class EvidenceOutput(BaseModel):
    evidence_items: list[EvidenceItem]
    overall_evidence_score: float
    overall_evidence_reasoning: str

"""
For Arguments:
"""
class ArgumentItem(BaseModel):
    source_id: str
    premises: str
    conclusion: str
    assumptions: str
    counterarguments: str
    weaknesses: str
    supporting_passages: list[str]


class ArgOutput(BaseModel):
    argument_items: list[ArgumentItem]
    overall_argument_score: float
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