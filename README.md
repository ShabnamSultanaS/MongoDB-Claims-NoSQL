# MongoDB Claims Document Model (Practice Project)

**Status: learning-in-progress.** This project remodels a slice of the
claims data from my Healthcare Claims Data Platform as MongoDB documents,
to practise NoSQL/document data modelling against the relational star
schema I already know well. It's a self-directed study project, run
locally, not a production system.

## Why this project exists

Every relational schema I've built (SQL Server, DuckDB) starts from
normalisation and joins. Document databases invert that: you design around
how the data is *read*, and you deliberately duplicate data to avoid joins.
Understanding that trade-off in practice, not just in theory, was the point
of this project.

## What's here

```
mongodb-claims-nosql/
├── python/
│   ├── document_model.py    # the document shape, and why it's shaped that way
│   ├── load_documents.py    # transforms relational claims data into documents
│   └── queries.py           # example queries + the aggregation pipeline equivalent of a SQL join
├── tests/
│   └── test_queries.py      # runnable tests — see "Running it" below
├── STUDY_NOTES.md
├── requirements.txt
└── README.md
```

## Running it without a real MongoDB server

This project uses [`mongomock`](https://github.com/mongomock/mongomock), a
pure-Python library that mimics MongoDB's API in memory. That means the
code and tests genuinely run and pass, no server, no Atlas signup needed,
which was useful for iterating on the data model quickly. Every query in
`queries.py` uses the real `pymongo` query syntax, so the same code runs
unmodified against a real MongoDB instance — only the connection setup
changes.

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pytest tests/ -v
```

## Running it against a real MongoDB instance

1. Create a free [MongoDB Atlas](https://www.mongodb.com/cloud/atlas/register) cluster (M0 tier, no cost)
2. Set the connection string: `export MONGO_URI="your-atlas-connection-string"`
3. In `python/load_documents.py` and `python/queries.py`, swap `mongomock.MongoClient()` for `pymongo.MongoClient(os.environ["MONGO_URI"])`
4. Run `python python/load_documents.py` to load sample data, then `python python/queries.py` to run the example queries against the real cluster

## What I'm getting out of this

See `STUDY_NOTES.md`, but the short version: this is where I practise
deciding *when* denormalisation is the right call, not just how to write
the query syntax. A claims document that embeds its line items is fast to
read but awkward to update; the star schema version is the opposite. Being
able to explain that trade-off with a concrete example is the actual skill
here, not the MongoDB syntax itself.

## Honesty note

This has been run and tested locally against `mongomock`, not against a
production MongoDB cluster at scale. I'm not claiming operational NoSQL
experience — I'm showing the modelling and query work I've done to start
learning it.
