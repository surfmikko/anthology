"""RESTful API for songs database"""

from bson.json_util import dumps

from flask import Flask
from flask_restful import Api, Resource, reqparse
from flask_restful.utils import OrderedDict

import anthology.database as db
from anthology.representations import output_bson


SONGS = [{"_id": 1}, {"_id": 2}]


class SongsList(Resource):
    """Songs resource."""

    @property
    def args(self):
        """Parse and sanitize request arguments."""

        parser = reqparse.RequestParser()
        parser.add_argument(
            'limit', default=10, type=int, help='Number of items to return')
        parser.add_argument(
            'skip', default=0, type=int, help='Number of items to skip')
        args = parser.parse_args()

        if args.limit > 100:
            args.limit = 100

        return args

    def get(self):
        """GET /songs"""

        songs_list = db.get_songs_list(
            skip=self.args.skip, limit=self.args.limit)
        result = {
            'data': [x for x in songs_list]
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
