from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func

db = SQLAlchemy(session_options={"autoflush": False})

class LINKS(db.Model):
    __tablename__ = 'offerLinks'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    offer_id = db.Column(db.String)
    date_added = db.Column(db.TIMESTAMP, nullable=False, default=func.now())
    date_modified = db.Column(db.TIMESTAMP, nullable=False, onupdate=db.func.current_timestamp())
    link = db.Column(db.Text)
    is_being_scraped = db.Column(db.SmallInteger)
    was_scraped = db.Column(db.SmallInteger)


    def __repr__(self):
        return f"<link: {self.url}"

