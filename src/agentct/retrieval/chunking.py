from langchain_text_splitters import RecursiveCharacterTextSplitter


def chunk_text(
    text: str,
    source_id: str = None,
    chunk_size: int = 1500,
    chunk_overlap: int = 200,
    text_basis: str = "full_text",
) -> list[dict]:
    """
    Split text into overlapping chunks.

    Returns:
        A list of dictionaries containing chunk text and metadata,
        including whether the text came from full text or an abstract.
    """

    if not text or not text.strip():
        return []

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )

    chunks = splitter.split_text(text)

    return [
        {
            "chunk_id": i,
            "text": chunk,
            "source_id": source_id,
            "text_basis": text_basis,
        }
        for i, chunk in enumerate(chunks)
    ]