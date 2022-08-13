#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

from flask import Flask, render_template, request, Response, flash, redirect, url_for, jsonify
from logging import Formatter, FileHandler
from flask_migrate import Migrate
from flask_moment import Moment
from datetime import datetime
from sqlalchemy import desc
from flask_wtf import Form
import dateutil.parser
from models import *
from forms import *
import logging
import babel
import json
import sys
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
# TODO: connect to a local postgresql database
db.init_app(app)
migrate = Migrate(app, db)
with app.app_context():
    db.create_all()


def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format, locale='en')


app.jinja_env.filters['datetime'] = format_datetime


def upcoming_shows(shows):
    qs = [show for show in shows if show.start_time > datetime.today()]

    upcoming_shows_list = []
    for show in qs:
        upcoming_shows_list.append({
            "artist_name": show.artists.name,
            "artist_id": show.artists.id,
            "artist_image_link": show.artists.image_link,
            "start_time": show.start_time.strftime("%m/%d/%Y, %H:%M:%S")
        })
    return upcoming_shows_list


def past_shows(shows):
    qs = [show for show in shows if show.start_time < datetime.today()]
    past_shows_list = []
    for show in qs:
        past_shows_list.append({
            "artist_name": show.artists.name,
            "artist_id": show.artists.id,
            "artist_image_link": show.artists.image_link,
            "start_time": show.start_time.strftime("%m/%d/%Y, %H:%M:%S")
        })
    return past_shows_list


#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#


@app.route('/')
def index():
    artists = Artist.query.order_by(desc(Artist.id)).all()
    venues = Venue.query.order_by(desc(Venue.id)).all()
    return render_template('pages/home.html', artists=artists, venues=venues)

#  Venues
#  ----------------------------------------------------------------


@app.route('/venues')
def venues():
    # TODO: replace with real venues data.
    #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.

    data = []
    qs = Venue.query.distinct(Venue.city, Venue.state).all()
    for query in qs:
        venue_map = {
            "city": query.city,
            "state": query.state
        }
        venue_qs = Venue.query.filter_by(
            city=query.city, state=query.state).all()
        venue_list = []
        for venue in venue_qs:
            venue_list.append({
                "id": venue.id,
                "name": venue.name,
                "num_upcoming_shows": len(list(filter(lambda x: x.start_time > datetime.now(), venue.shows)))
            })

        venue_map["venues"] = venue_list
        data.append(venue_map)

    return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
    search_term = request.form.get('search_term', '')
    qs = Venue.query.filter(
        Venue.name.ilike(f'%{search_term}%'),
        Venue.city.ilike(f'%{search_term}%'),
        Venue.state.ilike(f'%{search_term}%'),

    )
    data = []
    for venue in qs:
        upcoming_shows_list = upcoming_shows(venue.shows)
        data.append({
            "id": venue.id,
            "name": venue.name,
            "num_upcoming_shows": len(upcoming_shows_list)
        })

    response = {
        "count": qs.count(),
        "data": data
    }
    return render_template('pages/search_venues.html', results=response, search_term=search_term)


@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion

    error = False
    try:
        form = VenueForm(request.form)
        record = Venue(
            name=form.name.data,
            genres=form.genres.data,
            address=form.address.data,
            city=form.city.data,
            state=form.state.data,
            phone=form.phone.data,
            image_link=form.image_link.data,
            website_link=form.website_link.data,
            facebook_link=form.facebook_link.data,
            seeking_talent=form.seeking_talent.data,
            seeking_description=form.seeking_description.data,
        )
        db.session.add(record)
        db.session.commit()
        flash('Venue ' + request.form['name'] + ' was successfully listed!')
        return jsonify(reqeust.form.to_dict())
    except:
        # TODO: on unsuccessful db insert, flash an error instead.
        # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
        # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
        error = True
        flash('An error occurred. Venue ' +
              request.form['name'] + ' could not be listed.')
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
    if not error:
        return render_template('pages/home.html')


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using venue_id
    venue_qs = Venue.query.get(venue_id)

    past_shows_list = past_shows(venue_qs.shows)
    setattr(venue_qs, "past_shows", past_shows_list)
    setattr(venue_qs, "past_shows_count", len(past_shows_qs))

    upcoming_shows_list = upcoming_shows(venue_qs.shows)
    setattr(venue_qs, "upcoming_shows", upcoming_shows_list)
    setattr(venue_qs, "upcoming_shows_count", len(upcoming_shows_qs))

    return render_template('pages/show_venue.html', venue=venue_qs)


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    # TODO: populate form with values from venue with ID <venue_id>
    venue_qs = Venue.query.get(venue_id)
    form = VenueForm(obj=venue_qs)
    return render_template('forms/edit_venue.html', form=form, venue=venue_qs)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # TODO: take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes
    venue_qs = Venue.query.get(venue_id)
    form = VenueForm(request.form)

    if form.validate():
        try:
            venue = Venue.query.get(venue_id)

            venue.name = form.name.data
            venue.city = form.city.data
            venue.state = form.state.data
            venue.address = form.address.data
            venue.phone = form.phone.data
            venue.genres = form.genres.data
            venue.facebook_link = form.facebook_link.data
            venue.image_link = form.image_link.data
            venue.seeking_talent = form.seeking_talent.data
            venue.seeking_description = form.seeking_description.data
            venue.website_link = form.website_link.data

            db.session.add(venue)
            db.session.commit()
            # form.populate_obj(venue_qs)
            # form.save()

            flash("Venue " + form.name.data + " updated")

        except:
            db.session.rollback()
            print(sys.exc_info())
            flash("Error updating venue.")
        finally:
            db.session.close()

    return redirect(url_for('show_venue', venue_id=venue_id))


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    # TODO: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
    error = False
    try:
        record = Venue.query.get(venue_id)
        db.session.delete(record)
        db.session.commit()
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
    if not error:
        return jsonify({"success": True})
    else:
        return jsonify({"success": False})

    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage
    return None
#  Artists
#  ----------------------------------------------------------------


@app.route('/artists')
def artists():
    # TODO: replace with real data returned from querying the database
    data = Artist.query.all()
    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".
    search_term = request.form.get('search_term', '')
    qs = Artist.query.filter(
        Artist.name.ilike(f'%{search_term}%'),
        Artist.city.ilike(f'%{search_term}%'),
        Artist.state.ilike(f'%{search_term}%'),
    )
    data = []
    for artist in qs:
        upcoming_shows_list = upcoming_shows(artist.shows)
        data.append({
            "id": artist.id,
            "name": artist.name,
            "num_upcoming_shows": len(upcoming_shows_list)
        })

    response = {
        "count": qs.count(),
        "data": data
    }
    return render_template('pages/search_artists.html', results=response, search_term=search_term)


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the artist page with the given artist_id
    # TODO: replace with real artist data from the artist table, using artist_id
    data = Artist.query.get(artist_id)

    past_shows_list = past_shows(data.shows)
    setattr(data, "past_shows", past_shows_list)
    setattr(data, "past_shows_count", len(past_shows_qs))

    upcoming_shows_list = upcoming_shows(data.shows)
    setattr(data, "upcoming_shows", upcoming_shows_list)
    setattr(data, "upcoming_shows_count", len(upcoming_shows_qs))

    return render_template('pages/show_artist.html', artist=data)


@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    # called upon submitting the new artist listing form
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion

    form = ArtistForm(request.form)

    if form.validate():
        try:
            record = Artist(
                name=form.name.data,
                city=form.city.data,
                state=form.state.data,
                phone=form.phone.data,
                genres=form.genres.data,
                image_link=form.image_link.data,
                facebook_link=form.facebook_link.data,
                website_link=form.website_link.data,
                seeking_venue=form.seeking_venue.data,
                seeking_description=form.seeking_description.data,
            )
            # on successful db insert, flash success
            db.session.add(record)
            db.session.commit()
            flash("Artist " + request.form["name"] +
                  " was successfully listed!")
        except:
            db.session.rollback()
            # TODO: on unsuccessful db insert, flash an error instead.
            # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
            flash("Error Listing Artist.")
        finally:
            db.session.close()

        return redirect(url_for("index"))

    return render_template('pages/home.html')


@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    # TODO: populate form with fields from artist with ID <artist_id>
    artist_qs = Artist.query.get(artist_id)
    form = ArtistForm(obj=artist_qs)
    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    # TODO: take values from the form submitted, and update existing
    # artist record with ID <artist_id> using the new attributes
    form = ArtistForm(request.form)

    if form.validate():
        try:
            artist = Artist.query.get(artist_id)

            artist.name = form.name.data
            artist.city = form.city.data
            artist.state = form.state.data
            artist.phone = form.phone.data
            artist.genres = form.genres.data
            artist.facebook_link = form.facebook_link.data
            artist.image_link = form.image_link.data
            artist.seeking_venue = form.seeking_venue.data
            artist.seeking_description = form.seeking_description.data
            artist.website_link = form.website_link.data

            db.session.add(artist)
            db.session.commit()
            flash("Artist " + artist.name + " was successfully updated!")
        except:
            db.session.rollback()
            print(sys.exc_info())
            flash("Error Updating Artist")
        finally:
            db.session.close()

    return redirect(url_for('show_artist', artist_id=artist_id))


#  Shows
#  ----------------------------------------------------------------
@app.route('/shows')
def shows():
    # displays list of shows at /shows
    # TODO: replace with real venues data.
    data = []
    shows = Show.query.all()
    for show in shows:
        data.append({
            "venue_id": show.venues.id,
            "venue_name": show.venues.name,
            "artist_id": show.artists.id,
            "artist_name": show.artists.name,
            "artist_image_link": show.artists.image_link,
            "start_time": show.start_time.strftime("%m/%d/%Y, %H:%M:%S")
        })

    return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    # called to create new shows in the db, upon submitting new show listing form
    # TODO: insert form data as a new Show record in the db, instead
    form = ShowForm(request.form)

    if form.validate():
        try:
            record = Show(
                artist_id=form.artist_id.data,
                venue_id=form.venue_id.data,
                start_time=form.start_time.data
            )
            db.session.add(record)
            db.session.commit()
            # on successful db insert, flash success
            flash('Show was successfully listed!')
        except:
            # TODO: on unsuccessful db insert, flash an error instead.
            # e.g., flash('An error occurred. Show could not be listed.')
            # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
            db.session.rollback()
            print(sys.exc_info())
            flash('An error occurred. Show could not be listed.')
        finally:
            db.session.close()

        return redirect(url_for("index"))

    return render_template('pages/home.html')


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
