"""Shared RSS helper for Fed banks whose papers are on fedinprint.org."""
import re
import requests
import feedparser
from datetime import datetime
from bs4 import BeautifulSoup

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.6261.112 Safari/537.36"
    ),
}


def _number_from_url(url: str) -> str:
    slug = url.rstrip("/").split("/")[-1]
    slug = re.sub(r"\.(aspx|html|pdf|htm)$", "", slug, flags=re.I)
    return slug if slug else url[-30:]


def scrape_fedinprint(source: str, feed_url: str) -> list:
    try:
        r = requests.get(feed_url, headers=_HEADERS, timeout=30)
        r.raise_for_status()
        feed = feedparser.parse(r.content)
    except Exception:
        feed = feedparser.parse(feed_url)

    if not feed.entries:
        raise Exception(f"{source}: feed returned 0 entries")

    data = []
    for entry in feed.entries:
        try:
            series = getattr(entry, "bibo_series", "") or ""
            if "Working Paper" not in series:
                continue

            title = entry.title
            link = entry.link

            author = (
                getattr(entry, "dc_creator", "")
                or getattr(entry, "author", "")
                or ""
            )

            abstract = BeautifulSoup(
                getattr(entry, "summary", ""), "html.parser"
            ).get_text().strip()

            date = ""
            if getattr(entry, "published_parsed", None):
                date = datetime(*entry.published_parsed[:6]).strftime("%Y-%m-%d")
            elif hasattr(entry, "dc_date"):
                date = entry.dc_date

            number = _number_from_url(link)

            data.append({
                "Title": title,
                "Author": author,
                "Link": link,
                "Abstract": abstract,
                "Number": number,
                "Date": date,
            })
        except Exception as e:
            print(f"[{source}] entry error: {e}")

    return data
