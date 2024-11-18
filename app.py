# Libraries
from flask import Flask, jsonify, request
from redis import Redis
from redis.exceptions import ConnectionError
from rq import Queue
from rq_scheduler import Scheduler
from sqlalchemy.exc import IntegrityError
import re
import logging
import requests
from sqlalchemy import or_, and_

# User defined objects
from db_schema import db, LINKS, OFFERS, SCRAPEPAGES
from config import APPCONFIG, WEBDRIVERCONFIG
from definitions import ScrapingStatus, WorkerExceptions, ScrapingException
from otomoto.objects import offerStatus, OFFER

from otomoto import scripts, objects
from driver import initialise_selenium
from tasks import scrape_offers, scrape_scrollpage_links
from logger import setup_logger

setup_logger("MAIN_LOG", "MAIN_LOG")
main_log = logging.getLogger("MAIN_LOG")
main_log.info("Logger initialised.")

main_log.info("Initialising Flask App")
app = Flask(__name__)
app.config.from_object(APPCONFIG)
main_log.info("Initialising Database")
db.init_app(app)
main_log.info("Creating DB tables if they dont exist yet")
with app.app_context():
    db.create_all()

main_log.info("Initialising redis.")
redis_conn = Redis.from_url(app.config['REDIS_URL'])
main_log.info("Checking connection to redis server")
try:
    redis_conn.ping()
except ConnectionError as ce:
    main_log.error("There was an error when trying to connect to Redis server")
    raise ce
main_log.info(f"Successfully pinged Redis server")
main_log.info("Defining queues")
link_scraping_queue = Queue('link_scraping_queue',connection=redis_conn)
offer_scraping_queue = Queue('offer_scraping_queue', connection=redis_conn)

QUEUE_MAP = {
    "link_scraping_queue": link_scraping_queue,
    "offer_scraping_queue": offer_scraping_queue,
}

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

@app.route('/queue-length/<queue_name>', methods=['GET'])
def check_how_many_offer_scrollpage_links_in_queue(queue_name):
    if queue_name in QUEUE_MAP:
        queue = QUEUE_MAP[queue_name]
        queue_length = len(queue)
        return jsonify({"queue_name": queue_name, "queue_num_of_batches": queue_length}), 200
    else:
        return jsonify({"error": "Queue not found."}), 404
    
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

@app.route('/scrape-scrollpage-links', methods=['GET'])
def scrape_scrollpages():
    main_log.info("Request - scrape scrollpages")
    try:
        wd = initialise_selenium(
        browser_type="firefox",
        headless=WEBDRIVERCONFIG.headless)
        
        main_log.info("Getting car brands")
        car_brands = scripts.get_all_car_brands(wd)

        # car_brands = car_brands[1:2]

        num_of_car_brands = len(car_brands)
        main_log.info("Scraping number of scrollpages for each car brand")
        for i, car_brand in enumerate(car_brands):
            main_log.info(f"Generating scrollpage links for brand {car_brand}. <{i+1}/{num_of_car_brands}>")
            main_log.info(f"Getting number of pages for {car_brand}")
            num_pages = scripts.get_number_of_pages(wd, f"https://www.otomoto.pl/osobowe/{car_brand}")
            main_log.info(f"Number of pages for {car_brand} : {num_pages}")
            main_log.info(f"Generating list of scrollpage links to scrape")
            generated_scrollpage_links_to_scrape = scripts.generate_list_of_links_to_scrape(car_brand, num_pages)
            len_generated_scrollpage_links_to_scrape = len(generated_scrollpage_links_to_scrape)
            main_log.info(f"Adding {len_generated_scrollpage_links_to_scrape} scrollpage links to <SCRAPEPAGES> DB table")
            existing_values = db.session.query(SCRAPEPAGES).filter(and_(SCRAPEPAGES.car_brand==car_brand,
                                                                            or_(SCRAPEPAGES.scrapedTaskComplete==False, 
                                                                                SCRAPEPAGES.beingCurrentlyScraped==True
                                                                                )
                                                                        )
                                                                    ).all()
            main_log.debug(f"Filtered {len(existing_values)} exisiting values for {car_brand} in db")
            existing_values = [row.scrapepage_link for row in existing_values]                               
            # existing_values = {value[0] for value in existing_values} 
            print(existing_values)
            values_to_insert = [value for value in generated_scrollpage_links_to_scrape if value not in existing_values]
            main_log.info(f"{len(values_to_insert)} out of {len_generated_scrollpage_links_to_scrape} links are eligible to be added (There are no such links with unscraped status)")
            for value in values_to_insert:
                scrapepage = SCRAPEPAGES(scrapepage_link=value,
                                         car_brand=car_brand,
                                         scrapedTaskComplete=False,
                                         beingCurrentlyScraped=False)
                db.session.add(scrapepage)
            main_log.info(f"Commiting links for {car_brand} to db")
            db.session.commit()
            main_log.info("Links commited")

    except Exception as e:
        main_log.error(f"Exception was raised when scraping scrollpage links \n{e}")
        # return f"Error occurred when processing request: {e}", 500
        raise e
    finally:
        wd.close()
        return "Task finished successfully", 200

@app.route('/add-scrollpage-links-to-queue/<num_of_links>/<batch_size>', methods=['GET'])
def add_scrollpage_links_to_scraping_queue(num_of_links,batch_size):
    main_log.info(f"Request - add scrollpage links to scraping queue")
    main_log.info(f"Fetching {num_of_links} scrollpage links.")
    num_of_links = int(num_of_links)
    batch_size = int(batch_size)
    scrollpage_links_to_scrape = SCRAPEPAGES.query.filter_by(beingCurrentlyScraped=False,
                                                            scrapedTaskComplete=False).limit(num_of_links).all()
    if not scrollpage_links_to_scrape:
        message = "No links available for scraping."
        main_log.info(message)
        return message , 200
    main_log.info(f"Marking scollpage links as being scraped")
    for link in scrollpage_links_to_scrape:
        link.beingCurrentlyScraped = True
    scrollpage_links_to_scrape = {value.id:value.scrapepage_link for value in scrollpage_links_to_scrape}
    fragmented_dicts = [
        dict(list(scrollpage_links_to_scrape.items())[i:i + batch_size]) 
        for i in range(0, len(scrollpage_links_to_scrape), batch_size)
    ]
    main_log.info(f"Passing {len(scrollpage_links_to_scrape)} links in {len(fragmented_dicts)} batches to Redis queue")
    for link_batch in fragmented_dicts:
        link_scraping_queue.enqueue(scrape_scrollpage_links, link_batch)
    main_log.info(f"Scrollpage links added to Queue - commiting changes to DB")
    db.session.commit()
    message = f"Scrollpage links successfully added to Redis Queue. Links: {len(scrollpage_links_to_scrape)} Batches: {len(fragmented_dicts)}"
    main_log.info(message)
    return message, 200

@app.route('/pass_links_to_db', methods=['POST'])
def pass_offer_scrollpage_links_to_db():
    main_log.info("Received message with offer links from worker.")
    data = request.json
    status = data['status']
    if status == ScrapingStatus.status_ok:
        scrapepage_links = data['all_links']
    else:
        error_message = data['error_message']
        main_log.error(f"Received error message from worker.\n",
                       f"Scraping status:{status}\n"
                       f"\n Error message: {error_message}")
        main_log.info("Marking scrollpage links as part of failed process")
        scrapepage_ids = scrapepage_links.keys()
        for scrapepage_id in scrapepage_ids:
            scrapepage = db.session.query(SCRAPEPAGES).filter(SCRAPEPAGES.id == scrapepage_id).one()
            scrapepage.beingCurrentlyScraped=False
            scrapepage.scrapedTaskComplete = True
            scrapepage.scraping_status = status
            db.session.commit()
            main_log.info(f"Marked {len(scrapepage_ids)} scrapepages as failed")
        raise WorkerExceptions.ScrapingFailed
    try:
        y = 0
        num_of_links = 0
        for scrapepage_id, links in scrapepage_links.items():
            main_log.debug(f"Adding {len(links)} links for scrapepage ID {scrapepage_id} to DB.")
            i = 0
            num_of_links += len(links)
            for link in links:
                offer_id_in_link = re.search(r'ID\w+', link)
                offer_id_in_link = offer_id_in_link.group()
                existing_link = LINKS.query.filter_by(offer_id_in_link=offer_id_in_link).first()
                if not existing_link:
                    i += 1
                    y += 1
                    new_link = LINKS(
                                    offer_id_in_link = offer_id_in_link,
                                    t_scrapepages_id = scrapepage_id,
                                    link=link,
                                    is_being_scraped=False,
                                    was_scraped=False)
                    db.session.add(new_link)
            scrapepage = db.session.query(SCRAPEPAGES).filter(SCRAPEPAGES.id == scrapepage_id).one()
            scrapepage.beingCurrentlyScraped=False
            scrapepage.scrapedTaskComplete = True
            scrapepage.scraped_offers = len(links)
            scrapepage.inserted_offers = i
            scrapepage.scraping_status = status
        main_log.info(f"Commiting {y} / {num_of_links} links to the Database.")
        db.session.commit()
        main_log.info(f"Added {y} / {num_of_links} links to the Database.")
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

#Offer Scraping Logic ==============================================

@app.route('/add-links-to-scraping-queue/<num_of_chunks_to_fetch>/<batch_size>', methods=['GET'])
def add_links_to_scraping_queue(num_of_chunks_to_fetch, batch_size):
    main_log.info(f"Adding links to scraping queue.")
    num_of_chunks_to_fetch = int(num_of_chunks_to_fetch)
    chunk_size = int(batch_size)
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
            link.is_being_scraped = True
        main_log.info(f"Marking {len(links_to_scrape)} as being scraped")
        db.session.commit()

        main_log.info(f"Creating batches containing several links")
        links_to_scrape = {link.id:link.link for link in links_to_scrape}

        fragmented_dicts = [
            dict(list(links_to_scrape.items())[i:i + chunk_size]) 
            for i in range(0, len(links_to_scrape), chunk_size)
        ]
        main_log.info(f"Generated {len(fragmented_dicts)} batches.")
        for link_batch in fragmented_dicts:
            offer_scraping_queue.enqueue(scrape_offers, link_batch) 

        message = (f"{len(links_to_scrape)} in {len(fragmented_dicts)} batches have been added to scraping queue\n")
        main_log.info(message)
        return message, 200

    except Exception as e:
        message = f"An error has ocurred while fetching links to be scraped.\n{e}"
        main_log.error(message)
        main_log.info("Rolling back...")
        db.session.rollback()
        return message, 500

@app.route('/pass-offers-to-db', methods=['POST'])
def pass_offers_to_db():
    main_log.info("Received message with offers from worker.")
    data = request.json
    status = data['status']
    main_log.info(f"Scraping status: {status}")
    offer_objects = []
    if status == ScrapingStatus.status_ok:
        offers = data['all_offers']
        main_log.info(f"Inserting data for {len(offers)} offers into db.")
        for id, offer in offers.items():
            # Conver offer dict to offer object
            offer = OFFER.dict_into_offer(offer)
            # Mark link as scraped in links table
            link = LINKS.query.filter_by(id = id).first()
            link.was_scraped = True
            link.is_being_scraped = False 
            link.scraping_outcome = offer.offer_status
            if offer.offer_status == offerStatus.statusScrapeSuccess:
                main_log.debug(f"Marking link as scraped\n"
                           f"{link}")
                
                main_log.debug(f"\nPassing offer to DB: \n"
                               f"{offer}")
                new_offer = OFFERS(id=int(id),
                                   link = offer.link,
                                    id_oferty = offer.id_z_oferty,
                                    id_oferty_w_linku = offer.id_oferty_w_linku,
                                    tytul = offer.tytul,
                                    data_dodania=offer.data_dodania,
                                    cena = offer.cena,
                                    przebieg = offer.przebieg,
                                    rodzaj_paliwa = offer.rodzaj_paliwa,
                                    skrzynia_biegow = offer.skrzynia_biegow,
                                    pojemnosc_silnika=offer.pojemnosc_silnika,
                                    moc_silnika = offer.moc_silnika,
                                    opis = offer.opis,
                                    szczegoly = offer.szczegoly_json,
                                    wyposazenie = offer.wyposazenie_json,
                                    sprzedawca_nr_tel = offer.sprzedawca_nr_tel,
                                    sprzedawca_imie = offer.sprzedawca_imie,
                                    sprzedawca_rodzaj = offer.sprzedawca_rodzaj,
                                    sprzedawca_data_od_kiedy_na_otomoto = offer.sprzedawca_data_od_kiedy_na_otomoto,
                                    latitude = offer.latitude,
                                    longitude = offer.longitude,
                                    coords_exact = True
                )
                db.session.add(new_offer)
                main_log.debug(f"Adding offer {id} to query to be commited into offers table")
            else:
                error_message = offer.offer_scraping_error
                link.error_message = error_message

                
        db.session.commit()
        return f"Successfully added {len(offers)} to DB", 200
    else:
        return (f"\nWorker script returned error\n"
                f"Status: {status}\n"
                f"Error message: {data['error_message']}\n"), 500

@app.route('/test', methods=['GET'])
def test():
    scrape_offers(links=["https://www.otomoto.pl/osobowe/oferta/audi-a4-audi-a4b6-avant-1-6-benzyna-lpg-2003-r-ID6GN8b4.html",
                    "https://www.otomoto.pl/osobowe/oferta/audi-a7-audi-a7-3-0-tdi-quattro-s-line-webasto-pneumatyka-matrix-acc-ID6GOVVc.html"])
    return 200

if __name__ == "__main__":
    app.run(debug=True, port=5001)