# Project Nightfall Investigation Playbook

## Purpose and safety

This is a fictional, offline training case. Do not connect this application to real enterprise systems, execute evidence strings, or upload real logs. All records must remain synthetic.

## Suggested workflow

1. **Orient:** Read the case overview and timeline. Treat close timestamps as a lead, not proof of a shared cause.
2. **Triage evidence:** Filter the evidence table, inspect a full record, and distinguish source observation from interpretation.
3. **Record competing explanations:** Use the evidence worksheet to note what might explain each event and what would disprove your initial idea.
4. **Test hypotheses:** Inspect identity, endpoint, document-audit, DNS, proxy, and DLP sources as synthetic exercise prompts. The app does not query any of them.
5. **Map cautiously:** Search the v15.1 subset. Keep candidates proposed unless a rationale and evidence support a stronger judgment.
6. **Consider defenses:** Name the finding, purpose, evaluation telemetry, expected outcome, and limitations. Use D3FEND as a knowledge reference, not a prevention guarantee.
7. **Export:** Save the Navigator layer, investigation snapshot, and Markdown report. Review the report for unsupported conclusions before sharing.

## Questions to test

- Did the employee open the message or its link?
- Was the unusual sign-in initiated by the employee, an approved device, or another session?
- What process and file details explain the office-to-interpreter relationship?
- Was process enumeration routine inventory or a different activity?
- Were documents viewed, downloaded, or shared, and were they sensitive?
- Which process initiated the transfer, who controlled the destination, and what content moved?

## Close-out discipline

State four things separately: **observed**, **inferred**, **unknown**, and **next action**. Avoid declaring phishing, compromise, or exfiltration from a single alert.
