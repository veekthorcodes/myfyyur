from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()


class Venue(db.Model):
    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    __tablename__ = 'venue'
    id = db.Column(db.Integer, primary_key=True, unique=True)
    name = db.Column(db.String, nullable=False, unique=True)
    genres = db.Column(db.ARRAY(db.String))
    address = db.Column(db.String(120))
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    website_link = db.Column(db.String(120))
    facebook_link = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    seeking_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(120))
    shows = db.relationship('Show', backref='venues', lazy=True)

    def __repr__(self):
        return f'<Venue {self.id} {self.name}>'


class Artist(db.Model):
    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    __tablename__ = 'artist'
    id = db.Column(db.Integer, primary_key=True, unique=True)
    name = db.Column(db.String(120), nullable=False, unique=True)
    genres = db.Column(db.String(120))
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    website = db.Column(db.String(120))
    image_link = db.Column(db.String(500), unique=True)
    facebook_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    shows = db.relationship('Show', backref='artists', lazy=True)

    def __repr__(self):
        return f"<Artist {self.id} {self.name}>"


# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

class Show(db.Model):
    __tablename__ = 'show'
    id = db.Column(db.Integer, primary_key=True, unique=True)
    venue_id = db.Column(db.Integer, db.ForeignKey('venue.id'), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey(
        'artist.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)

    def past_shows(self):
        return Show.query.filter(Show.start_time < datetime.today()).all()

    def upcoming_shows(self):
        return Show.query.filter(Show.start_time > datetime.today()).all()

    def __repr__(self):
        return f"<Show {self.id} {self.venue_name} {self.artist_name} {self.start_time}>"
