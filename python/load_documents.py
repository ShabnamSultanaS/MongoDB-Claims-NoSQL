"""
load_documents.py

Loads a handful of sample claim documents into a `claims` collection.

By default this connects via mongomock (in-memory, no server required) so
the project runs out of the box. To point it at a real MongoDB instance,
see the "Running it against a real MongoDB instance" section in README.md.
"""

import os
import random
from datetime import date, timedelta

try:
    import mongomock as _mongo_lib

    _USE_MOCK = True
except ImportError:  # pragma: no cover
    _USE_MOCK = False

import pymongo

from document_model import build_example_document

REGIONS = ["Bengaluru", "Dublin", "Mumbai", "Hyderabad"]
PLAN_TIERS = ["bronze", "silver", "gold"]
STATUSES = ["approved", "pending", "denied"]


def get_client():
    mongo_uri = os.getenv("MONGO_URI")
    if mongo_uri:
        return pymongo.MongoClient(mongo_uri)
    if _USE_MOCK:
        return _mongo_lib.MongoClient()
    raise RuntimeError(
        "No MONGO_URI set and mongomock is not installed. "
        "Install requirements.txt or set MONGO_URI to a real cluster."
    )


def generate_sample_documents(n: int = 25) -> list[dict]:
    base = build_example_document()
    docs = []
    for i in range(n):
        doc = dict(base)
        doc["claim_id"] = f"CLM-{100000 + i}"
        doc["submission_date"] = (
            date(2026, 1, 1) + timedelta(days=random.randint(0, 200))
        ).isoformat()
        doc["status"] = random.choice(STATUSES)
        doc["patient"] = dict(base["patient"])
        doc["patient"]["region"] = random.choice(REGIONS)
        doc["patient"]["plan_tier"] = random.choice(PLAN_TIERS)
        docs.append(doc)
    return docs


def main() -> None:
    client = get_client()
    db = client["claims_db"]
    collection = db["claims"]

    collection.delete_many({})  # start clean each run
    docs = generate_sample_documents()
    result = collection.insert_many(docs)

    print(f"Inserted {len(result.inserted_ids)} documents into claims_db.claims")
    print("Backend:", "mongomock (in-memory)" if not os.getenv("MONGO_URI") else "real MongoDB")


if __name__ == "__main__":
    main()
