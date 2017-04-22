"""RESTful API for songs database"""

from bson.json_util import dumps

from flask import Flask
from flask_restful import Api, Resource
from flask_restful.utils import OrderedDict

import anthology.database as db
from anthology.representations import output_bson


SONGS = [{"_id": 1}, {"_id": 2}]


class SongsList(Resource):
    """Songs resource."""

    def get(self, skip=0):
        """GET /songs"""

        result = {
            'data': [x for x in db.get_songs_list(skip=skip, limit=10)]
        }

        return result


def get_app():
    """Configure main application.

    :returns: Flask application object
    """

    app = Flask(__name__)
    api = Api(app)

    api.add_resource(SongsList, '/songs')

    api.representations = OrderedDict([
        ('application/json', output_bson)
    ])

    return app


if __name__ == '__main__':
    get_app().run(debug=True)
