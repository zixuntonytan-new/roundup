from ..generic_scraper import GenericScraper
from src.scraper.sites._fedinprint import scrape_fedinprint


class FedMinneapolisScraper(GenericScraper):
    def __init__(self):
        super().__init__(source="FED-MINNEAPOLIS")

    def fetch_data(self):
        return scrape_fedinprint(
            source="FED-MINNEAPOLIS",
            feed_url="https://www.fedinprint.org/rss/minneapolis.rss",
        )
