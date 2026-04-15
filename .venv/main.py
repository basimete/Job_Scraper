import feedparser
import pandas as pd
import datetime
from cleaning import clean_html  

SIGNAL = ["sql","python","etl","pipeline","dbt","data quality","data integrity","warehouse","automation","transformation","cleaning"]
RED    = ["storytelling","stakeholder","insights","influence","strategic","policy","translate data","senior leadership"]

def score(text):
    t = text.lower()
    return sum(1 for w in SIGNAL if w in t) - sum(1 for w in RED if w in t)

feed = feedparser.parse("https://rss.app/feeds/xLVD44xRiE1A5RDp.xml")

rows = []
for e in feed.entries:
    # Get the raw text from the feed
    raw_body = e.get("summary", e.get("description", ""))
    
    # Use the function from your utils.py to clean it
    body = clean_html(raw_body)
    
    rows.append({
        "title":   e.title,
        "company": e.get("author", ""),
        "link":    e.link,
        "score":   score(body),
        "date":    e.get("published", ""),
        "snippet": body[:300] # This will now be clean text without HTML tags
    })

# Create the DataFrame and filter
df = pd.DataFrame(rows)

if not df.empty:
    # Only keep jobs with a positive score
    df = df.sort_values("score", ascending=False)
    df = df[df.score > 0]
    
    # Save and Print
    df.to_csv("jobs.csv", index=False)
    print(df[["title", "company", "score"]].to_string())
else:
    print("No entries found in the feed.")