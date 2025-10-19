
# Load .env variables
import os
from dotenv import load_dotenv
load_dotenv()
import os
from pinecone import Pinecone

def init_pinecone():
    api_key = os.getenv("PINECONE_API_KEY")
    index_name = os.getenv("PINECONE_INDEX")

    if not api_key:
        raise RuntimeError("PINECONE_API_KEY environment variable is not set")
    if not index_name:
        raise RuntimeError("PINECONE_INDEX environment variable is not set")

    # Initialize the Pinecone client
    pc = Pinecone(api_key=api_key)

    # Retrieve and connect to existing index
    try:
        index = pc.Index(index_name)
        print(f"✅ Connected to Pinecone index: {index_name}")
        return index
    except Exception as e:
        raise RuntimeError(f"Failed to connect to Pinecone index '{index_name}': {e}")
