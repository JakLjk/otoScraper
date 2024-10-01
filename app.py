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
from config import APPCONFIG, WEBDRIVERCONFIG, WORKERCONFIG
from definitions import ScrapingStatus, WorkerExceptions

from otomoto import scripts, objects
from driver import initialise_selenium
from tasks import scrape_links, scrape_scrollpage_links
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

QUEUE_MAP = {
    "link_scraping_queue": link_scraping_queue,
    "offer_scraping_queue": offer_scraping_queue,
}

@app.route('/queue-length/<queue_name>', methods=['GET'])
def check_how_many_offer_scrollpage_links_in_queue(queue_name):
    if queue_name in QUEUE_MAP:
        queue = QUEUE_MAP[queue_name]
        queue_length = len(queue)
        return jsonify({"queue_name": queue_name, "queue_length": queue_length}), 200
    else:
        return jsonify({"error": "Queue not found."}), 404
    
@app.route('/empty-queue/<queue_name>', methods=['GET'])
def clean_queue(queue_name):
    main_log.info(f"Emptying queue {queue_name}")
    if queue_name in QUEUE_MAP:
        queue = QUEUE_MAP[queue_name]
        queue.empty()
        main_log.info(f"Queue {queue_name} was emptied")
        return f"Queue {queue_name} was emptied", 200
    else:
        return f"Queue {queue_name} not found", 404


@app.route('/get-count-links-in-db', methods=['GET'])
def links_in_db_info():
    try:
        main_log.info("Fetching count of links from DB")
        unscraped_count = LINKS.query.filter_by(was_scraped=False).count()
        being_scraped_count = LINKS.query.filter_by(is_being_scraped=True).count()
        scraped_count = LINKS.query.filter_by(was_scraped=True).count()
        total_count = LINKS.query.count()
        
        main_log.info("Returning information about count of links in DB")
        return jsonify({"scraped_links_count":scraped_count,
                        "unscraped_links_count":unscraped_count,
                        "currently_scraped_links_count":being_scraped_count,
                        "total_links_count":total_count}), 200
    except Exception as e:
        message = (f"Error has ocurred while fetching count of links from DB\n",
                    f"Error message: {e}")
        main_log.error(message)
        return message, 500

@app.route('/add-link-scraping-task', methods=['GET'])
def add_link_pages_scraping_task():
    main_log.info("Request - scraping offer scrollpages")
    links_to_scrape = []
    wd = initialise_selenium(
        browser_type="firefox",
        headless=WEBDRIVERCONFIG.headless)
    try:
        main_log.info("Getting car brands")
        car_brands = scripts.get_all_car_brands(wd)
        num_of_car_brands = len(car_brands)
        main_log.info("Scraping number of scrollpages for each car brand")
        for i, car_brand in enumerate(car_brands):
            main_log.info(f"Generating scrollpage links for brand {car_brand}. <{i+1} / {num_of_car_brands}>")
            num_pages = scripts.get_number_of_pages(wd, f"https://www.otomoto.pl/osobowe/{car_brand}")
            links_to_scrape.extend(scripts.generate_list_of_links_to_scrape(car_brand, num_pages))

        main_log.info("passing links to queue")
        chunk_size = WORKERCONFIG.size_of_scraping_worker_batch
        for i in range(0, len(links_to_scrape), chunk_size):
            link_scraping_queue.enqueue(scrape_scrollpage_links, links_to_scrape[i:i + chunk_size])
        message = f"Added {len(links_to_scrape)} scroll page links in {int(len(links_to_scrape)/chunk_size)} batches to scrape" 
        main_log.info(f"Added {len(links_to_scrape)} offer scrollpage links to scrape queue")
        return message, 200

    except Exception as e:
        main_log.error(f"Failed to add offer scrollpage links to scraping queue \n {e}")
        return f"Failed to add offer scrollpage links to scraping queue \n {e}" , 500
    finally:
        wd.close()


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
        raise WorkerExceptions.ScrapingFailed
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


@app.route('/links-in-scraping-queue', methods=['POST'])
def num_of_links_in_scraping_queue():
    pass


@app.route('/add-links-to-scraping-queue', methods=['GET'])
def add_links_to_scraping_queue():
    main_log.info(f"Adding links to scraping queue.")
    num_of_chunks_to_fetch = WORKERCONFIG.number_of_link_batches_to_fetch
    chunk_size = WORKERCONFIG.size_of_scraping_worker_batch
    num_of_links_to_fetch = num_of_chunks_to_fetch * chunk_size
    try:
        main_log.info(f"Fetching {chunk_size} links from database to scrape.")
        links_to_scrape = LINKS.query.filter_by(is_being_scraped=False,
                                                 was_scraped=False).limit(num_of_links_to_fetch).all()
        
        if not links_to_scrape:
            message = "No links available for scraping."
            main_log.info(message)
            return message , 200

        for link in links_to_scrape:
            link.being_scraped = True
        main_log.info(f"Marking {len(links_to_scrape)} as being scraped")
        db.session.commit()

        main_log.info(f"Creating batches containing several links")
        fragmented_lists = [links_to_scrape[i:i + chunk_size] for i in range(0, len(links_to_scrape), chunk_size)]
        main_log.info(f"Generated {len(fragmented_lists)} batches.")
        for link_batch in fragmented_lists:
            offer_scraping_queue.enqueue(scrape_links, link_batch) 

        message = f"{len(links_to_scrape)} in {len(fragmented_lists)} batches have been added to scraping queue"
        main_log.info(message)
        return message, 200

    except Exception as e:
        message = f"An error has ocurred while fetching links to be scraped.\n{e}"
        main_log.error(message)
        main_log.info("Rolling back...")
        db.session.rollback()
        return message, 500


if __name__ == "__main__":
    app.run(debug=True)