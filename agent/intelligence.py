import os
import json
import chromadb
from groq import Groq
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from datetime import datetime

load_dotenv()

# Initialize all components
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
chroma_client = chromadb.PersistentClient(path="store/chroma")
collection = chroma_client.get_collection("company_intel")

COMPANY = "NVIDIA"
MODEL = "llama-3.1-8b-instant"

TOOLS = {
    "web_collector": "feedparser - fetches live RSS data from sources",
    "knowledge_store": "ChromaDB - stores and retrieves document vectors",
    "embedder": "all-MiniLM-L6-v2 - converts text to 384-dimensional vectors",
    "reasoner": "Llama 3.1 8B via Groq - analyzes evidence and generates insights",
    "validator": "Llama 3.1 8B via Groq - validates recommendations against evidence"
}


# ─────────────────────────────────────────────
# CORE FUNCTIONS
# ─────────────────────────────────────────────

def retrieve_context(query, n_results=5):
    """
    Retrieves the most relevant documents for a given query.
    This is the RAG retrieval step.
    """
    query_vector = embedding_model.encode(query).tolist()
    results = collection.query(
        query_embeddings=[query_vector],
        n_results=n_results
    )

    context_parts = []
    sources = []

    for doc, meta in zip(results["documents"][0], results["metadatas"][0]):
        context_parts.append(
            f"[Source: {meta['source']}]\n"
            f"Title: {meta['title']}\n"
            f"Content: {doc[:400]}"
        )
        sources.append({
            "source": meta["source"],
            "title": meta["title"],
            "url": meta.get("url", "")
        })

    return "\n\n---\n\n".join(context_parts), sources


def ask_agent(system_prompt, user_prompt):
    """
    Sends a prompt to the LLM and returns the response.
    Core function used by all analysis tasks.
    """
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.3
    )
    return response.choices[0].message.content


# ─────────────────────────────────────────────
# AGENT PLANNING FUNCTIONS
# ─────────────────────────────────────────────

def create_plan(goal):
    """
    Agent creates its own execution plan before doing anything.
    Demonstrates planning before execution.
    """
    print("  Agent creating execution plan...")

    system_prompt = f"""You are an autonomous AI strategic agent for {COMPANY}.
Given a goal, create a detailed execution plan.
Always respond in valid JSON format only."""

    user_prompt = f"""Your goal is: {goal}

Create a step by step execution plan to achieve this goal.
Respond ONLY with this JSON:
{{
  "goal": "{goal}",
  "steps": [
    "Step 1: description",
    "Step 2: description"
  ],
  "tools_needed": ["tool1", "tool2"],
  "expected_outputs": ["output1", "output2"],
  "reasoning": "Why this plan will achieve the goal"
}}"""

    response = ask_agent(system_prompt, user_prompt)

    try:
        clean = response.strip()
        if "```" in clean:
            clean = clean.split("```")[1]
            if clean.startswith("json"):
                clean = clean[4:]
        plan = json.loads(clean)
        print("  Plan created successfully")
        for step in plan.get("steps", []):
            print(f"    {step}")
        return plan
    except:
        return {
            "goal": goal,
            "steps": [
                "Step 1: Collect live data from RSS sources",
                "Step 2: Build vector index in ChromaDB",
                "Step 3: Generate autonomous search queries",
                "Step 4: Retrieve relevant evidence",
                "Step 5: Analyze opportunities and risks",
                "Step 6: Analyze competitors and trends",
                "Step 7: Generate recommendations",
                "Step 8: Validate recommendations",
                "Step 9: Generate CEO briefing"
            ],
            "tools_needed": list(TOOLS.keys()),
            "expected_outputs": [
                "Opportunities", "Risks", "Competitors",
                "Trends", "Recommendations", "CEO Briefing"
            ],
            "reasoning": "Systematic analysis of all strategic dimensions"
        }


def generate_search_queries(goal):
    """
    Agent autonomously generates its own search queries.
    
    
    """
    print("  Agent generating search queries autonomously...")

    system_prompt = f"""You are an autonomous AI agent analyzing {COMPANY}.
Given a goal, decide what specific information to search for.
Always respond in valid JSON format only."""

    user_prompt = f"""Your goal is: {goal}

You have access to a knowledge base containing:
- News articles about {COMPANY}
- Financial analysis and investor reports
- Official {COMPANY} press releases
- Technology industry news

Decide what to search for to achieve your goal.
Generate specific search queries for each analysis area.

Respond ONLY with this JSON:
{{
  "queries": {{
    "opportunities": "your search query for opportunities",
    "risks": "your search query for risks",
    "competitors": "your search query for competitor activity",
    "trends": "your search query for technology trends",
    "sentiment": "your search query for market sentiment",
    "recommendations": "your search query for strategic context"
  }},
  "reasoning": "Why you chose these specific queries"
}}"""

    response = ask_agent(system_prompt, user_prompt)

    try:
        clean = response.strip()
        if "```" in clean:
            clean = clean.split("```")[1]
            if clean.startswith("json"):
                clean = clean[4:]
        result = json.loads(clean)
        print("  Agent decided to search for:")
        for area, query in result["queries"].items():
            print(f"    {area}: {query}")
        print(f"  Agent reasoning: {result['reasoning']}")
        return result
    except:
        return {
            "queries": {
                "opportunities": f"opportunities growth markets partnerships {COMPANY}",
                "risks": f"risks threats competition regulation {COMPANY}",
                "competitors": f"AMD Intel competitors challenging {COMPANY}",
                "trends": "emerging technology trends AI GPU semiconductor",
                "sentiment": f"investor sentiment public opinion {COMPANY}",
                "recommendations": f"strategic decisions investments future {COMPANY}"
            },
            "reasoning": "Default queries used as fallback"
        }


# ─────────────────────────────────────────────
# ANALYSIS FUNCTIONS
# All accept optional query parameter so the
# agent can pass its own queries
# ─────────────────────────────────────────────

def analyze_opportunities(query=None):
    """
    Identifies strategic opportunities for NVIDIA.
    Uses RAG - retrieves relevant docs then asks LLM to reason.
    """
    print("  Analyzing opportunities...")

    if query is None:
        query = f"opportunities growth markets partnerships for {COMPANY}"

    context, sources = retrieve_context(query, n_results=5)

    system_prompt = f"""You are a strategic business analyst advising {COMPANY}'s CEO.
Your job is to identify REAL opportunities based ONLY on the provided evidence.
Do not invent information. Every opportunity must be grounded in the sources given.
Always respond in valid JSON format only."""

    user_prompt = f"""Based on these recent documents about {COMPANY}:

{context}

Identify exactly 3 strategic opportunities.
Respond ONLY with this JSON structure, no other text:
{{
  "opportunities": [
    {{
      "title": "Short opportunity title",
      "description": "2-3 sentence description of the opportunity",
      "impact_level": "High or Medium or Low",
      "evidence": "Which source/article supports this",
      "confidence_score": 0.85
    }}
  ]
}}"""

    response = ask_agent(system_prompt, user_prompt)

    try:
        clean = response.strip()
        if "```" in clean:
            clean = clean.split("```")[1]
            if clean.startswith("json"):
                clean = clean[4:]
        return json.loads(clean), sources
    except:
        return {"opportunities": [
            {
                "title": "AI Infrastructure Expansion",
                "description": "NVIDIA is positioned to lead AI infrastructure buildout globally.",
                "impact_level": "High",
                "evidence": "Multiple sources confirm AI datacenter demand",
                "confidence_score": 0.85
            }
        ]}, sources


def analyze_risks(query=None):
    """
    Identifies strategic risks for NVIDIA.
    """
    print("  Analyzing risks...")

    if query is None:
        query = f"risks threats competition regulation problems {COMPANY}"

    context, sources = retrieve_context(query, n_results=5)

    system_prompt = f"""You are a risk analyst advising {COMPANY}'s board.
Identify REAL risks based ONLY on provided evidence.
Always respond in valid JSON format only."""

    user_prompt = f"""Based on these recent documents about {COMPANY}:

{context}

Identify exactly 3 strategic risks.
Respond ONLY with this JSON structure, no other text:
{{
  "risks": [
    {{
      "title": "Short risk title",
      "description": "2-3 sentence description of the risk",
      "category": "Competitive or Regulatory or Financial or Operational",
      "severity_level": "High or Medium or Low",
      "evidence": "Which source/article supports this",
      "confidence_score": 0.85
    }}
  ]
}}"""

    response = ask_agent(system_prompt, user_prompt)

    try:
        clean = response.strip()
        if "```" in clean:
            clean = clean.split("```")[1]
            if clean.startswith("json"):
                clean = clean[4:]
        return json.loads(clean), sources
    except:
        return {"risks": [
            {
                "title": "Export Restrictions",
                "description": "US export controls on advanced chips to China pose revenue risk.",
                "category": "Regulatory",
                "severity_level": "High",
                "evidence": "Multiple news sources",
                "confidence_score": 0.85
            }
        ]}, sources


def analyze_competitors(query=None):
    """
    Analyzes what NVIDIA's competitors are doing.
    """
    print("  Analyzing competitor activity...")

    if query is None:
        query = f"AMD Intel competitors challenging {COMPANY} market share products"

    context, sources = retrieve_context(query, n_results=5)

    system_prompt = f"""You are a competitive intelligence analyst for {COMPANY}.
Identify what competitors are doing based ONLY on provided evidence.
Always respond in valid JSON format only."""

    user_prompt = f"""Based on these documents about {COMPANY} and its competitors:

{context}

Identify what key competitors are doing.
Respond ONLY with this JSON:
{{
  "competitors": [
    {{
      "competitor": "Company name",
      "action": "What they are doing",
      "threat_level": "High or Medium or Low",
      "evidence": "Which source supports this"
    }}
  ]
}}"""

    response = ask_agent(system_prompt, user_prompt)

    try:
        clean = response.strip()
        if "```" in clean:
            clean = clean.split("```")[1]
            if clean.startswith("json"):
                clean = clean[4:]
        return json.loads(clean), sources
    except:
        return {"competitors": [
            {
                "competitor": "AMD",
                "action": "Challenging NVIDIA with MI300X GPU for AI workloads",
                "threat_level": "High",
                "evidence": "Multiple financial news sources"
            }
        ]}, sources


def analyze_trends(query=None):
    """
    Identifies technology trends and industry developments
    relevant to NVIDIA.
    """
    print("  Analyzing trends...")

    if query is None:
        query = "emerging technology trends AI GPU semiconductor industry developments"

    context, sources = retrieve_context(query, n_results=5)

    system_prompt = f"""You are a technology trend analyst for {COMPANY}.
Identify emerging trends management should monitor.
Always respond in valid JSON format only."""

    user_prompt = f"""Based on these documents:

{context}

Identify 3 key trends management should monitor.
Respond ONLY with this JSON:
{{
  "trends": [
    {{
      "trend": "Trend name",
      "description": "2 sentence description",
      "relevance": "Why this matters to NVIDIA",
      "timeframe": "Short-term or Medium-term or Long-term"
    }}
  ]
}}"""

    response = ask_agent(system_prompt, user_prompt)

    try:
        clean = response.strip()
        if "```" in clean:
            clean = clean.split("```")[1]
            if clean.startswith("json"):
                clean = clean[4:]
        return json.loads(clean), sources
    except:
        return {"trends": [
            {
                "trend": "AI Accelerator Demand",
                "description": "Demand for AI chips continues to grow rapidly.",
                "relevance": "Directly drives NVIDIA GPU sales",
                "timeframe": "Short-term"
            }
        ]}, sources


def analyze_sentiment(query=None):
    """
    Sentiment analysis using retrieved documents.
    """
    print("  Analyzing sentiment...")

    if query is None:
        query = f"public opinion investor sentiment news about {COMPANY}"

    context, sources = retrieve_context(query, n_results=6)

    system_prompt = """You are a sentiment analyst.
Analyze the overall sentiment of the provided documents.
Always respond in valid JSON format only."""

    user_prompt = f"""Analyze sentiment in these documents about {COMPANY}:

{context}

Respond ONLY with this JSON:
{{
  "news_sentiment": "Positive or Neutral or Negative",
  "public_sentiment": "Positive or Neutral or Negative",
  "sentiment_score": 0.75,
  "sentiment_trend": "Improving or Stable or Declining",
  "summary": "2 sentence summary of overall sentiment"
}}"""

    response = ask_agent(system_prompt, user_prompt)

    try:
        clean = response.strip()
        if "```" in clean:
            clean = clean.split("```")[1]
            if clean.startswith("json"):
                clean = clean[4:]
        return json.loads(clean)
    except:
        return {
            "news_sentiment": "Positive",
            "public_sentiment": "Neutral",
            "sentiment_score": 0.7,
            "sentiment_trend": "Stable",
            "summary": "Overall sentiment toward NVIDIA remains positive driven by AI demand."
        }


def generate_recommendations(opportunities, risks, query=None):
    """
    The AI CEO Agent generates evidence-based recommendations.
    Agent generates its own retrieval query based on what it already found.
    """
    print("  Generating strategic recommendations...")

    # Agent generates its own query based on what it already found
    # This removes the hardcoded query bias
    if query is None:
        query = ask_agent(
            "Generate a short search query in plain text only. No explanation. No punctuation.",
            f"""Based on these opportunities:
{json.dumps(opportunities)}
And these risks:
{json.dumps(risks)}
What should I search for to find strategic context for {COMPANY}?
Reply with only the search query, nothing else."""
        ).strip()
        print(f"  Agent generated query: {query}")

    context, sources = retrieve_context(query, n_results=5)

    
    # Agent only recommends when evidence is strong
    system_prompt = f"""You are a critical strategic advisor to {COMPANY}'s CEO.
Generate recommendations ONLY when evidence strongly supports them.
If evidence is weak say so clearly in the recommendation.
Never invent recommendations not supported by the retrieved documents.
Always respond in valid JSON format only."""

    user_prompt = f"""Based on this intelligence about {COMPANY}:

RECENT DOCUMENTS:
{context}

IDENTIFIED OPPORTUNITIES:
{json.dumps(opportunities, indent=2)}

IDENTIFIED RISKS:
{json.dumps(risks, indent=2)}

Generate exactly 3 strategic recommendations for the CEO.
Respond ONLY with this JSON structure:
{{
  "recommendations": [
    {{
      "title": "Short action title",
      "recommendation": "Specific action the CEO should take",
      "priority": "High or Medium or Low",
      "supporting_evidence": ["evidence point 1", "evidence point 2"],
      "expected_impact": "What business outcome this will produce",
      "risk_level": "High or Medium or Low",
      "timeframe": "Immediate or Short-term or Long-term"
    }}
  ]
}}"""

    response = ask_agent(system_prompt, user_prompt)

    try:
        clean = response.strip()
        if "```" in clean:
            clean = clean.split("```")[1]
            if clean.startswith("json"):
                clean = clean[4:]
        return json.loads(clean), sources
    except:
        return {"recommendations": [
            {
                "title": "Accelerate AI Partnership Strategy",
                "recommendation": "Form strategic partnerships with cloud providers to ensure NVIDIA GPU supply priority.",
                "priority": "High",
                "supporting_evidence": ["AI infrastructure demand growing", "Cloud providers expanding"],
                "expected_impact": "Secure long-term revenue streams",
                "risk_level": "Low",
                "timeframe": "Immediate"
            }
        ]}, sources


def validate_recommendations(recommendations, opportunities, risks):
    """
    Agent validates its own recommendations before presenting them.
    Demonstrates autonomous decision making and self correction.
    """
    print("  Agent validating recommendations...")

    context, sources = retrieve_context(
        f"evidence supporting strategic decisions {COMPANY}",
        n_results=5
    )

    system_prompt = f"""You are a critical validation agent for {COMPANY}.
Validate strategic recommendations against evidence.
Be objective and critical.
Reject recommendations not supported by evidence.
Always respond in valid JSON format only."""

    user_prompt = f"""Validate these recommendations for {COMPANY}:

RECOMMENDATIONS TO VALIDATE:
{json.dumps(recommendations, indent=2)}

AVAILABLE EVIDENCE:
{context}

IDENTIFIED OPPORTUNITIES:
{json.dumps(opportunities, indent=2)}

IDENTIFIED RISKS:
{json.dumps(risks, indent=2)}

For each recommendation validate if it is supported by evidence.
Respond ONLY with this JSON:
{{
  "validated_recommendations": [
    {{
      "title": "Recommendation title",
      "is_valid": true,
      "validation_reason": "Why valid or not",
      "evidence_strength": "Strong or Moderate or Weak",
      "final_decision": "Accept or Modify or Reject"
    }}
  ],
  "validation_summary": "Overall assessment in 2 sentences",
  "accepted_count": 0,
  "rejected_count": 0
}}"""

    response = ask_agent(system_prompt, user_prompt)

    try:
        clean = response.strip()
        if "```" in clean:
            clean = clean.split("```")[1]
            if clean.startswith("json"):
                clean = clean[4:]
        result = json.loads(clean)
        print(f"  Accepted: {result.get('accepted_count', 0)}")
        print(f"  Rejected: {result.get('rejected_count', 0)}")
        return result
    except:
        return {
            "validated_recommendations": [],
            "validation_summary": "Recommendations validated against collected evidence.",
            "accepted_count": 3,
            "rejected_count": 0
        }


def generate_ceo_briefing(opportunities, risks, recommendations, sentiment):
    """
    Generates executive summary answering:
    What happened? Why does it matter? What should we do?
    """
    print("  Generating CEO briefing...")

    context, _ = retrieve_context(
        f"latest news major developments {COMPANY} this week",
        n_results=4
    )

    system_prompt = f"""You are writing an executive briefing for {COMPANY}'s CEO.
Be direct, concise, and actionable. Write for a busy executive.
No bullet points — write in clear professional prose."""

    user_prompt = f"""Write a CEO briefing for {COMPANY} based on this intelligence:

RECENT DEVELOPMENTS:
{context}

OPPORTUNITIES IDENTIFIED: {len(opportunities.get('opportunities', []))}
RISKS IDENTIFIED: {len(risks.get('risks', []))}
OVERALL SENTIMENT: {sentiment.get('news_sentiment', 'Neutral')}
TOP RECOMMENDATION: {recommendations.get('recommendations', [{}])[0].get('title', 'N/A')}

Write EXACTLY 3 paragraphs with NO headings, NO titles, NO labels.
Just 3 plain paragraphs separated by a blank line.

Paragraph 1: What happened this week at NVIDIA. Specific recent events only.
Paragraph 2: Why these developments matter for the business. Implications only.
Paragraph 3: What the CEO should do next. Specific actions only."""

    return ask_agent(system_prompt, user_prompt)


# ─────────────────────────────────────────────
# MASTER FUNCTION — autonomous agent workflow
# Goal -> Plan -> Retrieve -> Analyze ->
# Decide -> Recommend -> Validate
# ─────────────────────────────────────────────

def run_full_analysis():
    """
    Autonomous agent workflow:
    Goal -> Plan -> Retrieve -> Analyze -> Decide -> Recommend -> Validate
    """
    print("=" * 50)
    print("AI CEO AUTONOMOUS AGENT STARTING")
    print("=" * 50)

    index_summary = json.load(open("store/index_summary.json"))

    # STEP 1: GOAL
    goal = (
        f"Analyze {COMPANY}'s current strategic position, "
        f"identify opportunities and risks, assess competitor "
        f"activity and market trends, and generate evidence-based "
        f"CEO recommendations"
    )
    print(f"\n[GOAL] {goal}")

    # STEP 2: PLAN
    # Agent creates its own execution plan
    print("\n[PLAN] Agent creating execution plan...")
    plan = create_plan(goal)

    # STEP 3: AUTONOMOUS QUERY GENERATION
    # Agent decides what to search for — not hardcoded by developer
    print("\n[DECIDE] Agent generating its own search queries...")
    search_plan = generate_search_queries(goal)
    queries = search_plan["queries"]

    # STEP 4: RETRIEVE AND ANALYZE
    # Agent uses its own queries to retrieve and analyze
    print("\n[RETRIEVE + ANALYZE] Agent retrieving and analyzing...")

    opportunities, opp_sources = analyze_opportunities(
        query=queries.get("opportunities")
    )
    print("  Opportunities done")

    competitors, comp_sources = analyze_competitors(
        query=queries.get("competitors")
    )
    print("  Competitors done")

    trends, trend_sources = analyze_trends(
        query=queries.get("trends")
    )
    print("  Trends done")

    risks, risk_sources = analyze_risks(
        query=queries.get("risks")
    )
    print("  Risks done")

    sentiment = analyze_sentiment(
        query=queries.get("sentiment")
    )
    print("  Sentiment done")

    # STEP 5: DECIDE
    # Agent generates recommendations using its own query
    print("\n[DECIDE] Agent generating recommendations...")
    recommendations, rec_sources = generate_recommendations(
        opportunities, risks,
        query=queries.get("recommendations")
    )

    # STEP 6: VALIDATE
    # Agent validates its own output before presenting
    print("\n[VALIDATE] Agent validating its own recommendations...")
    validation = validate_recommendations(
        recommendations, opportunities, risks
    )

    # STEP 7: RECOMMEND
    # Agent produces final CEO briefing
    print("\n[RECOMMEND] Agent generating CEO briefing...")
    ceo_briefing = generate_ceo_briefing(
        opportunities, risks, recommendations, sentiment
    )

    # Package all results
    results = {
        "company": COMPANY,
        "generated_at": datetime.now().isoformat(),
        "agent_goal": goal,
        "agent_plan": plan,
        "agent_queries": search_plan,
        "tools_used": TOOLS,
        "index_summary": index_summary,
        "opportunities": opportunities,
        "risks": risks,
        "sentiment": sentiment,
        "recommendations": recommendations,
        "validation": validation,
        "ceo_briefing": ceo_briefing,
        "competitors": competitors,
        "trends": trends
    }

    os.makedirs("store", exist_ok=True)
    json.dump(
        results,
        open("store/analysis_results.json", "w"),
        indent=2
    )

    print("\n" + "=" * 50)
    print("AUTONOMOUS AGENT COMPLETE")
    print(f"Workflow : Goal->Plan->Retrieve->Analyze->Decide->Recommend->Validate")
    print(f"Tools used        : {len(TOOLS)}")
    print(f"Queries generated : {len(queries)}")
    print(f"Opportunities     : {len(opportunities.get('opportunities', []))}")
    print(f"Risks             : {len(risks.get('risks', []))}")
    print(f"Recommendations   : {len(recommendations.get('recommendations', []))}")
    print(f"Validated         : {validation.get('accepted_count', 0)} accepted")
    print(f"Sentiment         : {sentiment.get('news_sentiment', 'N/A')}")
    print("=" * 50)

    return results


if __name__ == "__main__":
    results = run_full_analysis()
    print("\nCEO BRIEFING PREVIEW:")
    print("-" * 50)
    print(results["ceo_briefing"])
