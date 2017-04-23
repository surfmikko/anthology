"""MongoDB backend"""

from pymongo import MongoClient, ASCENDING
from bson import ObjectId


class DatabaseError(Exception):
    """Raised for unrecoverable database errors"""
    pass


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


def get_songs_list(previous_id, limit, search_term=None, search_word=None):
    """Return songs from database. Parameters `previous_id` and `limit` are
    used to iterate over result set.

    Search is performed using parameter `search_term`. This performs search
    on text index for documents. Index is always required and without it search
    will fail.

    :offset: Number of items to skip
    :limit: Number of returned items
    :search_term: Partial word search term
    :search_word: Full word search term
    :returns: Iterable cursor object

    """

    query = [{}]

    # Search for partial words
    if search_term:
        search = {'$text': {
            '$search': search_term,
            '$language': 'none',
            '$caseSensitive': False,
            '$diacriticSensitive': False
        }}

        regex = {'$regex': search_term, '$options': 'i'}
        query.append({'$or': [{'title': regex}, {'artist': regex}]})

    # Search for full words
    if search_word:
        search = {'$text': {
            '$search': search_word,
            '$language': 'none',
            '$caseSensitive': False,
            '$diacriticSensitive': False
        }}
        query.append(search)

    if previous_id:
        query.append({'_id': {'$gt': ObjectId(previous_id)}})

    return db_songs().find({'$and': query}).sort('_id', ASCENDING).limit(limit)


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
        # BUGBUG: This will overflow with big dataset
        total_difficulty += total["total_difficulty"]
        number_of_songs += total["number_of_songs"]

    if number_of_songs == 0:
        return {}

    average_difficulty = total_difficulty / float(number_of_songs)

    return {
        'level': level,
        'average_difficulty': average_difficulty,
        'algorithm': 'fun'}


def get_song(song_id):
    """Return song with given id"""
    return db_songs().find_one({'_id': ObjectId(song_id)})


def update_song(song_id, fields):
    """Return song with given id"""
    result = db_songs().update_one(
        {'_id': ObjectId(song_id)},
        {'$set': fields})
    print result
