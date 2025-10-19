from fastapi import FastAPI
from pipeline.model_loader import load_model
from pipeline.pinecone_client import init_pinecone
from pipeline.data_handler import stream_data
import os
import asyncio
app = FastAPI(title="AI Career Embed Service")

DATA_FILE = os.path.join(os.path.dirname(__file__), "data/cleaned_jobs.json")
MODEL = None
INDEX = None
BATCH_SIZE = 256


@app.on_event("startup")
def startup_event():
    """Load the embedding model and initialize Pinecone once at startup."""
    global MODEL, INDEX
    print("Startup: loading model...")
    MODEL = load_model()
    print("Startup: initializing Pinecone...")
    INDEX = init_pinecone()
    print("Startup complete ✅")


@app.post("/embed")
async def embed_data():
    print("Entered /embed endpoint...")

    global MODEL, INDEX
    if MODEL is None or INDEX is None:
        raise RuntimeError("Model or Pinecone index not initialized")

    total_processed = 0
    batch_count = 0
    batch = []

    for record in stream_data(DATA_FILE):
        batch.append(record)
        if len(batch) >= BATCH_SIZE:
            texts = [
                f"{rec.get('job_title','')} at {rec.get('company_name','')}. Description: {rec.get('description','')}"
                for rec in batch
            ]

            # Run blocking embedding in a thread
            embeddings = await asyncio.to_thread(MODEL.encode, texts, normalize_embeddings=True)
            vectors = [
                {
                    "id": str(rec["id"]),
                    "values": emb.tolist(),
                    "metadata": {
                        "job_title": rec.get("job_title",""),
                        "company_name": rec.get("company_name",""),
                        "description": rec.get("description",""),
                        "location": rec.get("location",""),
                        "experience_level": rec.get("experience_level","")
                    }
                }
                for rec, emb in zip(batch, embeddings)
            ]

            # Run blocking upsert in a thread
            await asyncio.to_thread(INDEX.upsert, vectors=vectors)

            total_processed += len(batch)
            batch_count += 1
            print(f"Batch {batch_count}: Upserted {len(batch)} records (total {total_processed})")
            batch = []

    # Process remaining records
    if batch:
        texts = [
            f"{rec.get('job_title','')} at {rec.get('company_name','')}. Description: {rec.get('description','')}"
            for rec in batch
        ]
        embeddings = await asyncio.to_thread(MODEL.encode, texts, normalize_embeddings=True)
        vectors = [
            {
                "id": str(rec["id"]),
                "values": emb.tolist(),
                "metadata": {
                    "job_title": rec.get("job_title",""),
                    "company_name": rec.get("company_name",""),
                    "description": rec.get("description",""),
                    "location": rec.get("location",""),
                    "experience_level": rec.get("experience_level","")
                }
            }
            for rec, emb in zip(batch, embeddings)
        ]
        await asyncio.to_thread(INDEX.upsert, vectors=vectors)
        total_processed += len(batch)
        batch_count += 1
        print(f"Batch {batch_count}: Upserted {len(batch)} records (total {total_processed})")

    return {"message": f"Embedded and upserted {total_processed} job records in {batch_count} batches."}
