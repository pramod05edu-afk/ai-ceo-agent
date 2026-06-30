import feedparser
import json
import os
import hashlib
from datetime import datetime

def collect_finance_news(max_items=50):
    """
    Collects financial news about NVIDIA from Yahoo Finance 
    and other financial RSS feeds.
    """
    
    print("Collecting financial news...")
    
    feeds = [
        {
            "name": "Yahoo Finance NVIDIA",
            "url": "https://feeds.finance.yahoo.com/rss/2.0/headline?s=NVDA&region=US&lang=en-US"
        },
        {
            "name": "Yahoo Finance AI",
            "url": "https://feeds.finance.yahoo.com/rss/2.0/headline?s=NVDA+AMD+INTC&region=US&lang=en-US"
        },
        {
            "name": "Seeking Alpha NVIDIA",
            "url": "https://seekingalpha.com/api/sa/combined/NVDA.xml"
        },
        {
            "name": "MarketWatch Tech",
            "url": "https://feeds.content.dowjones.io/public/rss/mw_technology"
        },
        {
            "name": "Investopedia Tech",
            "url": "https://www.investopedia.com/feedbuilder/feed/getfeed?feedName=rss_technology"
        }
    ]
    
    docs = []
    keywords = ["nvidia", "nvda", "gpu", "jensen huang", "ai chip",
                "semiconductor", "amd", "intel", "cuda", "datacenter",
                "artificial intelligence", "machine learning", "h100", "blackwell"]
    
    for feed_info in feeds:
        try:
            print(f"  Fetching {feed_info['name']}...")
            feed = feedparser.parse(feed_info["url"])
            count = 0
            
            for entry in feed.entries[:max_items]:
                title = entry.get("title", "").strip()
                summary = entry.get("summary", "").strip()
                full_text = (title + " " + summary).lower()
                
                # For Yahoo Finance NVIDIA feed, all results are relevant
                # For others, filter by keywords
                if "yahoo" in feed_info["name"].lower():
                    is_relevant = True
                else:
                    is_relevant = any(kw in full_text for kw in keywords)
                
                if is_relevant and title:
                    doc = {
                        "source": f"finance_{feed_info['name'].lower().replace(' ', '_')}",
                        "title": title,
                        "text": summary if summary else title,
                        "url": entry.get("link", ""),
                        "published": entry.get("published", ""),
                        "collected_at": datetime.now().isoformat(),
                        "doc_id": hashlib.md5(
                            (title + summary).encode()
                        ).hexdigest()
                    }
                    docs.append(doc)
                    count += 1
            
            print(f"  Got {count} articles from {feed_info['name']}")
            
        except Exception as e:
            print(f"  Skipped {feed_info['name']}: {e}")
    
    print(f"Collected {len(docs)} financial news articles total")
    return docs


if __name__ == "__main__":
    docs = collect_finance_news()
    os.makedirs("data", exist_ok=True)
    output_path = "data/finance.json"
    json.dump(docs, open(output_path, "w", encoding="utf-8"), indent=2)
    print(f"Saved to {output_path}")
    if docs:
        print(f"First article: {docs[0]['title']}")