"""Hypothesis-driven hunting worksheet and progressive challenges."""

import streamlit as st

from src.data_loader import load_incident_events
from src.ui import all_events, initialize_session, page_header

st.set_page_config(page_title="Threat Hunting | Project Nightfall", page_icon="🧪", layout="wide")
initialize_session()
events = all_events(load_incident_events())
page_header("Threat Hunting", "Turn questions into testable hypotheses. The exercise does not query any real SIEM or enterprise system.")

tab_hunt, tab_challenges = st.tabs(["Investigation worksheet", "Progressive student challenges"])
with tab_hunt:
    hypotheses = st.session_state.hypotheses
    selected_id = st.selectbox(
        "Guided investigation question",
        [item["hypothesis_id"] for item in hypotheses],
        format_func=lambda value: next(
            f"{item['hypothesis_id']} — {item['question']}" for item in hypotheses if item["hypothesis_id"] == value
        ),
    )
    index = next(i for i, item in enumerate(hypotheses) if item["hypothesis_id"] == selected_id)
    hypothesis = hypotheses[index]
    st.write(f"**Supporting observations:** {', '.join(hypothesis['supporting_observations'])}")
    st.write(f"**Evidence that would contradict this hypothesis:** {hypothesis['contradicting_evidence']}")
    st.write(f"**Data sources to inspect:** {', '.join(hypothesis['data_sources'])}")
    st.info(f"**Synthetic search / analysis procedure:** {hypothesis['procedure']}")
    with st.form(f"hypothesis_{selected_id}"):
        findings = st.text_area("Findings (what the available records show)", hypothesis.get("findings", ""))
        conclusion = st.text_area("Conclusion (state what remains unproven)", hypothesis.get("conclusion", ""))
        confidence = st.slider("Analyst confidence (custom)", 0, 100, int(hypothesis.get("confidence", 0)), 5)
        next_action = st.text_area("Next investigative action", hypothesis.get("next_action", ""))
        save = st.form_submit_button("Save hypothesis worksheet")
    if save:
        hypothesis.update(
            {
                "findings": findings.strip(),
                "conclusion": conclusion.strip(),
                "confidence": confidence,
                "next_action": next_action.strip(),
            }
        )
        st.session_state.hypotheses[index] = hypothesis
        st.success("Worksheet saved to the current session.")
    st.caption("Available synthetic records: " + ", ".join(item["evidence_id"] for item in events))

with tab_challenges:
    step = st.session_state.challenge_step
    challenge_ready = True
    st.progress(step / 5, text=f"Challenge {step} of 5")
    challenges = {
        1: "Evidence or assumption?",
        2: "Find an ATT&CK mapping",
        3: "Identify the missing evidence",
        4: "Build the investigation map",
        5: "Defend your conclusion",
    }
    st.subheader(challenges[step])
    if step == 1:
        choice = st.radio(
            "Statement: “The employee was phished because an unexpected document email was received.”",
            ["Observed evidence", "Hypothesis", "Unsupported conclusion"],
        )
        submit_label = "Check classification"
    elif step == 2:
        choice = st.radio(
            "E-03 reports an office application spawning PowerShell, but omits command content. Which is the most defensible mapping now?",
            ["T1059.001 PowerShell — proposed candidate, pending context", "T1566 Phishing — confirmed", "T1041 Exfiltration Over C2 Channel — confirmed"],
        )
        submit_label = "Check mapping choice"
    elif step == 3:
        choice = st.radio(
            "To determine what initiated E-06 and whether it involved organisational data, which evidence is most useful?",
            [
                "Process-to-connection attribution plus proxy/DLP or content metadata",
                "A longer list of nearby timestamps only",
                "Assume the transfer was malicious based on its size",
            ],
        )
        submit_label = "Check evidence choice"
    elif step == 4:
        valid = [
            item for item in st.session_state.mappings
            if item.get("status") != "rejected"
            and item.get("rationale", "").strip()
            and item.get("evidence_ids")
        ]
        st.write(f"Your investigation currently has **{len(valid)}** non-rejected mapping(s) with rationale and evidence references.")
        challenge_ready = bool(valid)
        if not challenge_ready:
            st.warning("Add at least one evidence-linked mapping with rationale before completing this challenge.")
            st.page_link("pages/3_ATT&CK_Mapping.py", label="Open ATT&CK Mapping →")
        choice = st.radio(
            "Does the layer show a confirmed chronological attack sequence?",
            ["No. It groups analyst candidates by tactic; adjacency is not causality.", "Yes. ATT&CK tactic order proves the sequence."],
        )
        submit_label = "Review map challenge"
    else:
        choice = st.text_area(
            "In your own words, state one observation, one hypothesis, one unresolved issue, and one next action."
        )
        submit_label = "Submit conclusion"

    already_answered = step in st.session_state.challenge_answers
    if not already_answered and st.button(
        submit_label,
        key=f"challenge_submit_{step}",
        disabled=not challenge_ready,
    ):
        if step == 5 and len(choice.strip()) < 40:
            st.warning("Add a little more detail so you can distinguish evidence, inference, and next steps.")
        else:
            st.session_state.challenge_answers[step] = choice
            st.rerun()
    if already_answered:
        correct = True
        if step == 1:
            correct = st.session_state.challenge_answers[step] == "Unsupported conclusion"
            explanation = "The email receipt is observed. That it was phishing and caused later activity is not established."
        elif step == 2:
            correct = st.session_state.challenge_answers[step].startswith("T1059.001")
            explanation = "PowerShell execution is observed. A mapping can be proposed, but intent and script purpose need corroboration."
        elif step == 3:
            correct = st.session_state.challenge_answers[step].startswith("Process-to-connection")
            explanation = "Attribution and content/business context are needed; transfer volume alone cannot establish exfiltration."
        elif step == 4:
            correct = st.session_state.challenge_answers[step].startswith("No.")
            explanation = "Navigator tactic grouping is a matrix visualization. It does not encode verified event order or causality."
        else:
            answer = st.session_state.challenge_answers[step].casefold()
            criteria = ["observ", "hypoth", "unresolv", "next"]
            correct = all(term in answer for term in criteria)
            explanation = "A defensible conclusion labels observations, hypotheses, unknowns, and next actions separately. Review your response against that rubric."
        if correct:
            st.success("Good reasoning.")
        else:
            st.info("Revisit the evidence and try this reasoning again in your worksheet.")
        st.write(explanation)
        if not correct:
            if st.button("Try this challenge again", key=f"challenge_retry_{step}"):
                del st.session_state.challenge_answers[step]
                st.rerun()
        elif step < 5:
            if st.button("Continue to next challenge", key=f"challenge_next_{step}"):
                st.session_state.challenge_step += 1
                st.rerun()
        else:
            st.caption("You completed the five-step challenge sequence. Revisit the map and report to refine your work.")
