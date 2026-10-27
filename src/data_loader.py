"""Load and validate the small, offline-first synthetic exercise datasets."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from src.validation import (
    DataValidationError,
    validate_event_records,
    validate_technique_catalogue,
)

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def load_json(path: str | Path) -> Any:
    file_path = Path(path)
    try:
        with file_path.open("r", encoding="utf-8") as handle:
            return json.load(handle)
    except FileNotFoundError as exc:
        raise DataValidationError(f"Required data file was not found: {file_path.name}.") from exc
    except json.JSONDecodeError as exc:
        raise DataValidationError(
            f"{file_path.name} contains invalid JSON at line {exc.lineno}, column {exc.colno}."
        ) from exc


def load_incident_events(path: str | Path | None = None) -> list[dict[str, Any]]:
    data = load_json(path or DATA_DIR / "incident_events.json")
    if not isinstance(data, dict) or data.get("synthetic") is not True:
        raise DataValidationError("Incident data must be an object explicitly labelled synthetic.")
    return sorted(
        validate_event_records(data.get("events")),
        key=lambda event: event["timestamp"],
    )


def load_technique_catalogue(path: str | Path | None = None) -> dict[str, dict[str, Any]]:
    return validate_technique_catalogue(load_json(path or DATA_DIR / "attack_techniques.json"))


def load_hypotheses(path: str | Path | None = None) -> list[dict[str, Any]]:
    data = load_json(path or DATA_DIR / "investigation_hypotheses.json")
    hypotheses = data.get("hypotheses") if isinstance(data, dict) else None
    if not isinstance(hypotheses, list):
        raise DataValidationError("Investigation hypotheses must be a JSON array.")
    ids: set[str] = set()
    for item in hypotheses:
        if (
            not isinstance(item, dict)
            or not isinstance(item.get("hypothesis_id"), str)
            or not item["hypothesis_id"].strip()
            or not isinstance(item.get("question"), str)
            or not item["question"].strip()
        ):
            raise DataValidationError("Each hypothesis needs an ID and investigation question.")
        if item["hypothesis_id"] in ids:
            raise DataValidationError(f"Duplicate hypothesis ID: {item['hypothesis_id']}.")
        if not isinstance(item.get("confidence", 0), (int, float)) or not 0 <= item.get("confidence", 0) <= 100:
            raise DataValidationError(f"{item['hypothesis_id']} confidence must be from 0 to 100.")
        ids.add(item["hypothesis_id"])
    return hypotheses
