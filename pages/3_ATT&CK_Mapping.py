"""Create, inspect, and visualize evidence-linked ATT&CK candidates."""

import plotly.express as px
import streamlit as st

from src.attack_mapper import create_mapping, mappings_for_evidence, remove_mapping, update_mapping
from src.data_loader import load_incident_events, load_technique_catalogue
from src.ui import all_events, initialize_session, page_header
from src.validation import DataValidationError

st.set_page_config(page_title="ATT&CK Mapping | Project Nightfall", page_icon="🧭", layout="wide")
initialize_session()
events = all_events(load_incident_events())
techniques = load_technique_catalogue()
evidence_ids = {event["evidence_id"] for event in events}
page_header("ATT&CK Mapping", "Build candidate mappings from evidence. A technique is an analyst interpretation, not a verdict.")

st.caption("Catalogue: official Enterprise ATT&CK v15.1 release subset. Search by technique ID or name; filter by tactic.")
tactics = sorted({tactic for item in techniques.values() for tactic in item["tactics"]})
c1, c2, c3 = st.columns([1, 1, 1.5])
selected_event_id = c1.selectbox("Evidence record", sorted(evidence_ids))
query = c2.text_input("Search technique", placeholder="T1057 or process discovery")
selected_tactics = c3.multiselect("Filter by tactic", tactics)
matches = [
    item for item in techniques.values()
    if (not query or query.casefold() in item["technique_id"].casefold() or query.casefold() in item["name"].casefold())
    and (not selected_tactics or set(item["tactics"]).intersection(selected_tactics))
]
technique_ids = [item["technique_id"] for item in matches]
if not technique_ids:
    st.info("No catalogue entries match the search. This exercise catalogue is intentionally limited.")
else:
    technique_id = st.selectbox(
        "Candidate technique",
        technique_ids,
        format_func=lambda value: f"{value} — {techniques[value]['name']}",
    )
    technique = techniques[technique_id]
    st.markdown(f"### {technique['name']} · `{technique_id}`")
    st.write(technique["description"])
    st.caption(
        f"Tactic(s): {', '.join(technique['tactics'])} · "
        f"{'Sub-technique of ' + str(technique['parent_id']) if technique['is_subtechnique'] else 'Technique'} · "
        f"[Official ATT&CK reference]({technique['url']})"
    )
    related = mappings_for_evidence(st.session_state.mappings, selected_event_id)
    with st.form("new_mapping"):
        linked_evidence = st.multiselect(
            "Evidence supporting or contextualising this candidate",
            sorted(evidence_ids),
            default=[selected_event_id],
        )
        rationale = st.text_area("Analyst rationale (required for supported status)")
        alternatives = st.text_area("Alternative explanations")
        missing = st.text_area("Missing evidence / open investigative questions")
        confidence = st.slider("Analyst-assigned confidence (not MITRE metadata)", 0, 100, 30, 5)
        status = st.selectbox(
            "Mapping status",
            ["proposed", "supported", "needs further investigation", "rejected"],
        )
        add = st.form_submit_button("Add candidate mapping")
    if add:
        try:
            mapping = create_mapping(
                technique_id,
                linked_evidence,
                rationale,
                alternatives,
                missing,
                confidence,
                status,
                techniques,
                evidence_ids,
            )
            st.session_state.mappings.append(mapping)
            st.success("Candidate mapping added.")
        except DataValidationError as exc:
            st.error(str(exc))

if st.session_state.mappings:
    st.markdown("### Existing mappings")
    for index, mapping in enumerate(list(st.session_state.mappings)):
        record = techniques[mapping["technique_id"]]
        with st.expander(
            f"{record['technique_id']} {record['name']} · {mapping['status']} · {mapping['confidence']}%"
        ):
            st.write(f"**Evidence:** {', '.join(mapping['evidence_ids'])}")
            st.write(f"**Rationale:** {mapping['rationale'] or 'Not recorded'}")
            st.write(f"**Alternatives:** {mapping['alternative_explanations'] or 'Not recorded'}")
            st.write(f"**Missing evidence:** {mapping['missing_evidence'] or 'Not recorded'}")
            with st.form(f"edit_mapping_{mapping['mapping_id']}"):
                new_status = st.selectbox(
                    "Update status",
                    ["proposed", "supported", "needs further investigation", "rejected"],
                    index=["proposed", "supported", "needs further investigation", "rejected"].index(mapping["status"]),
                )
                new_rationale = st.text_area("Update rationale", mapping["rationale"])
                new_alternatives = st.text_area("Update alternative explanations", mapping["alternative_explanations"])
                new_missing = st.text_area("Update missing evidence", mapping["missing_evidence"])
                new_confidence = st.slider("Update analyst confidence", 0, 100, mapping["confidence"], 5)
                new_evidence = st.multiselect(
                    "Update evidence references",
                    sorted(evidence_ids),
                    default=mapping["evidence_ids"],
                )
                save = st.form_submit_button("Save mapping changes")
            if save:
                try:
                    st.session_state.mappings[index] = update_mapping(
                        mapping,
                        {
                            "status": new_status,
                            "rationale": new_rationale.strip(),
                            "alternative_explanations": new_alternatives.strip(),
                            "missing_evidence": new_missing.strip(),
                            "confidence": new_confidence,
                            "evidence_ids": new_evidence,
                        },
                        techniques,
                        evidence_ids,
                    )
                    st.success("Mapping updated.")
                    st.rerun()
                except DataValidationError as exc:
                    st.error(str(exc))
            if st.button("Remove mapping", key=f"remove_{mapping['mapping_id']}"):
                try:
                    st.session_state.mappings = remove_mapping(st.session_state.mappings, mapping["mapping_id"])
                    st.rerun()
                except DataValidationError as exc:
                    st.error(str(exc))

    chart_rows = []
    for mapping in st.session_state.mappings:
        record = techniques[mapping["technique_id"]]
        for tactic in record["tactics"]:
            chart_rows.append(
                {
                    "Tactic": tactic,
                    "Technique": f"{record['technique_id']} — {record['name']}",
                    "Status": mapping["status"],
                    "Confidence": mapping["confidence"],
                    "Evidence": ", ".join(mapping["evidence_ids"]),
                    "Rationale": mapping["rationale"] or "Not recorded",
                }
            )
    st.markdown("### ATT&CK tactic view")
    st.warning("Grouping by tactic is a matrix view, not a confirmed sequence or causal attack path.")
    fig = px.scatter(
        chart_rows,
        x="Tactic",
        y="Technique",
        color="Status",
        size="Confidence",
        hover_data=["Evidence", "Rationale", "Confidence"],
        color_discrete_map={
            "proposed": "#F4C542",
            "supported": "#55A868",
            "rejected": "#9AA0A6",
            "needs further investigation": "#4C9BE8",
        },
        title="Student candidate mappings grouped by tactic",
    )
    fig.update_layout(height=max(350, 60 * len(chart_rows)))
    st.plotly_chart(fig, width="stretch")
    st.caption("Legend: mapping status and analyst-entered confidence. Tooltips show evidence references and rationale.")

with st.expander("Candidate catalogue and mapping guidance"):
    for record in techniques.values():
        st.markdown(
            f"- [{record['technique_id']} — {record['name']}]({record['url']}) "
            f"({', '.join(record['tactics'])})"
        )
    st.info("E-01 does not prove phishing; E-02 does not prove credential abuse; E-06 does not prove exfiltration.")
st.page_link("pages/6_Export_Investigation.py", label="Export an ATT&CK Navigator layer →")
