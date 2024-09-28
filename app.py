from flask import Flask, jsonify
from redis import Redis
from rq import Queue
from db_schema import db, links_table
from config import APPCONFIG
from rq_scheduler import Scheduler

from driver import initialise_selenium
from otomoto import scripts, objects

app = Flask(__name__)
app.config.from_object(APPCONFIG)

db.init_app(app)

redis_conn = Redis.from_url(app.config['REDIS_URL'])
link_scraping_queue = Queue(connection=redis_conn)
offer_scraping_queue= Queue(connection=redis_conn)
# scheduler = Scheduler(queue=queue, connection=redis_conn)

currently_scraping = set()



def scrape_links(links_scrollpage:str):
    pass

@app.route('/add-link-scraping-task', methods=['GET'])
def add_link_pages_scraping_task():
    links_to_scrape = []
    wd = initialise_selenium(
        browser_type="firefox",
        headless=False)
    car_brands = car_brands = scripts.get_all_car_brands(wd)
    for car_brand in card_brands:
        num_pages = scripts.get_number_of_pages(wd, f"https://www.otomoto.pl/osobowe/{car_brand}")
        links_to_scrape.extend(generate_list_of_links_to_scrape(car_brand, num_pages))
    link_scraping_queue.enqueue(scrape_links, links_to_scrape)




if __name__ == "__main__":
    app.run(debug=True)