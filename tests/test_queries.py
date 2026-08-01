"""
test_queries.py

Runs against mongomock so these tests execute with no external services.
This is the same test-first pattern used in the Healthcare Claims Data
Platform and Payments Event Data Platform (pytest + GitHub Actions CI).
"""

import sys
import pathlib

import mongomock
import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "python"))

from document_model import build_example_document  # noqa: E402
from load_documents import generate_sample_documents  # noqa: E402
from queries import (  # noqa: E402
    claims_by_status,
    high_value_claims_with_line_item_detail,
    provider_claim_counts,
    total_approved_by_region,
)


@pytest.fixture
def collection():
    client = mongomock.MongoClient()
    coll = client["claims_db"]["claims"]
    coll.insert_many(generate_sample_documents(n=25))
    return coll


def test_example_document_shape():
    doc = build_example_document()
    assert doc["claim_id"].startswith("CLM-")
    assert "patient" in doc and "region" in doc["patient"]
    assert isinstance(doc["line_items"], list) and len(doc["line_items"]) > 0
    assert doc["total_billed"] >= doc["total_approved"]


def test_claims_by_status_filters_correctly(collection):
    approved = claims_by_status(collection, "approved")
    assert all(doc["status"] == "approved" for doc in approved)


def test_total_approved_by_region_groups_all_regions(collection):
    result = total_approved_by_region(collection)
    region_names = {row["_id"] for row in result}
    # every document's region should show up in the grouped result
    all_regions = {doc["patient"]["region"] for doc in collection.find()}
    assert region_names == all_regions


def test_high_value_claims_respects_threshold(collection):
    result = high_value_claims_with_line_item_detail(collection, threshold=1500)
    assert all(doc["total_billed"] > 1500 for doc in result)
    # embedded line items should come back with the claim, no second lookup
    assert all("line_items" in doc for doc in result)


def test_provider_claim_counts_sums_to_total(collection):
    result = provider_claim_counts(collection)
    total = sum(row["claim_count"] for row in result)
    assert total == collection.count_documents({})
