import time

class TabConfig:
    def __init__(self):
        self.dictionary = [
            {
            "domain": "news.yahoo.com",
            "persist": True,
            "profile": None,
            "idle_timeout": 60,
            "last_active": time.time(),
            "active": False,
            "page": None,
            },
            {
            "domain": "news.google.com",
            "persist": True,
            "profile": None,
            "idle_timeout": 60,
            "last_active": time.time(),
            "active": False,
            "page": None,
            },
            {
            "domain": "youtube.com",
            "persist": True,
            "profile": None,
            "idle_timeout": 60,
            "last_active": time.time(),
            "active": False,
            "page": None,
            },
            {
            "domain": "mail.google.com",
            "persist": True,
            "profile": None,
            "idle_timeout": 60,
            "last_active": time.time(),
            "active": False,
            "page": None,
            },
            {
            "domain": "*",
            "persist": False,
            "profile": None,
            "idle_timeout": 0,
            "last_active": time.time(),
            "active": False,
            "page": None,
            },
        ]
    def get_config_by_domain(self, domain):
        for config in self.dictionary:
            if config["domain"] == domain:
                return config
        return None

    def set_config(self, domain, key, value):
        config = self.get_config_by_domain(domain)
        if config:
            config[key] = value

    def get_all_configs(self):
        return self.dictionary

    def add_config(self, config):
        self.dictionary.append(config)

    def remove_config(self, domain):
        self.dictionary = [c for c in self.dictionary if c["domain"] != domain]

    def update_last_active(self, domain):
        config = self.get_config_by_domain(domain)
        if config:
            config["last_active"] = time.time()

    def set_active(self, domain, active=True):
        config = self.get_config_by_domain(domain)
        if config:
            config["active"] = active

    def get_active_domains(self):
        return [c["domain"] for c in self.dictionary if c["active"]]

    def set_profile(self, domain, profile):
        config = self.get_config_by_domain(domain)
        if config:
            config["profile"] = profile

    def get_profile(self, domain):
        config = self.get_config_by_domain(domain)
        if config:
            return config["profile"]
        return None
