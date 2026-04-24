from ..generic_scraper import GenericScraper
from src.scraper.sites._fedinprint import scrape_fedinprint


class FedKansasCityScraper(GenericScraper):
    def __init__(self):
        super().__init__(source="FED-KANSASCITY")

    def fetch_data(self):
        return scrape_fedinprint(
            source="FED-KANSASCITY",
            feed_url="https://www.fedinprint.org/rss/kansascity.rss",
        )
