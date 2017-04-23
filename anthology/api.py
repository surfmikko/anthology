"""RESTful API for songs database"""

from flask import Flask
from flask_restful import Api

from anthology.songs import search, average, rating


def get_app():
    """Configure main application.

    :returns: Flask application object
    """

    app = Flask(__name__)
    api = Api(app, catch_all_404s=True)

    api.add_resource(search.SongList, '/songs')
    api.add_resource(search.SongSearch, '/songs/search')
    api.add_resource(average.AverageDifficulty, '/songs/avg')
    api.add_resource(
        rating.Rating, '/songs/rating/<string:_id>', endpoint='song_rating')

    return app


if __name__ == '__main__':
    get_app().run(debug=True)
