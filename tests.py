from tasks import scrape_links


links = ["https://www.otomoto.pl/osobowe/oferta/bmw-seria-1-bmw-serii-1-ID6GHWKK.html",
         "https://www.otomoto.pl/osobowe/oferta/bmw-seria-4-bmw-4er-reihe-g26-gran-coup-m440i-ID6GLvK9.html",
         "https://www.otomoto.pl/osobowe/oferta/bmw-seria-5-bmw-530d-mozliwa-zamiana-ID6GLvBu.html"]

offers= scrape_links(links)
for offer in offers:
    print('XXXXX')
    print(offer)