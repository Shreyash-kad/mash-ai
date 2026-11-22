from backend.chunker import split_text
from backend.embeddings import create_embedding

from backend.vector_store import (
    add_document,
    search
)


# ==================================================
# INDEX DOCUMENT
# ==================================================

def index_document(
    text,
    filename,
    chat_id=None,
    document_id=None
):
    """
    Split a document into chunks,
    create embeddings and store them in FAISS.
    """

    if not text or not text.strip():
        return 0


    # ==================================================
    # CREATE CHUNKS
    # ==================================================

    chunks = split_text(text)

    total_chunks = 0


    # ==================================================
    # INDEX EACH CHUNK
    # ==================================================

    for chunk in chunks:

        if not chunk or not chunk.strip():
            continue


        # ------------------------------------------------
        # CREATE EMBEDDING
        # ------------------------------------------------

        embedding = create_embedding(
            chunk
        )


        # ------------------------------------------------
        # STORE CHUNK
        # ------------------------------------------------

        add_document(

            text=chunk,

            embedding=embedding,

            metadata={

                "file": filename,

                "chat_id": chat_id,

                "document_id": document_id

            }

        )


        total_chunks += 1


    return total_chunks


# ==================================================
# SEARCH DOCUMENTS
# ==================================================

def search_documents(
    question,
    chat_id=None,
    filename=None,
    document_id=None
):
    """
    Search relevant document chunks.

    The search can optionally be restricted
    to one particular document.
    """

    if not question or not question.strip():

        return "", 0, "Unknown"


    # ==================================================
    # QUESTION EMBEDDING
    # ==================================================

    question_embedding = create_embedding(
        question
    )


    # ==================================================
    # SEARCH FAISS
    # ==================================================

    results = search(

        query_embedding=question_embedding,

        k=5,

        chat_id=chat_id,

        filename=filename,

        document_id=document_id

    )


    # ==================================================
    # NOTHING FOUND
    # ==================================================

    if not results:

        return "", 0, "Unknown"


    # ==================================================
    # FILTER RELEVANT RESULTS
    # ==================================================

    valid_results = []


    for result in results:

        distance = result["distance"]


        # ------------------------------------------------
        # Convert distance to simple relevance score
        # ------------------------------------------------

        similarity = 1 / (
            1 + distance
        )


        # ------------------------------------------------
        # Keep reasonably relevant chunks
        # ------------------------------------------------

        if similarity >= 0.60:

            valid_results.append({

                "text": result["text"],

                "similarity": similarity,

                "metadata": result["metadata"]

            })


    # ==================================================
    # FALLBACK
    # ==================================================

    if not valid_results:

        best = results[0]

        valid_results.append({

            "text": best["text"],

            "similarity": 1 / (
                1 + best["distance"]
            ),

            "metadata": best["metadata"]

        })


    # ==================================================
    # BUILD CONTEXT
    # ==================================================

    context_parts = []


    for result in valid_results:

        context_parts.append(
            result["text"]
        )


    context = "\n\n".join(
        context_parts
    )


    # ==================================================
    # SOURCE FILE
    # ==================================================

    source = valid_results[0][
        "metadata"
    ].get(
        "file",
        "Unknown"
    )


    # ==================================================
    # BEST SCORE
    # ==================================================

    score = valid_results[0][
        "similarity"
    ]


    return (
        context,
        score,
        source
    )