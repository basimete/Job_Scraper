import pandas as pd
import os
import re

# Add 'csv_file' and 'output_html' as parameters
def create_filtered_dashboard(csv_file='jobs.csv', output_html='dashboard.html'):
    if not os.path.exists(csv_file):
        print(f"❌ Error: {csv_file} not found.")
        return

    # 1. Load and Filter
    df = pd.read_csv(csv_file)
    # Ensure there is data to process
    if df.empty:
        print(f"⚠️ {csv_file} is empty. Skipping.")
        return

    df['score'] = pd.to_numeric(df['score'], errors='coerce').fillna(0).astype(int)
    df = df[df['score'] >= 3].copy()

    # ... [Keep all your cleaning and formatting functions exactly the same] ...
    def final_clean(text, is_ai_task=False):
        if pd.isna(text) or text == "" or text == "nan": return ""
        t = str(text)
        if is_ai_task: t = t.replace('\\n', '\n')
        else:
            t = t.replace('\\n', ' ').replace('\n', ' ').replace('\t', ' ')
            t = re.sub(r'\s+', ' ', t)
        return t.strip()

    display_df = df.copy()
    meta_cols = ['title', 'company', 'snippet', 'date']
    for col in meta_cols:
        if col in display_df.columns:
            display_df[col] = display_df[col].apply(lambda x: final_clean(x, is_ai_task=False))

    def make_link(row):
        name = row.get('company', 'Link')
        url = row.get('link', '#')
        return f'<a href="{url}" target="_blank" class="source-link">{name}</a>'
    
    display_df['Source'] = display_df.apply(make_link, axis=1)

    def score_badge(s):
        color = "#188038" if s >= 5 else "#e37400" if s >= 4 else "#5f6368"
        return f'<span class="score-badge" style="background: {color}">{s}</span>'
    
    display_df['score'] = display_df['score'].apply(score_badge)

    def format_ai_text(text):
        if not text or str(text).lower() == "nan" or str(text).strip() == "": 
            return '<span class="muted">Pending AI Analysis...</span>'
        clean_text = final_clean(text, is_ai_task=True)
        clean_text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', clean_text)
        clean_text = re.sub(r'\n\s*\n+', '\n', clean_text)
        clean_text = clean_text.replace('\n', '<br>')
        clean_text = clean_text.replace('•', '<br>•').replace('- ', '<br>• ')
        if clean_text.startswith('<br>'): clean_text = clean_text[4:]
        return f'<div class="insight-text">{clean_text}</div>'

    if 'daily_tasks' in display_df.columns:
        display_df['daily_tasks'] = display_df['daily_tasks'].apply(format_ai_text)

    def make_accordion(text):
        if not text or text == "No data": return '<span class="muted">No snippet</span>'
        preview = text[:60] + "..." if len(text) > 60 else text
        return f'<details><summary>{preview}</summary><div class="full-text">{text}</div></details>'
    
    display_df['snippet'] = display_df['snippet'].apply(make_accordion)

    # 5. Select and Order Columns
    cols = ['date', 'score', 'title', 'Source', 'daily_tasks', 'snippet']
    display_df = display_df[[c for c in cols if c in display_df.columns]]

    # 6. Convert to HTML Table
    html_table = display_df.to_html(classes='job-table', index=False, escape=False, border=0)

    # 7. The Full HTML Wrapper (Updated Title to reflect location)
    location_name = csv_file.replace('_jobs.csv', '').title()
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <style>
            /* ... [Keep your CSS exactly the same] ... */
            :root {{ --bg: #f4f7f9; --text: #2c3e50; --border: #dcdfe6; }}
            body {{ font-family: 'Inter', -apple-system, sans-serif; margin: 20px; background: var(--bg); color: var(--text); }}
            .container {{ max-width: 100%; margin: auto; }}
            h1 {{ font-size: 22px; margin-bottom: 20px; padding-left: 5px; }}
            .job-table {{ border-collapse: separate; border-spacing: 0; width: 100%; background: white; table-layout: auto; box-shadow: 0 4px 12px rgba(0,0,0,0.05); border-radius: 8px; overflow: hidden; }}
            .job-table th {{ background: #ffffff; color: #909399; padding: 12px; text-align: left; font-size: 10px; text-transform: uppercase; letter-spacing: 0.5px; border-bottom: 1px solid var(--border); }}
            .job-table td {{ padding: 12px; border-bottom: 1px solid #f0f2f5; vertical-align: top; font-size: 13px; word-wrap: break-word; }}
            .score-badge {{ color: white; padding: 3px 8px; border-radius: 12px; font-size: 11px; font-weight: bold; display: inline-block; }}
            .source-link {{ color: #409eff; text-decoration: none; font-weight: 600; font-size: 13px; }}
            .insight-text {{ line-height: 1.5; color: #333; font-size: 12.5px; }}
            details {{ cursor: pointer; background: #f8f9fa; padding: 6px 10px; border-radius: 4px; border: 1px solid #ebeef5; }}
            .full-text {{ margin-top: 10px; font-size: 12px; background: white; padding: 10px; border: 1px solid #eee; white-space: pre-wrap; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚀 Job Search Dashboard: {location_name}</h1>
            {html_table}
        </div>
    </body>
    </html>
    """

    with open(output_html, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✨ Dashboard Ready: {output_html}")

# This part runs when you execute the script directly
if __name__ == "__main__":
    # Define your mappings
    jobs_to_dashboards = [
        ("london_jobs.csv", "london_dashboard.html"),
        ("wellington_jobs.csv", "wellington_dashboard.html"),
        ("xchurch_jobs.csv", "xchurch_dashboard.html")
    ]
    
    for csv, html in jobs_to_dashboards:
        create_filtered_dashboard(csv, html)