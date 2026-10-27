"""Document defensive recommendations and their evidence requirements."""

import streamlit as st

from src.ui import DEFAULT_RECOMMENDATIONS, initialize_session, page_header

st.set_page_config(page_title="Defensive Recommendations | Project Nightfall", page_icon="🛡️", layout="wide")
initialize_session()
page_header("Defensive Recommendations", "Translate findings into measured preventive, detective, or response actions.")
st.info(
    "ATT&CK describes adversary behaviour; MITRE D3FEND organises defensive countermeasure knowledge. "
    "A recommendation is not a guarantee of prevention and requires validation in context."
)
st.markdown("[MITRE D3FEND — official defensive knowledge base](https://d3fend.mitre.org/)")

for index, recommendation in enumerate(st.session_state.recommendations):
    with st.expander(f"{recommendation['recommendation_id']} · {recommendation['purpose']}"):
        with st.form(f"recommendation_{recommendation['recommendation_id']}"):
            finding = st.text_input("Related finding", recommendation["finding"])
            action = st.text_area("Proposed defensive action", recommendation["action"])
            purpose = st.selectbox(
                "Purpose",
                ["Preventive", "Detective", "Response", "Preventive / detective", "Detective / response"],
                index=[
                    "Preventive", "Detective", "Response", "Preventive / detective", "Detective / response"
                ].index(recommendation["purpose"]),
            )
            telemetry = st.text_area("Telemetry needed to evaluate effectiveness", recommendation["telemetry"])
            expected = st.text_area("Expected outcome", recommendation["expected_outcome"])
            limitations = st.text_area("Limitations and assumptions", recommendation["limitations"])
            reference = st.text_input("Authoritative reference URL", recommendation["reference"])
            save = st.form_submit_button("Save recommendation")
        if save:
            st.session_state.recommendations[index] = {
                **recommendation,
                "finding": finding.strip(),
                "action": action.strip(),
                "purpose": purpose,
                "telemetry": telemetry.strip(),
                "expected_outcome": expected.strip(),
                "limitations": limitations.strip(),
                "reference": reference.strip(),
            }
            st.success("Recommendation saved to the current session.")

st.markdown("### Recommendation design prompts")
st.markdown(
    """
    - Which observation does this recommendation address?
    - What telemetry would show whether it works?
    - What legitimate workflows could trigger the same signal?
    - What assumptions and residual risks remain?
    """
)
st.caption("The seeded recommendations cite the official D3FEND knowledge base without inventing technique identifiers.")
