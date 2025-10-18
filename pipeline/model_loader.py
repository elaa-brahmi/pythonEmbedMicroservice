from sentence_transformers import SentenceTransformer

def load_model(model_name="intfloat/multilingual-e5-large"):
    print(f"Loading model: {model_name}")
    return SentenceTransformer(model_name)
