import json

import pytest

from src.attack_mapper import create_mapping
from src.data_loader import load_technique_catalogue
from src.navigator_export import (
    build_navigator_layer,
    export_navigator_json,
    validate_navigator_layer,
)
from src.validation import DataValidationError


def test_layer_metadata_annotations_and_tactic_are_valid():
    catalogue = load_technique_catalogue()
    mapping = create_mapping(
        "T1059.001",
        ["E-03"],
        "Office application launched a PowerShell process.",
        "Approved add-in or administrative workflow.",
        "Need signer, process IDs, and script contents.",
        60,
        "needs further investigation",
        catalogue,
        {"E-03"},
    )
    result = export_navigator_json([mapping], catalogue, {"E-03"})
    layer = json.loads(result)
    assert layer["domain"] == "enterprise-attack"
    assert layer["versions"] == {"attack": "15.1", "navigator": "4.9.0", "layer": "4.5"}
    assert layer["techniques"][0]["techniqueID"] == "T1059.001"
    assert layer["techniques"][0]["tactic"] == "execution"
    assert "E-03" in layer["techniques"][0]["comment"]
    assert "needs further investigation" in layer["techniques"][0]["comment"]
    assert "60%" in layer["techniques"][0]["comment"]
    validate_navigator_layer(layer, catalogue)


def test_empty_investigation_exports_valid_empty_layer():
    catalogue = load_technique_catalogue()
    layer = build_navigator_layer([], catalogue, set())
    validate_navigator_layer(layer, catalogue)
    assert layer["techniques"] == []


def test_invalid_technique_and_invalid_layer_are_rejected():
    catalogue = load_technique_catalogue()
    with pytest.raises(DataValidationError, match="Unsupported technique"):
        export_navigator_json(
            [
                {
                    "mapping_id": "test-mapping",
                    "technique_id": "T0000",
                    "status": "proposed",
                    "confidence": 1,
                    "evidence_ids": ["E-1"],
                    "rationale": "Test fixture",
                    "alternative_explanations": "",
                    "missing_evidence": "",
                }
            ],
            catalogue,
            {"E-1"},
        )
    layer = build_navigator_layer([], catalogue, set())
    layer["versions"]["attack"] = "latest"
    with pytest.raises(DataValidationError, match="15.1"):
        validate_navigator_layer(layer, catalogue)


def test_annotations_survive_multiple_mapping_export():
    catalogue = load_technique_catalogue()
    mapping1 = create_mapping(
        "T1078", ["E-02"], "Unfamiliar successful sign-in.", "Employee travel is possible.",
        "Need MFA and device context.", 30, "proposed", catalogue, {"E-02"},
    )
    mapping2 = create_mapping(
        "T1078", ["E-08"], "Later familiar sign-in is a comparison point.", "Concurrent sessions possible.",
        "Need session identifiers.", 20, "needs further investigation", catalogue, {"E-08"},
    )
    layer = json.loads(export_navigator_json([mapping1, mapping2], catalogue, {"E-02", "E-08"}))
    comments = layer["techniques"][0]["comment"]
    assert "E-02" in comments and "E-08" in comments
    assert "Alternative explanations" in comments
