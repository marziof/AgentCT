from typing import List, Optional#, TypedDict
from pydantic import BaseModel

from src.agentct.models.schemas import * #SourceOutput, PlausibilityOutput, ArgOutput, EvidenceOutput, MetaOutput, F

class AgentState(BaseModel):
    claim: str
    retrieved_docs: List[dict]
    relevant_passages: Optional[List[dict]] = []
    source_output: Optional[SourceOutput] = None
    plausibility_output: Optional[PlausibilityOutput] = None
    arg_output: Optional[ArgOutput] = None
    evidence_output: Optional[EvidenceOutput] = None
    meta_output: Optional[MetaOutput] = None
    final_report: Optional[FinalReport] = None
    source_assessment_error: Optional[str] = None
    evidence_assessment_error: Optional[str] = None
    argument_assessment_error: Optional[str] = None
    retrieval_stats: Optional[dict] = None


    

