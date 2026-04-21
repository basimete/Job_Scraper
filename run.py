from scrape import run_scraper
from analyse import run_ai_analysis
from makedashboard import create_filtered_dashboard

def main():
    # Step 1: Get the data
    run_scraper()
    
    # Step 2: Get the AI insights
    run_ai_analysis()
    
    # Step 3: ONLY NOW build the dashboards
    print("\n--- Building Final Dashboards ---")
    cities = [
        ("london_jobs.csv", "london_dashboard.html"),
        ("wellington_jobs.csv", "wellington_dashboard.html"),
        ("xchurch_jobs.csv", "xchurch_dashboard.html")
    ]
    for csv, html in cities:
        create_filtered_dashboard(csv, html)
    
    print("🚀 Pipeline complete. All 3 dashboards updated!")

if __name__ == "__main__":
    main()