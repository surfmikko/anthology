# Anthology

[![Build Status](https://travis-ci.org/surfmikko/anthology.svg?branch=master)](https://travis-ci.org/surfmikko/anthology) 

Anthology is a RESTful API for querying songs database.

## Installing required libraries

Anthology requires recent version of MongoDB running:

```shell
sudo yum -y install mongodb-org-server
sudo service mongod start
```

Python requirements can be installed in virtualenv environment with pip:

```shell
virtualenv venv
source venv/bin/activate
pip install -r requirements_dev.txt
export PYTHONPATH=.
```

## Running tests

Use pytest for tests with stand-alone database:

  ```shell
  py.test -sv tests
  ```

If you have older MongoDB try skipping tests with text indexes:

```shell
py.test -sv tests --skip-text-index
```

## Running test service

With configured environment test server can be started with command:

  ```shell
  python anthology/api.py
  ```

Test the API in other terminal with curl:

  curl http://localhost:5000/songs

## Importing data

For successful requests we need some data. Import provided test dataset with
command:

  ```shell
  python -m anthology.dbimport tests/data/songs.json
  ```

For experimental / just for fun averaging feature you can import aggregated dataset with command:
 
  ```shell
  luigi --module anthology.aggregate RunTotals --local-scheduler
  ```

## Usage examples

Try out API with some example curl commands:

  ```shell
  curl http://localhost:5000/songs?limit=3&previous_id=<id>

  curl http://localhost:5000/songs/avg?level=9
  curl http://localhost:5000/songs/avg?algorithm=fun

  curl http://localhost:5000/songs/search?message=night
  curl http://localhost:5000/songs/search?message=me
  curl http://localhost:5000/songs/search?word=me

  curl http://localhost:5000/songs/rating/<id>
  curl http://localhost:5000/songs/rating/<id> --data 'rating=5'
  ```

## Known issues

Anthology has been tested with Python 2.7 and MongoDB 3.4.4.

  * Old versions of MongoDB have unresolved issues with text indexes (2.4/2.6)
