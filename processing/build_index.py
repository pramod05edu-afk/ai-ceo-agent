import json
import glob
import os
import hashlib
import chromadb
from sentence_transformers import SentenceTransformer
from datetime import datetime

def clean_text(text):
    """
    Cleans raw text by removing HTML tags, 
    extra whitespace.
    """
    import re
    # Remove HTML tags
    text = re.sub(r"<[^>]+>", " ", text)
    # Remove extra whitespace
    text = re.sub(r"\s+", " ", text).strip()
    return text

def load_all_documents():
    
    docs = []
    files_found = glob.glob("data/*.json")
    
    print(f"Found {len(files_found)} data files: {files_found}")
    
    for path in files_found:
        try:
            loaded = json.load(open(path, encoding="utf-8"))
            docs.extend(loaded)
            print(f"  Loaded {len(loaded)} documents from {path}")
        except Exception as e:
            print(f"  Skipped {path}: {e}")
    
    return docs

def deduplicate(docs):
    """
    Removes duplicate documents using MD5 hash of their text.
    Two documents with identical text produce the same hash
    and only the first one is kept.
    """
    seen = set()
    clean = []
    
    for doc in docs:
        # Combine title and text as the full content
        title = clean_text(doc.get("title", ""))
        text = clean_text(doc.get("text", ""))
        full_text = f"{title}. {text}".strip()
        
        # Skip if content is too short to be useful
        if len(full_text) < 30:
            continue
        
        # Skip if we have seen this exact content before
        content_hash = hashlib.md5(full_text.encode()).hexdigest()
        if content_hash in seen:
            continue
        
        seen.add(content_hash)
        doc["full_text"] = full_text
        clean.append(doc)
    
    return clean

def build_index():
    """
    Main function that:
    1. Loads all collected documents
    2. Cleans and deduplicates them
    3. Generates embeddings
    4. Stores everything in ChromaDB
    """
    
    print("=" * 50)
    print("BUILDING KNOWLEDGE INDEX")
    print("=" * 50)
    
    # Step 1: Load all documents
    print("\n[1/4] Loading documents...")
    docs = load_all_documents()
    print(f"Total raw documents: {len(docs)}")
    
    # Step 2: Clean and deduplicate
    print("\n[2/4] Cleaning and deduplicating...")
    clean_docs = deduplicate(docs)
    removed = len(docs) - len(clean_docs)
    print(f"After cleaning: {len(clean_docs)} documents")
    print(f"Removed {removed} duplicates/short documents")
    
    # Step 3: Generate embeddings
    print("\n[3/4] Generating embeddings...")
    print("Loading embedding model (first time may take 1-2 minutes to download)...")
    
    model = SentenceTransformer("all-MiniLM-L6-v2")
    
    texts = [doc["full_text"] for doc in clean_docs]
    
    print(f"Embedding {len(texts)} documents...")
    embeddings = model.encode(
        texts,
        show_progress_bar=True,
        batch_size=32
    ).tolist()
    
    print("Embeddings generated!")
    
    # Step 4: Store in ChromaDB
    print("\n[4/4] Storing in ChromaDB...")
    
    os.makedirs("store", exist_ok=True)
    client = chromadb.PersistentClient(path="store/chroma")
    
    # Delete existing collection if rebuilding
    try:
        client.delete_collection("company_intel")
        print("Cleared existing collection")
    except:
        pass
    
    col = client.get_or_create_collection(
        name="company_intel",
        metadata={"hnsw:space": "cosine"}
    )
    
    # Add documents in batches to avoid memory issues
    batch_size = 50
    for i in range(0, len(clean_docs), batch_size):
        batch_docs = clean_docs[i:i + batch_size]
        batch_emb = embeddings[i:i + batch_size]
        
        col.add(
            ids=[f"doc_{i + j}" for j in range(len(batch_docs))],
            embeddings=batch_emb,
            documents=[d["full_text"] for d in batch_docs],
            metadatas=[{
                "source": d.get("source", "unknown"),
                "url": d.get("url", ""),
                "title": d.get("title", ""),
                "published": d.get("published", ""),
                "collected_at": d.get("collected_at", "")
            } for d in batch_docs]
        )
        print(f"  Stored batch {i // batch_size + 1} ({len(batch_docs)} docs)")
    
    print(f"\nTotal documents in ChromaDB: {col.count()}")
    
    # Save a summary for the dashboard
    summary = {
        "total_documents": col.count(),
        "sources": list(set(d.get("source", "") for d in clean_docs)),
        "num_sources": len(set(d.get("source", "") for d in clean_docs)),
        "built_at": datetime.now().isoformat(),
        "duplicates_removed": removed
    }
    json.dump(summary, open("store/index_summary.json", "w"), indent=2)
    
    print("\n" + "=" * 50)
    print("INDEX BUILT SUCCESSFULLY")
    print(f"Documents indexed : {col.count()}")
    print(f"Sources           : {summary['num_sources']}")
    print(f"Stored at         : store/chroma")
    print("=" * 50)
    
    return col

if __name__ == "__main__":
    build_index()