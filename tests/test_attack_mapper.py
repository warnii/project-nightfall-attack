import pytest

from src.attack_mapper import create_mapping, mappings_for_evidence, remove_mapping, update_mapping
from src.data_loader import load_technique_catalogue
from src.validation import DataValidationError


@pytest.fixture
def catalogue():
    return load_technique_catalogue()


def test_create_and_filter_mapping_preserves_evidence_reference(catalogue):
    mapping = create_mapping(
        "T1057", ["E-04"], "Process list observed.", "Routine inventory is possible.",
        "Need raw process IDs.", 55, "proposed", catalogue, {"E-04"},
    )
    assert mapping["evidence_ids"] == ["E-04"]
    assert mappings_for_evidence([mapping], "E-04") == [mapping]
    assert mappings_for_evidence([mapping], "E-01") == []


def test_supported_mapping_requires_rationale(catalogue):
    with pytest.raises(DataValidationError, match="rationale"):
        create_mapping(
            "T1057", ["E-04"], "", "", "", 50, "supported", catalogue, {"E-04"}
        )


def test_unknown_technique_and_evidence_are_rejected(catalogue):
    with pytest.raises(DataValidationError, match="Unsupported technique"):
        create_mapping("T9999", ["E-01"], "Reason", "", "", 50, "proposed", catalogue, {"E-01"})
    with pytest.raises(DataValidationError, match="unknown evidence"):
        create_mapping("T1566", ["E-404"], "Reason", "", "", 50, "proposed", catalogue, {"E-01"})


def test_update_status_and_reject_unsupported_transition(catalogue):
    mapping = create_mapping(
        "T1059.001", ["E-03"], "Interpreter process observed.", "Approved add-in possible.",
        "Need process arguments.", 45, "proposed", catalogue, {"E-03"},
    )
    updated = update_mapping(mapping, {"status": "supported"}, catalogue, {"E-03"})
    assert updated["status"] == "supported"
    with pytest.raises(DataValidationError, match="not allowed"):
        update_mapping(updated, {"status": "unknown"}, catalogue, {"E-03"})
    revised = update_mapping(updated, {"status": "proposed"}, catalogue, {"E-03"})
    assert revised["status"] == "proposed"

    rejected = update_mapping(revised, {"status": "rejected"}, catalogue, {"E-03"})
    with pytest.raises(DataValidationError, match="not allowed"):
        update_mapping(rejected, {"status": "supported"}, catalogue, {"E-03"})


def test_remove_mapping_requires_existing_id(catalogue):
    mapping = create_mapping(
        "T1057", ["E-04"], "Observed process names.", "", "", 30,
        "proposed", catalogue, {"E-04"},
    )
    assert remove_mapping([mapping], mapping["mapping_id"]) == []
    with pytest.raises(DataValidationError, match="does not exist"):
        remove_mapping([mapping], "missing")
