# 🚀 AI Job Hunter & Dashboard

Ingests job listings from RSS feeds, scores by technical signal words, pipes top results to Claude API to extract what the role actually outputs day-to-day. Built to solve a real problem in my own job search - data analyst roles can be a huge variety of things! 

A modularized job search pipeline designed to filter out the noise and highlight high-quality technical opportunities. This system uses keyword-based scoring to rank jobs and Anthropic's Claude AI to summarize day-to-day responsibilities for top-tier matches.

## 🛠️ System Architecture

The project is split into three modules to balance automated discovery with smart API cost management:

1. **The Scraper (`scraper.py`)**: 
   - Runs every 3 hours (via Cron or background task).
   - Fetches jobs via RSS, cleans HTML, and calculates a **Match Score**.
   - Automatically triggers a dashboard refresh.

2. **AI Analyst (`ai_analysis.py`)**: 
   - Triggered **manually** to control API costs.
   - Filters for high-scoring jobs (Score 4+) that lack summaries.
   - Uses Claude 3.5 Sonnet to list 3 specific "Deliverables" for the role.
   - Refreshes the dashboard upon completion.

3. **Dashboard Generator (`makedashboard.py`)**: 
   - The shared visualization engine.
   - Converts `jobs.csv` into a clean, searchable HTML dashboard.
   - Filters view to show only high-potential jobs (Score 2+).

## ⚙️ Scoring Logic

Jobs are ranked using a net-density calculation:
`Score = (Technical Signals) - (Management/Red Flags)`

* **SIGNAL:** sql, python, etl, pipeline, dbt, automation, etc.
* **RED FLAGS:** storytelling, stakeholder, policy, senior leadership, etc.

## 📁 File Structure
- `scraper.py`: Feed ingestion and scoring.
- `ai_analysis.py`: LLM integration.
- `makedashboard.py`: UI/UX logic.
- `jobs.csv`: The local "database".

## ⏭️ Next Steps
- [ ] Add RSS feed integration for **Indeed**.
- [ ] Implement deduplication for cross-posted roles.
- [ ] Add "Applied" status tracking in the dashboard.
