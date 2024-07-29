from abc import ABC, classmethod
from datetime import datetime


from scraped_details import scrapedDetais


class webpage(ABC):
    def __init__(self, link:str) -> None:
        self.link:str = None
        self.was_scraped:bool = False
        self.scrape_date:str = None
        self.scraped_data:scrapedDetais = scrapedDetais()

    def __repr__(self) -> str:
        return super().__repr__()

    @classmethod
    def scrape_page(self) -> scrapedDetais:
        """Scrape webpage, save data in variable scraped_data and return object if needed"""
        self.was_scraped = True
        self.scrape_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return scrapedDetais

