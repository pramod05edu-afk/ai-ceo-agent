import streamlit as st
import json
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

st.set_page_config(
    page_title="AI CEO Strategic Intelligence",
    layout="wide"
)

st.markdown("""
<style>
    .main {
        background-color: #0D1117;
    }
    h1 {
        color: #76B900;
        font-weight: 700;
    }
    h2 {
        color: #76B900;
        border-bottom: 2px solid #76B900;
        padding-bottom: 8px;
    }
    div[data-testid="stMetric"] {
        background-color: #1A1F24;
        border: 1px solid #76B900;
        border-radius: 10px;
        padding: 15px;
    }
    div[data-testid="stMetricValue"] {
        color: #76B900;
    }
    .stExpander {
        border: 1px solid #2A2F35;
        border-radius: 8px;
        background-color: #161B22;
    }
    .stButton button {
        background-color: #76B900;
        color: white;
        border-radius: 8px;
        border: none;
        font-weight: 600;
    }
    .stButton button:hover {
        background-color: #5A8F00;
        color: white;
    }
</style>
""", unsafe_allow_html=True)


st.markdown("""
<div style="background: linear-gradient(90deg, #76B900 0%, #1A1F24 100%);
            padding: 25px; border-radius: 12px; margin-bottom: 20px;">
    <h1 style="color: white; margin: 0; border: none;">
        AI CEO Strategic Intelligence Dashboard
    </h1>
    <p style="color: #E0E0E0; margin: 5px 0 0 0;">
        Powered by RAG + Llama 3.1 | Company: NVIDIA
    </p>
</div>
""", unsafe_allow_html=True)

# Load data
@st.cache_data(ttl=300)
def load_results():
    try:
        return json.load(open("store/analysis_results.json", encoding="utf-8"))
    except:
        return None

@st.cache_data(ttl=300)
def load_summary():
    try:
        return json.load(open("store/index_summary.json", encoding="utf-8"))
    except:
        return None

results = load_results()
summary = load_summary()

if not results:
    st.error("No analysis found. Run: python agent/intelligence.py first")
    st.stop()

# Sidebar
with st.sidebar:
    st.header("Controls")
    st.write("**Company:** NVIDIA")
    st.write("**Model:** Llama 3.1 8B via Groq")
    st.write("**Embedding:** all-MiniLM-L6-v2")
    st.divider()

    if st.button("Run New Analysis", use_container_width=True):
        with st.spinner("Running AI analysis... (1-2 mins)"):
            from agent.intelligence import run_full_analysis
            results = run_full_analysis()
            st.cache_data.clear()
            st.success("Analysis complete!")
            st.rerun()

    if st.button("Recollect Data", use_container_width=True):
        with st.spinner("Collecting fresh data..."):
            from collectors.run_all import run_all_collectors
            run_all_collectors()
            st.success("Data collected!")

    st.divider()
    generated = results.get("generated_at", "")
    if generated:
        dt = datetime.fromisoformat(generated)
        st.caption(f"Last updated: {dt.strftime('%d %b %Y, %H:%M')}")

# Agent Workflow Section
st.header("Agent Workflow")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Goal")
    st.info(results.get("agent_goal", "No goal found"))

    st.subheader("Execution Plan")
    plan = results.get("agent_plan", {})
    for step in plan.get("steps", []):
        st.write(f"- {step}")

with col2:
    st.subheader("Tools Used")
    tools = results.get("tools_used", {})
    for tool, description in tools.items():
        st.write(f"- {description}")

    st.subheader("Agent Generated Queries")
    queries = results.get("agent_queries", {}).get("queries", {})
    for area, query in queries.items():
        with st.expander(f"{area.title()}"):
            st.write(query)

    reasoning = results.get("agent_queries", {}).get("reasoning", "")
    if reasoning:
        st.caption(f"Agent reasoning: {reasoning}")

st.divider()

# Validation Section
st.header("Recommendation Validation")

validation = results.get("validation", {})
validated = validation.get("validated_recommendations", [])

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Accepted", validation.get("accepted_count", 0))
with col2:
    st.metric("Rejected", validation.get("rejected_count", 0))
with col3:
    st.metric("Total Validated", len(validated))

st.write(validation.get("validation_summary", ""))

if validated:
    for v in validated:
        decision = v.get("final_decision", "Accept")
        with st.expander(
            f"{v.get('title', 'Recommendation')} "
            f"— {decision} "
            f"— Evidence: {v.get('evidence_strength', 'N/A')}"
        ):
            st.write(v.get("validation_reason", ""))

st.divider()


# Section 1: Company Overview
st.header("Section 1: Company Overview")

col1, col2, col3, col4 = st.columns(4)

index = results.get("index_summary", {})

with col1:
    st.metric("Company", "NVIDIA")
with col2:
    st.metric("Documents Collected", index.get("total_documents", 0))
with col3:
    st.metric("Data Sources", index.get("num_sources", 0))
with col4:
    generated = results.get("generated_at", "")
    if generated:
        dt = datetime.fromisoformat(generated)
        st.metric("Last Updated", dt.strftime("%H:%M, %d %b"))

st.divider()

# Section 2: Market Intelligence
st.header("Section 2: Market Intelligence")

try:
    news_data = json.load(open("data/news.json", encoding="utf-8"))
    company_data = json.load(open("data/company.json", encoding="utf-8"))

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Recent News")
        for article in news_data[:5]:
            with st.expander(article["title"][:80]):
                st.write(article.get("text", "")[:300])
                st.caption(
                    f"Source: {article['source']} | "
                    f"{article.get('published', '')[:16]}"
                )
                if article.get("url"):
                    st.link_button("Read more", article["url"])

    with col2:
        st.subheader("NVIDIA Official Announcements")
        for item in company_data[:5]:
            with st.expander(item["title"][:80]):
                st.write(item.get("text", "")[:300])
                st.caption(f"Published: {item.get('published', '')[:16]}")
                if item.get("url"):
                    st.link_button("Read more", item["url"])

except Exception as e:
    st.warning(f"Could not load market data: {e}")

st.divider()

# Section 3: Opportunity Monitor
st.header("Section 3: Opportunity Monitor")

opportunities = results.get("opportunities", {}).get("opportunities", [])

if opportunities:
    for opp in opportunities:
        impact = opp.get("impact_level", "Medium")
        with st.expander(
            f"{opp.get('title', 'Opportunity')} — Impact: {impact}"
        ):
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(opp.get("description", ""))
                st.info(f"Evidence: {opp.get('evidence', 'N/A')}")
            with col2:
                score = opp.get("confidence_score", 0.8)
                st.metric("Confidence", f"{score:.0%}")
else:
    st.warning("No opportunities found. Run analysis first.")

st.divider()

# Section 4: Risk Monitor
st.header("Section 4: Risk Monitor")

risks = results.get("risks", {}).get("risks", [])

if risks:
    for risk in risks:
        severity = risk.get("severity_level", "Medium")
        with st.expander(
            f"{risk.get('title', 'Risk')} — Severity: {severity}"
        ):
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(risk.get("description", ""))
                st.caption(f"Category: {risk.get('category', 'N/A')}")
                st.warning(f"Evidence: {risk.get('evidence', 'N/A')}")
            with col2:
                score = risk.get("confidence_score", 0.8)
                st.metric("Confidence", f"{score:.0%}")
else:
    st.warning("No risks found. Run analysis first.")

st.divider() 

# Section 5: Competitor Analysis
st.header("Section 5: Competitor Analysis")

competitors = results.get("competitors", {}).get("competitors", [])

if competitors:
    for comp in competitors:
        threat = comp.get("threat_level", "Medium")
        with st.expander(
            f"{comp.get('competitor', 'Competitor')} — Threat Level: {threat}"
        ):
            st.write(f"**Action:** {comp.get('action', '')}")
            st.caption(f"Evidence: {comp.get('evidence', 'N/A')}")
else:
    st.warning("No competitor data found. Run analysis first.")

st.divider()

# Section 6: Technology Trends
st.header("Section 6: Technology Trends")

trends = results.get("trends", {}).get("trends", [])

if trends:
    for trend in trends:
        with st.expander(
            f"{trend.get('trend', 'Trend')} — {trend.get('timeframe', '')}"
        ):
            st.write(trend.get("description", ""))
            st.info(f"Relevance to NVIDIA: {trend.get('relevance', 'N/A')}")
else:
    st.warning("No trends found. Run analysis first.")

st.divider()


# Section 7: Sentiment Analysis
st.header("Section 7: Sentiment Analysis")

sentiment = results.get("sentiment", {})

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "News Sentiment",
        sentiment.get("news_sentiment", "N/A"),
        delta=sentiment.get("sentiment_trend", "Stable")
    )
with col2:
    st.metric(
        "Public Sentiment",
        sentiment.get("public_sentiment", "N/A")
    )
with col3:
    score = sentiment.get("sentiment_score", 0.5)
    st.metric("Sentiment Score", f"{score:.2f} / 1.00")

st.write(sentiment.get("summary", ""))

# Sentiment gauge chart
fig_gauge = go.Figure(go.Indicator(
    mode="gauge+number",
    value=sentiment.get("sentiment_score", 0.5) * 100,
    title={"text": "Overall Sentiment Score", "font": {"color": "#FAFAFA"}},
    number={"font": {"color": "#FAFAFA"}},
    gauge={
        "axis": {"range": [0, 100], "tickcolor": "#FAFAFA"},
        "bar": {"color": "#76B900"},
        "bgcolor": "#1A1F24",
        "borderwidth": 1,
        "bordercolor": "#2A2F35",
        "steps": [
            {"range": [0, 33], "color": "#C0392B"},
            {"range": [33, 66], "color": "#D4A017"},
            {"range": [66, 100], "color": "#1E5631"}
        ],
        "threshold": {
            "line": {"color": "#FFFFFF", "width": 4},
            "thickness": 0.8,
            "value": sentiment.get("sentiment_score", 0.5) * 100
        }
    }
))
fig_gauge.update_layout(
    height=300,
    paper_bgcolor="#0D1117",
    font={"color": "#FAFAFA"}
)

st.plotly_chart(fig_gauge, use_container_width=True)


# Source distribution pie chart
try:
    all_docs = []
    for fname in ["news.json", "arxiv.json", "company.json",
                  "finance.json", "reddit.json"]:
        try:
            d = json.load(open(f"data/{fname}", encoding="utf-8"))
            all_docs.extend(d)
        except:
            pass

    source_counts = {}
    for doc in all_docs:
        src = doc.get("source", "unknown")
        source_counts[src] = source_counts.get(src, 0) + 1

    fig_pie = px.pie(
        values=list(source_counts.values()),
        names=list(source_counts.keys()),
        title="Documents by Source",
        color_discrete_sequence=[
            "#76B900",  # NVIDIA green
            "#3498DB",  # blue
            "#E67E22",  # orange
            "#9B59B6",  # purple
            "#E74C3C",  # red
            "#F1C40F"   # yellow
        ]
    )
    fig_pie.update_layout(
        paper_bgcolor="#0D1117",
        font={"color": "#FAFAFA"},
        legend={"font": {"color": "#FAFAFA"}}
    )
    st.plotly_chart(fig_pie, use_container_width=True)

except Exception as e:
    st.caption(f"Chart unavailable: {e}")

st.divider()

# Section 8: Strategic Recommendations
st.header("Section 8: Strategic Recommendations")

recommendations = results.get("recommendations", {}).get("recommendations", [])

priority_order = {"High": 0, "Medium": 1, "Low": 2}
recommendations = sorted(
    recommendations,
    key=lambda x: priority_order.get(x.get("priority", "Low"), 2)
)

if recommendations:
    for rec in recommendations:
        priority = rec.get("priority", "Medium")
        risk_level = rec.get("risk_level", "Medium")

        with st.expander(
            f"[{priority} Priority] {rec.get('title', 'Recommendation')}"
        ):
            st.write(f"**Action:** {rec.get('recommendation', '')}")
            st.divider()

            col1, col2, col3 = st.columns(3)
            with col1:
                st.write("**Supporting Evidence**")
                for ev in rec.get("supporting_evidence", []):
                    st.write(f"- {ev}")
            with col2:
                st.write("**Expected Impact**")
                st.write(rec.get("expected_impact", "N/A"))
            with col3:
                st.write("**Risk Level**")
                st.write(risk_level)
                st.write("**Timeframe**")
                st.write(rec.get("timeframe", "N/A"))
else:
    st.warning("No recommendations found. Run analysis first.")

st.divider()

# Section 9: CEO Briefing
st.header("Section 9: CEO Briefing")

briefing = results.get("ceo_briefing", "")

if briefing:
    paragraphs = [p.strip() for p in briefing.split("\n\n") if p.strip()]
    labels = ["What Happened", "Why It Matters", "What To Do Next"]

    for i, para in enumerate(paragraphs[:3]):
        label = labels[i] if i < len(labels) else f"Point {i+1}"
        st.subheader(label)
        clean = para.replace("**", "").strip()
        st.write(clean)
else:
    st.warning("No briefing available. Run analysis first.")

st.divider()
st.caption(
    "AI CEO Strategic Intelligence Agent | "
    "NLP Examination Project | "
    "SRH University Heidelberg"
)