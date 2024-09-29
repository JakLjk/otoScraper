import requests

def scrape_links(links_scrollpage_link:str):
    print("starting scraping job")
    response = requests.post(
            "http://127.0.0.1:5000/response",
            json={"response_link":links_scrollpage_link}
        )
    
    print("Response sent.")
