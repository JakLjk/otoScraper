from scraper.webpage import Webpage

import time



def get_all_car_brands():
    link = "https://www.otomoto.pl/"
    print("x")
    wp = Webpage(headless=False)
    wp.load_page(link)
    onetrust_button = wp.get_element("onetrust-accept-btn-handler", "id",3)
    onetrust_button.click_element()
    time.sleep(0.5)
    car_type_list = wp.get_element('[aria-label="Marka pojazdu"]', "css-selector")
    car_type_list.click_element()
    wp.close_webpage()