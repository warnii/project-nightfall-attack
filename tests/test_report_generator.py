from src.data_loader import load_incident_events, load_technique_catalogue
from src.report_generator import generate_report


def test_report_labels_case_simulated_and_does_not_infer_confirmation():
    report = generate_report(
        load_incident_events(),
        [],
        load_technique_catalogue(),
        [],
        [],
        {"case_id": "NIGHTFALL-SIM-001", "attack_version": "15.1"},
    )
    assert "SIMULATED TRAINING CASE" in report
    assert "No mappings have been recorded." in report
    assert "ATT&CK Enterprise: 15.1" in report
    assert "E-06" in report
