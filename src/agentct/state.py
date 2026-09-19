from typing import List, Optional#, TypedDict
from pydantic import BaseModel

from src.agentct.models.schemas import SourceOutput, PlausibilityOutput, ArgOutput, EvidenceOutput, MetaOutput

class AgentState(BaseModel):
    claim: str
    retrieved_docs: List[dict]
    source_output: Optional[SourceOutput]
    plausibility_output: Optional[PlausibilityOutput]
    arg_output: Optional[ArgOutput] 
    evidence_output: Optional[EvidenceOutput]
    meta_output: Optional[MetaOutput]
    final_report: Optional[str]


    

