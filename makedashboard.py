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
    df['score'] = pd.to_numeric(df['score'], errors='coerce').fillna(0).astype(int)
    df = df[df['score'] >= 3].copy()

    # 2. Cleaning Function
    def final_clean(text, is_ai_task=False):
        if pd.isna(text) or text == "" or text == "nan":
            return ""
        t = str(text)
        if is_ai_task:
            t = t.replace('\\n', '\n')
        else:
            t = t.replace('\\n', ' ').replace('\n', ' ').replace('\t', ' ')
            t = re.sub(r'\s+', ' ', t)
        return t.strip()

    # 3. Apply cleaning to a temporary copy to avoid mangling HTML on re-runs
    display_df = df.copy()

    meta_cols = ['title', 'company', 'snippet', 'date']
    for col in meta_cols:
        if col in display_df.columns:
            display_df[col] = display_df[col].apply(lambda x: final_clean(x, is_ai_task=False))

    # 4. Transform Columns into HTML
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
        
        # 1. Initial clean
        clean_text = final_clean(text, is_ai_task=True)
        
        # 2. Convert Markdown **bold** to HTML <b>
        clean_text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', clean_text)
        
        # 3. CRUSH EXTRA SPACING: Replace 2 or more newlines with a single newline
        clean_text = re.sub(r'\n\s*\n+', '\n', clean_text)
        
        # 4. Convert newlines to single breaks
        clean_text = clean_text.replace('\n', '<br>')
        
        # 5. Clean up bullet points so they don't create massive gaps
        # This replaces bullets with a single break + bullet, then removes any double-breaks we just created
        clean_text = clean_text.replace('•', '<br>•').replace('- ', '<br>• ')
        clean_text = clean_text.replace('<br><br>•', '<br>•')
        
        # 6. Final trim: if the text starts with a break, remove it
        if clean_text.startswith('<br>'):
            clean_text = clean_text[4:]
            
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

    # 7. The Full HTML Wrapper
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <style>
            :root {{ --bg: #f4f7f9; --text: #2c3e50; --border: #dcdfe6; }}
            body {{ font-family: 'Inter', -apple-system, sans-serif; margin: 20px; background: var(--bg); color: var(--text); }}
            .container {{ max-width: 100%; margin: auto; }}
            h1 {{ font-size: 22px; margin-bottom: 20px; padding-left: 5px; }}
            .job-table {{ border-collapse: separate; border-spacing: 0; width: 100%; background: white; table-layout: auto; box-shadow: 0 4px 12px rgba(0,0,0,0.05); border-radius: 8px; overflow: hidden; }}
            .job-table th {{ background: #ffffff; color: #909399; padding: 12px; text-align: left; font-size: 10px; text-transform: uppercase; letter-spacing: 0.5px; border-bottom: 1px solid var(--border); }}
            .job-table td {{ padding: 12px; border-bottom: 1px solid #f0f2f5; vertical-align: top; font-size: 13px; word-wrap: break-word; }}
            th:nth-child(1) {{ width: 8%; }}
            th:nth-child(2) {{ width: 5%; text-align: center; }}
            th:nth-child(3) {{ width: 15%; font-weight: 600; }}
            th:nth-child(4) {{ width: 12%; }}
            th:nth-child(5) {{ width: 30%; }}
            th:nth-child(6) {{ width: 30%; }}
            .score-badge {{ color: white; padding: 3px 8px; border-radius: 12px; font-size: 11px; font-weight: bold; display: inline-block; }}
            .insight-text {{ line-height: 1.5; color: #333; font-size: 12.5px; }}
            .insight-text b {{ color: #000; font-weight: 700; }}
            .source-link {{ color: #409eff; text-decoration: none; font-weight: 600; font-size: 13px; }}
            details {{ cursor: pointer; background: #f8f9fa; padding: 6px 10px; border-radius: 4px; border: 1px solid #ebeef5; max-width: 100%; }}
            summary {{ font-size: 11px; color: #606266; font-weight: 500; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }}
            .full-text {{ margin-top: 10px; font-size: 12px; background: white; padding: 10px; border: 1px solid #eee; white-space: pre-wrap; word-break: break-word; }}
            .muted {{ color: #c0c4cc; font-style: italic; }}
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

    with open('dashboard.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print("✨ Dashboard Ready!")

# CRITICAL: This is what actually runs the code
if __name__ == "__main__":
    create_filtered_dashboard()