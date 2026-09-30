from langchain_text_splitters import RecursiveCharacterTextSplitter


def chunk_text(
    text: str,
    source_id: str = None,
    chunk_size: int = 1500,
    chunk_overlap: int = 200,
) -> list[dict]:
    """
    Split full text into overlapping chunks.

    Returns:
        A list of dictionaries containing chunk text and metadata.
    """

    if not text:
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
            "source_id": source_id
        }
        for i, chunk in enumerate(chunks)
    ]