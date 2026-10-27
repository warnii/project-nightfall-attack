"""Build and validate ATT&CK Navigator layer-format 4.5 JSON."""

from __future__ import annotations

import json
from typing import Any

from src.validation import DataValidationError, validate_mapping

LAYER_FORMAT_VERSION = "4.5"
NAVIGATOR_MINIMUM_VERSION = "4.9.0"
STATUS_COLORS = {
    "proposed": "#F4C542",
    "supported": "#55A868",
    "rejected": "#9AA0A6",
    "needs further investigation": "#4C9BE8",
}


def build_navigator_layer(
    mappings: list[dict[str, Any]],
    techniques: dict[str, dict[str, Any]],
    evidence_ids: set[str],
    name: str = "Project Nightfall — student investigation",
) -> dict[str, Any]:
    entries: dict[tuple[str, str], dict[str, Any]] = {}
    for mapping in mappings:
        validate_mapping(mapping, techniques, evidence_ids)
        record = techniques[mapping["technique_id"]]
        comments = [
            f"Mapping status: {mapping['status']}.",
            f"Analyst-assigned confidence: {mapping['confidence']}% (not a MITRE classification).",
            f"Evidence: {', '.join(mapping['evidence_ids'])}.",
            f"Rationale: {mapping['rationale'] or 'Not supplied.'}",
            f"Alternative explanations: {mapping['alternative_explanations'] or 'Not recorded.'}",
            f"Missing evidence / open questions: {mapping['missing_evidence'] or 'Not recorded.'}",
        ]
        for tactic in record["tactics"]:
            key = (mapping["technique_id"], tactic)
            entry = entries.setdefault(
                key,
                {
                    "techniqueID": mapping["technique_id"],
                    "tactic": tactic,
                    "score": mapping["confidence"],
                    "color": STATUS_COLORS[mapping["status"]],
                    "comment": "",
                },
            )
            # Keep annotations for repeated mappings of the same technique+tactic.
            entry["score"] = max(entry["score"], mapping["confidence"])
            if entry["color"] != STATUS_COLORS[mapping["status"]]:
                entry["color"] = "#9B72CF"
            entry["comment"] += ("\n\n" if entry["comment"] else "") + "\n".join(comments)
    return {
        "name": name,
        "description": (
            "Synthetic Project Nightfall workshop investigation. Mapping states and confidence "
            "are student analysis, not confirmed activity or official MITRE classifications."
        ),
        "domain": "enterprise-attack",
        "versions": {
            "attack": "15.1",
            "navigator": NAVIGATOR_MINIMUM_VERSION,
            "layer": LAYER_FORMAT_VERSION,
        },
        "filters": {"platforms": ["Windows", "Office 365", "Azure AD"]},
        "sorting": 0,
        "hideDisabled": False,
        "techniques": list(entries.values()),
        "legendItems": [
            {"label": "Proposed", "color": STATUS_COLORS["proposed"]},
            {"label": "Supported (analyst assessment)", "color": STATUS_COLORS["supported"]},
            {"label": "Needs further investigation", "color": STATUS_COLORS["needs further investigation"]},
            {"label": "Rejected", "color": STATUS_COLORS["rejected"]},
            {"label": "Conflicting mapping states", "color": "#9B72CF"},
        ],
        "metadata": [
            {"name": "Case", "value": "NIGHTFALL-SIM-001 (synthetic)"},
            {"name": "ATT&CK provenance", "value": "Official MITRE Enterprise ATT&CK STIX v15.1"},
            {"name": "Export format", "value": "ATT&CK Navigator layer format 4.5"},
        ],
        "showID": True,
        "showName": True,
        "selectTechniquesAcrossTactics": True,
        "selectSubtechniquesWithParent": False,
        "selectVisibleTechniques": False,
    }


def validate_navigator_layer(
    layer: Any, techniques: dict[str, dict[str, Any]]
) -> None:
    if not isinstance(layer, dict):
        raise DataValidationError("Navigator layer must be a JSON object.")
    if not layer.get("name") or layer.get("domain") != "enterprise-attack":
        raise DataValidationError("Navigator layer needs a name and enterprise-attack domain.")
    versions = layer.get("versions")
    if not isinstance(versions, dict) or versions.get("attack") != "15.1":
        raise DataValidationError("Navigator layer must declare ATT&CK version 15.1.")
    if versions.get("layer") != LAYER_FORMAT_VERSION or not versions.get("navigator"):
        raise DataValidationError("Navigator layer version metadata is incomplete.")
    if not isinstance(layer.get("techniques"), list):
        raise DataValidationError("Navigator layer techniques must be an array.")
    for entry in layer["techniques"]:
        if not isinstance(entry, dict) or entry.get("techniqueID") not in techniques:
            raise DataValidationError("Navigator layer contains an unknown technique ID.")
        if entry.get("tactic") not in techniques[entry["techniqueID"]]["tactics"]:
            raise DataValidationError(f"Invalid tactic for {entry['techniqueID']}.")
        if not isinstance(entry.get("score"), (int, float)) or not 0 <= entry["score"] <= 100:
            raise DataValidationError("Navigator technique score must be between 0 and 100.")
        if not isinstance(entry.get("comment", ""), str):
            raise DataValidationError("Navigator technique comment must be text.")


def export_navigator_json(
    mappings: list[dict[str, Any]],
    techniques: dict[str, dict[str, Any]],
    evidence_ids: set[str],
) -> str:
    layer = build_navigator_layer(mappings, techniques, evidence_ids)
    validate_navigator_layer(layer, techniques)
    return json.dumps(layer, indent=2, ensure_ascii=False) + "\n"
