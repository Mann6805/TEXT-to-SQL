import chromadb
from sentence_transformers import SentenceTransformer

# Persistent DB path
CHROMA_PATH = "chroma_db"

# Load embedding model
embed_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

# Load Chroma client
chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)

# Create / get the collection
collection = chroma_client.get_or_create_collection(
    name="university_data",
    metadata={"hnsw:space": "cosine"}
)

# Read RAG docs
with open("data/university_docs.txt", "r") as f:
    text = f.read()

# Chunking (simple splitting)
chunks = text.split("\n\n")  # split paragraphs

# Insert chunks into Chroma
for idx, chunk in enumerate(chunks):
    chunk_id = f"chunk_{idx}"
    emb = embed_model.encode(chunk).tolist()

    collection.add(
        ids=[chunk_id],
        documents=[chunk],
        embeddings=[emb],
        metadatas=[{"source": "university_docs"}]
    )

print("Vector DB built successfully!")