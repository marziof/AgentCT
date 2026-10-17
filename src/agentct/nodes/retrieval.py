from langgraph.graph import StateGraph, END

from src.agentct.state import AgentState
from src.agentct.models.schemas import SourceOutput, SourceAssessments, KeywordExtraction, FinalReport
from src.agentct.retrieval.openalex import search_openalex, reconstruct_abstract
from src.agentct.retrieval.europepmc import search_europepmc
from src.agentct.retrieval.mergesources import merge_sources
from src.agentct.utils.retry import invoke_with_retry
from src.agentct.retrieval.fulltext import retrieve_fulltext
from src.agentct.retrieval.chunking import chunk_text
from src.agentct.retrieval.embeddings import embed_chunks, embed_claim, model, retrieve_relevant_passages

from src.agentct.config import llm

#structured_model = llm.with_structured_output(SourceAssessments)
structured_model_with_keywords = llm.with_structured_output(KeywordExtraction, method="json_schema")
#structured_model_with_final_report = llm.with_structured_output(FinalReport)



def rank_sources_by_relevance(claim, sources, model, top_n=6, min_similarity=0.25):
    texts = [f"{s.get('title', '')}. {s.get('content', '')}" for s in sources]
    claim_vec = model.encode(claim, normalize_embeddings=True)
    doc_vecs = model.encode(texts, normalize_embeddings=True)
    sims = doc_vecs @ claim_vec
    ranked = sorted(zip(sims, sources), key=lambda x: x[0], reverse=True)
    return [s for sim, s in ranked if sim >= min_similarity][:top_n]




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
    openalex_results = search_openalex(query, limit=10)
    europepmc_results = search_europepmc(query, limit=10)
    merged_sources = merge_sources(openalex_results, europepmc_results)

    sources_ranked = rank_sources_by_relevance(state.claim, merged_sources, model, top_n=6, min_similarity=0.25)
    
    return {"retrieved_docs": sources_ranked}


def retrieve_passages_node(state: AgentState) -> dict:
    all_chunks = []
    fulltext_count = 0
    abstract_count = 0
    no_text_sources = []

    for source in state.retrieved_docs:
        source_id = (
            source.get("pmcid")
            or source.get("doi")
            or source.get("id")
            or source.get("openalex_id")
        )

        result = retrieve_fulltext(source)
        fulltext = result.get("fulltext") or ""

        if fulltext.strip():
            text = fulltext
            text_basis = "full_text"
            fulltext_count += 1
        else:
            #================================
            print("\n=== ABSTRACT DEBUG ===")
            print("Title:", source.get("title"))
            print("Source URL:", source.get("url"))
            print("Source ID:", source.get("openalex_id"))
            print("PMCID:", source.get("pmcid"))
            print("DOI:", source.get("doi"))

            for key in (
                "abstract",
                "abstractText",
                "abstract_inverted_index",
                "content",
            ):
                value = source.get(key)
                print(
                    f"{key}: type={type(value).__name__}, "
                    f"length={len(value) if isinstance(value, (str, dict)) else 'N/A'}, "
                    f"preview={repr(value)[:500]}"
                )
            #================================
            abstract = (
                source.get("abstract")
                or source.get("abstractText")
                or source.get("abstract_inverted_index")
                or source.get("content")
                or ""
            )

            if isinstance(abstract, dict):
                abstract = reconstruct_abstract(abstract)

            text = abstract if isinstance(abstract, str) else ""

            if text.strip():
                text_basis = "abstract"
                abstract_count += 1
            else:
                no_text_sources.append({
                    "source_id": str(source_id) if source_id else None,
                    "title": source.get("title", ""),
                    "reason": "No usable full text or abstract",
                })
                continue

        chunks = chunk_text(
            text,
            source_id=source_id,
            text_basis=text_basis,
        )
        all_chunks.extend(chunks)

    if not all_chunks:
        return {
            "relevant_passages": [],
            "retrieval_stats": {
                "fulltext_sources": fulltext_count,
                "abstract_sources": abstract_count,
                "sources_without_text": len(no_text_sources),
                "no_text_sources": no_text_sources,
            },
        }

    embedded_chunks = embed_chunks(all_chunks, model)
    claim_embedding = embed_claim(state.claim, model)

    top_passages = retrieve_relevant_passages(
        claim_embedding,
        embedded_chunks,
        top_k=5,
    )

    return {
        "relevant_passages": top_passages,
        "retrieval_stats": {
            "fulltext_sources": fulltext_count,
            "abstract_sources": abstract_count,
            "sources_without_text": len(no_text_sources),
            "no_text_sources": no_text_sources,
        },
    }