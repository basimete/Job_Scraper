import pandas as pd
import os
import re

def create_filtered_dashboard():
    csv_file = 'jobs.csv'
    if not os.path.exists(csv_file):
        print("❌ Error: jobs.csv not found.")
        return

    # 1. Load and Filter
    df = pd.read_csv(csv_file)
    df = df[df['score'] >= 3].copy()
    df = df.sort_values(by='score', ascending=False)

    # 2. Aggressive Cleaning Function
    def final_clean(text):
        if pd.isna(text) or text == "" or text == "nan":
            return ""
        t = str(text)
        t = t.replace('\\n', ' ').replace('\n', ' ').replace('\t', ' ')
        t = re.sub(r'\s+', ' ', t)
        return t.strip()

    # 3. Apply cleaning to data
    for col in ['title', 'company', 'snippet', 'date', 'ai_insight']:
        if col in df.columns:
            df[col] = df[col].apply(final_clean)

    # 4. Transform Columns into HTML
    def make_link(row):
        name = row.get('company', 'Link')
        url = row.get('link', '#')
        return f'<a href="{url}" target="_blank" class="source-link">{name}</a>'
    df['Source'] = df.apply(make_link, axis=1)

    # AI Insights formatting (Removing blue color)
    df['ai_insight'] = df['ai_insight'].str.replace('•', '<br>•')
    df['ai_insight'] = '<div class="insight-text">' + df['ai_insight'] + '</div>'

    # Accordion Snippets
    def make_accordion(text):
        if not text: return "No data"
        preview = text[:50] + "..." if len(text) > 50 else text
        return f'<details><summary>{preview}</summary><div class="full-text">{text}</div></details>'
    df['snippet'] = df['snippet'].apply(make_accordion)

    # 5. Select and Order Columns
    cols = ['date', 'score', 'title', 'Source', 'ai_insight', 'snippet']
    df = df[[c for c in cols if c in df.columns]]

    # 6. Convert to HTML Table
    html_table = df.to_html(classes='job-table', index=False, escape=False, border=0)

    # 7. The Full HTML Wrapper
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{ font-family: -apple-system, system-ui, sans-serif; margin: 20px; background: #fafafa; }}
            .container {{ max-width: 98%; margin: auto; }}
            h1 {{ color: #202124; font-size: 24px; padding-left: 10px; }}

            .job-table {{ 
                border-collapse: collapse; 
                width: 100%; 
                background: white; 
                table-layout: fixed; 
                box-shadow: 0 1px 3px rgba(0,0,0,0.1); 
            }}
            
            .job-table th {{ background: #f8f9fa; color: #5f6368; padding: 12px; text-align: left; font-size: 11px; text-transform: uppercase; border-bottom: 2px solid #eee; }}
            .job-table td {{ padding: 12px; border-bottom: 1px solid #f1f3f4; vertical-align: top; font-size: 13px; overflow: hidden; }}

            /* --- FIXED COLUMN WIDTHS --- */
            th:nth-child(1) {{ width: 90px; }}   /* Date */
            th:nth-child(2) {{ width: 50px; text-align: center; }}  /* Score */
            th:nth-child(3) {{ width: 180px; }}  /* Title */
            th:nth-child(4) {{ width: 130px; }}  /* Source */
            th:nth-child(5) {{ width: 400px; }}  /* AI Insight */
            th:nth-child(6) {{ width: 600px; }}  /* Snippet - WIDEST */

            /* AI Insight Text (Now Dark Grey, Not Blue) */
            .insight-text {{ line-height: 1.6; color: #3c4043; font-weight: 500; }}

            /* Source Link Styling */
            .source-link {{ color: #1a73e8; text-decoration: none; font-weight: bold; border-bottom: 1px solid transparent; }}
            .source-link:hover {{ border-bottom: 1px solid #1a73e8; }}

            /* Snippet/Accordion Styling */
            details {{ cursor: pointer; background: #f1f3f4; padding: 10px; border-radius: 4px; width: 95%; }}
            summary {{ font-size: 11px; color: #5f6368; outline: none; font-weight: bold; }}
            .full-text {{ 
                margin-top: 10px; 
                font-size: 13px; 
                color: #3c4043; 
                line-height: 1.6; 
                background: white; 
                padding: 15px; 
                border: 1px solid #eee; 
                white-space: pre-wrap; 
                width: 95%;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚀 Job Search Dashboard</h1>
            {html_table}
        </div>
    </body>
    </html>
    """

    with open('dashboard.html', 'w') as f:
        f.write(html_content)
    
    print("✨ Dashboard Ready! Widths balanced and AI text color fixed.")

if __name__ == "__main__":
    create_filtered_dashboard()