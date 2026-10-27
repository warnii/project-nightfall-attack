from src.data_loader import load_incident_events
from src.evidence_analysis import filter_evidence


def test_search_category_host_identity_and_confidence_filters():
    events = load_incident_events()
    endpoint = filter_evidence(events, search="powershell", categories={"Endpoint"})
    assert [event["evidence_id"] for event in endpoint] == ["E-03"]

    host_records = filter_evidence(events, hosts={"NSC-LT-042"})
    assert host_records
    assert all(event["host_or_identity"] == "NSC-LT-042" for event in host_records)

    identity_records = filter_evidence(
        events, identities={"avery.quill@northstar.example"}, min_confidence=0.9
    )
    assert identity_records
    assert all(
        event["host_or_identity"] == "avery.quill@northstar.example"
        and event["confidence"] >= 0.9
        for event in identity_records
    )


def test_time_status_and_empty_search_results():
    events = load_incident_events()
    filtered = filter_evidence(
        events,
        start_date="2025-04-15",
        end_date="2025-04-15",
        statuses={"follow-up needed"},
        event_notes={"E-06": {"status": "follow-up needed"}},
    )
    assert [event["evidence_id"] for event in filtered] == ["E-06"]
    assert filter_evidence(events, search="no such synthetic event") == []
