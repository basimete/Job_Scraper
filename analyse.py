import os
import pandas as pd
from dotenv import load_dotenv
from anthropic import Anthropic
from makedashboard import create_filtered_dashboard

load_dotenv()
client = Anthropic(api_key=os.getenv("CLAUDE_API_KEY"))

# Define the files to process
FILES_TO_ANALYZE = ["london_jobs.csv", "wellington_jobs.csv", "xchurch_jobs.csv"]

def analyze_file(csv_file):
    if not os.path.exists(csv_file):
        print(f"--- Skipping {csv_file} (File not found) ---")
        return

    print(f"--- Starting AI Analysis for {csv_file} ---")
    df = pd.read_csv(csv_file)
    
    if 'daily_tasks' not in df.columns:
        df['daily_tasks'] = ""

    # FILTER: Score >= 4 and daily_tasks is empty
    mask = (df['score'] >= 4) & (df['daily_tasks'].fillna('').str.strip() == "")
    to_analyze = df[mask]

    if to_analyze.empty:
        print(f"✅ No new high-scoring jobs to analyze in {csv_file}.")
        return

    print(f"🤖 Processing {len(to_analyze)} new high-scoring rows...")

    for index, row in to_analyze.iterrows():
        try:
            print(f"Analyzing: {row['title']}...")
            message = client.messages.create(
                model="claude-sonnet-4-6", # Note: Standardizing to current model name
                max_tokens=200,
                temperature=0,
                messages=[{
                    "role": "user", 
                    "content": f"Based on this job: {row['title']} - {row['snippet']}. "
                    "List 3 bullet points of what the candidate actually PRODUCES day-to-day. Return ONLY the bullet points. Do not include introductory or concluding text."
                }]
            )
            
            # Save progress row-by-row so you don't lose credits if it crashes
            df.at[index, 'daily_tasks'] = message.content[0].text.strip()
            df.to_csv(csv_file, index=False)
            print("✅ Success")

        except Exception as e:
            print(f"❌ Error during AI call: {e}")
            return # Exit this file if there is an API error

def run_ai_analysis():
    for csv_file in FILES_TO_ANALYZE:
        analyze_file(csv_file)

if __name__ == "__main__":
    run_ai_analysis()