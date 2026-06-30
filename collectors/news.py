import feedparser
import json
import os
import hashlib
from datetime import datetime

def collect_news(company="NVIDIA", max_items=60):
    """
    Collects news articles from Google News RSS feed.
    Returns a list of article dictionaries.
    """
    
    print(f"Collecting news for: {company}")
    
    # Google News RSS URL 
    url = f"https://news.google.com/rss/search?q={company}&hl=en-US&gl=US&ceid=US:en"
    
    # Parse the RSS feed
    feed = feedparser.parse(url)
    
    docs = []
    for entry in feed.entries[:max_items]:
        
        # Extract text content
        title = entry.get("title", "").strip()
        summary = entry.get("summary", "").strip()
        
        # Skip if both title and summary are empty
        if not title and not summary:
            continue
        
        # Build the document
        doc = {
            "source": "google_news",
            "title": title,
            "text": summary,
            "url": entry.get("link", ""),
            "published": entry.get("published", ""),
            "collected_at": datetime.now().isoformat(),
            "doc_id": hashlib.md5((title + summary).encode()).hexdigest()
        }
        
        docs.append(doc)
    
    print(f"Collected {len(docs)} articles from Google News")
    return docs


if __name__ == "__main__":
    
    # Collect news
    docs = collect_news("NVIDIA")
    
    # Make sure data folder exists
    os.makedirs("data", exist_ok=True)
    
    # Save to file
    output_path = "data/news.json"
    json.dump(docs, open(output_path, "w", encoding="utf-8"), indent=2)
    
    print(f"Saved to {output_path}")
    print(f"First article title: {docs[0]['title'] if docs else 'none'}")