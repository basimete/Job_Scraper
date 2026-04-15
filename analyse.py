import os
import time
import pandas as pd
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()
client = Anthropic(api_key=os.getenv("CLAUDE_API_KEY"))

def extract_job_details():
    df = pd.read_csv('jobs.csv')
    
    # Initialize the column if it doesn't exist
    if 'daily_tasks' not in df.columns:
        df['daily_tasks'] = ""

    # FILTER: Only look at 4s and 5s that haven't been analyzed yet
    # Adjust 'Score' to match your exact column name (e.g., 'score' or 'Rating')
    mask = (df['score'] >= 4) & (df['daily_tasks'].isna() | (df['daily_tasks'] == ""))
    to_analyze = df[mask]

    print(f"Found {len(to_analyze)} high-scoring jobs to analyze...")

    for index, row in to_analyze.iterrows():
        print(f"Extracting details for: {row['title']}...")

        try:
            # Using the 2026 Sonnet 4.6 model
            message = client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=150,
                temperature=0,
                system="You are a career coach. Extract only the concrete daily outputs of a job.",
                messages=[{
                    "role": "user", 
                    "content": f"Based on this job snippet, what does the person actually produce or do every day? Summarize in 2 bullet points. \nSnippet: {row['snippet']}"
                }]
            )
            
            tasks = message.content[0].text.strip()
            df.at[index, 'daily_tasks'] = tasks
            print(f"✅ Success")
            
            # Save progress immediately
            df.to_csv('jobs.csv', index=False)
            time.sleep(0.5) 

        except Exception as e:
            print(f"❌ Error on {row['title']}: {e}")
            continue

    print("Done! Check your jobs.csv for the 'Daily_Tasks' column.")

if __name__ == "__main__":
    extract_job_details()