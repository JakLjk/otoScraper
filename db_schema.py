from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
from sqlalchemy import UnicodeText

db = SQLAlchemy(session_options={"autoflush": False})

class LINKS(db.Model):
    __tablename__ = 'offerLinks'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    offer_id = db.Column(db.String)
    offer_id_in_link = db.Column(db.String)
    date_added = db.Column(db.TIMESTAMP, nullable=False, default=func.now())
    date_modified = db.Column(db.TIMESTAMP, nullable=False, onupdate=db.func.current_timestamp())
    link = db.Column(db.Text)
    is_being_scraped = db.Column(db.SmallInteger)
    was_scraped = db.Column(db.SmallInteger)
    scraping_outcome = db.Column(db.Text)
    error_message = db.Column(db.Text)


    def __repr__(self):
        return (f"\n<link: {self.link}>\n"
                f"Offer ID: {self.offer_id}\n"
                f"Being scraped: {self.is_being_scraped}\n"
                f"Was scraped: {self.was_scraped}\n")

class OFFERS(db.Model):
    __tablename__ = 'offers'
    id =  db.Column(db.Integer,
                    db.ForeignKey('offerLinks.id'),
                    primary_key=True)
    id_oferty = db.Column(db.String)
    id_oferty_w_linku  = db.Column(db.String)
    data_dodania_rekordu = db.Column(db.TIMESTAMP, nullable=False, default=func.now())
    data_modyfikacji_rekordu = db.Column(db.TIMESTAMP, nullable=False,  onupdate=db.func.current_timestamp())
    link = db.Column(db.Text)
    tytul = db.Column(db.String)
    data_dodania = db.Column(db.String)
    cena = db.Column(db.String)
    przebieg = db.Column(db.String)
    rodzaj_paliwa = db.Column(db.String)
    skrzynia_biegow = db.Column(db.String)
    pojemnosc_silnika = db.Column(db.String)
    moc_silnika = db.Column(db.String)
    opis = db.Column(db.Text)
    szczegoly = db.Column(UnicodeText(collation='utf8mb4_unicode_ci')) 
    wyposazenie =  db.Column(db.Text)
    sprzedawca_nr_tel = db.Column(db.String)
    sprzedawca_imie = db.Column(db.String)
    sprzedawca_rodzaj = db.Column(db.String)
    sprzedawca_data_od_kiedy_na_otomoto = db.Column(db.String)
    latitude = db.Column(db.Double)
    longitude = db.Column(db.Double)
    coords_exact = db.Column(db.SmallInteger)