from ..generic_scraper import GenericScraper
from src.scraper.sites._fedinprint import scrape_fedinprint


class FedStLouisScraper(GenericScraper):
    def __init__(self):
        super().__init__(source="FED-STLOUIS")

    def fetch_data(self):
        return scrape_fedinprint(
            source="FED-STLOUIS",
            feed_url="https://www.fedinprint.org/rss/stlouis.rss",
        )
