"""Common configuration for tests"""

import os
import shutil
import tempfile
import subprocess
import signal
import logging

from json import loads

import pytest

import pymongo

import anthology.database
from anthology.database import db_songs, db_averages
from anthology.dbimport import import_json
from anthology.api import get_app

logging.basicConfig(loglevel=logging.debug)

TEST_DB_PORT = 45684


@pytest.fixture(scope="function")
def client_fx():
    """Return test client for the application"""
    return get_app().test_client()


@pytest.fixture(scope="function")
def response_fx():
    """Return test client for the application"""

    client = get_app().test_client()

    def _get(uri):
        """Return server response as JSON"""
        response = client.get(uri)
        return loads(response.data)

    return _get


@pytest.fixture(scope='session', autouse=True)
def _mkdtemp(request):
    """Create and cleanup temporary directories"""

    if not os.path.isdir('.tmp'):
        os.makedirs('.tmp')

    def _mkdtemp(prefix):
        """Return temp path"""
        return tempfile.mkdtemp(prefix=prefix, dir='.tmp')

    def _fin():
        """Remove temporary files"""
        shutil.rmtree('.tmp')

    request.addfinalizer(_fin)

    return _mkdtemp


class MongoProc(object):
    """Object wrapper for mongodb server process"""

    def __init__(self, db_path):
        """Setup the class"""
        self.pid = None
        self.proc = None
        self.db_path = db_path
        self.db_port = TEST_DB_PORT

    def start(self):
        """Run process"""
        self.proc = subprocess.Popen(
            ['mongod', '--dbpath', self.db_path,
             '--port', str(self.db_port),
             '--unixSocketPrefix', self.db_path,
             '--noprealloc', '--nojournal', '--smallfiles'],
            shell=False,
            preexec_fn=os.setsid)
        self.pid = self.proc.pid

    def kill(self):
        """End the process"""
        if self.proc:
            self.proc.terminate()
            self.proc.wait()
            try:
                os.killpg(self.proc.pid, signal.SIGKILL)
            except OSError:
                pass
            self.proc = None

    def __del__(self):
        """Ensure self.kill() gest called"""
        self.kill()


@pytest.fixture(scope='session', autouse=True)
def mongo_proc(request, _mkdtemp):
    """Start mongod process"""

    db_path = _mkdtemp(prefix="mongodb.")

    mongodb = MongoProc(db_path)
    mongodb.start()

    connection = pymongo.MongoClient(host="localhost:%s" % TEST_DB_PORT)

    setattr(anthology.database, 'connection', lambda: connection)

    def _fin():
        """Shutdown database"""
        mongodb.kill()

    request.addfinalizer(_fin)


@pytest.fixture(autouse=True, scope='function')
def testdata_fx():
    """Use temporary MongoDB instance for testing"""

    db_songs().remove()
    db_averages().remove()
    import_json('tests/data/songs.json')
