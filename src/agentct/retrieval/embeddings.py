from sentence_transformers import SentenceTransformer

model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')


def embed_chunks(chunks: list[dict], embedding_model) -> list[dict]:
    """
    Embed each chunk using the specified embedding model.

    Args:
        chunks: A list of dictionaries containing chunk text and metadata.
        embedding_model: The embedding model to use for generating embeddings.

    Returns:
        A list of dictionaries containing chunk text, metadata, and embeddings.
    """
    texts = [chunk["text"] for chunk in chunks]
    embeddings = embedding_model.encode(texts)
    for chunk, embedding in zip(chunks, embeddings):
        chunk["embedding"] = embedding
    return chunks

def embed_claim(claim: str, embedding_model) -> list[float]:
    """
    Embed the claim using the specified embedding model.

    Args:
        claim: The claim text to embed.
        embedding_model: The embedding model to use for generating embeddings.

    Returns:
        A list of floats representing the claim's embedding.
    """
    return embedding_model.encode(claim)


import numpy as np
def retrieve_relevant_passages(claim_embedding, embedded_chunks: list[dict], top_k: int = 5) -> list[dict]:
    """
    Rank chunks by cosine similarity to the claim and return the top-k most relevant.

    Args:
        claim_embedding: The embedded claim (from embed_claim).
        embedded_chunks: Chunks with 'embedding' populated (from embed_chunks).
        top_k: Number of top-ranked chunks to return.

    Returns:
        list[dict]: The top-k chunks, each with a 'similarity' score added, sorted descending.
    """
    claim_vec = np.array(claim_embedding)
    claim_norm = claim_vec / np.linalg.norm(claim_vec)

    scored_chunks = []
    for chunk in embedded_chunks:
        chunk_vec = np.array(chunk["embedding"])
        chunk_norm = chunk_vec / np.linalg.norm(chunk_vec)
        similarity = float(np.dot(claim_norm, chunk_norm))
        scored_chunks.append({**chunk, "similarity": similarity})

    scored_chunks.sort(key=lambda c: c["similarity"], reverse=True)
    return scored_chunks[:top_k]
