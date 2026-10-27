"""Candidate mapping operations with explicit evidence and status validation."""

from __future__ import annotations

from typing import Any
from uuid import uuid4

from src.validation import (
    DataValidationError,
    validate_mapping,
    validate_status_transition,
)


def create_mapping(
    technique_id: str,
    evidence_ids: list[str],
    rationale: str,
    alternatives: str,
    missing_evidence: str,
    confidence: int,
    status: str,
    techniques: dict[str, dict[str, Any]],
    known_evidence_ids: set[str],
) -> dict[str, Any]:
    mapping = {
        "mapping_id": str(uuid4()),
        "technique_id": technique_id,
        "evidence_ids": list(dict.fromkeys(evidence_ids)),
        "rationale": rationale.strip(),
        "alternative_explanations": alternatives.strip(),
        "missing_evidence": missing_evidence.strip(),
        "confidence": confidence,
        "status": status,
    }
    validate_mapping(mapping, techniques, known_evidence_ids)
    return mapping


def update_mapping(
    mapping: dict[str, Any],
    updates: dict[str, Any],
    techniques: dict[str, dict[str, Any]],
    known_evidence_ids: set[str],
) -> dict[str, Any]:
    updated = {**mapping, **updates}
    if "status" in updates:
        validate_status_transition(mapping.get("status", ""), updates["status"])
    validate_mapping(updated, techniques, known_evidence_ids)
    return updated


def remove_mapping(mappings: list[dict[str, Any]], mapping_id: str) -> list[dict[str, Any]]:
    remaining = [item for item in mappings if item["mapping_id"] != mapping_id]
    if len(remaining) == len(mappings):
        raise DataValidationError(f"Mapping {mapping_id!r} does not exist.")
    return remaining


def mappings_for_evidence(
    mappings: list[dict[str, Any]], evidence_id: str
) -> list[dict[str, Any]]:
    return [mapping for mapping in mappings if evidence_id in mapping["evidence_ids"]]
