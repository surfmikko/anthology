"""Song ratings"""

from flask_restful import fields, marshal_with

import anthology.database as db
from anthology.resource import ParameterResource
from anthology.fields import Integer


RATING_FIELDS = {
    "id": fields.String(attribute=lambda x: x["_id"]),
    "rating": Integer()
}


def rating_value(value):
    """Check that given value is integer and between 1 and 5."""
    if 1 <= int(value) <= 5:
        return int(value)
    raise ValueError("Expected rating between 1 and 5, but got %s" % value)


class Rating(ParameterResource):
    """Ratings for songs"""

    def add_arguments(self, parser):
        """Song rating gets single parameter `rating`"""

        parser.add_argument(
            'rating', type=rating_value)

        return parser

    # pylint: disable=no-self-use
    @marshal_with(RATING_FIELDS)
    def get(self, _id):
        """Return rating for single song"""
        return db.get_song(_id)

    @marshal_with(RATING_FIELDS)
    def post(self, _id):
        """Set rating for given `song_id`"""
        db.update_song(_id, {'rating': self.args.rating})
        return db.get_song(_id)
