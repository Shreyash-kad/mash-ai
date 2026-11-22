def split_text(
    text,
    chunk_size=800,
    overlap=150
):
    """
    Split document text into overlapping chunks.
    """

    if not text:
        return []

    text = text.strip()

    if not text:
        return []

    chunks = []

    start = 0

    step = chunk_size - overlap

    while start < len(text):

        end = start + chunk_size

        chunk = text[start:end].strip()

        if chunk:

            chunks.append(chunk)

        start += step

    return chunks