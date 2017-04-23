"""Import data to songs database"""

import sys
from json import loads

from pymongo import TEXT

from anthology.database import db_songs


def import_json(filename, text_index=True):
    """Import data from JSON file.

    File must contain single dictionary on single row for each song.

    For example::

        {"title: "mysong 1", difficulty: 1, level: 5}
        {"title: "mysong 2", difficulty: 2, level: 6}
        ...

    :filename: Path to JSON file
    :returns: None

    """
    with open(filename) as infile:
        for song_json in infile.readlines():
            db_songs().insert(loads(song_json))

    index_fields = [
        ('title', TEXT),
        ('artist', TEXT)]

    if text_index:
        db_songs().create_index(index_fields, default_language='none')


if __name__ == "__main__":
    import_json(sys.argv[1])
