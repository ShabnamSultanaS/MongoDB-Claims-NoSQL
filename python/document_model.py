"""
document_model.py

Defines the shape of a claims document, and explains why it's shaped that
way compared to the relational star schema in the DuckDB/Snowflake
versions of this project.

In the relational model:
    fact_claims (one row per claim, foreign keys out to dimensions)
    dim_patient, dim_provider, dim_date, + a separate claim_line_items table

In this document model:
    One claims document per claim, with the patient snapshot and line
    items EMBEDDED directly. Provider is kept as a REFERENCE (not
    embedded), because provider records are large, shared across many
    claims, and change independently of any one claim.

That mixed approach (embed some things, reference others) is the actual
skill in document modelling — not "always embed" or "always reference".
"""

from datetime import date
from typing import TypedDict


class LineItem(TypedDict):
    procedure_code: str
    description: str
    billed_amount: float
    approved_amount: float


class PatientSnapshot(TypedDict):
    """
    Embedded, not referenced. Rationale: claims are legal/audit records —
    if the patient's address or plan details change next year, this claim
    should still show what was true *at the time it was submitted*. That's
    the document-database answer to the SCD Type 2 problem I solved with
    effective/expiry dates in the relational version: instead of versioning
    rows in a shared dimension table, each document just carries its own
    point-in-time copy.
    """

    patient_id: str
    date_of_birth: str
    region: str
    plan_tier: str


class ClaimDocument(TypedDict):
    claim_id: str
    submission_date: str
    status: str
    provider_id: str  # reference, not embedded — see module docstring
    patient: PatientSnapshot  # embedded snapshot
    line_items: list[LineItem]  # embedded — always read together with the claim
    total_billed: float
    total_approved: float
    data_quality_flag: str


def build_example_document() -> ClaimDocument:
    """A single worked example, used by the tests and by load_documents.py."""
    return {
        "claim_id": "CLM-100234",
        "submission_date": date(2026, 3, 14).isoformat(),
        "status": "approved",
        "provider_id": "PRV-5521",
        "patient": {
            "patient_id": "PAT-88291",
            "date_of_birth": "1987-06-02",
            "region": "Bengaluru",
            "plan_tier": "gold",
        },
        "line_items": [
            {
                "procedure_code": "P-0110",
                "description": "Outpatient consultation",
                "billed_amount": 1200.00,
                "approved_amount": 1200.00,
            },
            {
                "procedure_code": "P-0442",
                "description": "Blood panel",
                "billed_amount": 850.00,
                "approved_amount": 680.00,
            },
        ],
        "total_billed": 2050.00,
        "total_approved": 1880.00,
        "data_quality_flag": "clean",
    }
