import feedparser
import pandas as pd
import os
from cleaning import clean_html
from makedashboard import create_filtered_dashboard


SIGNAL = ["excel","sql","python","etl","pipeline","dbt","data quality","data integrity","warehouse","automation","transformation","cleaning"]
RED    = ["storytelling","stakeholder","insights","influence","strategic","policy","translate data","senior leadership","narrative", "communicate to non-technical", "business partnering", "commercial acumen", "data-driven culture"]

# Define your feeds and their corresponding filenames
FEEDS = [
    {"name": "londonrss",     "url": "https://rss.app/feeds/xLVD44xRiE1A5RDp.xml",      "file": "london_jobs.csv"},
    {"name": "wellingtonrss", "url": "https://rss.app/feeds/maBHYOfvMWL0hlLj.xml",  "file": "wellington_jobs.csv"},
    {"name": "xchurchrss",    "url": "https://rss.app/feeds/EVDHE0YpoOwAWE4D.xml", "file": "xchurch_jobs.csv"}
]

def score(text):
    t = text.lower()
    return sum(1 for w in SIGNAL if w in t) - sum(1 for w in RED if w in t)

def process_feed(feed_config):
    db_file = feed_config["file"]
    print(f"--- Processing {feed_config['name']} ---")

    # 1. Load existing jobs
    if os.path.exists(db_file):
        df_existing = pd.read_csv(db_file)
        existing_links = set(df_existing['link'])
    else:
        df_existing = pd.DataFrame()
        existing_links = set()

    # 2. Fetch the feed
    feed = feedparser.parse(feed_config["url"])

    new_rows = []
    for e in feed.entries:
        if e.link not in existing_links:
            body = clean_html(e.get("summary", e.get("description", "")))
            s = score(body)
            if s > 0:
                new_rows.append({
                    "title":   e.title,
                    "company": e.get("author", ""),
                    "link":    e.link,
                    "score":   s,
                    "date":    e.get("published", ""),
                    "snippet": body[:3000]
                })

    # 3. Combine and Save
    if new_rows:
        df_new = pd.DataFrame(new_rows)
        df_final = pd.concat([df_existing, df_new], ignore_index=True)
        df_final = df_final.sort_values("score", ascending=False)
        df_final.to_csv(db_file, index=False)
        print(f"Added {len(new_rows)} new jobs. Total: {len(df_final)}")
    else:
        print(f"No new jobs for {feed_config['name']}.")

# Main execution loop
def run_scraper():
    for f in FEEDS:
        process_feed(f)

if __name__ == "__main__":
    run_scraper()