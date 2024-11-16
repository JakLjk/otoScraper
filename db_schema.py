from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
from sqlalchemy import UnicodeText

db = SQLAlchemy(session_options={"autoflush": False})


class SCRAPEPAGES(db.Model):
    __tablename__ = 'scrapePages'
    id = db.Column(db.Integer, primary_key = True, autoincrement=True)
    scrapepage_link = db.Column(db.String(256))
    car_brand = db.Column(db.String(80))
    # Task complete no matter what was the status of job
    scrapedTaskComplete = db.Column(db.SmallInteger)
    beingCurrentlyScraped = db.Column(db.SmallInteger)
    scraped_offers = db.Column(db.Integer)
    inserted_offers = db.Column(db.Integer)
    scraping_status = db.Column(db.String(256))

class LINKS(db.Model):
    __tablename__ = 'offerLinks'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    t_scrapepages_id = db.Column(db.Integer,
                    db.ForeignKey('scrapePages.id'),
                    primary_key=True)
    offer_id_in_link = db.Column(db.String(256))
    date_added = db.Column(db.TIMESTAMP, nullable=False, default=func.now())
    date_modified = db.Column(db.TIMESTAMP, nullable=False, onupdate=db.func.current_timestamp())
    link = db.Column(db.Text)
    is_being_scraped = db.Column(db.SmallInteger)
    was_scraped = db.Column(db.SmallInteger)
    scraping_outcome = db.Column(db.Text)
    error_message = db.Column(db.Text)


    def __repr__(self):
        return (f"\n<link: {self.link}>\n"
                f"Offer ID: {self.offer_id_in_link}\n"
                f"Being scraped: {self.is_being_scraped}\n"
                f"Was scraped: {self.was_scraped}\n")

class OFFERS(db.Model):
    __tablename__ = 'offers'
    id =  db.Column(db.Integer,
                    db.ForeignKey('offerLinks.id'),
                    primary_key=True)
    id_oferty = db.Column(db.String(256))
    id_oferty_w_linku  = db.Column(db.String(256))
    data_dodania_rekordu = db.Column(db.TIMESTAMP, nullable=False, default=func.now())
    data_modyfikacji_rekordu = db.Column(db.TIMESTAMP, nullable=False,  onupdate=db.func.current_timestamp())
    link = db.Column(db.Text)
    tytul = db.Column(db.String(256))
    data_dodania = db.Column(db.String(256))
    cena = db.Column(db.String(256))
    przebieg = db.Column(db.String(256))
    rodzaj_paliwa = db.Column(db.String(256))
    skrzynia_biegow = db.Column(db.String(256))
    pojemnosc_silnika = db.Column(db.String(256))
    moc_silnika = db.Column(db.String(256))
    opis = db.Column(db.Text)
    szczegoly = db.Column(UnicodeText(collation='utf8mb4_unicode_ci')) 
    wyposazenie =  db.Column(db.Text)
    sprzedawca_nr_tel = db.Column(db.String(256))
    sprzedawca_imie = db.Column(db.String(256))
    sprzedawca_rodzaj = db.Column(db.String(256))
    sprzedawca_data_od_kiedy_na_otomoto = db.Column(db.String(256))
    latitude = db.Column(db.Double)
    longitude = db.Column(db.Double)
    coords_exact = db.Column(db.SmallInteger)