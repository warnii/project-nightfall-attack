# Project Nightfall — Threat Hunting & ATT&CK Investigation Lab

**Investigate the evidence. Map the behaviour. Defend the organisation.**

Project Nightfall is a local, offline-first training application for a hands-on workshop on threat intelligence and incident response. Students investigate an entirely synthetic case, distinguish observations from hypotheses, map candidate behaviour to a curated MITRE ATT&CK Enterprise v15.1 subset, and export an ATT&CK Navigator layer.

> **SIMULATED TRAINING CASE:** all identities, events, hosts, documents, and IP addresses are invented or reserved documentation examples. The app does not access real systems, send email, execute evidence, scan targets, or query a SIEM.

## Learning objectives

- Separate observed evidence, analyst hypothesis, and unsupported conclusion.
- Review ambiguous identity, endpoint, file-access, and network evidence.
- Formulate a testable hypothesis and identify corroborating or contradictory telemetry.
- Map only evidence-supported candidate behaviours to ATT&CK.
- Create an annotated, importable Navigator layer and a cautious investigation report.
- State confidence, limitations, alternatives, and next investigative steps.

## Features

- Interactive home dashboard and Plotly evidence timeline.
- Searchable/filterable evidence explorer, full record view, analyst worksheets, safe synthetic CSV import, and filtered CSV export.
- Curated, provenance-labelled ATT&CK Enterprise 15.1 technique catalogue with tactic and sub-technique relationships.
- Evidence-linked mapping workflow with proposed/supported/rejected/further-investigation states, rationale validation, confidence, and alternatives.
- Tactic-grouped map with status colors and evidence tooltips; the visualization does not imply a confirmed sequence.
- Five progressive student challenges with explanations.
- Hypothesis worksheets and editable preventive, detective, and response recommendations.
- Validated Navigator layer-format 4.5 JSON download, session snapshot, and Markdown report.
- Automated offline pytest suite.

## Screenshots

No screenshots are bundled because the app must be launched to capture accurate UI. After launch, capture the home dashboard and one investigation page using your operating system's screenshot tool. Save images as `screenshots/home.png` and `screenshots/mapping.png` to fill these placeholders:

![Home dashboard — capture after launch](screenshots/home.png)

![ATT&CK mapping — capture after adding a candidate](screenshots/mapping.png)

## Project structure

```text
project-nightfall-attack-investigation/
├── app.py
├── requirements.txt
├── README.md
├── LICENSE
├── .gitignore
├── .env.example
├── data/
│   ├── incident_events.json
│   ├── attack_techniques.json
│   └── investigation_hypotheses.json
├── src/
│   ├── data_loader.py
│   ├── evidence_analysis.py
│   ├── attack_mapper.py
│   ├── navigator_export.py
│   ├── timeline.py
│   ├── report_generator.py
│   ├── validation.py
│   └── ui.py
├── pages/
│   ├── 1_Incident_Timeline.py
│   ├── 2_Evidence_Explorer.py
│   ├── 3_ATT&CK_Mapping.py
│   ├── 4_Threat_Hunting.py
│   ├── 5_Defensive_Recommendations.py
│   └── 6_Export_Investigation.py
├── tests/
├── docs/
└── outputs/
```

## Prerequisites

- Python 3.11 or newer
- Git (optional, for version control)
- A current web browser

The direct dependencies are pinned to the tested releases in `requirements.txt`. Those releases declare support for Python 3.11 or newer.

The first dependency installation needs package-index access. Once dependencies and local data are present, the application and tests do not require a cloud service, API key, external database, or runtime network access.

## Setup in VS Code

1. Open this project folder in VS Code.
2. Open a terminal at the project root.
3. Create and activate a virtual environment.

### Windows PowerShell

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, use the interpreter directly: `.\.venv\Scripts\python.exe`.

### macOS/Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

Launch the app:

```bash
streamlit run app.py
```

Run tests:

```bash
python -m pytest -q
```

## How to investigate the case

1. Begin on the dashboard and inspect the UTC timeline.
2. Open **Evidence Explorer**. Search and filter records, inspect the complete source record, and record observations, interpretations, alternatives, confidence, and needed evidence separately.
3. Open **Threat Hunting**. Choose a question, document findings and confidence, and identify the next action. These are guided synthetic procedures, not live queries.
4. Open **ATT&CK Mapping**. Select an evidence record, search the local catalogue by name/ID and tactic, then record evidence, rationale, alternatives, missing evidence, status, and custom confidence. A rationale is required for supported status.
5. Review the tactic-grouped view. Tactic grouping does not prove event order or causality.
6. Open **Defensive Recommendations** and adapt the suggested action, evaluation telemetry, expected outcome, and limitations.
7. Complete the five progressive challenges.

## Navigator export

Open **Export Investigation** and select **Download Navigator JSON**. The exporter validates the JSON before download and emits the official Navigator layer format 4.5 with:

- Domain `enterprise-attack`
- ATT&CK version `15.1` (v15 release family)
- Layer format `4.5`
- Evidence references, rationale, alternatives, mapping status, and student confidence in technique comments

To load the layer, open [ATT&CK Navigator](https://mitre-attack.github.io/attack-navigator/), choose **Open Existing Layer → Upload from local**, and select `project-nightfall-navigator-layer.json`. Choose the Enterprise ATT&CK 15.1 matrix/version where offered. Reopen saved work by uploading the layer JSON again. The separate investigation snapshot preserves worksheets and notes not represented by the Navigator format.

Navigator documentation: [official layer file format 4.5](https://github.com/mitre-attack/attack-navigator/blob/master/layers/spec/v4.5/layerformat.md).

## Investigation report

On **Export Investigation**, select **Download Markdown investigation report**. The report includes the synthetic case scope, timeline, observations, candidate mappings, confidence, alternatives, unresolved questions, recommendations, limitations, next steps, and ATT&CK provenance. Review the report before sharing. An empty investigation is allowed and does not invent a finding.

## Data provenance and ATT&CK version

The exercise uses selected technique identifiers, names, tactics, and sub-technique relationships checked against [MITRE's official version-pinned Enterprise STIX v15.1 release](https://github.com/mitre-attack/attack-stix-data/blob/v15.1/enterprise-attack/enterprise-attack.json), retrieved on 2026-10-27. The local catalogue is intentionally limited and its descriptions are concise educational summaries; it is not the complete ATT&CK knowledge base. Catalogue metadata is in `data/attack_techniques.json`; mapping decisions remain the student's.

## GitHub setup

Follow [docs/GITHUB_SETUP.md](docs/GITHUB_SETUP.md) to create and push a repository manually. Suggested initial commit: `Build Project Nightfall investigation lab`. No repository, remote, or push is created by the app.

## Troubleshooting

- **`streamlit` command not found:** Activate the virtual environment or run `python -m streamlit run app.py`.
- **Missing dependency:** Verify the virtual environment is active, then run `python -m pip install -r requirements.txt`.
- **Port already in use:** Start on another local port with `streamlit run app.py --server.port 8502`.
- **PowerShell activation is blocked:** Call `.venv\Scripts\python.exe -m streamlit run app.py` without activating.
- **Invalid JSON/CSV:** Check file syntax, required columns, timestamps, unique evidence IDs, and the explicit synthetic-data attestation. Imports are rejected with an explanation; evidence text is never executed.
- **ATT&CK technique not found:** Only a small v15.1 subset is included. This is intentional and prevents silently substituting another version.
- **Navigator version not offered:** Select an Enterprise v15.1 matrix if supported by the deployed Navigator. The layer metadata remains explicitly versioned; do not relabel it as a different ATT&CK release.
- **Lost session notes:** Download and later import the investigation session snapshot. Streamlit session state is otherwise temporary.

## Ethical and safety statement

This project is for defensive education. It contains synthetic evidence only, no attack payloads or malware, and no integration with real accounts, hosts, logs, or SIEMs. Do not upload real personal or incident data. This prototype is not validated for production incident response.
