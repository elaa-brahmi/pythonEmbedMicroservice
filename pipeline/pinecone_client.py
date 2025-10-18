import os
import pinecone


def init_pinecone(index_name: str = None, dimension: int = 1024):
    """Initialize Pinecone and return an Index object.

    Expects the environment variable PINECONE_API_KEY to be set. Optionally
    set PINECONE_INDEX_NAME and PINECONE_ENV (for Pinecone environment).
    """
    api_key = os.getenv("PINECONE_API_KEY")
    if not api_key:
        raise RuntimeError("PINECONE_API_KEY environment variable is not set")

    index_name = index_name or os.getenv("PINECONE_INDEX_NAME", "rag-jobs")
    pinecone_env = os.getenv("PINECONE_ENV")  # optional

    # Initialize client
    pinecone.init(api_key=api_key, environment=pinecone_env)

    # Create index if it doesn't exist
    existing = pinecone.list_indexes()
    if index_name not in existing:
        pinecone.create_index(name=index_name, dimension=dimension, metric="cosine")

    return pinecone.Index(index_name)
