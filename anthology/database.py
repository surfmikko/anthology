"""MongoDB backend"""

from pymongo import MongoClient, ASCENDING
from bson import ObjectId


def connection():
    """Return MongoClient connection object.

    pymongo.MongoClient has it's own instance caching/connection pool.

    MongoMock however does not, so we will mockup this in tests and provide our
    own instance cache.

    """
    return MongoClient()


def db_songs():
    """Return songs collection"""
    return connection().anthology.songs


def db_averages():
    """Return averages collection"""
    return connection().anthology.averages


def get_songs_list(previous_id, limit):
    """Return songs from database

    :offset: Number of items to skip
    :limit: Number of returned items
    :returns: Iterable cursor object

    """

    query = {}

    if previous_id:
        query = {'_id': {'$gt': ObjectId(previous_id)}}
    return db_songs().find(query).sort('_id', ASCENDING).limit(limit)


def get_average_difficulty(level):
    """Return average difficulty for all songs on given level.

    If difficulty is not given, return difficulty for all songs in database.

    :level: Song level to search
    :collection: Collection to search from
    :returns: Dictionary with level and average difficulty

    """

    collection = db_songs()

    pipeline = [
        {"$group": {
            "_id": None,
            "average_difficulty": {"$avg": "$difficulty"}
        }}]

    if level:
        pipeline.insert(0, {"$match": {"level": level}})

    results = collection.aggregate(pipeline)

    try:
        result = results.next()
        result["algorithm"] = 'trivial'
        return result
    except StopIteration:
        return {}


def filter_songs_by_level(songs, level):
    """Filter out all bad values"""
    for song in songs:
        if level is None:
            yield song
        if level == song["level"]:
            yield song


def get_average_difficulty_fun(level):
    """Just for fun implementation for averages.

    Most data was already batch processed beforehand, so we can calculate rest
    efficiently in Python.

    If difficulty is not given, return difficulty for all songs in database.

    :level: Song level to search
    :collection: Collection to search from
    :returns: Dictionary with level and average difficulty

    """

    totals = db_averages().find()

    total_difficulty = 0
    number_of_songs = 0

    for total in filter_songs_by_level(totals, level):
        # BUGBUG: This will overflow
        total_difficulty += total["total_difficulty"]
        number_of_songs += total["number_of_songs"]

    if number_of_songs == 0:
        return {}

    average_difficulty = total_difficulty / float(number_of_songs)

    return {
        'level': level,
        'average_difficulty': average_difficulty,
        'algorithm': 'fun'}
