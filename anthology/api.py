"""RESTful API for songs database"""

from bson.json_util import dumps

from flask import Flask, url_for
from flask_restful import Api, Resource, reqparse, fields, marshal_with
from flask_restful.utils import OrderedDict

import anthology.database as db
from anthology.representations import output_bson


SONGS = [{"_id": 1}, {"_id": 2}]


SONG_FIELDS = {
    "id": fields.String(attribute=lambda x: x["_id"]),
    "artist": fields.String(),
    "title": fields.String(),
    "difficulty": fields.Float(),
    "level": fields.String(),
    "released": fields.String(),
}


SONGLIST_FIELDS = {
    "data": fields.List(fields.Nested(SONG_FIELDS)),
    "next": fields.String()  # fields.Url() line urlparse() is broken
}


class SongList(Resource):
    """Songs resource."""

    @property
    def args(self):
        """Parse and sanitize request arguments."""

        parser = reqparse.RequestParser()
        parser.add_argument(
            'limit', default=10, type=int, help='Number of items to return')
        parser.add_argument(
            'previous_id', type=str, help="Return items after this item")
        args = parser.parse_args()

        if args.limit > 100:
            args.limit = 100

        return args

    @marshal_with(SONGLIST_FIELDS)
    def get(self):
        """GET /songs"""

        songs_list = db.get_songs_list(
            previous_id=self.args.previous_id, limit=self.args.limit)

        songlist = [x for x in songs_list]

        try:
            last_id = songlist[-1]["_id"]
        except IndexError:
            last_id = None

        return {
            'data': songlist,
            'next': url_for(
                "songlist", previous_id=last_id, limit=self.args.limit)
        }


def get_app():
    """Configure main application.

    :returns: Flask application object
    """

    app = Flask(__name__)
    api = Api(app)

    api.add_resource(SongList, '/songs')

    api.representations = OrderedDict([
        ('application/json', output_bson)
    ])

    return app


if __name__ == '__main__':
    get_app().run(debug=True)
