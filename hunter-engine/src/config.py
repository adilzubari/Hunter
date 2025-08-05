# Central configuration for the scraping engine.
# - Defines the global queue of requests/tasks.
# - Sets output file, scraping limits, headless mode, user agents, and viewports.
class Config:
    # GLOBAL_QUEUE: List of tasks to process. Each task can have:
    #   url: str (required)
    #   search_query: str (optional, for search engines)
    #   num_pages: int (optional, for paginated results)
    #   ...add more fields as needed per domain
    GLOBAL_QUEUE = [
        {
            "url": "https://www.google.com",
            "search_query": "Indian news",
            "num_pages": 1
        },
        # Add more task objects as needed
    ]
    OUTPUT_FILE = "daily_aapl_news.csv"
    MAX_ITEMS = 20
    HEADLESS = False
    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/114.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 Version/16.1 Safari/605.1.15",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/115.0.0.0 Safari/537.36"
    ]
    VIEWPORTS = [
        {"width": 1920, "height": 1080},
        {"width": 1366, "height": 768},
        {"width": 1440, "height": 900}
    ]
    LOCALES = ["en-US", "en-GB"]
    TIMEZONES = ["America/New_York", "Europe/London"]
    SESSION_FILE = "auth.json"
