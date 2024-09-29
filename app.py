from flask import Flask, jsonify, request
from redis import Redis
from rq import Queue
import requests
from rq_scheduler import Scheduler
from sqlalchemy.exc import IntegrityError
import re

from db_schema import db, LINKS
from config import APPCONFIG
from definitions import ScrapingStatus

from driver import initialise_selenium
from otomoto import scripts, objects
from tasks import scrape_links


app = Flask(__name__)
app.config.from_object(APPCONFIG)

db.init_app(app)

redis_conn = Redis.from_url(app.config['REDIS_URL'])
link_scraping_queue = Queue('link_scraping_queue',connection=redis_conn)
offer_scraping_queue = Queue('offer_scraping_queue', connection=redis_conn)
# scheduler = Scheduler(queue=queue, connection=redis_conn)

currently_scraping = set()







@app.route('/add-link-scraping-task', methods=['GET'])
def add_link_pages_scraping_task():
    #TODO send batch of x links, that will be sent to worker, it will process x request and reutnr x resulst
    # links_to_scrape = []
    # wd = initialise_selenium(
    #     browser_type="firefox",
    #     headless=False)
    try:
    #     car_brands = scripts.get_all_car_brands(wd)
    #     for car_brand in car_brands:
    #         print(f"CAR BRAND:{car_brand}")
    #         num_pages = scripts.get_number_of_pages(wd, f"https://www.otomoto.pl/osobowe/{car_brand}")
    #         print(f"NUM PAGES ({car_brand}): {num_pages}")
    #         links_to_scrape.extend(scripts.generate_list_of_links_to_scrape(car_brand, num_pages))
    #         print(len(links_to_scrape))
        l = [['https://www.otomoto.pl/osobowe/bmw?page=1', "https://www.otomoto.pl/osobowe/bmw?page=2"], 
                 ["https://www.otomoto.pl/osobowe/bmw?page=3", "https://www.otomoto.pl/osobowe/bmw?page=4"]]
        for link in l:
            print(link)
            link_scraping_queue.enqueue(scrape_links, link)

        return "Added links to scape" , 200
    
    finally:
        # wd.close()
        pass

@app.route('/pass_links_to_db', methods=['POST'])
def received_response():
    data = request.json
    status = data['status']
    if status == ScrapingStatus.status_ok:
        links = data['all_links_len']
    try:
        for link in links:
            print("Adding link to db")
            offer_id = re.search(r'ID\w+', link)
            id_part = offer_id.group()
            print(id_part)
            existing_link = LINKS.query.filter_by(offer_id=offer_id).first()
            if not existing_link:
                new_link = LINKS(offer_id=id_part,
                                link=link,
                                is_being_scraped=False,
                                was_scraped=False)
                db.session.add(new_link)
        db.session.commit()
        print(f"Added {len(links)} links to the database.")
        return "Added links to scape" , 200
    
    except IntegrityError:
        db.session.rollback()
        print("Error: One or more links already exist in the database and were not added.")
    except Exception as e:
        db.session.rollback()
        print(f"An error occurred--: {e}")






        return jsonify({"message": "Link updated"}), 200

if __name__ == "__main__":
    # add_link_pages_scraping_task() 
    app.run(debug=True)