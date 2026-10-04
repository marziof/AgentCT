from langgraph.graph import StateGraph, END

from src.agentct.state import AgentState
from src.agentct.models.schemas import SourceOutput, SourceAssessments, KeywordExtraction, FinalReport
from src.agentct.retrieval.openalex import search_openalex
from src.agentct.retrieval.europepmc import search_europepmc
from src.agentct.retrieval.mergesources import merge_sources
from src.agentct.utils.retry import invoke_with_retry
from src.agentct.retrieval.fulltext import retrieve_fulltext
from src.agentct.retrieval.chunking import chunk_text
from src.agentct.retrieval.embeddings import embed_chunks, embed_claim, model, retrieve_relevant_passages

from src.agentct.config import llm

structured_model = llm.with_structured_output(SourceAssessments)
structured_model_with_keywords = llm.with_structured_output(KeywordExtraction)
structured_model_with_final_report = llm.with_structured_output(FinalReport)



def search_sources_node(state: AgentState) -> dict:
    # use few shot prompting to extract key words from the claim and use them to query OpenAlex for relevant sources

    prompt = f"Please extract the key words for the following claim: {state.claim}. " \
             "The words should be neutral in tone and relevant to the claim.\n" \
             "Here are a few examples of key words to be extracted from input claims:\n" \
             "example 1: Smoking is good for your health. -> keywords: smoking, health, impact\n" \
             "example 2: Is eating meat beneficial for your health? -> keywords: eating meat, health, impact\n" \
             "example 3: Are vaccines safe and effective? -> keywords: vaccines, safety, effectiveness\n"
    
    key_words_response = invoke_with_retry(structured_model_with_keywords, prompt)
    query = key_words_response.keywords
    print(f"Extracted key words: {query}")
    # Retrieve documents from different sources
    openalex_results = search_openalex(query, limit=5)
    europepmc_results = search_europepmc(query, limit=5)
    merged_sources = merge_sources(openalex_results, europepmc_results)

    return {"retrieved_docs": merged_sources}



def retrieve_passages_node(state: AgentState) -> dict:
    all_chunks = []
    for source in state.retrieved_docs:
        result = retrieve_fulltext(source)
        if not result.get("fulltext"):
            continue
        chunks = chunk_text(result["fulltext"], source_id=source.get("pmcid") or source.get("doi"))
        all_chunks.extend(chunks)

    if not all_chunks:
        return {"relevant_passages": []}

    embedded_chunks = embed_chunks(all_chunks, model)
    claim_embedding = embed_claim(state.claim, model)
    top_passages = retrieve_relevant_passages(claim_embedding, embedded_chunks, top_k=8)

    return {"relevant_passages": top_passages}