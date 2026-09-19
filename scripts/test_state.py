from pathlib import Path
import sys
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

from src.agentct.state import AgentState

claim = "Smoking tobacco is beneficial for your health."
retrieved_docs = [
    {"title": "The Grey Hoodie Project: Big Tobacco, Big Tech, and the Threat on Academic Integrity", "content": "This source discusses the influence of big tobacco and big tech on academic integrity."},
    {"title": "Spatial, temporal, and demographic patterns in prevalence of smoking tobacco use and attributable disease burden in 204 countries and territories, 1990–2019: a systematic analysis from the Global Burden of Disease Study 2019", "content": "This source provides a systematic analysis of smoking tobacco use and its health impacts across various countries and demographics."},    
{"title": "A 1950s cigarette advertisement claiming that doctors preferred a particular cigarette brand.", "content": "This source is a historical advertisement from the 1950s that claims doctors preferred a specific cigarette brand."}
]

AgentState_instance = AgentState(
    claim=claim,
    retrieved_docs=retrieved_docs,
    source_output=None,
    plausibility_output=None,
    arg_output=None,
    source_assessment=None,
    evidence_output=None,
    meta_output=None
)