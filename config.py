import os

class URL:
    otomoto_main_webpage = "https://www.otomoto.pl/"

class TIMERS:
    standard_load_element_wait = 3


class APPCONFIG:
    SQLALCHEMY_DATABASE_URI = ""
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")