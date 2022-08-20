# ----------------------------------------------------------------------------#
# Imports
# ----------------------------------------------------------------------------#

from traceback import print_tb
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from models import db, Artist, Venue, Show

# ----------------------------------------------------------------------------#
# App Config.
# ----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object("config")
db.init_app(app)
migrate = Migrate(app, db)


# ----------------------------------------------------------------------------#
# Filters.
# ----------------------------------------------------------------------------#


def format_datetime(value, format="medium"):
    date = dateutil.parser.parse(value)
    if format == "full":
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == "medium":
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format, locale="en")


app.jinja_env.filters["datetime"] = format_datetime

# ----------------------------------------------------------------------------#
# Controllers.
# ----------------------------------------------------------------------------#


@app.route("/")
def index():
    return render_template("pages/home.html")


#  Venues
#  ----------------------------------------------------------------


@app.route("/venues")
def venues():
    qry = Venue.query.distinct(Venue.city, Venue.state).all()

    data = [
        {
            "city": venue.city,
            "state": venue.state,
            "venues": [
                {
                    "id": v.id,
                    "name": v.name,
                    "num_upcoming_show": len(
                        [
                            show.id
                            for show in v.shows
                            if show.start_time > datetime.now()
                        ]
                    ),
                }
                for v in Venue.query.filter(
                    Venue.city == venue.city, Venue.state == venue.state
                ).all()
            ],
        }
        for venue in qry
    ]

    return render_template("pages/venues.html", areas=data)


@app.route("/venues/search", methods=["POST"])
def search_venues():
    search_term = request.form.get("search_term", "")
    qry = Venue.query.filter(Venue.name.ilike(f"%{search_term}%")).all()
    response = {
        "count": len(qry),
        "data": [
            {
                "id": venue.id,
                "name": venue.name,
                "num_upcoming_shows": len(
                    [
                        show.id
                        for show in venue.shows
                        if show.start_time > datetime.now()
                    ]
                ),
            }
            for venue in qry
        ],
    }
    return render_template(
        "pages/search_venues.html",
        results=response,
        search_term=request.form.get("search_term", ""),
    )


@app.route("/venues/<int:venue_id>")
def show_venue(venue_id):
    qry = Venue.query.filter_by(id=venue_id).first()
    upcoming = [
        {
            "artist_id": show.artist_id,
            "artist_name": show.artist.name,
            "artist_image_link": show.artist.image_link,
            "start_time": show.start_time.strftime("%Y-%m-%d %H:%M:%S"),
        }
        for show in qry.shows
        if show.start_time > datetime.now()
    ]
    past = [
        {
            "artist_id": show.artist_id,
            "artist_name": show.artist.name,
            "artist_image_link": show.artist.image_link,
            "start_time": show.start_time.strftime("%Y-%m-%d %H:%M:%S"),
        }
        for show in qry.shows
        if show.start_time <= datetime.now()
    ]
    print(qry.genres)
    data = {
        "id": qry.id,
        "name": qry.name,
        "genres": qry.genres.split(","),
        "city": qry.city,
        "address": qry.address,
        "state": qry.state,
        "phone": qry.phone,
        "website": qry.website,
        "facebook_link": qry.facebook_link,
        "seeking_talent": qry.seeking_talent,
        "seeking_description": qry.seeking_description,
        "image_link": qry.image_link,
        "past_shows": past,
        "upcoming_shows": upcoming,
        "past_shows_count": len(past),
        "upcoming_shows_count": len(upcoming),
    }
    return render_template("pages/show_venue.html", venue=data)


#  Create Venue
#  ----------------------------------------------------------------


@app.route("/venues/create", methods=["GET"])
def create_venue_form():
    form = VenueForm()
    return render_template("forms/new_venue.html", form=form)


@app.route("/venues/create", methods=["POST"])
def create_venue_submission():
    try:
        venue_dic = request.form.to_dict()
        venue_dic.pop("website_link")
        venue_dic.pop("seeking_talent")
        venue_dic.pop("genres")
        venue = Venue(
            **venue_dic,
            website=request.form["website_link"],
            seeking_talent=request.form.get("seeking_talent", "n") == "y",
            genres=",".join(request.form.getlist("genres")),
        )
        db.session.add(venue)
        db.session.commit()
        flash("Venue " + request.form["name"] + " was successfully listed!")
    except Exception as e:
        print(e)
        db.session.rollback()
        flash(
            "An error occurred. Venue " + request.form["name"] + " could not be listed."
        )
    finally:
        db.session.close()
    return render_template("pages/home.html")


@app.route("/venues/<venue_id>", methods=["DELETE"])
def delete_venue(venue_id):
    try:
        venue = Venue.query.filter_by(id=venue_id).first()
        db.session.delete(venue)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
    finally:
        db.session.close()
    return None
    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage


#  Artists
#  ----------------------------------------------------------------
@app.route("/artists")
def artists():
    data = Artist.query.all()
    return render_template("pages/artists.html", artists=data)


@app.route("/artists/search", methods=["POST"])
def search_artists():
    search_term = request.form.get("search_term", "")

    qry = Artist.query.filter(Artist.name.ilike(f"%{search_term}%")).all()
    response = {
        "count": len(qry),
        "data": [
            {
                "id": artist.id,
                "name": artist.name,
                "num_upcoming_shows": len(
                    [
                        show.id
                        for show in artist.shows
                        if show.start_time > datetime.now()
                    ]
                ),
            }
            for artist in qry
        ],
    }
    return render_template(
        "pages/search_artists.html",
        results=response,
        search_term=request.form.get("search_term", ""),
    )


@app.route("/artists/<int:artist_id>")
def show_artist(artist_id):
    qry = Artist.query.filter_by(id=artist_id).first()
    upcoming = [
        {
            "venue_id": show.venue_id,
            "venue_name": show.venue.name,
            "venue_image_link": show.venue.image_link,
            "start_time": show.start_time.strftime("%Y-%m-%d %H:%M:%S"),
        }
        for show in qry.shows
        if show.start_time > datetime.now()
    ]
    past = [
        {
            "venue_id": show.venue_id,
            "venue_name": show.venue.name,
            "venue_image_link": show.venue.image_link,
            "start_time": show.start_time.strftime("%Y-%m-%d %H:%M:%S"),
        }
        for show in qry.shows
        if show.start_time <= datetime.now()
    ]
    data = {
        "id": qry.id,
        "name": qry.name,
        "genres": qry.genres.split(","),
        "city": qry.city,
        "state": qry.state,
        "phone": qry.phone,
        "website": qry.website,
        "facebook_link": qry.facebook_link,
        "seeking_venue": qry.seeking_venue,
        "seeking_description": qry.seeking_description,
        "image_link": qry.image_link,
        "past_shows": past,
        "upcoming_shows": upcoming,
        "past_shows_count": len(past),
        "upcoming_shows_count": len(upcoming),
    }
    # upcoming = Show.query.filter(artist_id==artist_id, start_time > datetime.datetime.now())
    return render_template("pages/show_artist.html", artist=data)


#  Update
#  ----------------------------------------------------------------
@app.route("/artists/<int:artist_id>/edit", methods=["GET"])
def edit_artist(artist_id):
    artist = Artist.query.filter_by(id=artist_id).first()
    artist.genres = artist.genres.split(",")
    artist.website_link = artist.website
    form = ArtistForm(obj=artist)
    return render_template("forms/edit_artist.html", form=form, artist=artist)


@app.route("/artists/<int:artist_id>/edit", methods=["POST"])
def edit_artist_submission(artist_id):
    try:
        artist = Artist.query.filter_by(id=artist_id).first()
        form_artist = request.form.to_dict().items()
        for k, v in form_artist:
            setattr(artist, k, v)
        artist.genres = ",".join(request.form.getlist("genres"))
        artist.website = request.form["website_link"]
        artist.seeking_venue = request.form.get("seeking_venue", "n") == "y"
        print(artist.genres)
        db.session.commit()
    except Exception as e:
        print(e)
        db.session.rollback()
    finally:
        db.session.close()
    return redirect(url_for("show_artist", artist_id=artist_id))


@app.route("/venues/<int:venue_id>/edit", methods=["GET"])
def edit_venue(venue_id):
    venue = Venue.query.filter_by(id=venue_id).first()
    venue.genres = venue.genres.split(",")
    venue.website_link = venue.website
    form = VenueForm(obj=venue)
    return render_template("forms/edit_venue.html", form=form, venue=venue)


@app.route("/venues/<int:venue_id>/edit", methods=["POST"])
def edit_venue_submission(venue_id):
    try:
        venue = Venue.query.filter_by(id=venue_id).first()
        form_venue = request.form.to_dict().items()
        print(form_venue)
        for k, v in form_venue:
            setattr(venue, k, v)
        venue.website = request.form["website_link"]
        venue.seeking_talent = request.form.get("seeking_talent", "n") == "y"
        venue.genres = ",".join(request.form.getlist("genres"))
        db.session.commit()
    except Exception as e:
        print(e)
        db.session.rollback()
    finally:
        db.session.close()
    return redirect(url_for("show_venue", venue_id=venue_id))


#  Create Artist
#  ----------------------------------------------------------------


@app.route("/artists/create", methods=["GET"])
def create_artist_form():
    form = ArtistForm()
    return render_template("forms/new_artist.html", form=form)


@app.route("/artists/create", methods=["POST"])
def create_artist_submission():
    try:
        artist_dic = request.form.to_dict()
        artist_dic.pop("website_link")
        artist_dic.pop("seeking_venue")
        artist_dic.pop("genres")

        artist = Artist(
            **artist_dic,
            website=request.form["website_link"],
            seeking_venue=request.form.get("seeking_venue", "n") == "y",
            genres=",".join(request.form.getlist("genres")),
        )
        db.session.add(artist)
        db.session.commit()
        flash("Artist " + request.form["name"] + " was successfully listed!")
    except Exception as e:
        print(e)
        db.session.rollback()
        flash(
            "An error occurred. Artist "
            + request.form["name"]
            + " could not be listed."
        )
    finally:
        db.session.close()
    return render_template("pages/home.html")


#  Shows
#  ----------------------------------------------------------------


@app.route("/shows")
def shows():
    qry = Show.query.all()
    data = [
        {
            "venue_id": show.venue_id,
            "venue_name": show.venue.name,
            "artist_id": show.artist_id,
            "artist_name": show.artist.name,
            "artist_image_link": show.artist.image_link,
            "start_time": show.start_time.strftime("%Y-%m-%d %H:%M:%S"),
        }
        for show in qry
    ]
    return render_template("pages/shows.html", shows=data)


@app.route("/shows/create")
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template("forms/new_show.html", form=form)


@app.route("/shows/create", methods=["POST"])
def create_show_submission():
    try:
        show = Show(**request.form.to_dict())
        db.session.add(show)
        db.session.commit()
        flash("Show was successfully listed!")
    except Exception as e:
        db.session.rollback()
        flash("An error occurred. Show could not be listed.")
    finally:
        db.session.close()
    return render_template("pages/home.html")


@app.errorhandler(404)
def not_found_error(error):
    return render_template("errors/404.html"), 404


@app.errorhandler(500)
def server_error(error):
    return render_template("errors/500.html"), 500


if not app.debug:
    file_handler = FileHandler("error.log")
    file_handler.setFormatter(
        Formatter("%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]")
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info("errors")

# ----------------------------------------------------------------------------#
# Launch.
# ----------------------------------------------------------------------------#

# Default port:
if __name__ == "__main__":
    app.run()

# Or specify port manually:
"""
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
"""
