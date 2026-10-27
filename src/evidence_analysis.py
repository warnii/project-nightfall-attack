"""Evidence search, filtering, and analyst note helpers."""

from __future__ import annotations

from typing import Any, Iterable


def filter_evidence(
    events: Iterable[dict[str, Any]],
    search: str = "",
    categories: set[str] | None = None,
    hosts: set[str] | None = None,
    identities: set[str] | None = None,
    min_confidence: float = 0.0,
    start_date: str | None = None,
    end_date: str | None = None,
    statuses: set[str] | None = None,
    event_notes: dict[str, dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    needle = search.casefold().strip()
    result: list[dict[str, Any]] = []
    for event in events:
        note = (event_notes or {}).get(event["evidence_id"], {})
        searchable = " ".join(
            str(event.get(key, ""))
            for key in (
                "evidence_id",
                "host_or_identity",
                "category",
                "description",
                "data_source",
                "observed_behaviour",
                "potential_significance",
            )
        ).casefold()
        event_date = event["timestamp"][:10]
        if needle and needle not in searchable:
            continue
        if categories and event["category"] not in categories:
            continue
        if hosts or identities:
            entity = event["host_or_identity"]
            is_identity = "@" in entity
            selected = identities if is_identity else hosts
            if not selected or entity not in selected:
                continue
        if event["confidence"] < min_confidence:
            continue
        if start_date and event_date < start_date:
            continue
        if end_date and event_date > end_date:
            continue
        if statuses and note.get("status", "unreviewed") not in statuses:
            continue
        result.append({**event, "analyst_note": note})
    return sorted(result, key=lambda event: event["timestamp"])
