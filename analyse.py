import pandas as pd
from google import genai
import os
import time
import warnings

print("--- TEST SUCCESSFUL ---")

# --- 1. SILENCE THE NOISE ---
# This hides the "Python 3.9" and "LibreSSL" warnings so you can see your data
warnings.filterwarnings("ignore")
os.environ['GRPC_PYTHON_SHOW_CYBER_HEALTH_CHECK'] = '0'

# --- 2. SETUP ---
# CRITICAL: Use the NEW key from a NEW project in AI Studio to bypass the 403 error
API_KEY = ""
MODEL_ID = "gemini-1.5-flash" 
DB_FILE = "jobs.csv"

client = genai.Client(
    api_key=API_KEY,
    http_options={'api_version': 'v1'} # Forces the stable production API
)

def get_gemini_insight(description):
    """Sends job text to Gemini and returns 3 output-focused bullet points."""
    prompt = f"""
    Analyze this job description:
    {description}
    
    Provide exactly 3 bullet points explaining what the role actually PRODUCES day-to-day. 
    Focus on tangible output (e.g., 'Maintains SQL pipelines', 'Drafts executive briefs').
    """
    
    try:
        response = client.models.generate_content(
            model=MODEL_ID,
            contents=prompt
        )
        return response.text.strip()
    except Exception as e:
        # If it fails, we want to know why in the terminal, not just the CSV
        print(f"   ⚠️ Gemini failed on this row: {e}")
        return f"Error: {e}"

def run_analysis():
    print("Checking for jobs.csv...")
    if not os.path.exists(DB_FILE):
        print(f"❌ Error: {DB_FILE} not found. Did you run scraper.py?")
        return

    df = pd.read_csv(DB_FILE)
    print(f"Loaded CSV with {len(df)} total rows.")
    
    if 'ai_insight' not in df.columns:
        print("Column 'ai_insight' missing. Adding it now...")
        df['ai_insight'] = ""

    # --- DEBUGGING THE FILTER ---
    high_score_count = len(df[df['score'] >= 3])
    print(f"Jobs with score >= 3: {high_score_count}")
    
    no_insight_count = len(df[(df['ai_insight'].isna()) | (df['ai_insight'] == "")])
    print(f"Jobs with NO insight yet: {no_insight_count}")

    # The actual filter
    mask = (df['score'] >= 3)
    targets = df[mask]
    
    print(f"Combined filter found {len(targets)} jobs to process.")

    if not targets.empty:
        for idx, row in targets.iterrows():
            print(f"🧐 Now attempting to analyze: {row['title']}...")
            insight = get_gemini_insight(row['snippet'])
            df.at[idx, 'ai_insight'] = insight
            df.to_csv(DB_FILE, index=False)
            print(f"✅ Success for {row['title']}. Sleeping 6s...")
            time.sleep(6) 
    else:
        print("Empty-handed! Either no scores are high enough, or they all have insights already.")

if __name__ == "__main__":
    run_analysis()
