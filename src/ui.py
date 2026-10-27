"""Shared Streamlit session-state and presentation helpers."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

import streamlit as st

from src.data_loader import load_hypotheses


DEFAULT_RECOMMENDATIONS = [
    {
        "recommendation_id": "R-01",
        "finding": "E-02: unfamiliar successful sign-in (unconfirmed)",
        "action": "Review sign-in context and strengthen risk-based MFA and session controls where appropriate.",
        "purpose": "Preventive / detective",
        "telemetry": "MFA outcomes, device posture, session identifiers, identity risk events",
        "expected_outcome": "Improve the ability to distinguish expected access from anomalous sessions.",
        "limitations": "MFA does not by itself establish the legitimacy of every session; validate user and device context.",
        "reference": "https://d3fend.mitre.org/",
    },
    {
        "recommendation_id": "R-02",
        "finding": "E-03 and E-04: office-to-interpreter process chain and discovery observations",
        "action": "Collect and alert on office-application child-process relationships; validate approved add-ins and management tools.",
        "purpose": "Detective",
        "telemetry": "Endpoint process creation, signer, image path, user, parent and child process IDs",
        "expected_outcome": "Provide sufficient context to triage unusual process ancestry and reduce false positives.",
        "limitations": "A process relationship is a signal, not proof; legitimate workflows can create similar events.",
        "reference": "https://d3fend.mitre.org/",
    },
    {
        "recommendation_id": "R-03",
        "finding": "E-05 and E-06: unusual document access and outbound transfer alert",
        "action": "Correlate document audit, proxy, DNS, endpoint network attribution, and data-loss-prevention telemetry.",
        "purpose": "Detective / response",
        "telemetry": "Document access and download events, destination metadata, process-to-connection data, DLP findings",
        "expected_outcome": "Establish whether the transfer had an approved business purpose and what data category was involved.",
        "limitations": "Volume or timing alone cannot establish data exfiltration; content may remain unavailable.",
        "reference": "https://d3fend.mitre.org/",
    },
]


def initialize_session() -> None:
    if "mappings" not in st.session_state:
        st.session_state.mappings = []
    if "event_notes" not in st.session_state:
        st.session_state.event_notes = {}
    if "hypotheses" not in st.session_state:
        st.session_state.hypotheses = deepcopy(load_hypotheses())
    if "recommendations" not in st.session_state:
        st.session_state.recommendations = deepcopy(DEFAULT_RECOMMENDATIONS)
    if "challenge_step" not in st.session_state:
        st.session_state.challenge_step = 1
    if "challenge_answers" not in st.session_state:
        st.session_state.challenge_answers = {}
    if "additional_events" not in st.session_state:
        st.session_state.additional_events = []


def page_header(title: str, subtitle: str) -> None:
    st.markdown(f'<div class="eyebrow">PROJECT NIGHTFALL · TRAINING LAB</div>', unsafe_allow_html=True)
    st.title(title)
    st.caption(subtitle)
    st.warning(
        "SIMULATED EVIDENCE ONLY — This learning exercise is not connected to real systems. "
        "Suspicious does not mean confirmed malicious.",
        icon="⚠️",
    )


def all_events(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    extras = st.session_state.get("additional_events", [])
    return sorted([*events, *extras], key=lambda item: item["timestamp"])
