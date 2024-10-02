import requests

from definitions import ScrapingStatus
from driver import initialise_selenium
from otomoto.scripts import get_all_offer_links_from_scrollpage, get_offer_details
from config import WEBDRIVERCONFIG

def scrape_scrollpage_links(links_scrollpage:list):
    print("starting scraping job")
    try:
        wd = initialise_selenium(
            browser_type="firefox",
            headless=WEBDRIVERCONFIG.headless)
        
        all_offer_links = []
        for scrollpage_link in links_scrollpage:
            print(f"Scraping scrollpage {scrollpage_link}")
            links = get_all_offer_links_from_scrollpage(wd, scrollpage_link)
            all_offer_links.extend(links)

        response = requests.post(
                "http://127.0.0.1:5000/pass_links_to_db",
                json={"status":ScrapingStatus.status_ok,
                      "error_message": "",
                      "all_links":all_offer_links}
            )
    except Exception as e:
        response = requests.post(
                "http://127.0.0.1:5000/pass_links_to_db",
                json={"status":ScrapingStatus.status_failed,
                      "error_message": str(e)}
            )
        raise e
    finally:
        wd.close()
    print("Finishing scraping job")


def scrape_links(links:list):
    print("Starting links scraping job")
    try:
        wd = initialise_selenium(
            browser_type="firefox",
            headless=WEBDRIVERCONFIG.headless)
        offers = []
        for link in links:
            offer_details = get_offer_details(wd, link)
            offers.append(offer_details)
        return offers
        

    # except:
    #     pass
    finally:
        # wd.close()
        pass

