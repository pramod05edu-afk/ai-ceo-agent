import feedparser
import json
import os
import hashlib
from datetime import datetime

def collect_company_news(max_items=40):
    """
    Collects official press releases directly from NVIDIA's newsroom.
    This is the company's own voice - what NVIDIA says about itself.
    No API key needed.
    """
    
    print("Collecting from NVIDIA official newsroom...")
    
    url = "https://nvidianews.nvidia.com/releases.xml"
    
    feed = feedparser.parse(url)
    
    docs = []
    for entry in feed.entries[:max_items]:
        
        title = entry.get("title", "").strip()
        summary = entry.get("summary", "").strip()
        
        if not title and not summary:
            continue
        
        doc = {
            "source": "nvidia_newsroom",
            "title": title,
            "text": summary,
            "url": entry.get("link", ""),
            "published": entry.get("published", ""),
            "collected_at": datetime.now().isoformat(),
            "doc_id": hashlib.md5((title + summary).encode()).hexdigest()
        }
        
        docs.append(doc)
    
    print(f"Collected {len(docs)} press releases from NVIDIA newsroom")
    return docs


if __name__ == "__main__":
    
    docs = collect_company_news()
    
    os.makedirs("data", exist_ok=True)
    
    output_path = "data/company.json"
    json.dump(docs, open(output_path, "w", encoding="utf-8"), indent=2)
    
    print(f"Saved to {output_path}")
    print(f"First release title: {docs[0]['title'] if docs else 'none'}")