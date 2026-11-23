
from functools import lru_cache
import os

# Reduce unnecessary tokenizer parallelism.
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")


# ==========================================
# LOAD MODEL ONLY WHEN REQUIRED
# ==========================================

@lru_cache(maxsize=1)
def get_embedding_model():
    import torch
    from sentence_transformers import SentenceTransformer

    # Limit CPU thread usage.
    torch.set_num_threads(1)

    model = SentenceTransformer(
        "all-MiniLM-L6-v2",
        device="cpu"
    )

    model.eval()

    return model


# ==========================================
# CREATE EMBEDDING
# ==========================================

def create_embedding(text: str):

    """
    Convert text into a 384-dimensional
    vector embedding.
    """

    if not text or not text.strip():
        return []

    model = get_embedding_model()

    embedding = model.encode(
        text,
        show_progress_bar=False,
        convert_to_numpy=True
    )

    return embedding.tolist()
