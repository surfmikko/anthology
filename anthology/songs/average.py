"""Average calculation views"""

from flask_restful import fields, marshal_with

import anthology.database as db
from anthology.resource import ParameterResource
from anthology.fields import ArbitaryFloat, Integer


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
