import pytest

from src.validation import (
    DataValidationError,
    validate_evidence_csv,
    validate_investigation_state,
    validate_status_transition,
)


def test_csv_import_accepts_required_synthetic_fixture():
    rows = validate_evidence_csv(
        "evidence_id,timestamp,host_or_identity,category,description\n"
        "X-01,2025-01-01T12:00:00Z,host.example,Test,synthetic row\n"
    )
    assert rows[0]["evidence_id"] == "X-01"


@pytest.mark.parametrize(
    "content",
    [
        "event,host\nX-01,h1\n",
        "evidence_id,timestamp,host_or_identity,category,description\nX-01,bad,host,Test,row\n",
        "evidence_id,timestamp,host_or_identity,category,description\nX-01,2025-01-01T00:00:00Z,host,Test,row\nX-01,2025-01-02T00:00:00Z,host,Test,duplicate\n",
    ],
)
def test_csv_import_rejects_invalid_rows(content):
    with pytest.raises(DataValidationError):
        validate_evidence_csv(content)


def test_session_snapshot_schema_is_allowlisted():
    assert validate_investigation_state({"mappings": [], "event_notes": {}}) == {
        "mappings": [], "event_notes": {}
    }
    with pytest.raises(DataValidationError, match="unsupported fields"):
        validate_investigation_state({"arbitrary": []})
    with pytest.raises(DataValidationError, match="mappings must be an array"):
        validate_investigation_state({"mappings": {}})


def test_mapping_status_transition_rules():
    validate_status_transition("proposed", "supported")
    with pytest.raises(DataValidationError, match="not allowed"):
        validate_status_transition("rejected", "supported")
