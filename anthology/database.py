"""MongoDB backend"""

from pymongo import MongoClient


def connection():
    """Return MongoClient connection object.

    pymongo.MongoClient has it's own instance caching/connection pool.

    MongoMock however does not, so we will mockup this in tests and provide our
    own instance cache.

    """
    return MongoClient()


def collection():
    """Return songs collection"""

    return connection().anthology.songs


def get_songs_list(skip, limit):
    """Return songs from database

    :offset: Number of items to skip
    :limit: Number of returned items
    :returns: Iterable cursor object

    """

    return collection().find(skip=skip, limit=limit)
