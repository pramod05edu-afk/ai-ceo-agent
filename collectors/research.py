import feedparser
import json
import os
import hashlib
from datetime import datetime

def collect_arxiv(query="NVIDIA GPU artificial intelligence", max_items=50):
    """
    Collects tech news from multiple reliable RSS sources.
    Uses TechCrunch, The Verge, and Ars Technica - all free public RSS feeds.
    """
    
    print("Collecting from tech news RSS feeds...")
    
    # Multiple reliable RSS sources - no API key needed
    feeds = [
        {
            "name": "TechCrunch",
            "url": "https://techcrunch.com/feed/"
        },
        {
            "name": "The Verge",
            "url": "https://www.theverge.com/rss/index.xml"
        },
        {
            "name": "Ars Technica",
            "url": "https://feeds.arstechnica.com/arstechnica/technology-lab"
        },
        {
            "name": "VentureBeat AI",
            "url": "https://venturebeat.com/category/ai/feed/"
        }
    ]
    
    docs = []
    keywords = ["nvidia", "gpu", "ai chip", "cuda", "jensen", "geforce", 
                "datacenter", "artificial intelligence", "semiconductor",
                "amd", "intel", "machine learning", "deep learning"]
    
    for feed_info in feeds:
        try:
            print(f"  Fetching {feed_info['name']}...")
            feed = feedparser.parse(feed_info["url"])
            count = 0
            
            for entry in feed.entries:
                title = entry.get("title", "").strip()
                summary = entry.get("summary", "").strip()
                full_text = (title + " " + summary).lower()
                
                # Only keep articles relevant to NVIDIA/AI/chips
                if any(kw in full_text for kw in keywords):
                    doc = {
                        "source": f"tech_news_{feed_info['name'].lower().replace(' ', '_')}",
                        "title": title,
                        "text": summary,
                        "url": entry.get("link", ""),
                        "published": entry.get("published", ""),
                        "collected_at": datetime.now().isoformat(),
                        "doc_id": hashlib.md5((title + summary).encode()).hexdigest()
                    }
                    docs.append(doc)
                    count += 1
            
            print(f"  Got {count} relevant articles from {feed_info['name']}")
            
        except Exception as e:
            print(f"  Skipped {feed_info['name']}: {e}")
    
    print(f"Collected {len(docs)} tech news articles total")
    return docs


if __name__ == "__main__":
    docs = collect_arxiv()
    os.makedirs("data", exist_ok=True)
    output_path = "data/arxiv.json"
    json.dump(docs, open(output_path, "w", encoding="utf-8"), indent=2)
    print(f"Saved to {output_path}")
    if docs:
        print(f"First article: {docs[0]['title']}")