"""Generic Flas RESTful resource classes"""

from flask_restful import Resource, reqparse


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


