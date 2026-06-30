from collectors.news import collect_news
from collectors.research import collect_arxiv
from collectors.company import collect_company_news
from collectors.finance import collect_finance_news
import json
import os

def run_all_collectors():

    os.makedirs("data", exist_ok=True)

    print("=" * 50)
    print("STARTING DATA COLLECTION")
    print("=" * 50)

    # Source 1: Google News
    news = collect_news("NVIDIA", max_items=60)
    json.dump(news, open("data/news.json", "w", encoding="utf-8"), indent=2)
    print()

    # Source 2: Tech news RSS feeds
    tech = collect_arxiv()
    json.dump(tech, open("data/arxiv.json", "w", encoding="utf-8"), indent=2)
    print()

    # Source 3: NVIDIA official newsroom
    company = collect_company_news(max_items=40)
    json.dump(company, open("data/company.json", "w", encoding="utf-8"), indent=2)
    print()


    # Source 4: Financial news
    finance = collect_finance_news(max_items=50)
    json.dump(finance, open("data/finance.json", "w", encoding="utf-8"), indent=2)
    print()

    total = len(news) + len(tech) + len(company) + len(finance)

    print("=" * 50)
    print("COLLECTION COMPLETE")
    print(f"Google News          : {len(news)}")
    print(f"Tech news RSS        : {len(tech)}")
    print(f"NVIDIA newsroom      : {len(company)}")
    print(f"Financial news       : {len(finance)}")
    print(f"TOTAL DOCUMENTS      : {total}")
    print(f"Minimum required     : 100")
    print(f"Status               : {' PASS' if total >= 100 else ' NEED MORE'}")
    print("=" * 50)

    return news, tech, company, finance


if __name__ == "__main__":
    run_all_collectors()