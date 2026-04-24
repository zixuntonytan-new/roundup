from ..generic_scraper import GenericScraper
from src.scraper.sites._fedinprint import scrape_fedinprint


class FedBostonScraper(GenericScraper):
    def __init__(self):
        super().__init__(source="FED-BOSTON")

    def fetch_data(self):
        return scrape_fedinprint(
            source="FED-BOSTON",
            feed_url="https://www.fedinprint.org/rss/boston.rss",
        )
