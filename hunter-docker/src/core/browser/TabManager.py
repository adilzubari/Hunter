from urllib.parse import urlparse
from .TabConfig import TabConfig  # Assuming TabConfig is defined in the same directory

# Assuming TabConfig is defined elsewhere in your project
# If not, you need to import or define TabConfig
# from .TabConfig import TabConfig

class TabManager:
    def __init__(self):
        self.tabs = []
        self.page = None

    def get_tab_for_url(self, url):
        domain = urlparse(url).netloc
        for tab in self.tabs:
            if tab.domain in domain and tab.page is not None:
                return tab
        return None

    def register_tab(self, domain, persist=False, profile=None, idle_timeout=60):
        print(f"Registering tab for domain: {domain}")
        config = TabConfig().get_config_by_domain(domain)
        self.tabs.append(config)
        return config

    def get_or_create_tab(self, url):
        domain = urlparse(url).netloc
        tab = self.get_tab_for_url(url)
        if not tab:
            tab = self.register_tab(domain, persist=True if domain in ['youtube.com', 'mail.google.com'] else False)
        return tab

    def remove_tab(self, tab):
        if tab in self.tabs:
            self.tabs.remove(tab)
