import time
import random
import pandas as pd
from bs4 import BeautifulSoup
from src.core.storage.smanager import SManager

def extract_data_from_html(html):
    soup = BeautifulSoup(html, 'html.parser')
    articles = soup.find_all('li', class_='js-stream-content')
    data = []

    for article in articles[:MAX_ITEMS]:
        title_tag = article.find('h3')
        if title_tag:
            link_tag = title_tag.find('a')
            title = title_tag.get_text(strip=True)
            # url = TARGET_URL if link_tag else ''
            data.append({
                'title': title,
                # 'url': url,
                'timestamp': time.strftime('%Y-%m-%d')
            })

    return pd.DataFrame(data)