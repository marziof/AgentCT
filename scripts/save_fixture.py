from pathlib import Path
import sys
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

import json
from src.agentct.state import AgentState
from src.agentct.nodes.retrieval import search_sources_node, retrieve_passages_node

claim = "Smoking tobacco is beneficial for your health."
slug = "smoking"

state = AgentState(claim=claim)
state = state.model_copy(update=search_sources_node(state))
state = state.model_copy(update=retrieve_passages_node(state))

# Embeddings are numpy arrays and not JSON-serializable; drop them.
passages = [{k: v for k, v in p.items() if k != "embedding"} for p in state.relevant_passages]

out = Path("tests/fixtures"); out.mkdir(parents=True, exist_ok=True)
(out / f"{slug}.json").write_text(json.dumps(
    {"claim": claim, "retrieved_docs": state.retrieved_docs, "relevant_passages": passages},
    indent=2, default=str))