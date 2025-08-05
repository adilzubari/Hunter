# Entry point for running the scraper as a script.
# - Instantiates and runs the Scraper.
# - Handles graceful shutdown on keyboard interrupt.
import sys
from .scraper import Scraper

if __name__ == "__main__":
    try:
        print("Starting execution...", file=sys.stdout, flush=True)
        scraper = Scraper()
        scraper.run_scraper()
    except KeyboardInterrupt:
        print("Exiting script.", file=sys.stdout, flush=True)
