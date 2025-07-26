import json
from pathlib import Path

class SManager:
    def __init__(self, base_path="storage"):
        self._base_path = Path(base_path)
        self._base_path.mkdir(exist_ok=True)
        self._config_file = self._base_path / "storage.json"

        # Defaults
        self.OUTPUT_FILE = "daily_aapl_news.csv"
        self.MAX_ITEMS = 1000
        self.HEADLESS = False
        self.USER_AGENTS = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/114.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 Version/16.1 Safari/605.1.15",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/115.0.0.0 Safari/537.36"
        ]
        self.VIEWPORTS = [
            {"width": 1920, "height": 1080},
            {"width": 1366, "height": 768},
            {"width": 1440, "height": 900}
        ]
        self.LOCALES = ["en-US"]
        self.TIMEZONES = ["America/New_York", "Europe/London"]
        self.SESSION_FILE = "auth.json"

    def save(self):
        data = {
            k: v for k, v in self.__dict__.items()
            if not k.startswith("_")
        }
        with open(self._config_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def load(self):
        if self._config_file.exists():
            with open(self._config_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                for k, v in data.items():
                    setattr(self, k, v)

    def set(self, key, value):
        setattr(self, key, value)
        self.save()

    async def save_clean_storage_state(self, context, path="auth.json"):
            """Save only cookies and localStorage to a JSON file, stripping tabs/session data."""
            state = await context.storage_state()
            clean_state = {
                "cookies": state.get("cookies", []),
                "origins": [
                    {
                        "origin": o["origin"],
                        "localStorage": o.get("localStorage", [])
                    }
                    for o in state.get("origins", [])
                ]
            }
            with open(path, "w") as f:
                json.dump(clean_state, f)
