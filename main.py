import feedparser
import pandas as pd
import os
from cleaning import clean_html
from makedashboard import create_filtered_dashboard

SIGNAL = ["sql","python","etl","pipeline","dbt","data quality","data integrity","warehouse","automation","transformation","cleaning"]
RED    = ["storytelling","stakeholder","insights","influence","strategic","policy","translate data","senior leadership"]
DB_FILE = "jobs.csv"

def score(text):
    t = text.lower()
    return sum(1 for w in SIGNAL if w in t) - sum(1 for w in RED if w in t)

# 1. Load existing jobs so we don't save duplicates
if os.path.exists(DB_FILE):
    df_existing = pd.read_csv(DB_FILE)
    existing_links = set(df_existing['link'])
else:
    df_existing = pd.DataFrame()
    existing_links = set()

# 2. Fetch the feed
feed = feedparser.parse("https://rss.app/feeds/xLVD44xRiE1A5RDp.xml")

new_rows = []
for e in feed.entries:
    if e.link not in existing_links: # Only process if it's new
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
    df_final.to_csv(DB_FILE, index=False)
    print(f"Added {len(new_rows)} new jobs. Total jobs: {len(df_final)}")
    create_filtered_dashboard() # Trigger dashboard update
else:
    print("No new jobs found today.")
