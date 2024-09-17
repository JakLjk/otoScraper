from flask import Flask, jsonify
from redis import Redis
from rq import Queue
from db_schema import db, links_table
from config import APPCONFIG


app = Flask(__name__)
app.config.from_object(APPCONFIG)

db.init_app(app)

redis_conn = Redis.from_url(app.config['REDIS_URL'])
queue = Queue(connection=redis_conn)

currently_scraping = ()


def scrape_links():
    pass
