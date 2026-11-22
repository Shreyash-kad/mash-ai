import faiss
import numpy as np


# ==================================================
# CONFIG
# ==================================================

DIMENSION = 384


# ==================================================
# FAISS INDEX
# ==================================================

index = faiss.IndexFlatL2(DIMENSION)


# ==================================================
# DOCUMENT / CHUNK STORAGE
# ==================================================

documents = []


# ==================================================
# ADD DOCUMENT CHUNK
# ==================================================

def add_document(
    text,
    embedding,
    metadata=None
):
    """
    Add one text chunk to FAISS.

    metadata keeps information about where
    the chunk came from.
    """

    if not text or not text.strip():
        return

    vector = np.array(
        [embedding],
        dtype="float32"
    )

    index.add(vector)

    documents.append({
        "text": text,
        "metadata": metadata or {}
    })


# ==================================================
# SEARCH
# ==================================================

def search(
    query_embedding,
    k=5,
    chat_id=None,
    filename=None,
    document_id=None
):
    """
    Search for relevant document chunks.

    Optional filters:
        chat_id
        filename
        document_id
    """

    if index.ntotal == 0:
        return []

    vector = np.array(
        [query_embedding],
        dtype="float32"
    )

    # ------------------------------------------------
    # IMPORTANT
    # ------------------------------------------------
    # If we have a filter, search all vectors first.
    #
    # Otherwise FAISS might return the top 5 chunks
    # from other documents and THEN we filter them out.
    #
    # That can cause relevant chunks to disappear.
    # ------------------------------------------------

    if (
        chat_id is not None
        or filename is not None
        or document_id is not None
    ):
        actual_k = index.ntotal
    else:
        actual_k = min(k, index.ntotal)

    distances, indices = index.search(
        vector,
        actual_k
    )

    results = []

    for idx, distance in zip(
        indices[0],
        distances[0]
    ):

        if idx == -1:
            continue

        document = documents[idx]

        metadata = document.get(
            "metadata",
            {}
        )

        # ==================================================
        # CHAT FILTER
        # ==================================================

        if chat_id is not None:

            stored_chat_id = metadata.get(
                "chat_id"
            )

            if str(stored_chat_id) != str(chat_id):
                continue


        # ==================================================
        # FILE FILTER
        # ==================================================

        if filename is not None:

            stored_filename = metadata.get(
                "file"
            )

            if stored_filename != filename:
                continue


        # ==================================================
        # DOCUMENT ID FILTER
        # ==================================================

        if document_id is not None:

            stored_document_id = metadata.get(
                "document_id"
            )

            if str(stored_document_id) != str(document_id):
                continue


        # ==================================================
        # SAVE RESULT
        # ==================================================

        results.append({
            "text": document["text"],
            "metadata": metadata,
            "distance": float(distance)
        })


    # ==================================================
    # SORT BY RELEVANCE
    # ==================================================

    results.sort(
        key=lambda item: item["distance"]
    )


    # Return only requested number
    return results[:k]


# ==================================================
# CLEAR INDEX
# ==================================================

def clear_index():

    global index
    global documents

    index = faiss.IndexFlatL2(
        DIMENSION
    )

    documents = []


# ==================================================
# INDEX INFO
# ==================================================

def get_index_size():

    return index.ntotal


# ==================================================
# GET ALL INDEXED DOCUMENTS
# ==================================================

def get_indexed_documents():

    files = {}

    for document in documents:

        metadata = document.get(
            "metadata",
            {}
        )

        filename = metadata.get(
            "file",
            "Unknown"
        )

        document_id = metadata.get(
            "document_id"
        )

        if filename not in files:

            files[filename] = {
                "filename": filename,
                "document_id": document_id,
                "chunks": 0
            }

        files[filename]["chunks"] += 1


    return list(files.values())