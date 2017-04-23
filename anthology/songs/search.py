"""Views for songs and searches"""

from flask import url_for
from flask_restful import fields, marshal_with

import anthology.database as db
from anthology.resource import ParameterResource
from anthology.fields import Integer


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
