# Provides data extraction utilities.
# - Extracts structured data (e.g., news articles) from HTML using BeautifulSoup.
# - Returns results as a pandas DataFrame.
import time
import pandas as pd
from bs4 import BeautifulSoup
from .config import Config

class Extractor:
    @staticmethod
    def extract_data_from_html(html):
        soup = BeautifulSoup(html, 'html.parser')
        articles = soup.find_all('li', class_='js-stream-content')
        data = []
        for article in articles[:Config.MAX_ITEMS]:
            title_tag = article.find('h3')
            if title_tag:
                title = title_tag.get_text(strip=True)
                data.append({
                    'title': title,
                    'timestamp': time.strftime('%Y-%m-%d')
                })
        return pd.DataFrame(data)
