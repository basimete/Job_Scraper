import os
import pandas as pd
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()
client = Anthropic(api_key=os.getenv("CLAUDE_API_KEY"))

# 1. Get the absolute path of the folder containing THIS script (/code)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 2. Go up one level to /Job_Scraper, then into /CSV_files
CSV_DIR = os.path.join(BASE_DIR, "..", "CSV_files")

# List only the filenames
FILES_TO_ANALYZE = ["london_jobs.csv", "wellington_jobs.csv", "xchurch_jobs.csv"]

def analyze_file(filename):
    # Construct the full path to the file
    csv_path = os.path.join(CSV_DIR, filename)
    
    if not os.path.exists(csv_path):
        print(f"--- Skipping {filename} (Not found at {csv_path}) ---")
        return

    print(f"--- Starting AI Analysis for {filename} ---")
    df = pd.read_csv(csv_path)
    
    if 'daily_tasks' not in df.columns:
        df['daily_tasks'] = ""

    mask = (df['score'] >= 4) & (df['daily_tasks'].fillna('').str.strip() == "")
    to_analyze = df[mask]

    if to_analyze.empty:
        print(f"✅ No new high-scoring jobs to analyze in {filename}.")
        return

    print(f"🤖 Processing {len(to_analyze)} new high-scoring rows...")

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
                    "List 3 bullet points of what the candidate actually PRODUCES day-to-day. Return ONLY the bullet points."
                }]
            )
            
            df.at[index, 'daily_tasks'] = message.content[0].text.strip()
            # Save back using the full absolute path
            df.to_csv(csv_path, index=False)
            print("✅ Success")

        except Exception as e:
            print(f"❌ Error during AI call: {e}")
            return 

def run_ai_analysis():
    # Final check that the target directory actually exists
    if not os.path.exists(CSV_DIR):
        print(f"❌ Error: The directory {CSV_DIR} does not exist.")
        return

    for filename in FILES_TO_ANALYZE:
        analyze_file(filename)

if __name__ == "__main__":
    run_ai_analysis()