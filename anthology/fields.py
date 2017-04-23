"""Additional field formatting"""

from flask_restful import fields
from flask_restful.fields import MarshallingException


# oh, bummer...
# pylint: disable=too-few-public-methods
class ArbitaryFloat(fields.Raw):
    """
    A double as IEEE-754 double precision, with arbitary precision.

    Note this is not suitable for all calculations, because of floating point
    precision limitations. For more information see Python documentation:

    https://docs.python.org/2/tutorial/floatingpoint.html#tut-fp-issues

    """

    def __init__(self, precision=None):
        """Setup class"""
        super(ArbitaryFloat, self).__init__()
        self.precision = precision

    def format(self, value):
        """Return truncated float value"""
        try:
            return round(float(value), self.precision)
        except ValueError as error:
            raise MarshallingException(error)


class Integer(fields.Raw):
    """ Field for outputting an integer value. This allows also None values for
    integer.

    Modified from flask_restful.fields.Integer.

    :param int default: The default value for the field, if no value is
        specified.
    """
    def format(self, value):
        try:
            if value is None:
                return None
            return int(value)
        except ValueError as error:
            raise MarshallingException(error)
