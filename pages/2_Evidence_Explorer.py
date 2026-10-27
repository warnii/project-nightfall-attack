"""Search evidence and record analyst observations."""

import csv
import io

import pandas as pd
import streamlit as st

from src.data_loader import load_incident_events
from src.evidence_analysis import filter_evidence
from src.ui import all_events, initialize_session, page_header
from src.validation import DataValidationError, validate_evidence_csv

st.set_page_config(page_title="Evidence Explorer | Project Nightfall", page_icon="🔎", layout="wide")
initialize_session()
events = all_events(load_incident_events())
page_header("Evidence Explorer", "Search records, preserve the raw observation, and write your analysis separately.")

with st.expander("Import additional exercise evidence (optional)", expanded=False):
    st.caption("CSV is parsed as inert text only. Do not upload real logs, personal data, or sensitive records.")
    uploaded = st.file_uploader("Synthetic evidence CSV", type=["csv"], key="evidence_csv")
    attested = st.checkbox("I confirm this file contains synthetic training evidence only.")
    import_requested = st.button(
        "Validate and import synthetic evidence",
        disabled=uploaded is None or not attested,
        key="import_evidence_csv",
    )
    if uploaded is not None and attested and import_requested:
        try:
            rows = validate_evidence_csv(uploaded.getvalue().decode("utf-8-sig"))
            existing = {event["evidence_id"] for event in events}
            duplicate_ids = existing.intersection(row["evidence_id"] for row in rows)
            if duplicate_ids:
                raise DataValidationError(f"Evidence IDs already exist: {', '.join(sorted(duplicate_ids))}.")
            for row in rows:
                st.session_state.additional_events.append(
                    {
                        "evidence_id": row["evidence_id"],
                        "timestamp": row["timestamp"],
                        "host_or_identity": row["host_or_identity"],
                        "category": row["category"],
                        "description": row["description"],
                        "data_source": row.get("data_source", "Student-provided synthetic CSV"),
                        "observed_behaviour": row.get("observed_behaviour", row["description"]),
                        "potential_significance": row.get("potential_significance", "Not assessed."),
                        "confidence": 0.5,
                        "evidence_limitations": row.get("evidence_limitations", "Student-provided record."),
                        "related_events": [],
                        "synthetic": True,
                    }
                )
            st.success(f"Validated and added {len(rows)} synthetic records for this session.")
            st.rerun()
        except (UnicodeDecodeError, DataValidationError) as exc:
            st.error(f"CSV import rejected: {exc}")
    elif uploaded is not None:
        st.info("Confirm that the file contains synthetic training evidence before importing.")

query = st.text_input("Search evidence", placeholder="Search IDs, descriptions, source, host, or observed behaviour")
f1, f2, f3, f4 = st.columns(4)
categories = f1.multiselect("Category", sorted({item["category"] for item in events}))
hosts = f2.multiselect(
    "Host", sorted({item["host_or_identity"] for item in events if "@" not in item["host_or_identity"]})
)
identities = f3.multiselect(
    "Identity", sorted({item["host_or_identity"] for item in events if "@" in item["host_or_identity"]})
)
min_confidence = f4.slider("Minimum source confidence (%)", 0, 100, 0, 5)
review_statuses = st.multiselect("Review status", ["unreviewed", "reviewed", "follow-up needed"])
filtered = filter_evidence(
    events,
    search=query,
    categories=set(categories) if categories else None,
    hosts=set(hosts) if hosts else None,
    identities=set(identities) if identities else None,
    min_confidence=min_confidence / 100,
    statuses=set(review_statuses) if review_statuses else None,
    event_notes=st.session_state.event_notes,
)
evidence_table = pd.DataFrame(
    [
        {
            "Evidence ID": event["evidence_id"],
            "Timestamp (UTC)": event["timestamp"],
            "Host / identity": event["host_or_identity"],
            "Category": event["category"],
            "Observed behaviour": event["observed_behaviour"],
            "Review status": event.get("analyst_note", {}).get("status", "unreviewed"),
        }
        for event in filtered
    ],
    columns=[
        "Evidence ID",
        "Timestamp (UTC)",
        "Host / identity",
        "Category",
        "Observed behaviour",
        "Review status",
    ],
)
st.dataframe(
    evidence_table,
    width="stretch",
    hide_index=True,
)

csv_buffer = io.StringIO()
writer = csv.DictWriter(csv_buffer, fieldnames=[
    "evidence_id", "timestamp", "host_or_identity", "category", "description",
    "data_source", "observed_behaviour", "potential_significance", "confidence",
    "evidence_limitations", "related_events", "synthetic",
])
writer.writeheader()
for event in filtered:
    safe_row = {}
    for key in writer.fieldnames:
        value = event.get(key, "")
        if isinstance(value, list):
            value = ", ".join(value)
        text = str(value)
        safe_row[key] = f"'{text}" if text.startswith(("=", "+", "-", "@")) else text
    writer.writerow(safe_row)
st.download_button(
    "Download filtered evidence as CSV",
    csv_buffer.getvalue(),
    file_name="nightfall-filtered-evidence.csv",
    mime="text/csv",
)

if filtered:
    selected_id = st.selectbox("Inspect a complete evidence record", [item["evidence_id"] for item in filtered])
    event = next(item for item in filtered if item["evidence_id"] == selected_id)
    with st.expander(f"{event['evidence_id']} — complete source record", expanded=True):
        st.json(event)
    current_note = st.session_state.event_notes.get(selected_id, {})
    with st.form("evidence_analysis"):
        st.markdown("#### Analyst worksheet")
        observed = st.text_area("What was directly observed?", current_note.get("observation", event["observed_behaviour"]))
        interpretation = st.text_area("What might it indicate?", current_note.get("interpretation", ""))
        alternatives = st.text_area("Alternative explanations", current_note.get("alternatives", ""))
        additional = st.text_area("What additional evidence is needed?", current_note.get("additional_evidence", event["evidence_limitations"]))
        confidence = st.slider("Analyst confidence (custom)", 0, 100, int(current_note.get("confidence", 0)), 5)
        related = st.multiselect(
            "Potentially related records (relationship is not established)",
            [item["evidence_id"] for item in events if item["evidence_id"] != selected_id],
            default=current_note.get("related_events", event["related_events"]),
        )
        status = st.selectbox(
            "Review status",
            ["unreviewed", "reviewed", "follow-up needed"],
            index=["unreviewed", "reviewed", "follow-up needed"].index(current_note.get("status", "unreviewed")),
        )
        save = st.form_submit_button("Save analyst worksheet")
    if save:
        st.session_state.event_notes[selected_id] = {
            "observation": observed.strip(),
            "interpretation": interpretation.strip(),
            "alternatives": alternatives.strip(),
            "additional_evidence": additional.strip(),
            "confidence": confidence,
            "related_events": related,
            "status": status,
        }
        st.success(f"Saved notes for {selected_id} in this browser session.")
else:
    st.info("No evidence matches these filters.")
