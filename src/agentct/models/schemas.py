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

class SourceOutput(BaseModel):
    sources: list[SourceAssessment]
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
For Arguments:
"""
class ArgOutput(BaseModel):
    arguments_score: float
    arguments_reasoning: str


"""
For Evidence:
"""
class EvidenceOutput(BaseModel):
    evidence_score: float
    evidence_reasoning: str


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