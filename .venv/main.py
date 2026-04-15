import feedparser, pandas as pd, datetime

SIGNAL = ["sql","python","etl","pipeline","dbt","data quality","data integrity","warehouse","automation","transformation","cleaning"]
RED    = ["storytelling","stakeholder","insights","influence","strategic","policy","translate data","senior leadership"]

def score(text):
    t = text.lower()
    return sum(1 for w in SIGNAL if w in t) - sum(1 for w in RED if w in t)

feed = feedparser.parse("https://rss.app/feeds/xLVD44xRiE1A5RDp.xml")
print(f"Found {len(feed.entries)} entries in the feed.")

rows = []
for e in feed.entries:
    body = e.get("summary","")
    rows.append({
        "title":   e.title,
        "company": e.get("author",""),
        "link":    e.link,
        "score":   score(body),
        "date":    e.get("published",""),
        "snippet": body[:300]
    })

df = pd.DataFrame(rows).sort_values("score", ascending=False)
df = df[df.score > 0]          # drop everything that scores zero or below
df.to_csv("jobs.csv", index=False)
print(df[["title","company","score"]].to_string())