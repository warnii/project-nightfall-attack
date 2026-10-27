"""Generate a cautious, evidence-first Markdown case report."""

from __future__ import annotations

from typing import Any


def _bullet(value: str) -> str:
    return str(value or "Not recorded.").replace("\n", " ").strip()


def generate_report(
    events: list[dict[str, Any]],
    mappings: list[dict[str, Any]],
    techniques: dict[str, dict[str, Any]],
    hypotheses: list[dict[str, Any]],
    recommendations: list[dict[str, Any]],
    provenance: dict[str, Any],
) -> str:
    lines = [
        "# Project Nightfall — Investigation Report",
        "",
        "> **SIMULATED TRAINING CASE.** All records and identities are synthetic. "
        "This report is not an operational incident assessment.",
        "",
        "## 1. Executive summary",
        "",
        f"Case: {provenance.get('case_id', 'NIGHTFALL-SIM-001')}. "
        f"{len(events)} synthetic evidence records were reviewed. "
        f"{len(mappings)} ATT&CK candidate mappings are recorded. "
        "No hypothesis is treated as confirmed solely because events are temporally adjacent.",
        "",
        "## 2. Incident scope",
        "",
        _bullet(provenance.get("summary", "Synthetic exercise evidence only.")),
        "",
        "## 3. Evidence timeline",
        "",
        "| Evidence | Timestamp (UTC) | Host / identity | Category | Direct observation |",
        "|---|---|---|---|---|",
    ]
    for event in sorted(events, key=lambda item: item["timestamp"]):
        lines.append(
            f"| {event['evidence_id']} | {event['timestamp']} | "
            f"{event['host_or_identity']} | {event['category']} | "
            f"{_bullet(event['observed_behaviour'])} |"
        )
    lines.extend(["", "## 4. Key observations", ""])
    for event in events:
        note = event.get("analyst_note", {})
        lines.append(
            f"- **{event['evidence_id']} — observed:** {_bullet(event['observed_behaviour'])} "
            f"**Analyst interpretation:** {_bullet(note.get('interpretation', 'Not recorded.'))} "
            f"**Confidence:** {note.get('confidence', 'Not recorded')}."
        )
    lines.extend(["", "## 5. Candidate ATT&CK mappings", ""])
    if mappings:
        for mapping in mappings:
            technique = techniques[mapping["technique_id"]]
            lines.extend(
                [
                    f"### {technique['technique_id']} — {technique['name']}",
                    "",
                    f"- Status: {mapping['status']}",
                    f"- Evidence: {', '.join(mapping['evidence_ids'])}",
                    f"- Analyst-assigned confidence: {mapping['confidence']}% "
                    "(custom assessment, not an official MITRE rating)",
                    f"- Rationale: {_bullet(mapping.get('rationale'))}",
                    f"- Alternatives: {_bullet(mapping.get('alternative_explanations'))}",
                    f"- Missing evidence: {_bullet(mapping.get('missing_evidence'))}",
                    "",
                ]
            )
    else:
        lines.extend(["No mappings have been recorded.", ""])
    lines.extend(["## 6. Confidence and unresolved questions", ""])
    for hypothesis in hypotheses:
        if not hypothesis.get("conclusion") or hypothesis.get("confidence", 0) < 100:
            lines.append(
                f"- **{hypothesis['hypothesis_id']} — {hypothesis['question']}** "
                f"Confidence: {hypothesis.get('confidence', 0)}%. "
                f"Next action: {_bullet(hypothesis.get('next_action'))}"
            )
    lines.extend(["", "## 7. Alternative explanations", ""])
    for event in events:
        if event.get("potential_significance"):
            lines.append(
                f"- **{event['evidence_id']}:** {_bullet(event['potential_significance'])}"
            )
    lines.extend(["", "## 8. Defensive recommendations", ""])
    if recommendations:
        for item in recommendations:
            lines.append(
                f"- **{_bullet(item.get('purpose'))}:** {_bullet(item.get('action'))} "
                f"Related finding: {_bullet(item.get('finding'))} "
                f"Limitations: {_bullet(item.get('limitations'))}"
            )
    else:
        lines.append("No defensive recommendations have been recorded.")
    lines.extend(
        [
            "",
            "## 9. Limitations",
            "",
            "- All evidence is synthetic and incomplete; no real systems were accessed.",
            "- Temporal proximity does not prove causation or a single activity chain.",
            "- The exercise catalogue is a curated subset, not the complete ATT&CK knowledge base.",
            "- Analyst confidence values are student-entered and are not MITRE classifications.",
            "",
            "## 10. Suggested next investigative steps",
            "",
        ]
    )
    for hypothesis in hypotheses:
        lines.append(f"- {hypothesis['hypothesis_id']}: {_bullet(hypothesis.get('next_action'))}")
    lines.extend(
        [
            "",
            "## 11. ATT&CK version and provenance",
            "",
            f"- ATT&CK Enterprise: {provenance.get('attack_version', '15.1')} "
            "(v15 release family)",
            f"- Catalogue source: {provenance.get('source_url', 'Official MITRE STIX release v15.1')}",
            f"- Retrieval date: {provenance.get('retrieved_date', '2026-10-27')}",
            "- Navigator layer format: 4.5.",
            "",
        ]
    )
    return "\n".join(lines)
