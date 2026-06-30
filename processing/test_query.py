import chromadb
from sentence_transformers import SentenceTransformer

print("Loading model and database...")
model = SentenceTransformer("all-MiniLM-L6-v2")
client = chromadb.PersistentClient(path="store/chroma")
col = client.get_collection("company_intel")

print(f"Collection has {col.count()} documents\n")

# Test 3 different strategic questions
test_queries = [
    "What are the biggest risks facing NVIDIA?",
    "What opportunities does NVIDIA have in AI?",
    "What are NVIDIA competitors doing?"
]

for query in test_queries:
    print(f"QUERY: {query}")
    print("-" * 50)
    
    # Convert question to vector
    query_vector = model.encode(query).tolist()
    
    # Find 3 most relevant documents
    results = col.query(
        query_embeddings=[query_vector],
        n_results=3
    )
    
    for i, (doc, meta) in enumerate(zip(
        results["documents"][0],
        results["metadatas"][0]
    )):
        print(f"Result {i+1} [{meta['source']}]")
        print(f"Title : {meta['title'][:80]}")
        print(f"Text  : {doc[:120]}...")
        print()
    
    print("=" * 50)
    print()