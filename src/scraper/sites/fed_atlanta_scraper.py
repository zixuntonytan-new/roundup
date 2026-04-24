import feedparser
from datetime import datetime
from ..generic_scraper import GenericScraper


class FedAtlantaScraper(GenericScraper):
    def __init__(self):
        super().__init__(source="FED-ATLANTA")

    def fetch_data(self):
        f = feedparser.parse("https://www.atlantafed.org/rss/wps")

        data = []
        for entry in f.entries:
            try:
                if not getattr(entry, "published_parsed", None):
                    continue

                dt = datetime(*entry.published_parsed[:6])
                date_str = dt.strftime("%Y-%m-%d")
                month_year = dt.strftime("%B %Y")

                abstract = (
                    entry.description.split(month_year)[1].strip()
                    if month_year in entry.description
                    else ""
                )
                author = entry.description.split("Working Paper")[0].strip()

                try:
                    number = (
                        entry.description
                        .split("Working Paper ")[1]
                        .split(month_year)[0]
                        .strip()
                    )
                except (IndexError, ValueError):
                    number = entry.link.rstrip("/").split("/")[-1]

                data.append({
                    "Title": entry.title,
                    "Link": entry.link,
                    "Date": date_str,
                    "Abstract": abstract,
                    "Author": author,
                    "Number": number,
                })
            except Exception as e:
                print(f"[FED-ATLANTA] entry error: {e}")

        return data
