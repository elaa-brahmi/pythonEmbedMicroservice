import time
from tqdm import tqdm
from .embedder import generate_embeddings


def upsert_batches(index, model, data, batch_size=64):
    """
    Embeds and uploads job records to a Pinecone index in batches.
    Each record must have:
      id, job_title, description, company_name, location, experience_level, etc.
    """

    for i in tqdm(range(0, len(data), batch_size), desc="Upserting batches"):
        batch = data[i : i + batch_size]

        # Combine job title + description for richer semantic meaning
        texts = [
            f"{item['job_title']} at {item.get('company_name', '')}. "
            f"Location: {item.get('location', '')}. "
            f"Experience: {item.get('experience_level', '')}. "
            f"Industry: {item.get('industry', '')}. "
            f"Description: {item.get('description', '')}"
            for item in batch
        ]
        # Generate embeddings using the embedder helper
        if not texts:
            continue

        embeddings = generate_embeddings(model, texts)

        # Prepare vectors for Pinecone upsert
        vectors = []
        for j, item in enumerate(batch):
            # Defensive: skip if embedding missing
            if j >= len(embeddings):
                print(f"Warning: missing embedding for batch item {j} in batch starting at {i}")
                continue

            vec = embeddings[j]
            # If numpy array, convert to list
            try:
                values = vec.tolist()
            except Exception:
                values = list(vec)

            vectors.append({
                "id": str(item.get("id", f"batch-{i}-{j}")),
                "values": values,
                "metadata": {
                    "job_title": item.get("job_title", ""),
                    "company_name": item.get("company_name", ""),
                    "location": item.get("location", ""),
                    "experience_level": item.get("experience_level", ""),
                    "industry": item.get("industry", ""),
                    "education_required": item.get("education_required", ""),
                    "years_experience": item.get("years_experience", ""),
                    "remote_mode": item.get("remote_mode", ""),
                    "skills": ", ".join(item.get("skills", [])) if isinstance(item.get("skills", []), (list, tuple)) else str(item.get("skills", "")),
                    "salary_usd": item.get("salary_usd", ""),
                    "source": item.get("source", "")
                }
            })

        # Upsert batch into Pinecone index with error handling
        try:
            if vectors:
                index.upsert(vectors=vectors)
        except Exception as e:
            print(f"Error upserting batch starting at {i}: {e}")

        # Optional throttle (avoid API rate limits)
        time.sleep(0.1)

    print(f"✅ Successfully upserted {len(data)} job records to Pinecone.")
