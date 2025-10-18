def generate_embeddings(model, texts):
    return model.encode(texts, normalize_embeddings=True)
