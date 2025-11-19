import chromadb
from sentence_transformers import SentenceTransformer

CHROMA_PATH = "chroma_db"
DOC_PATH = "data/university_docs.txt"

embedder = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
client = chromadb.PersistentClient(path=CHROMA_PATH)

def load_docs():
    with open(DOC_PATH, "r", encoding="utf-8") as f:
        text = f.read()

    # Split on TABLE keyword (cleanest)
    chunks = [c.strip() for c in text.split("TABLE:") if c.strip()]
    docs = ["TABLE: " + c for c in chunks]
    return docs

def build_rag():
    docs = load_docs()

    try:
        client.delete_collection("university_data")
    except:
        pass

    collection = client.create_collection("university_data")

    embeddings = embedder.encode(docs).tolist()

    ids = [f"doc_{i}" for i in range(len(docs))]

    collection.add(
        ids=ids,
        documents=docs,
        embeddings=embeddings
    )
    print("RAG build complete.")

if __name__ == "__main__":
    build_rag()