"""Shared helpers for all working paper scrapers."""
import requests
from datetime import datetime
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.6261.112 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
}


def _make_driver() -> webdriver.Chrome:
    opts = Options()
    opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-gpu")
    opts.add_argument(f"user-agent={HEADERS['User-Agent']}")
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=opts)


def get_soup_js(url: str, wait_css: str = None, timeout: int = 15) -> BeautifulSoup:
    """Fetch a JS-rendered page via headless Chrome and return a BeautifulSoup."""
    driver = _make_driver()
    try:
        driver.get(url)
        if wait_css:
            WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, wait_css))
            )
        return BeautifulSoup(driver.page_source, "html.parser")
    finally:
        driver.quit()


def get_soup(url: str, headers: dict = None) -> BeautifulSoup:
    r = requests.get(url, headers=headers or HEADERS, timeout=30)
    r.raise_for_status()
    return BeautifulSoup(r.content, "html.parser")


def get_json(url: str, headers: dict = None, params: dict = None) -> dict:
    r = requests.get(url, headers=headers or HEADERS, params=params, timeout=60)
    r.raise_for_status()
    return r.json()


def post_json(url: str, headers: dict, data: dict, files=None) -> dict:
    r = requests.post(url, headers=headers, data=data, files=files or [], timeout=120)
    r.raise_for_status()
    return r.json()


def pack(source: str, title: str, url: str, author: str, abstract: str, date_str: str) -> dict:
    return {
        "source": source,
        "title": title,
        "url": url,
        "summary": f"{author}\n\n{abstract}".strip(),
        "published_at": parse_date(date_str),
    }


def parse_date(s: str):
    """
    Parse a date string into a datetime.
    Returns None (not utcnow) so the DB column default (fetched_at) takes over
    when we have no specific date or only month/year precision — both cases
    where inventing a day-1 date would be misleading for the recency slider.
    """
    if not s:
        return None
    s = s.strip()
    # Strip ISO time component if present
    if "T" in s:
        s = s.split("T")[0]
    # Full date formats — day is known, use them
    for fmt in (
        "%Y-%m-%d",
        "%B %d, %Y",
        "%b %d, %Y",
        "%d %B %Y",
        "%d %b %Y",
        "%m/%d/%Y",
    ):
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            pass
    # Month/year only — return None so fetched_at is used instead of a fake day-1
    for fmt in ("%B %Y", "%b %Y", "%B, %Y"):
        try:
            datetime.strptime(s, fmt)  # validate it parses
            return None                # but don't use it
        except ValueError:
            pass
    return None
