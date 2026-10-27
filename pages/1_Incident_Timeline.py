"""Filter and inspect the synthetic event timeline."""

import streamlit as st

from src.data_loader import load_incident_events
from src.evidence_analysis import filter_evidence
from src.timeline import create_timeline
from src.ui import all_events, initialize_session, page_header

st.set_page_config(page_title="Incident Timeline | Project Nightfall", page_icon="🕒", layout="wide")
initialize_session()
events = all_events(load_incident_events())
page_header("Incident Timeline", "Filter the event sequence while keeping timestamps, observations, and assumptions distinct.")

with st.expander("Timeline filters", expanded=True):
    a, b, c = st.columns(3)
    categories = a.multiselect("Evidence category", sorted({item["category"] for item in events}))
    hosts = sorted({item["host_or_identity"] for item in events if "@" not in item["host_or_identity"]})
    identities = sorted({item["host_or_identity"] for item in events if "@" in item["host_or_identity"]})
    selected_hosts = b.multiselect("Host", hosts)
    selected_identities = c.multiselect("Identity", identities)
    min_confidence = st.slider("Minimum source confidence (%)", 0, 100, 0, 5)
    dates = sorted({item["timestamp"][:10] for item in events})
    d, e = st.columns(2)
    start = d.selectbox("From date", dates, index=0)
    end = e.selectbox("Through date", dates, index=len(dates) - 1)
    statuses = st.multiselect("Analyst review status", ["unreviewed", "reviewed", "follow-up needed"])

filtered = filter_evidence(
    events,
    categories=set(categories) if categories else None,
    hosts=set(selected_hosts) if selected_hosts else None,
    identities=set(selected_identities) if selected_identities else None,
    min_confidence=min_confidence / 100,
    start_date=start,
    end_date=end,
    statuses=set(statuses) if statuses else None,
    event_notes=st.session_state.event_notes,
)
st.metric("Matching evidence records", len(filtered))
st.plotly_chart(create_timeline(filtered), width="stretch")
st.dataframe(
    [
        {
            "Evidence ID": item["evidence_id"],
            "Timestamp (UTC)": item["timestamp"],
            "Host / identity": item["host_or_identity"],
            "Category": item["category"],
            "Observed behaviour": item["observed_behaviour"],
            "Source confidence": f"{item['confidence']:.0%}",
            "Review status": item.get("analyst_note", {}).get("status", "unreviewed"),
        }
        for item in filtered
    ],
    width="stretch",
    hide_index=True,
)
st.caption("Source confidence describes the exercise record's reported reliability; it is not analyst confidence in a hypothesis.")
st.page_link("pages/2_Evidence_Explorer.py", label="Open the evidence explorer →")
