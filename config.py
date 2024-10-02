import os

class URL:
    otomoto_main_webpage = "https://www.otomoto.pl/"

class TIMERS:
    standard_load_element_wait = 3

class APPCONFIG:
    SQLALCHEMY_DATABASE_URI = 'mysql://root:casaos@192.168.0.226:3306/OTOMOTO'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")


class LOGGERCONFIG:
    pass

class WEBDRIVERCONFIG:
    browser="firefox",
    headless=False

class WORKERCONFIG:
    number_of_link_batches_to_fetch = 5
    size_of_scraping_worker_batch = 10