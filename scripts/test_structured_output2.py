
from pathlib import Path
import sys
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))
from src.agentct.config import llm
from src.agentct.models.schemas import EvidenceOutput


ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

from src.agentct.config import llm
from src.agentct.models.schemas import ArgOutput

structured_model = llm.with_structured_output(ArgOutput)

result = structured_model.invoke(
    """
    Return an ArgOutput with exactly these required fields:
    - argument_items: an empty list
    - overall_argument_score: 0.0
    - overall_argument_reasoning: a short explanation that no argument
      items were supplied.

    Include every required field. Do not omit any fields.
    Do not invent arguments.
    """
)

print(result)
print(type(result))

