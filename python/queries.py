"""
queries.py

Example queries against the claims collection, each with a comment
comparing it to how I'd write the equivalent in SQL against the star
schema.
"""

import os

try:
    import mongomock as _mongo_lib

    _USE_MOCK = True
except ImportError:  # pragma: no cover
    _USE_MOCK = False

import pymongo


def get_client():
    mongo_uri = os.getenv("MONGO_URI")
    if mongo_uri:
        return pymongo.MongoClient(mongo_uri)
    if _USE_MOCK:
        return _mongo_lib.MongoClient()
    raise RuntimeError("No MONGO_URI set and mongomock is not installed.")


def claims_by_status(collection, status: str) -> list[dict]:
    """
    SQL equivalent:
        SELECT * FROM fact_claims WHERE claim_status = 'approved';
    No join needed on either side — this one's a straight comparison.
    """
    return list(collection.find({"status": status}))


def total_approved_by_region(collection) -> list[dict]:
    """
    SQL equivalent:
        SELECT p.region, SUM(f.approved_amount) AS total_approved
        FROM fact_claims f
        JOIN dim_patient p ON f.patient_key = p.patient_key
        GROUP BY p.region;

    In the relational version this needs a join to dim_patient. In the
    document version, region is already embedded in the claim document,
    so the aggregation pipeline never has to reach into another
    collection at all. This is the concrete trade-off from
    document_model.py showing up in a real query: the embed decision
    made this query cheaper, at the cost of region being duplicated
    across every claim for the same patient.
    """
    pipeline = [
        {"$group": {"_id": "$patient.region", "total_approved": {"$sum": "$total_approved"}}},
        {"$sort": {"total_approved": -1}},
    ]
    return list(collection.aggregate(pipeline))


def high_value_claims_with_line_item_detail(collection, threshold: float) -> list[dict]:
    """
    SQL equivalent:
        SELECT f.claim_id, f.total_billed, l.procedure_code, l.billed_amount
        FROM fact_claims f
        JOIN claim_line_items l ON f.claim_key = l.claim_key
        WHERE f.total_billed > :threshold;

    Relationally this is a one-to-many join (a claim has many line items).
    In the document model, line_items is already embedded as an array
    inside the claim document, so "join" is just reading a field that's
    already there — no separate lookup required.
    """
    return list(
        collection.find(
            {"total_billed": {"$gt": threshold}},
            {"claim_id": 1, "total_billed": 1, "line_items": 1, "_id": 0},
        )
    )


def provider_claim_counts(collection) -> list[dict]:
    """
    SQL equivalent:
        SELECT provider_id, COUNT(*) AS claim_count
        FROM fact_claims
        GROUP BY provider_id;

    provider_id is a REFERENCE in this document model (see
    document_model.py), not embedded — so this query behaves almost
    exactly like the relational version, since provider details would
    still need a separate lookup either way.
    """
    pipeline = [
        {"$group": {"_id": "$provider_id", "claim_count": {"$sum": 1}}},
        {"$sort": {"claim_count": -1}},
    ]
    return list(collection.aggregate(pipeline))


if __name__ == "__main__":
    client = get_client()
    collection = client["claims_db"]["claims"]

    print("Approved claims:", len(claims_by_status(collection, "approved")))
    print("Total approved by region:", total_approved_by_region(collection))
    print("High-value claims (>1500):", len(high_value_claims_with_line_item_detail(collection, 1500)))
    print("Claim counts by provider:", provider_claim_counts(collection))
