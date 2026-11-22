from sentence_transformers import SentenceTransformer


# ==========================================
# EMBEDDING MODEL
# ==========================================

model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)


# ==========================================
# CREATE EMBEDDING
# ==========================================

def create_embedding(text: str):

    """
    Convert text into a 384-dimensional
    vector embedding.
    """

    return model.encode(
        text
    ).tolist()