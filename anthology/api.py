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


class ParameterResource(Resource):
    """Resource with HTTP request parameter handling"""

    @property
    def args(self):
        """Return request parameters as dictionary"""
        parser = reqparse.RequestParser()
        self.add_arguments(parser)
        return parser.parse_args()


class SongList(ParameterResource):
    """Songs resource."""

    def add_arguments(self, parser):
        """Parameters for the resource"""

        parser.add_argument(
            'limit', default=10, type=int, help='Number of items to return')
        parser.add_argument(
            'previous_id', type=str, help="Return items after this item")
        parser.add_argument(
            'message', default=None,
            type=str, help='Search term (partial word)')
        parser.add_argument(
            'word', default=None,
            type=str, help='Search term (full word)')

        return parser

    @marshal_with(SONGLIST_FIELDS)
    def get(self):
        """GET /songs"""

        if self.args.limit > 100:
            self.args.limit = 100

        results = db.get_songs_list(
            previous_id=self.args.previous_id,
            limit=self.args.limit,
            search_term=self.args.message,
            search_word=self.args.word)

        songlist = list(results)

        pagination = pagination_uri(
            endpoint=self.endpoint,
            items=songlist,
            limit=self.args.limit,
            message=self.args.message,
            word=self.args.word)

        return {'data': songlist, 'next': pagination}


class SongSearch(SongList):
    """Flask Restful seems to require separate class for each route. Routing
    same class to different routes causes AssertionError."""
    pass


def pagination_uri(endpoint, items, limit, **kwargs):
    """Return paginated URL for given endpoint."""

    if len(items) == 0:
        return None

    last_id = items[-1]["_id"]

    return url_for(endpoint, previous_id=last_id, limit=limit, **kwargs)


AVERAGE_FIELDS = {
    "average_difficulty": ArbitaryFloat(2),
    "level": fields.Integer(),
    "algorithm": fields.String()
}


class AverageDifficulty(ParameterResource):
    """Songs resource."""

    def add_arguments(self, parser):
        """Parse and sanitize request arguments."""

        parser.add_argument(
            'level', default=None,
            type=int, help='Level of songs to get averages')
        parser.add_argument(
            'algorithm', type=str, help='Some fun averages?')

        return parser

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
    api.add_resource(SongSearch, '/songs/search')
    api.add_resource(AverageDifficulty, '/songs/avg')

    api.representations = OrderedDict([
        ('application/json', output_bson)
    ])

    return app


if __name__ == '__main__':
    get_app().run(debug=True)
