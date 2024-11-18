import os

class URL:
    otomoto_main_webpage = "https://www.otomoto.pl/"

class TIMERS:
    standard_load_element_wait = 3

class APPCONFIG:
    SQLALCHEMY_DATABASE_URI = 'mysql://root:casaos@192.168.0.226:3306/OTOMOTO'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    REDIS_URL = os.getenv("REDIS_URL", "redis://192.168.0.226:6379")

class LOGGERCONFIG:
    pass

class WEBDRIVERCONFIG:
    browser="firefox",
    headless=True

class SERVERCONFIG:
    ip_port = "127.0.0.1:5001"


