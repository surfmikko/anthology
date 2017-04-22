"""RESTful API for songs database"""

from flask import Flask
from flask_restful import Api, Resource


SONGS = [{"_id": 1}, {"_id": 2}]


class SongsList(Resource):
    def get(self, page=0):
        return SONGS


def get_app():
    """Configure main application.

    :returns: Flask application object
    """

    app = Flask(__name__)
    api = Api(app)

    api.add_resource(SongsList, '/songs')

    return app


if __name__ == '__main__':
    get_app().run(debug=True)
