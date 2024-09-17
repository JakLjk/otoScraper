from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()



class link_table(db.Model):
    __tablename__ = "links"

    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(500), nullable=False) 
    being_scraped = db.Column(db.Boolean, default=False)
    scraped = db.Column(db.Boolean, default=False) 

    def __repr__(self):
        return f"<link: {self.url}"

