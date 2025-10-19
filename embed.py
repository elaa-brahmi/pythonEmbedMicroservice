from fastapi import FastAPI
from pipeline.model_loader import load_model
from pipeline.pinecone_client import init_pinecone
from pipeline.data_handler import load_data, stream_data
from pipeline.indexer import upsert_batches
import itertools
from typing import Optional
import os

app = FastAPI(title="AI Career Embed Service")

# Path to the cleaned jobs JSON
DATA_FILE = os.path.join(os.path.dirname(__file__), "data/mock_data.json")

# Cached globals to avoid re-loading heavy objects on every request
MODEL = None
INDEX = None


@app.on_event("startup")
def startup_event():
    """Load the embedding model and initialize Pinecone once at startup.

    This keeps the /embed endpoint fast and avoids re-downloading models
    for every request.
    """
    global MODEL, INDEX
    MODEL = load_model()
    INDEX = init_pinecone()


@app.post("/embed")
async def embed_data(limit: Optional[int] = None):
    if MODEL is None or INDEX is None:
        # Fallback in case startup didn't run (e.g. direct call)
        MODEL = load_model()
        INDEX = init_pinecone()

    # Stream data to avoid loading large file into memory
    data_iter = stream_data(DATA_FILE)
    print(f"Streaming job entries from {DATA_FILE}")

    # Optionally limit items for quick testing
    if limit is not None and limit > 0:
        data_iter = itertools.islice(data_iter, limit)

    processed = upsert_batches(INDEX, MODEL, data_iter)
    return {"message": f"Embedded {processed} jobs successfully."}
