# Anthology
Anthology is a RESTful API for querying songs database.

Use virtualenv to setup required Python libraries:

```shell
virtualenv venv
source venv/bin/activate
pip install -r requirements_dev.txt
export PYTHONPATH=.
```

Use pytest for tests with stand-alone database:

  ```shell
  py.test -sv tests
  ```

Running test server::

  ```shell
  python anthology/api.py
  ```

Trying out API with curl:

  ```shell
  curl http://localhost:5000/songs
  ```

Importing data from JSON file into songs database:

  ```shell
  python -m anthology.dbimport tests/data/songs.json
  ```

Calculating aggregates from JSON file:

  ```shell
  luigi --module anthology.aggregate RunTotals --local-scheduler
  ```

Trying out more API requests:

  ```shell
  curl http://localhost:5000/songs/avg
  curl http://localhost:5000/songs/avg?level=9
  curl http://localhost:5000/songs/avg?algorithm=fun
  ```
