import requests
import json

from definitions import ScrapingStatus
from driver import initialise_selenium
from otomoto.scripts import get_all_offer_links_from_scrollpage, get_offer_details
from config import WEBDRIVERCONFIG
from otomoto.objects import offerStatus, OFFER


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

def scrape_offers(links:list):
    print("Starting offer scraping job")
    try:
        wd = initialise_selenium(
            browser_type="firefox",
            headless=WEBDRIVERCONFIG.headless)
        offers = {}
        for link_id, link in links.items():
            print(f"Scraping ID:{link_id} LINK: {link}")
            try: 
                offer_details = get_offer_details(wd, link)
                offers[link_id] = offer_details.offer_info_dict()
            except Exception as e:
                print(f"Error ocurred while scraping link {link_id} | {link}")
                print(e)
                offer = OFFER(link)
                offer.id = link_id
                offer.offer_status = offerStatus.scrapingError
                offer.offer_scraping_error = e
                offers[link_id] = offer.offer_info_dict()
        response = requests.post(
        "http://127.0.0.1:5000//pass-offers-to-db",
        json={"status":ScrapingStatus.status_ok,
                "error_message": "",
                "all_offers":offers})
        print("Scraping job completed")
    except Exception as e:
            response = requests.post(
                "http://127.0.0.1:5000/pass-offers-to-db",
                json={"status":ScrapingStatus.status_failed,
                      "error_message": str(e),
                      "scraping_failed_for_links":links}
            )
            raise e
    finally:
        wd.close()
        

