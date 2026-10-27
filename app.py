"""Project Nightfall Streamlit entry point."""

from __future__ import annotations

import streamlit as st

from src.data_loader import load_incident_events, load_technique_catalogue
from src.timeline import create_timeline
from src.ui import all_events, initialize_session

st.set_page_config(
    page_title="Project Nightfall — Investigation Lab",
    page_icon="🌙",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    :root { --nightfall-ink: #17233c; --nightfall-blue: #2f6fed; }
    .stApp { background: linear-gradient(180deg, #f7f9fd 0%, #ffffff 40%); }
    .block-container { max-width: 1440px; padding-top: 2rem; }
    .eyebrow { color: #4263a0; font-size: .75rem; font-weight: 700; letter-spacing: .16em; }
    [data-testid="stMetric"] { background: #fff; padding: 1rem; border: 1px solid #e7ebf3; border-radius: 12px; }
    div[data-testid="stAlert"] { border-radius: 10px; }
    </style>
    """,
    unsafe_allow_html=True,
)

try:
    source_events = load_incident_events()
    techniques = load_technique_catalogue()
except (OSError, ValueError) as exc:
    st.error(f"Could not load the validated exercise data: {exc}")
    st.stop()

initialize_session()
events = all_events(source_events)

st.markdown('<div class="eyebrow">INVESTIGATE THE EVIDENCE · MAP THE BEHAVIOUR · DEFEND THE ORGANISATION</div>', unsafe_allow_html=True)
st.title("Project Nightfall")
st.subheader("Threat Hunting & ATT&CK Investigation Lab")
st.write(
    "A hands-on, hypothesis-driven investigation of a **fictional** corporate case. "
    "Separate what the records show from what you infer, map only defensible candidate behaviour, "
    "and document what remains unknown."
)
st.warning(
    "TRAINING CASE — Every identity, host, event, and network address is synthetic. "
    "The application never connects to enterprise systems or executes content from evidence.",
    icon="⚠️",
)

open_questions = sum(
    1 for item in st.session_state.hypotheses if not str(item.get("conclusion", "")).strip()
)
metrics = st.columns(4)
metrics[0].metric("Case status", "Investigation open")
metrics[1].metric("Evidence records", len(events))
metrics[2].metric("Candidate mappings", len(st.session_state.mappings))
metrics[3].metric("Unresolved questions", open_questions)

st.markdown("### Incident overview")
st.markdown(
    """
    An unexpected document-review email is followed by an unfamiliar successful sign-in,
    an office-application child process, system-inventory observations, unusual document
    access, and an outbound-transfer alert. Additional baseline and ambiguous evidence
    is included. **The records do not establish that the events share a cause.**
    """
)

left, right = st.columns([1.7, 1])
with left:
    st.plotly_chart(create_timeline(events), width="stretch")
with right:
    st.markdown("#### Investigation guardrails")
    st.info("Email received ≠ phishing confirmed.")
    st.info("Unfamiliar sign-in ≠ account compromise confirmed.")
    st.info("Outbound alert ≠ data exfiltration confirmed.")
    st.markdown(
        f"**ATT&CK scope:** Enterprise v15.1 (v15 release family)  \n"
        f"**Local catalogue:** {len(techniques)} selected techniques  \n"
        "**Navigator layer format:** 4.5"
    )

st.markdown("### Start the investigation")
nav = st.columns(3)
nav[0].page_link("pages/1_Incident_Timeline.py", label="Review the timeline", icon="🕒")
nav[1].page_link("pages/2_Evidence_Explorer.py", label="Explore evidence", icon="🔎")
nav[2].page_link("pages/3_ATT&CK_Mapping.py", label="Build candidate mappings", icon="🧭")
nav = st.columns(3)
nav[0].page_link("pages/4_Threat_Hunting.py", label="Test hypotheses & challenges", icon="🧪")
nav[1].page_link("pages/5_Defensive_Recommendations.py", label="Consider defenses", icon="🛡️")
nav[2].page_link("pages/6_Export_Investigation.py", label="Export your work", icon="📄")
with st.sidebar:
    st.markdown("## Case workspace")
    st.caption("NIGHTFALL-SIM-001 · synthetic · offline")
    st.progress(min(1.0, len(st.session_state.mappings) / 5), text="Investigation progress (indicative)")
    st.caption("Progress is a learning aid, not an incident severity score.")
