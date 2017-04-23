"""RESTful API for songs database"""

from flask import Flask, url_for
from flask_restful import Api, Resource, reqparse, fields, marshal_with

import anthology.database as db
from anthology.fields import ArbitaryFloat, Integer


SONG_FIELDS = {
    "id": fields.String(attribute=lambda x: x["_id"]),
    "artist": fields.String(),
    "title": fields.String(),
    "difficulty": fields.Float(),
    "level": fields.String(),
    "released": fields.String(),
    "rating": Integer(),
    "rating_url": fields.Url('song_rating')
}

SONGLIST_FIELDS = {
    "data": fields.List(fields.Nested(SONG_FIELDS)),
    "next": fields.String()  # fields.Url() line urlparse() is broken
}


class ParameterResource(Resource):
    """Resource with HTTP request parameter handling"""

    def add_arguments(self, parser):
        """Add URL parameters for the resource"""
        raise NotImplementedError("Remember to override this")

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
            endpoint=getattr(self, 'endpoint'),
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

    if items == []:
        return None

    last_id = items[-1]["_id"]

    return url_for(endpoint, previous_id=last_id, limit=limit, **kwargs)


AVERAGE_FIELDS = {
    "average_difficulty": ArbitaryFloat(2),
    "level": Integer(),
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


RATING_FIELDS = {
    "id": fields.String(attribute=lambda x: x["_id"]),
    "rating": Integer()
}


class Rating(ParameterResource):
    """Ratings for songs"""

    def add_arguments(self, parser):
        """Song rating gets single parameter `rating`"""

        parser.add_argument(
            'rating', type=int, help='New rating for the song')

        return parser

    @marshal_with(RATING_FIELDS)
    def get(self, _id):
        """Return rating for single song"""
        return db.get_song(_id)

    @marshal_with(RATING_FIELDS)
    def post(self, _id):
        """Set rating for given `song_id`"""
        db.update_song(_id, {'rating': self.args.rating})
        return db.get_song(_id)


def get_app():
    """Configure main application.

    :returns: Flask application object
    """

    app = Flask(__name__)
    api = Api(app, catch_all_404s=True)

    api.add_resource(SongList, '/songs')
    api.add_resource(SongSearch, '/songs/search')
    api.add_resource(AverageDifficulty, '/songs/avg')
    api.add_resource(
        Rating, '/songs/rating/<string:_id>', endpoint='song_rating')

    return app


if __name__ == '__main__':
    get_app().run(debug=True)
