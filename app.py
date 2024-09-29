# Libraries
from flask import Flask, jsonify, request
from redis import Redis
from rq import Queue
from rq_scheduler import Scheduler
from sqlalchemy.exc import IntegrityError
import re
import logging

# User defined objects
from db_schema import db, LINKS
from config import APPCONFIG
from definitions import ScrapingStatus

from otomoto import scripts, objects
from driver import initialise_selenium
from tasks import scrape_links
from logger import setup_logger

setup_logger("MAIN_LOG", "MAIN_LOG")
main_log = logging.getLogger("MAIN_LOG")
main_log.info("Logger initialised.")

main_log.info("Initialising Flask App")
app = Flask(__name__)
app.config.from_object(APPCONFIG)
main_log.info("Initialising Database")
db.init_app(app)

main_log.info("Initialising redis.")
redis_conn = Redis.from_url(app.config['REDIS_URL'])
main_log.info("Defining queues")
link_scraping_queue = Queue('link_scraping_queue',connection=redis_conn)
offer_scraping_queue = Queue('offer_scraping_queue', connection=redis_conn)


# scheduler = Scheduler(queue=queue, connection=redis_conn)
# currently_scraping = set()


@app.route('/add-link-scraping-task', methods=['GET'])
def add_link_pages_scraping_task():
    main_log.info("Request - scraping offer scrollpages")
    links_to_scrape = []
    wd = initialise_selenium(
        browser_type="firefox",
        headless=False)
    try:
        main_log.info("Getting car brands")
        car_brands = scripts.get_all_car_brands(wd)
        for car_brand in car_brands:
            num_pages = scripts.get_number_of_pages(wd, f"https://www.otomoto.pl/osobowe/{car_brand}")
            links_to_scrape.extend(scripts.generate_list_of_links_to_scrape(car_brand, num_pages))

        main_log.info("passing links to queue")
        for link in links_to_scrape:
            link_scraping_queue.enqueue(scrape_links, link)
        main_log.info(f"Added {len(links_to_scrape)} offer scrollpage links to scrape")
        return f"Added {len(links_to_scrape)} offer scrollpage links to scrape" , 200

    except Exception as e:
        main_log.error(f"Failed to add offer scrollpage links to scraping queue \n {e}")
        return f"Failed to add offer scrollpage links to scraping queue \n {e}" , 500
    finally:
        wd.close()


def check_how_many_offer_scrollpage_links_in_queue():
    pass

def links_in_db_info():
    pass

@app.route('/pass_links_to_db', methods=['POST'])
def pass_offer_scrollpage_links_to_db():
    main_log.info("Received message with offer links from worker.")
    data = request.json
    status = data['status']
    if status == ScrapingStatus.status_ok:
        links = data['all_links']
    else:
        error_message = data['error_message']
        main_log.error(f"Received error message from worker.\n",
                       f"Scraping status:{status}\n"
                       f"\n Error message: {error_message}")
    try:
        num_of_links = len(links)
        i = 0
        main_log.info(f"Adding {num_of_links} links to Database")
        for link in links:
            offer_id = re.search(r'ID\w+', link)
            id_part = offer_id.group()
            existing_link = LINKS.query.filter_by(offer_id=offer_id).first()

            if not existing_link:
                i += 1
                new_link = LINKS(offer_id=id_part,
                                link=link,
                                is_being_scraped=False,
                                was_scraped=False)
                db.session.add(new_link)
        main_log.info(f"Commiting {i} / {num_of_links} links to the Database.")
        db.session.commit()
        main_log.info(f"Added {i} / {num_of_links} links to the Database.")
        return "Added links to Database" , 200
    
    except IntegrityError as ie:
        main_log.error(f"Integrity Error ocurred when commiting to Database. Rolling Back \n",
                       f"Error message: {ie}")
        db.session.rollback()
        return "Integrity Error has ocurred when oassing offer to Database.\n", 500
    except Exception as e:
        main_log.error(f"Error ocurred when commiting to Database. Rolling Back \n",
                f"Error message: {e}")
        db.session.rollback()
        return f"Error has ocurred when passing offer to Database.\n {e} ",500

if __name__ == "__main__":
    # add_link_pages_scraping_task() 
    app.run(debug=True)