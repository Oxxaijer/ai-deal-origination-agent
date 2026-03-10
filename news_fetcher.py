import os
import requests
from dotenv import load_dotenv

load_dotenv()

NEWS_API_KEY = os.getenv("NEWS_API_KEY")


def fetch_company_news(query: str, page_size: int = 5):
    """
    Fetch company/business news from NewsAPI.
    """
    if not NEWS_API_KEY:
        raise ValueError("Missing NEWS_API_KEY in .env file")

    url = "https://newsapi.org/v2/everything"

    params = {
        "q": query,
        "language": "en",
        "sortBy": "publishedAt",
        "pageSize": page_size,
        "apiKey": NEWS_API_KEY,
    }

    response = requests.get(url, params=params, timeout=20)
    response.raise_for_status()

    data = response.json()
    return data.get("articles", [])