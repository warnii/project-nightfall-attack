import json

import pytest

from src.data_loader import load_incident_events, load_technique_catalogue
from src.validation import DataValidationError


def test_loads_synthetic_events_in_chronological_order():
    events = load_incident_events()
    assert len(events) >= 6
    assert all(event["synthetic"] is True for event in events)
    assert [event["timestamp"] for event in events] == sorted(
        event["timestamp"] for event in events
    )
    assert [event["evidence_id"] for event in events[:6]] == [
        "E-10", "E-01", "E-02", "E-03", "E-04", "E-07"
    ]


def test_rejects_missing_required_field(tmp_path):
    source = tmp_path / "events.json"
    source.write_text(json.dumps({"synthetic": True, "events": [{"evidence_id": "E-1"}]}), encoding="utf-8")
    with pytest.raises(DataValidationError, match="missing"):
        load_incident_events(source)


def test_rejects_malformed_json(tmp_path):
    source = tmp_path / "events.json"
    source.write_text("{", encoding="utf-8")
    with pytest.raises(DataValidationError, match="invalid JSON"):
        load_incident_events(source)


def test_rejects_unlabelled_or_unknown_related_evidence(tmp_path):
    source = tmp_path / "events.json"
    source.write_text(
        json.dumps(
            {
                "synthetic": True,
                "events": [
                    {
                        "evidence_id": "E-1",
                        "timestamp": "2025-01-01T10:00:00Z",
                        "host_or_identity": "unit.test",
                        "category": "Test",
                        "description": "Synthetic record",
                        "data_source": "Fixture",
                        "observed_behaviour": "Observed",
                        "potential_significance": "Unknown",
                        "confidence": 0.5,
                        "evidence_limitations": "Fixture only",
                        "related_events": ["E-missing"],
                        "synthetic": True,
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    with pytest.raises(DataValidationError, match="unknown evidence"):
        load_incident_events(source)


def test_catalogue_is_pinned_and_subtechnique_relationships_are_valid():
    catalogue = load_technique_catalogue()
    assert catalogue["T1059.001"]["parent_id"] == "T1059"
    assert catalogue["T1518.001"]["parent_id"] == "T1518"
    assert catalogue["T1566"]["name"] == "Phishing"
