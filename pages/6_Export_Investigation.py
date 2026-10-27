"""Export an annotated Navigator layer, report, evidence, and session snapshot."""

import json

import streamlit as st

from src.data_loader import DATA_DIR, load_incident_events, load_json, load_technique_catalogue
from src.navigator_export import export_navigator_json
from src.report_generator import generate_report
from src.ui import all_events, initialize_session, page_header
from src.validation import DataValidationError, validate_investigation_state, validate_mapping

st.set_page_config(page_title="Export Investigation | Project Nightfall", page_icon="📄", layout="wide")
initialize_session()
events = all_events(load_incident_events())
techniques = load_technique_catalogue()
evidence_ids = {item["evidence_id"] for item in events}
page_header("Export Investigation", "Download portable outputs and preserve your work. Exports contain only this synthetic exercise and your notes.")

st.markdown("### ATT&CK Navigator layer")
st.write(
    "The JSON follows MITRE ATT&CK Navigator **layer format 4.5**, declares the "
    "**Enterprise ATT&CK 15.1** release, uses supported technique annotations, and is "
    "validated locally before download."
)
try:
    layer_json = export_navigator_json(st.session_state.mappings, techniques, evidence_ids)
    st.success(f"Navigator layer validated · {len(st.session_state.mappings)} mapping(s).")
    st.download_button(
        "Download Navigator JSON",
        layer_json,
        file_name="project-nightfall-navigator-layer.json",
        mime="application/json",
    )
except DataValidationError as exc:
    st.error(f"Navigator export is blocked until mapping data is corrected: {exc}")

with st.expander("Import a saved investigation snapshot"):
    st.caption("This import accepts the application's session-snapshot format. It is parsed as JSON and never executed.")
    snapshot = st.file_uploader("Investigation snapshot JSON", type=["json"], key="snapshot_upload")
    if snapshot is not None and st.button("Validate and load snapshot", key="load_snapshot"):
        try:
            snapshot_bytes = snapshot.getvalue()
            if len(snapshot_bytes) > 2_000_000:
                raise DataValidationError("Snapshot exceeds the 2 MB import limit.")
            state = validate_investigation_state(json.loads(snapshot_bytes.decode("utf-8")))
            imported_events = state.get("additional_events", [])
            imported_ids = {item["evidence_id"] for item in imported_events}
            duplicate_ids = imported_ids.intersection(
                item["evidence_id"] for item in load_incident_events()
            )
            if duplicate_ids:
                raise DataValidationError(
                    f"Snapshot evidence IDs already exist in the case: {', '.join(sorted(duplicate_ids))}."
                )
            all_evidence_ids = evidence_ids | imported_ids
            candidate_mappings = state.get("mappings", [])
            if not isinstance(candidate_mappings, list):
                raise DataValidationError("Snapshot mappings must be an array.")
            for mapping in candidate_mappings:
                validate_mapping(mapping, techniques, all_evidence_ids)
            mapping_ids = [item["mapping_id"] for item in candidate_mappings]
            if len(set(mapping_ids)) != len(mapping_ids):
                raise DataValidationError("Snapshot mapping IDs must be unique.")
            for hypothesis in state.get("hypotheses", []):
                missing = set(hypothesis["supporting_observations"]) - all_evidence_ids
                if missing:
                    raise DataValidationError(
                        f"{hypothesis['hypothesis_id']} references unknown evidence: {', '.join(sorted(missing))}."
                    )
            if set(state.get("event_notes", {})) - all_evidence_ids:
                raise DataValidationError("Snapshot notes reference evidence IDs not present in the case.")
            for key, value in state.items():
                st.session_state[key] = value
            st.success("Snapshot validated and loaded for this session.")
            st.rerun()
        except (UnicodeDecodeError, json.JSONDecodeError, RecursionError, DataValidationError) as exc:
            st.error(f"Snapshot was rejected: {exc}")

state = {
    "mappings": st.session_state.mappings,
    "hypotheses": st.session_state.hypotheses,
    "recommendations": st.session_state.recommendations,
    "event_notes": st.session_state.event_notes,
    "additional_events": st.session_state.additional_events,
}
st.download_button(
    "Download investigation session snapshot",
    json.dumps(state, indent=2, ensure_ascii=False),
    file_name="project-nightfall-investigation-state.json",
    mime="application/json",
)

incident = load_json(DATA_DIR / "incident_events.json")
catalogue_metadata = load_json(DATA_DIR / "attack_techniques.json")
report = generate_report(
    events,
    st.session_state.mappings,
    techniques,
    st.session_state.hypotheses,
    st.session_state.recommendations,
    {
        "case_id": incident["case_id"],
        "summary": incident["summary"],
        "attack_version": catalogue_metadata["attack_version"],
        "source_url": catalogue_metadata["source_url"],
        "retrieved_date": catalogue_metadata["retrieved_date"],
    },
)
st.markdown("### Investigation report")
st.download_button(
    "Download Markdown investigation report",
    report,
    file_name="project-nightfall-investigation-report.md",
    mime="text/markdown",
)
with st.expander("Preview report"):
    st.markdown(report)

st.markdown("### Import your layer into ATT&CK Navigator")
st.markdown(
    """
    1. Open [ATT&CK Navigator](https://mitre-attack.github.io/attack-navigator/).
    2. Choose **Open Existing Layer** and **Upload from local**, then select the downloaded JSON.
    3. Check the layer's version metadata: ATT&CK **15.1**, domain **enterprise-attack**, layer format **4.5**.
    4. The Navigator must have the Enterprise ATT&CK 15.1 matrix available to display this layer. If your deployed Navigator does not offer that release, choose the v15.1 Enterprise matrix in its version selector first.
    5. To reopen saved work later, use **Open Existing Layer → Upload from local** and select the same JSON file. The file preserves the layer annotations; session notes and hypotheses are in the separate investigation snapshot.

    An empty investigation still exports a valid empty layer. A candidate mapping is not a finding of confirmed adversary activity.
    """
)
