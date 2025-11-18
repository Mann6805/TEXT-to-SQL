import torch
import time
import sqlite3
import chromadb
from sentence_transformers import SentenceTransformer
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline


CHROMA_PATH = "chroma_db"
DB_PATH = "db/university.db"

# Load embedding model
print("Loading embedding model...")
embedder = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

# Load Chroma vector DB
print("Loading vector DB...")
chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)
collection = chroma_client.get_collection(name="university_data")

# Load Local LLM (Phi-2)
print("Loading Phi-2 model (1.4GB)...")
model_name = "microsoft/phi-2"

tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    device_map="cpu",
    torch_dtype="float32",
    low_cpu_mem_usage=True
)

# SQL Generation function
def generate_sql(user_query):
    # 1. Embed user query
    user_emb = embedder.encode(user_query).tolist()

    # 2. Retrieve top RAG chunks
    results = collection.query(
        query_embeddings=[user_emb],
        n_results=3
    )
    context = "\n".join(results["documents"][0])

    # 3. Prompt
    prompt = f"""
You are an expert SQL generator. Return ONLY a valid SQLite SQL query.

CONTEXT:
{context}

QUESTION:
{user_query}

SQL:
"""

    # 4. Tokenize
    input_ids = tokenizer.encode(prompt, return_tensors="pt")
    attention_mask = torch.ones_like(input_ids)

    # 5. Generate
    start = time.time()
    with torch.no_grad():
        output_ids = model.generate(
            input_ids=input_ids,
            attention_mask=attention_mask,
            max_new_tokens=64,
            do_sample=False,
            pad_token_id=tokenizer.eos_token_id,
            eos_token_id=tokenizer.eos_token_id
        )
    duration = time.time() - start
    print(f"⚡ Generated in {duration:.2f}s")

    # 6. Decode & clean SQL
    text = tokenizer.decode(output_ids[0], skip_special_tokens=True)
    sql = text.split("SQL:")[-1].strip()
    sql = sql.replace("```sql", "").replace("```", "").strip()

    # Optional: cut at first semicolon
    if ";" in sql:
        sql = sql.split(";")[0] + ";"

    return sql

# Execute SQL on SQLite
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

# Main CLI
def main():
    print("\n🟦 University Text-to-SQL Assistant (RAG + Phi-2)")
    print("Type 'exit' to quit.\n")

    while True:
        query = input("Ask your question: ")

        if query.lower() in ["exit", "quit"]:
            break

        print("\n⏳ Generating SQL...")
        sql = generate_sql(query)

        print("\n📘 Generated SQL:")
        print(sql)

        print("\n⏳ Executing SQL...")
        cols, result = run_sql(sql)

        if isinstance(result, str):
            print(result)
        else:
            print("\n📊 Results:")
            print(cols)
            for row in result:
                print(row)

        print("\n" + "-"*60 + "\n")


if __name__ == "__main__":
    main()