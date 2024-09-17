from driver import initialise_selenium

from otomoto import scripts, objects



def main():
    wd = initialise_selenium(
        browser_type="firefox",
        headless=False)
    
    try:
        # car_brands = scripts.get_all_car_brands(wd)
        # num_pages = scripts.get_number_of_pages(wd, "https://www.otomoto.pl/osobowe/bmw")
        # offer_links = scripts.get_all_offer_links_from_scrollpage(wd,
        #                                                           "https://www.otomoto.pl/osobowe/bmw"
        #
        #
        offer = scripts.get_offer_details(wd, "https://www.otomoto.pl/osobowe/oferta/bmw-seria-3-kabriolet-bmw-320i-ID6GCN7n.html")
        print(offer)
    finally:
        wd.quit()
        pass

    # print(car_brands)
    # print(num_pages)

if __name__ == "__main__":
    main()


# TODO you can make a class thath will parse and store web elements in a way that will 

# be easy to input into db 