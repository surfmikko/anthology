"""RESTful API for songs database"""

from bson.json_util import dumps

from flask import Flask, url_for
from flask_restful import Api, Resource, reqparse, fields, marshal_with
from flask_restful.utils import OrderedDict

import anthology.database as db
from anthology.representations import output_bson
from anthology.fields import ArbitaryFloat


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

        return {
            'data': songlist,
            'next': pagination_uri("songlist", songlist, self.args.limit)
        }


def pagination_uri(endpoint, items, limit):
    """Return paginated URL for given endpoint."""

    if len(items) < limit:
        return None

    last_id = items[-1]["_id"]

    return url_for(endpoint, previous_id=last_id, limit=limit)


AVERAGE_FIELDS = {
    "average_difficulty": ArbitaryFloat(2),
    "level": fields.Integer(),
    "algorithm": fields.String()
}


class AverageDifficulty(Resource):
    """Songs resource."""

    @property
    def args(self):
        """Parse and sanitize request arguments."""

        parser = reqparse.RequestParser()
        parser.add_argument(
            'level', default=None,
            type=int, help='Level of songs to get averages')
        parser.add_argument(
            'algorithm', type=str, help='Some fun averages?')
        args = parser.parse_args()

        return args

    @marshal_with(AVERAGE_FIELDS)
    def get(self):
        """GET /songs"""

        if self.args.algorithm == 'fun':
            return db.get_average_difficulty_fun(
                level=self.args.level)

        return db.get_average_difficulty(
            level=self.args.level)


def get_app():
    """Configure main application.

    :returns: Flask application object
    """

    app = Flask(__name__)
    api = Api(app)

    api.add_resource(SongList, '/songs')
    api.add_resource(AverageDifficulty, '/songs/avg')

    api.representations = OrderedDict([
        ('application/json', output_bson)
    ])

    return app


if __name__ == '__main__':
    get_app().run(debug=True)
