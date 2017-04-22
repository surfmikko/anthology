# Anthology
Anthology is a RESTful API for querying songs database.

Use virtualenv to setup required Python libraries:

```shell
virtualenv venv
source venv/bin/activate
pip install -r requirements_dev.txt
```

Use pytest for testing:

```shell
PYTHONPATH=. py.test -sv tests
```

Running test server::

```shell
PYTHONPATH=. python anthology/api.py
```

Trying out API with curl:

```shell
curl http://localhost:5000/songs
```
