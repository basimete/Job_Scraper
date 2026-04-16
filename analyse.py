#i can run this ad hoc to create a dahsboard and do the AI analysis, it's not automated.
import os
import pandas as pd
from dotenv import load_dotenv
from anthropic import Anthropic
from makedashboard import create_filtered_dashboard

load_dotenv()
client = Anthropic(api_key=os.getenv("CLAUDE_API_KEY"))

def extract_job_details():
    df = pd.read_csv('jobs.csv')
    
    # Ensure column exists in lowercase
    if 'daily_tasks' not in df.columns:
        df['daily_tasks'] = ""

    # FILTER: 
    # 1. Score is 4 or 5
    # 2. daily_tasks is empty (handling NaN and empty strings)
    mask = (df['score'] >= 4) & (df['daily_tasks'].fillna('').str.strip() == "")
    to_analyze = df[mask]

    print(f"⏭️ Skipping {len(df) - len(to_analyze)} rows (already done or low score).")
    print(f"🤖 Processing {len(to_analyze)} new high-scoring rows...")
    create_filtered_dashboard() # Trigger dashboard update

    for index, row in to_analyze.iterrows():
        try:
            print(f"Analyzing: {row['title']}...")
            message = client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=200,
                temperature=0,
                messages=[{
                    "role": "user", 
                    "content": f"Based on this job: {row['title']} - {row['snippet']}. "
                    "List 3 bullet points of what the candidate actually PRODUCES day-to-day. Return ONLY the bullet points. Do not include introductory or concluding text."
                }]
            )
            
            df.at[index, 'daily_tasks'] = message.content[0].text.strip()
            df.to_csv('jobs.csv', index=False)
            print("✅ Success")

        except Exception as e:
            print(f"❌ Error: {e}")
            break

if __name__ == "__main__":
    extract_job_details()