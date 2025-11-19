import time
import sqlite3
import chromadb
from sentence_transformers import SentenceTransformer
from llama_cpp import Llama

CHROMA_PATH = "chroma_db"
DB_PATH = "db/university.db"
MODEL_PATH = "models/Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf"

# Embedding model
embedder = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

# Chroma
client = chromadb.PersistentClient(path=CHROMA_PATH)
collection = client.get_collection(name="university_data")

# Llama model
llm = Llama(
    model_path=MODEL_PATH,
    n_ctx=4096,
    n_threads=8,
    n_gpu_layers=30,
    verbose=False
)

STOP_STRINGS = ["```", "SQL Query:", "Answer:", "Explanation:", "\n\n"]


def clean_sql(text):
    # Remove after stop strings
    for stop in STOP_STRINGS:
        if stop in text:
            text = text.split(stop)[0]

    # Remove formatting
    text = text.replace("```sql", "").replace("```", "").strip()

    # Keep only first SQL statement
    if ";" in text:
        text = text.split(";")[0] + ";"

    # Enforce semicolon
    if not text.endswith(";"):
        text += ";"

    return text.strip()


def generate_sql(user_query):
    # 1. Embed the user query
    emb = embedder.encode(user_query).tolist()

    # 2. Retrieve relevant table context
    result = collection.query(
        query_embeddings=[emb],
        n_results=2
    )
    context = "\n".join(result["documents"][0])

    # 3. Llama prompt (very important for GGUF)
    prompt = f"""
You are a highly accurate SQLite SQL generator. 
Use ONLY the database schema provided in CONTEXT.
Output strictly one SQL query. No explanation. No additional text.

CONTEXT:
{context}

QUESTION:
{user_query}

SQL:
"""

    start = time.time()

    output = llm(
        prompt,
        max_tokens=128,
        temperature=0.0,
        top_p=1.0,
        repeat_penalty=1.1,
        stop=["#", "```", "\n\n", "Answer:", "Explanation:"]
    )

    print(f"Generated in {time.time() - start:.2f}s")

    sql = output["choices"][0]["text"]
    sql = clean_sql(sql)

    return sql


def run_sql(sql_query):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    try:
        cur.execute(sql_query)
        rows = cur.fetchall()
        columns = [desc[0] for desc in cur.description]
        conn.close()
        return columns, rows
    except Exception as e:
        conn.close()
        return None, f"SQL Error: {str(e)}"


def main():
    print("University Text-to-SQL Assistant (LLaMA-3.1 GGUF)")
    print("Type 'exit' to quit.\n")

    while True:
        query = input("Ask your question: ")

        if query.lower() in ["exit", "quit"]:
            break

        print("\nGenerating SQL...")
        sql = generate_sql(query)

        print("\nGenerated SQL:")
        print(sql)

        print("\nExecuting SQL...")
        cols, result = run_sql(sql)

        if isinstance(result, str):
            print(result)
        else:
            print(cols)
            for row in result:
                print(row)

        print("\n" + "-" * 50 + "\n")


if __name__ == "__main__":
    main()