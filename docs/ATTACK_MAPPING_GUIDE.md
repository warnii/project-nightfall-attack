# ATT&CK Mapping Guide

## Version and source

This workshop targets MITRE ATT&CK Enterprise **15.1**, in the v15 release family. The local subset was checked against the official version-pinned [MITRE attack-stix-data v15.1 Enterprise bundle](https://github.com/mitre-attack/attack-stix-data/blob/v15.1/enterprise-attack/enterprise-attack.json), retrieved 2026-10-27. The exercise catalogue contains a deliberately small set of relevant techniques, exact IDs/names/tactics, and parent relationships; concise descriptions are educational summaries. It is not the full ATT&CK dataset. See `data/attack_techniques.json` for provenance.

## A defensible mapping

1. Select the evidence record(s) that directly support the behaviour.
2. Search by technique ID/name and inspect its tactic, description, and parent relationship.
3. State what is actually observed before offering an interpretation.
4. Record alternative explanations, missing evidence, and analyst-assigned confidence.
5. Keep a mapping proposed until evidence and rationale justify a stronger analyst assessment. A rationale is mandatory for `supported`.
6. Preserve evidence IDs in every mapping. A mapping does not assert actor, intent, causality, or incident confirmation.

ATT&CK describes adversary behaviour; it does not prescribe a single sequence. Techniques grouped under adjacent tactics in a matrix are not proof of chronology.

## Exercise-specific cautions

- E-01: an email was received; opening, clicking, malicious content, and resulting access are not established.
- E-02: an unfamiliar sign-in was successful; compromise and credential abuse are not established.
- E-03: an office application spawned PowerShell; script purpose and user action are unknown.
- E-04: process and security-software information was queried; routine inventory is an alternative.
- E-06: transfer volume triggered an alert; destination ownership, process attribution, and data content are unknown. Do not select an exfiltration technique without specific supporting evidence.

## Navigator export

The exporter follows the official [ATT&CK Navigator layer format 4.5 specification](https://github.com/mitre-attack/attack-navigator/blob/master/layers/spec/v4.5/layerformat.md). Its `versions` object declares `attack: "15.1"`, `navigator: "4.9.0"` (the schema's stated minimum), and `layer: "4.5"`. `domain` is `enterprise-attack`. Comments preserve mapping status, evidence IDs, rationale, alternatives, missing evidence, and the student's confidence. Scores and colors are student annotation conventions, not official MITRE labels.

Open the layer in ATT&CK Navigator through **Open Existing Layer → Upload from local**. Select the Enterprise v15.1 matrix where available. To reopen the layer, upload its saved JSON again. The separate investigation snapshot preserves worksheets that are outside the Navigator format.
