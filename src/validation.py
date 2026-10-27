"""Input and business-rule validation for synthetic exercise data."""

from __future__ import annotations

import csv
import io
import re
from datetime import datetime, timezone
from typing import Any


EVENT_REQUIRED_FIELDS = {
    "evidence_id",
    "timestamp",
    "host_or_identity",
    "category",
    "description",
    "data_source",
    "observed_behaviour",
    "potential_significance",
    "confidence",
    "evidence_limitations",
    "related_events",
    "synthetic",
}
MAPPING_STATUSES = {"proposed", "supported", "rejected", "needs further investigation"}
ALLOWED_STATUS_TRANSITIONS = {
    "proposed": {"proposed", "supported", "rejected", "needs further investigation"},
    "supported": {"supported", "proposed", "rejected", "needs further investigation"},
    "rejected": {"rejected", "proposed"},
    "needs further investigation": {
        "needs further investigation",
        "proposed",
        "supported",
        "rejected",
    },
}
TECHNIQUE_ID_PATTERN = re.compile(r"^T\d{4}(?:\.\d{3})?$")


class DataValidationError(ValueError):
    """Raised when an input record fails an explicit validation rule."""


def _normalize_utc_timestamp(value: Any, context: str) -> str:
    try:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError as exc:
        raise DataValidationError(f"{context} has an invalid ISO-8601 timestamp.") from exc
    if parsed.tzinfo is None:
        raise DataValidationError(f"{context} timestamp must include a timezone.")
    return parsed.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def validate_event_records(events: Any) -> list[dict[str, Any]]:
    if not isinstance(events, list):
        raise DataValidationError("Events must be a JSON array.")
    seen: set[str] = set()
    cleaned: list[dict[str, Any]] = []
    for index, event in enumerate(events):
        if not isinstance(event, dict):
            raise DataValidationError(f"Event {index + 1} must be an object.")
        missing = EVENT_REQUIRED_FIELDS - event.keys()
        if missing:
            raise DataValidationError(
                f"Event {index + 1} is missing: {', '.join(sorted(missing))}."
            )
        for field in (
            "evidence_id",
            "timestamp",
            "host_or_identity",
            "category",
            "description",
            "data_source",
            "observed_behaviour",
            "potential_significance",
            "evidence_limitations",
        ):
            if not isinstance(event[field], str) or not event[field].strip():
                raise DataValidationError(f"Event {index + 1} has an invalid {field}.")
        event_id = event["evidence_id"]
        if not isinstance(event_id, str) or not event_id.strip() or event_id in seen:
            raise DataValidationError(f"Event {index + 1} has an invalid or duplicate evidence ID.")
        seen.add(event_id)
        normalized_event = dict(event)
        normalized_event["timestamp"] = _normalize_utc_timestamp(event["timestamp"], event_id)
        if (
            not isinstance(event["confidence"], (int, float))
            or isinstance(event["confidence"], bool)
            or not 0 <= event["confidence"] <= 1
        ):
            raise DataValidationError(f"{event_id} confidence must be between 0 and 1.")
        if event["synthetic"] is not True:
            raise DataValidationError(f"{event_id} is not explicitly labelled synthetic.")
        if not isinstance(event["related_events"], list) or any(
            not isinstance(reference, str) or not reference for reference in event["related_events"]
        ):
            raise DataValidationError(f"{event_id} related_events must be an array.")
        cleaned.append(normalized_event)
    ids = {event["evidence_id"] for event in cleaned}
    for event in cleaned:
        unknown = set(event["related_events"]) - ids
        if unknown:
            raise DataValidationError(
                f"{event['evidence_id']} references unknown evidence: {', '.join(sorted(unknown))}."
            )
    return cleaned


def validate_technique_catalogue(catalogue: Any) -> dict[str, dict[str, Any]]:
    if not isinstance(catalogue, dict) or catalogue.get("domain") != "enterprise-attack":
        raise DataValidationError("Technique catalogue must declare the Enterprise ATT&CK domain.")
    if catalogue.get("attack_version") != "15.1":
        raise DataValidationError("This workshop catalogue must be pinned to ATT&CK 15.1.")
    records = catalogue.get("records")
    if not isinstance(records, list):
        raise DataValidationError("Technique catalogue records must be an array.")
    indexed: dict[str, dict[str, Any]] = {}
    for record in records:
        if not isinstance(record, dict):
            raise DataValidationError("Each technique record must be an object.")
        technique_id = record.get("technique_id")
        if not isinstance(technique_id, str) or not TECHNIQUE_ID_PATTERN.fullmatch(technique_id):
            raise DataValidationError(f"Invalid ATT&CK technique ID: {technique_id!r}.")
        if technique_id in indexed:
            raise DataValidationError(f"Duplicate ATT&CK technique ID: {technique_id}.")
        if not record.get("name") or not isinstance(record.get("tactics"), list):
            raise DataValidationError(f"{technique_id} needs a name and a tactics array.")
        indexed[technique_id] = dict(record)
    for technique_id, record in indexed.items():
        parent_id = record.get("parent_id")
        if record.get("is_subtechnique"):
            expected_parent = technique_id.split(".", 1)[0]
            if parent_id != expected_parent or parent_id not in indexed:
                raise DataValidationError(f"{technique_id} has an invalid or missing parent relationship.")
        elif parent_id is not None:
            raise DataValidationError(f"Parent technique must be null for parent technique {technique_id}.")
    return indexed


def validate_mapping(
    mapping: dict[str, Any],
    techniques: dict[str, dict[str, Any]],
    evidence_ids: set[str],
) -> None:
    if not isinstance(mapping.get("mapping_id"), str) or not mapping["mapping_id"].strip():
        raise DataValidationError("A mapping must have a non-empty mapping ID.")
    technique_id = mapping.get("technique_id")
    if not isinstance(technique_id, str) or technique_id not in techniques:
        raise DataValidationError(f"Unsupported technique ID: {technique_id!r}.")
    if not isinstance(mapping.get("status"), str) or mapping["status"] not in MAPPING_STATUSES:
        raise DataValidationError(f"Unsupported mapping status: {mapping.get('status')!r}.")
    if (
        not isinstance(mapping.get("confidence"), int)
        or isinstance(mapping["confidence"], bool)
        or not 0 <= mapping["confidence"] <= 100
    ):
        raise DataValidationError("Analyst confidence must be an integer from 0 to 100.")
    references = mapping.get("evidence_ids")
    if (
        not isinstance(references, list)
        or not references
        or any(not isinstance(item, str) or not item for item in references)
    ):
        raise DataValidationError("A mapping must retain at least one evidence reference.")
    for field in ("rationale", "alternative_explanations", "missing_evidence"):
        if not isinstance(mapping.get(field), str):
            raise DataValidationError(f"Mapping {field} must be text.")
    unknown = set(references) - evidence_ids
    if unknown:
        raise DataValidationError(f"Mapping references unknown evidence: {', '.join(sorted(unknown))}.")
    if mapping["status"] == "supported" and not str(mapping.get("rationale", "")).strip():
        raise DataValidationError("A rationale is required before a mapping can be marked supported.")


def validate_status_transition(old_status: str, new_status: str) -> None:
    if not isinstance(old_status, str) or not isinstance(new_status, str):
        raise DataValidationError("Mapping statuses must be text.")
    allowed = ALLOWED_STATUS_TRANSITIONS.get(old_status)
    if allowed is None or new_status not in allowed:
        raise DataValidationError(f"Status transition from {old_status!r} to {new_status!r} is not allowed.")


def validate_evidence_csv(content: str) -> list[dict[str, str]]:
    """Parse inert CSV text; never interpret or execute cell contents."""
    if len(content.encode("utf-8")) > 2_000_000:
        raise DataValidationError("CSV exceeds the 2 MB training-import limit.")
    required = {"evidence_id", "timestamp", "host_or_identity", "category", "description"}
    try:
        reader = csv.DictReader(io.StringIO(content))
        headers = set(reader.fieldnames or [])
        if not required.issubset(headers):
            missing = ", ".join(sorted(required - headers))
            raise DataValidationError(f"CSV is missing required columns: {missing}.")
        rows: list[dict[str, str]] = []
        seen: set[str] = set()
        for line_number, row in enumerate(reader, start=2):
            if not row or any(value is None for value in row.values()):
                raise DataValidationError(f"CSV row {line_number} has an invalid number of columns.")
            if not row["evidence_id"].strip() or row["evidence_id"] in seen:
                raise DataValidationError(f"CSV row {line_number} has a missing or duplicate evidence ID.")
            seen.add(row["evidence_id"])
            row["timestamp"] = _normalize_utc_timestamp(row["timestamp"], f"CSV row {line_number}")
            if any(not row[field].strip() for field in required):
                raise DataValidationError(f"CSV row {line_number} has an empty required value.")
            rows.append({key: value for key, value in row.items() if key is not None})
            if len(rows) > 500:
                raise DataValidationError("CSV exceeds the 500-record training-import limit.")
        return rows
    except csv.Error as exc:
        raise DataValidationError(f"CSV could not be parsed: {exc}") from exc


def validate_investigation_state(state: Any) -> dict[str, Any]:
    if not isinstance(state, dict):
        raise DataValidationError("Investigation state must be a JSON object.")
    allowed = {
        "mappings",
        "hypotheses",
        "recommendations",
        "event_notes",
        "additional_events",
    }
    if set(state) - allowed:
        raise DataValidationError("Investigation state contains unsupported fields.")
    for key in ("mappings", "hypotheses", "recommendations", "additional_events"):
        if key in state and not isinstance(state[key], list):
            raise DataValidationError(f"{key} must be an array.")
    if "event_notes" in state and not isinstance(state["event_notes"], dict):
        raise DataValidationError("event_notes must be an object.")
    for key in ("mappings", "hypotheses", "recommendations"):
        if key in state and any(not isinstance(item, dict) for item in state[key]):
            raise DataValidationError(f"Every {key} entry must be an object.")
    if "additional_events" in state:
        validate_event_records(state["additional_events"])
    if "hypotheses" in state:
        hypothesis_ids: set[str] = set()
        for item in state["hypotheses"]:
            hypothesis_id = item.get("hypothesis_id")
            if not isinstance(hypothesis_id, str) or not hypothesis_id or hypothesis_id in hypothesis_ids:
                raise DataValidationError("Snapshot hypothesis IDs must be non-empty and unique.")
            if not isinstance(item.get("question"), str) or not item["question"].strip():
                raise DataValidationError(f"{hypothesis_id} needs an investigation question.")
            if (
                not isinstance(item.get("confidence", 0), (int, float))
                or isinstance(item.get("confidence", 0), bool)
                or not 0 <= item.get("confidence", 0) <= 100
            ):
                raise DataValidationError(f"{hypothesis_id} confidence must be from 0 to 100.")
            if not isinstance(item.get("supporting_observations"), list) or any(
                not isinstance(reference, str) for reference in item["supporting_observations"]
            ):
                raise DataValidationError(f"{hypothesis_id} supporting observations must be an array of IDs.")
            if not isinstance(item.get("data_sources"), list) or any(
                not isinstance(source, str) for source in item["data_sources"]
            ):
                raise DataValidationError(f"{hypothesis_id} data sources must be an array of strings.")
            for field in ("contradicting_evidence", "procedure", "findings", "conclusion", "next_action"):
                if not isinstance(item.get(field), str):
                    raise DataValidationError(f"{hypothesis_id} {field} must be text.")
            hypothesis_ids.add(hypothesis_id)
    if "recommendations" in state:
        recommendation_ids: set[str] = set()
        for item in state["recommendations"]:
            recommendation_id = item.get("recommendation_id")
            if not isinstance(recommendation_id, str) or not recommendation_id or recommendation_id in recommendation_ids:
                raise DataValidationError("Snapshot recommendation IDs must be non-empty and unique.")
            for field in ("finding", "action", "purpose", "telemetry", "expected_outcome", "limitations", "reference"):
                if not isinstance(item.get(field), str):
                    raise DataValidationError(f"{recommendation_id} {field} must be text.")
            recommendation_ids.add(recommendation_id)
    for evidence_id, note in state.get("event_notes", {}).items():
        if not isinstance(evidence_id, str) or not isinstance(note, dict):
            raise DataValidationError("Every event_notes entry must map an evidence ID to an object.")
        if note.get("status", "unreviewed") not in {"unreviewed", "reviewed", "follow-up needed"}:
            raise DataValidationError(f"{evidence_id} has an unsupported review status.")
        for field in ("observation", "interpretation", "alternatives", "additional_evidence"):
            if field in note and not isinstance(note[field], str):
                raise DataValidationError(f"{evidence_id} note field {field} must be text.")
        if "related_events" in note and (
            not isinstance(note["related_events"], list)
            or any(not isinstance(reference, str) for reference in note["related_events"])
        ):
            raise DataValidationError(f"{evidence_id} related events must be an array of IDs.")
        if "confidence" in note and (
            not isinstance(note["confidence"], int) or not 0 <= note["confidence"] <= 100
        ):
            raise DataValidationError(f"{evidence_id} analyst confidence must be from 0 to 100.")
    return state
