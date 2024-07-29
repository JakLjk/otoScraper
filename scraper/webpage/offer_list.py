from abc import ABC, classmethod

class offerList(ABC):
    def __init__(self) -> None:
        pass

    @classmethod
    def links_to_scrape(self) -> dict:
        """should return a dict containing all urls that are to be scraped"""
        pass