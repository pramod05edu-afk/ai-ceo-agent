# AI CEO Strategic Intelligence Agent

**NLP Examination Project — SRH University Heidelberg**
**Student:** Pramodkumar Shivanna
**Company Analyzed:** NVIDIA Corporation
**Module:** Natural Language Processing

---

## Project Overview

This project builds an AI-powered Autonomous Strategic Intelligence Agent that automatically collects live information about NVIDIA from multiple public sources, processes and stores it in a vector database, and uses a Large Language Model to plan, reason, validate, and generate executive-level strategic recommendations.

The system answers the core question:

> "If you were the CEO today, what would you do next and why?"

The agent follows a complete autonomous workflow:

> **Goal → Plan → Retrieve → Analyze → Decide → Recommend → Validate**

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    DATA COLLECTION LAYER                    │
│                                                             │
│  Google News RSS  |  NVIDIA Newsroom  |  Yahoo Finance      │
│  VentureBeat AI   |  Ars Technica     |  Seeking Alpha      │
│                                                             │
│                   collectors/run_all.py                     │
│                   131 documents saved to data/*.json        │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                   PROCESSING LAYER                          │
│                                                             │
│   1. Clean text (remove HTML, whitespace)                   │
│   2. Deduplicate (MD5 hash comparison)                      │
│   3. Embed (all-MiniLM-L6-v2 → 384-dim vectors)             │
│   4. Store (ChromaDB with cosine similarity)                │
│                                                             │
│              processing/build_index.py                      │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                 KNOWLEDGE STORE (ChromaDB)                  │
│                                                             │
│   131 documents x 384-dimensional vectors                   │
│   Metadata: source, title, url, published date              │
│   Search method: cosine similarity (HNSW)                   │
│                   store/chroma/                             │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│              AUTONOMOUS AI CEO AGENT                        │
│                                                             │
│   STEP 1: GOAL    — agent receives high level goal          │
│   STEP 2: PLAN    — create_plan() autonomous plan           │
│   STEP 3: RETRIEVE— generate_search_queries() own queries   │
│   STEP 4: ANALYZE — opportunities, risks, competitors,      │
│                     trends, sentiment                       │
│   STEP 5: DECIDE  — generate_recommendations()              │
│   STEP 6: VALIDATE— validate_recommendations() self-check   │
│   STEP 7: RECOMMEND- generate_ceo_briefing()                │
│                                                             │
│                 agent/intelligence.py                       │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│              EXECUTIVE DASHBOARD (Streamlit)                │
│                                                             │
│   Agent Workflow  (goal, plan, tools, queries)              │
│   Validation      (accepted, rejected, reasoning)           │
│   Section 1: Company Overview                               │
│   Section 2: Market Intelligence                            │
│   Section 3: Opportunity Monitor                            │
│   Section 4: Risk Monitor                                   │
│   Section 5: Competitor Analysis                            │
│   Section 6: Technology Trends                              │
│   Section 7: Sentiment Analysis                             │
│   Section 8: Strategic Recommendations                      │
│   Section 9: CEO Briefing                                   │
│                  dashboard/app.py                           │
└─────────────────────────────────────────────────────────────┘
```

---

## Autonomous Agent Workflow

```
GOAL
"Analyze NVIDIA's strategic position and recommend actions"
        |
        v
PLAN
create_plan() — agent creates its own execution plan
        |
        v
RETRIEVE
generate_search_queries() — agent generates its own queries
retrieve_context() — ChromaDB returns relevant documents
        |
        v
ANALYZE
Agent reads evidence and analyzes 5 dimensions:
  opportunities, risks, competitors, trends, sentiment
        |
        v
DECIDE
generate_recommendations() — agent synthesizes findings
Agent generates its own retrieval query based on what it found
        |
        v
VALIDATE
validate_recommendations() — agent checks its own output
Accepts or rejects each recommendation based on evidence
        |
        v
RECOMMEND
generate_ceo_briefing() — final 3 paragraph executive summary
What happened / Why it matters / What to do next
```

---

## Data Flow Diagram

```
Internet Sources
      |
      |  RSS feeds (feedparser)
      v
Raw Documents (JSON)
      |
      |  Clean → Deduplicate → Embed
      v
Clean Documents
      |
      |  all-MiniLM-L6-v2 (SentenceTransformers)
      v
384-dimensional Vectors
      |
      |  ChromaDB PersistentClient
      v
Vector Database
      |
      |  Agent sets goal and creates plan
      v
Agent generates autonomous search queries
      |
      |  Query → Embed → Cosine Similarity Search
      v
Top 5 most relevant documents per query
      |
      |  Context + System Prompt + User Prompt
      v
Groq API (Llama 3.1 8B Instant)
      |
      |  Structured JSON output
      v
Validation — agent checks its own recommendations
      |
      |  Saved to store/analysis_results.json
      v
Streamlit Dashboard (Agent Workflow + Validation + 9 Sections)
```

---

## Technology Stack

| Component | Technology | Purpose |
|---|---|---|
| Language | Python 3.11 | Core development language |
| LLM | Llama 3.1 8B Instant | Strategic reasoning and validation |
| LLM Provider | Groq (free tier) | Fast open-source model inference |
| Embedding Model | all-MiniLM-L6-v2 | Text to vector conversion |
| Vector Database | ChromaDB | Semantic search and storage |
| Data Collection | feedparser | RSS feed parsing |
| Dashboard | Streamlit | Interactive web interface |
| Charts | Plotly | Data visualization |
| Environment | python-dotenv | Secure API key management |
| Similarity Search | Cosine Similarity (HNSW) | Document retrieval |

---

## Agent Tools

| Tool | Technology | Purpose |
|---|---|---|
| web_collector | feedparser | Fetches live RSS data from 4 sources |
| knowledge_store | ChromaDB | Stores and retrieves document vectors |
| embedder | all-MiniLM-L6-v2 | Converts text to 384-dimensional vectors |
| reasoner | Llama 3.1 8B via Groq | Analyzes evidence and generates insights |
| validator | Llama 3.1 8B via Groq | Validates recommendations against evidence |

---

## Project Structure

```
ai-ceo-agent/
|
├── collectors/                  # Task 1: Live data collection
│   ├── __init__.py
│   ├── news.py                  # Google News RSS (60 articles)
│   ├── company.py               # NVIDIA official newsroom (20 releases)
│   ├── research.py              # Tech news RSS feeds (7 articles)
│   ├── finance.py               # Yahoo Finance + Seeking Alpha (45 articles)
│   ├── reddit_alt.py            # Reddit RSS feeds
│   └── run_all.py               # Master collector (runs all sources)
|
├── processing/                  # Task 3: Information processing
│   ├── build_index.py           # Clean, embed, store in ChromaDB
│   └── test_query.py            # Retrieval verification
|
├── agent/                       # Tasks 4, 5, 6: Intelligence engine
│   ├── intelligence.py          # Autonomous agent — full workflow
│   └── intelligence_local.py   # Backup — runs on Ollama locally
|
├── dashboard/                   # Dashboard requirement
│   └── app.py                   # Streamlit dashboard
|
├── data/                        # Raw collected documents
│   ├── news.json
│   ├── company.json
│   ├── arxiv.json
│   ├── finance.json
│   └── reddit.json
|
├── store/                       # Task 2: Knowledge repository
│   ├── chroma/                  # ChromaDB vector database
│   ├── index_summary.json       # Collection statistics
│   └── analysis_results.json   # Latest agent output
|
├── .env                         # API keys (not committed to Git)
├── .streamlit/
│   └── config.toml              # Dashboard theme configuration
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

---

## Data Sources

| Source | Type | Documents | Why Included |
|---|---|---|---|
| Google News RSS | General news | 60 | Broad media coverage and multiple perspectives |
| NVIDIA Newsroom | Official company | 20 | Company voice — press releases and announcements |
| Yahoo Finance | Financial news | ~30 | Investor reactions and market sentiment |
| Seeking Alpha | Financial analysis | ~15 | Analyst opinions and stock analysis |
| VentureBeat AI | Tech industry | ~5 | AI and technology specialist coverage |
| Ars Technica | Tech industry | ~2 | Technical analysis and industry developments |
| **Total** | **4 categories** | **131** | **Complete strategic picture** |

---

## AI Pipeline

### Step 1: Data Collection

```python
feed = feedparser.parse(rss_url)
for entry in feed.entries:
    doc = {
        "source": source_name,
        "title": entry.get("title", ""),
        "text": entry.get("summary", ""),
        "doc_id": hashlib.md5((title + text).encode()).hexdigest()
    }
```

### Step 2: Processing

```python
# Deduplication using MD5 hashing
content_hash = hashlib.md5(full_text.encode()).hexdigest()
if content_hash not in seen:
    seen.add(content_hash)
    clean_docs.append(doc)

# Embedding
model = SentenceTransformer("all-MiniLM-L6-v2")
embeddings = model.encode(texts, batch_size=32).tolist()
```

### Step 3: Storage

```python
collection = client.get_or_create_collection(
    name="company_intel",
    metadata={"hnsw:space": "cosine"}
)
collection.add(ids=ids, embeddings=embeddings,
               documents=texts, metadatas=metadata)
```

### Step 4: Agent Planning

```python
# Agent creates its own execution plan
plan = create_plan(goal)

# Agent generates its own search queries
search_plan = generate_search_queries(goal)
queries = search_plan["queries"]
```

### Step 5: Autonomous Retrieval

```python
# Agent uses its own queries — not hardcoded by developer
query_vector = embedding_model.encode(query).tolist()
results = collection.query(
    query_embeddings=[query_vector],
    n_results=5
)
```

### Step 6: LLM Reasoning

```python
response = client.chat.completions.create(
    model="llama-3.1-8b-instant",
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": context + question}
    ],
    temperature=0.3
)
```

### Step 7: Self Validation

```python
# Agent validates its own recommendations
validation = validate_recommendations(
    recommendations, opportunities, risks
)
# Returns: accepted_count, rejected_count, validation_reason
```

---

## Design Decisions

### Why autonomous query generation instead of hardcoded queries?

Hardcoded queries introduce developer bias — the developer decides what the agent searches for, not the agent itself. The autonomous agent uses generate_search_queries() to decide its own retrieval strategy from a high level goal. This means the agent adapts its search based on the current situation rather than always using fixed terms.

### Why RAG instead of fine-tuning?

Fine-tuning would require expensive GPU resources and would bake in knowledge at training time. RAG allows the system to use live, current documents without any training. When NVIDIA announces something today, the system reasons about it today — no retraining required.

### Why validate recommendations?

Without validation the agent always produces output regardless of evidence quality. The validate_recommendations() function makes the agent critical of its own output — it reads recommendations against available evidence and accepts, modifies, or rejects each one. This demonstrates genuine autonomous decision making.

### Why ChromaDB over FAISS?

ChromaDB offers persistent storage, built-in metadata filtering, and a simple Python API. FAISS requires manual persistence and index management. ChromaDB provided better developer experience while providing equivalent retrieval quality.

### Why Groq over local Ollama?

The development machine has an Intel i5-1335U with integrated graphics only — no dedicated GPU. Running an 8B parameter model locally would produce approximately 2-4 tokens per second. Groq's free tier serves Llama 3.1 on custom LPU hardware at hundreds of tokens per second while keeping the model open-source and freely accessible. A local Ollama backup using Llama 3.2 3B is available in intelligence_local.py.

### Why all-MiniLM-L6-v2 for embeddings?

Produces 384-dimensional embeddings of good quality. Only 22MB — runs in under 2 seconds on CPU. Specifically trained on sentence similarity tasks. Runs completely locally — no API call needed.

### Why temperature 0.3?

Business analysis requires consistency rather than creativity. Temperature 0.3 keeps outputs focused and reproducible while allowing slight natural variation.

### Why JSON output format?

Structured JSON allows the dashboard to access individual fields directly. Free-form prose would require additional parsing and would be unreliable.

---

## How to Run

### Prerequisites

- Python 3.11+
- Groq API key (free at console.groq.com)

### Installation

```bash
cd ai-ceo-agent

python -m venv venv
venv\Scripts\activate          # Windows
source venv/bin/activate        # Mac/Linux

pip install -r requirements.txt

# Add Groq API key to .env file
GROQ_API_KEY=your_key_here
```

### Running the Full Pipeline

```bash
# Step 1: Collect live data
python -m collectors.run_all

# Step 2: Build the knowledge index
python processing\build_index.py

# Step 3: Run the autonomous AI CEO agent
python agent\intelligence.py

# Step 4: Launch the dashboard
python -m streamlit run dashboard\app.py
```

### Running with local model (no internet required)

```bash
# Install Ollama from ollama.com
ollama pull llama3.2:3b

# Run with local model
python agent\intelligence_local.py
```

---

## Requirements

```
feedparser
sentence-transformers
chromadb
streamlit
plotly
groq
python-dotenv
requests
beautifulsoup4
rank_bm25
ollama
```

---

## Key Concepts

**Autonomous Agent:** A system that receives a high level goal, creates its own execution plan, decides what to retrieve, uses multiple tools, validates its own output, and produces recommendations without being told exactly what to do at each step.

**RAG (Retrieval Augmented Generation):** Retrieves relevant documents from a database and injects them into an LLM prompt before generating a response. Grounds output in real current evidence rather than training data.

**Embeddings:** Numerical representations of text capturing semantic meaning. Documents with similar meaning produce similar vectors. Enables search by meaning rather than keyword match.

**Cosine Similarity:** Measures the angle between two vectors. Vectors pointing in the same direction have similarity 1.0. Used by ChromaDB to find the most relevant documents for any query.

**HNSW:** Hierarchical Navigable Small World — the graph-based algorithm ChromaDB uses for approximate nearest-neighbor search in O(log n) time.

**Self Validation:** The agent reviews its own recommendations against available evidence before presenting them, accepting or rejecting each based on evidence strength.

---

## Project Requirements Mapping

| Brief Requirement | Implementation |
|---|---|
| Live data from 3+ sources | 6 RSS feeds across 4 source categories |
| 100+ documents | 131 documents collected |
| Knowledge repository | ChromaDB vector database |
| Clean and deduplicate | MD5 hash deduplication in build_index.py |
| Generate embeddings | all-MiniLM-L6-v2 via SentenceTransformers |
| Planning before execution | create_plan() — agent creates its own plan |
| Autonomous decision making | generate_search_queries() — agent decides what to search |
| Tool usage beyond LLM | 5 tools: feedparser, ChromaDB, embedder, reasoner, validator |
| Identify opportunities | analyze_opportunities() with autonomous RAG |
| Identify risks | analyze_risks() with autonomous RAG |
| Competitor analysis | analyze_competitors() with autonomous RAG |
| Technology trends | analyze_trends() with autonomous RAG |
| Strategic recommendations | generate_recommendations() with self-generated query |
| Validation of recommendations | validate_recommendations() — agent checks own output |
| Evidence-based output | Every function returns evidence field |
| Open-source LLM | Llama 3.1 8B (Meta, open weights) via Groq free tier |
| Dashboard | Streamlit with workflow, validation, and 9 sections |
| Sentiment analysis | analyze_sentiment() with gauge chart |
| CEO Briefing | generate_ceo_briefing() — 3 paragraphs |
| Full agent workflow | Goal→Plan→Retrieve→Analyze→Decide→Recommend→Validate |

---

*AI CEO Strategic Intelligence Agent | NLP Examination | SRH University Heidelberg*
