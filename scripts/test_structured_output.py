
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

from src.agentct.models.schemas import SourceOutput, SourceAssessment
from src.agentct.config import llm

#model = llm
structured_model = (llm.with_structured_output(SourceOutput))



template = "Please provide an assessment of the following claim: {claim} based on the following sources: {source_list}. " \
"For each source, you should provide a stance with respect to the claim, " \
"a benevolence score (0-1), benevolence reasoning, expertise score (0-1), expertise reasoning, " \
"and then overall a concordance score (0-1) between expert sources, concordance reasoning, and overall confidence in the claim (0-1) (0 being that claim is not supported by the evidence), and overall confidence reasoning."

claim = "Smoking tobacco is beneficial for your health."
source_list = [
    "Source 1: The Grey Hoodie Project: Big Tobacco, Big Tech, and the Threat on Academic Integrity",
    "Source 2: Spatial, temporal, and demographic patterns in prevalence of smoking tobacco use and attributable disease burden in 204 countries and territories, 1990–2019: a systematic analysis from the Global Burden of Disease Study 2019",
    "Source 3: A 1950s cigarette advertisement claiming that doctors preferred a particular cigarette brand."
]
prompt = template.format(claim=claim,source_list=", ".join(source_list))


structured_response = structured_model.invoke(
    input=prompt
)

print(structured_response)