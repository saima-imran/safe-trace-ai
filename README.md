SafeTrace-AI

Deterministic change-impact analysis with policy-governed, advisory AI assistance for requirements traceability and verification evidence.

SafeTrace-AI is a research prototype that compares versions of safety-related software requirements, resolves links to verification artifacts, evaluates existing evidence using deterministic rules, and optionally asks a local Large Language Model (LLM) to explain the verified findings.

The prototype also includes a deterministic governance layer that decides whether an AI-assisted activity is permitted, requires explicit human authorization, or is restricted.

Core assurance principle: Deterministic logic establishes engineering facts and governs whether AI may participate. The LLM may explain authorized facts, but it does not determine verification status, modify authoritative trace links, approve compliance, or certify safety.

Contents

1. Motivation

2. System scope

3. Design principles

4. System context

5. Architecture

6. Deterministic analysis pipeline

7. AI governance layer

8. Human authorization

9. Advisory LLM layer

10. Data model and case study

11. Streamlit interface

12. Repository structure

13. Installation

14. Running the project

15. Testing

16. Demonstration scenarios

17. Current limitations

18. Accountability and recovery roadmap

19. Research scope

20. Disclaimer

1. Motivation

When a software requirement changes, engineers must determine:

What changed between the two versions?

Which test cases verify the requirement?

Which historical test results are connected to those test cases?

Does the existing evidence still address the updated requirement?

Is engineering review or re-verification required?

Where may generative AI assist without becoming an engineering authority?

Who is allowed to authorize safety-related AI assistance?

Which activities must remain deterministic?

SafeTrace-AI explores these questions through a small, inspectable technical demonstrator based on a seat-belt warning system.

2. System scope

In scope

Load controlled requirements, test cases, and test results from YAML.

Compare two versions of a requirement baseline.

Detect modified, unchanged, added, and removed requirements.

Resolve explicit Requirement -> Test Case -> Test Result links.

Collect verification evidence affected by modified requirements.

Apply deterministic evidence-assessment rules.

Optionally generate a grounded advisory explanation through local Ollama.

Evaluate a machine-readable governance policy before LLM execution.

Require an allowed engineering role and explicit authorization where configured.

Restrict AI from modifying authoritative traceability links.

Present analysis and governance behavior through Streamlit.

Generate a downloadable text analysis report.

Out of scope

ISO 26262 certification or conformity assessment.

Hazard analysis, risk classification, or safety acceptance.

Legal or regulatory compliance determination.

Automatic creation, approval, modification, or removal of authoritative trace links.

Replacement of requirements, verification, safety, or compliance engineers.

Production integration with SystemWeaver or other lifecycle-management platforms.

Persistent organizational identity, accountability logs, trusted-state rollback, and recovery orchestration in the current baseline.

3. Design principles

Principle

Meaning in SafeTrace-AI

Deterministic authority

Python establishes change status, trace links, measurements, and evidence status.

Policy before execution

Governance is evaluated before any LLM request.

Bounded AI assistance

The LLM receives a limited task, verified inputs, and explicit prohibitions.

Human responsibility

Safety-impact explanations require an allowed role and explicit authorization.

No AI at the traceability core

AI cannot create, modify, approve, or remove authoritative trace links.

Fail closed

Unknown activities, unauthorized roles, and restricted activities do not receive AI execution.

Local processing

The configured model runs locally through Ollama.

Research transparency

Implemented controls and planned controls are distinguished explicitly.

4. System context

flowchart LR
    RE[Requirements engineer] --> ST[SafeTrace-AI]
    VE[Verification or safety engineer] --> ST
    ART[Requirements, tests, results] --> ST
    ST --> FIND[Deterministic findings]
    ST --> OLL[Local Ollama model]
    OLL --> ADV[Advisory explanation]

Engineering artifacts are controlled inputs. Deterministic findings remain authoritative. A local LLM can provide an advisory explanation only when the governance decision permits execution.

5. Architecture

flowchart TB
    UI[Streamlit analysis and governance pages]
    MAIN[Analysis orchestration]
    GOV[Governance policy and authorization]
    DET[Deterministic change, traceability, impact, and evidence analysis]
    LLM[Advisory LLM adapter]
    DATA[YAML case-study data]
    POL[Governance policy YAML]
    REP[Text report generator]

    UI --> MAIN
    UI --> GOV
    MAIN --> DET
    MAIN --> GOV
    GOV --> LLM
    DET --> LLM
    DATA --> DET
    POL --> GOV
    MAIN --> REP

Main components

Component

Responsibility

data_loader.py

Safely loads YAML engineering data.

change_detector.py

Compares requirement baselines by stable ID and normalized text.

traceability.py

Resolves requirement-to-test and test-to-result links.

impact_analyzer.py

Collects evidence connected to modified requirements.

evidence_assessor.py

Applies deterministic evidence rules, currently including timing.

governance_policy.py

Loads, validates, and selects the policy for an activity.

governance_authorization.py

Evaluates roles, explicit authorization, and restricted use.

llm_analyzer.py

Builds a grounded prompt and communicates with Ollama.

main.py

Orchestrates governed analysis and returns structured results.

app.py

Presents analysis results and a downloadable report.

pages/1_Governance.py

Demonstrates policy selection and authorization outcomes.

report_generator.py

Creates a plain-text analysis report.

6. Deterministic analysis pipeline

flowchart LR
    V[Requirement V1 and V2] --> C[Change detection]
    C --> T[Traceability resolution]
    T --> I[Impact analysis]
    I --> E[Evidence assessment]
    E --> F[Authoritative finding]
    F --> G[Governance gate]
    G -->|Allowed| A[Advisory explanation]
    G -->|Blocked| B[No AI execution]

Change detection

Whitespace is normalized before comparison. Requirements are indexed by ID and classified as:

modified

unchanged

added

removed

The current downstream impact pipeline analyzes modified requirements.

Traceability model

flowchart LR
    R[Requirement] -->|verified by| TC[Test case]
    TC -->|executed as| TR[Test result]

For example:

SSR-002 -> TC-002 -> TR-002

The links are read from controlled YAML fields. The LLM does not create or alter them.

Deterministic evidence assessment

The timing example demonstrates why a historical pass verdict cannot automatically be reused after a requirement change:

Old maximum response time: 500 ms
New maximum response time: 200 ms
Historical measurement:    420 ms

The historical result satisfied the old threshold:

420 ms <= 500 ms

It exceeds the updated threshold:

420 ms > 200 ms

SafeTrace-AI therefore assigns:

RE_VERIFICATION_REQUIRED

Other modified requirements currently receive REVIEW_REQUIRED unless a specialized deterministic rule produces a stronger finding.

7. AI governance layer

Governance policies are machine-readable and stored in:

config/governance_policies.yaml

The current demonstrator defines three policy boundaries:

Policy

Activity

Decision

Meaning

POL-AI-001

Summarize a low-consequence change

AI_PERMITTED

AI may run without additional authorization.

POL-AI-002

Explain a safety-requirement impact

HUMAN_AUTHORIZATION_REQUIRED

An allowed role must explicitly authorize bounded AI assistance.

POL-AI-003

Modify an authoritative trace link

AI_RESTRICTED

AI execution remains blocked; no role can authorize it.

Governance decision flow

flowchart TB
    ACT[Engineering activity requested] --> LOOK[Deterministic policy lookup]
    LOOK --> P[AI permitted]
    LOOK --> H[Human authorization required]
    LOOK --> R[AI restricted]
    P --> RUN[AI execution allowed]
    H --> CHECK[Validate role and explicit authorization]
    CHECK -->|Valid| RUN
    CHECK -->|Missing or invalid| BLOCK[AI execution blocked]
    R --> BLOCK

The LLM does not select, interpret, or modify the governance policy.

Authorization outcomes

Outcome

AI allowed?

Meaning

PERMITTED

Yes

Policy permits the activity without additional authorization.

AUTHORIZED

Yes

An allowed role explicitly authorized the bounded activity.

AUTHORIZATION_REQUIRED

No

The role is allowed, but explicit authorization was not granted.

UNAUTHORIZED_ROLE

No

No role was selected or the selected role is not allowed.

RESTRICTED

No

Policy prohibits AI execution for the activity.

AI_NOT_REQUESTED

No

Analysis was intentionally run without the LLM.

8. Human authorization

For a safety-requirement impact explanation, the current policy permits explicit authorization by configured engineering roles such as:

requirements_engineer

verification_engineer

safety_engineer

Authorization requires both:

Selection of an allowed role.

An explicit authorization action in the governance interface.

Selecting a role without explicit authorization is insufficient. Explicit authorization by an unauthorized role is also insufficient. A restricted activity remains restricted regardless of role or checkbox state.

This is a technical role-policy demonstrator. It does not yet authenticate a real organizational identity or persist a signed approval record.

9. Advisory LLM layer

SafeTrace-AI currently uses:

Ollama endpoint: http://localhost:11434/api/generate
Model: llama3.2:3b

The LLM receives verified information including:

old and new requirement text

deterministic evidence status

deterministic reason

linked test-case IDs

linked test-result IDs

The requested response uses four headings:

Change Type:
Semantic Impact:
Evidence Concern:
Suggested Review:

The prompt instructs the model to preserve numbers and logical operators and prohibits it from inventing requirements, measurements, tests, trace links, regulations, certification, or compliance conclusions.

These prompt constraints reduce risk but do not constitute deterministic output validation. Generated text remains advisory and subject to human engineering review.

10. Data model and case study

The case study contains two versions of six seat-belt warning requirements, six test cases, and six historical test results.

Requirement

Version 1

Version 2

Current deterministic finding

SSR-001

Activation above 10 km/h

Activation above 5 km/h

REVIEW_REQUIRED

SSR-002

Activate within 500 ms

Activate within 200 ms

RE_VERIFICATION_REQUIRED

SSR-003

Unavailable signal produces fault

Unavailable or implausible signal produces fault and diagnostic event

REVIEW_REQUIRED

SSR-004

Fastened belt deactivates warning

Fastened belt and valid signal deactivate warning

REVIEW_REQUIRED

SSR-005

Visual warning indication

Unchanged

Not analyzed downstream

SSR-006

Restart-state determination

Unchanged

Not analyzed downstream

Historical test results remain associated with requirement version 1. A prior pass verdict is not reinterpreted as proof that the updated requirement is satisfied.

11. Streamlit interface

The application is a Streamlit multipage interface.

Analysis page

Runs deterministic change-impact analysis.

Optionally requests Ollama explanations.

Shows old and new requirement text.

Shows deterministic status and reason.

Shows linked test cases and test results.

Shows the advisory explanation when governance allows execution.

Provides a downloadable text report.

Governance page

Displays the machine-readable policy overview.

Allows selection of an engineering activity.

Displays the applicable policy and allowed roles.

Demonstrates role selection and explicit authorization.

Displays whether AI execution is permitted, authorized, blocked, or restricted.

Does not call Ollama; it demonstrates the pre-execution decision logic.

12. Repository structure

safe-trace-ai/
├── config/
│   └── governance_policies.yaml
├── data/
│   └── case_study/
│       ├── requirements_v1.yaml
│       ├── requirements_v2.yaml
│       ├── test_cases.yaml
│       └── test_results.yaml
├── src/
│   ├── pages/
│   │   └── 1_Governance.py
│   ├── app.py
│   ├── change_detector.py
│   ├── data_loader.py
│   ├── evidence_assessor.py
│   ├── governance_authorization.py
│   ├── governance_policy.py
│   ├── impact_analyzer.py
│   ├── llm_analyzer.py
│   ├── main.py
│   ├── report_generator.py
│   └── traceability.py
├── tests/
│   ├── test_change_detector.py
│   ├── test_evidence_assessor.py
│   ├── test_governance_authorization.py
│   ├── test_governance_policy.py
│   ├── test_governed_analysis.py
│   ├── test_llm_analyzer.py
│   └── test_traceability.py
├── requirements.txt
└── README.md

13. Installation

Prerequisites

Python 3

Git

Ollama, only for LLM-enabled analysis

The local llama3.2:3b model, only for LLM-enabled analysis

Clone and install

git clone https://github.com/saima-imran/safe-trace-ai.git
cd safe-trace-ai
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt

Check the local Ollama installation and model:

ollama --version
ollama list

If the model is not installed:

ollama pull llama3.2:3b

14. Running the project

Run the Streamlit application

From the repository root:

streamlit run src/app.py

Open http://localhost:8501 if the browser does not open automatically. Stop the server with Ctrl+C in the terminal.

Run deterministic analysis without Ollama

Use the Streamlit checkbox to disable Ollama explanations before running the analysis. This preserves deterministic change, traceability, impact, and evidence analysis without local model execution.

Ollama performance note

The configured 3-billion-parameter model may use 100% CPU while generating a response on CPU-only hardware. A request can take time because each changed requirement can produce a separate model call.

Useful commands:

ollama ps
ollama stop llama3.2:3b

15. Testing

Run all automated tests from the repository root:

pytest -v

Documented baseline:

19 passed

The tests cover:

requirement change detection

deterministic timing evidence assessment

requirement-to-test-to-result traceability

grounded prompt construction

mocked Ollama response and empty-response handling

governance policy loading and validation

permitted, authorization-required, authorized, unauthorized, and restricted outcomes

enforcement of governance before LLM execution

Automated LLM adapter tests mock the HTTP response and therefore do not require a real generation call.

16. Demonstration scenarios

Scenario A: AI permitted

Select the low-consequence summarization activity. POL-AI-001 produces PERMITTED, and AI execution is allowed without additional authorization.

Scenario B: Human authorization required

Select the safety-impact explanation activity without an allowed role and explicit authorization. POL-AI-002 blocks execution. Select an allowed role and explicitly authorize bounded assistance; the result becomes AUTHORIZED.

Scenario C: Restricted traceability core

Select authoritative trace-link modification. POL-AI-003 returns RESTRICTED, even if an engineering role is selected and explicit authorization is checked.

17. Current limitations

The case study is intentionally small and synthetic.

Only modified requirements are currently processed by the downstream impact pipeline.

Timing is the only specialized deterministic evidence rule.

YAML input data has no complete schema validation, signatures, or provenance protection.

Governance selection is activity-based and does not yet include artifact criticality, lifecycle state, risk classification, or organizational context.

Roles are interface selections rather than authenticated identities.

Human authorization is evaluated in memory and is not persistently logged.

Prompt restrictions are not yet backed by deterministic output validation.

LLM output quality depends on the local model and remains variable.

Proposed AI output and trusted engineering state are not yet persisted separately.

Trusted-state recovery and rollback are not implemented.

The prototype has no direct integration with industrial requirements or evidence-management platforms.

18. Accountability and recovery roadmap

The implemented governance layer establishes pre-execution AI-use boundaries. The next research steps address organizational accountability and recovery:

flowchart LR
    I[Implemented policy gate] --> L[Persistent accountability log]
    L --> W[Human review workflow]
    W --> V[Deterministic output validator]
    V --> S[Proposed versus trusted state]
    S --> R[Recovery demonstrator]

Planned capabilities include:

Persistent accountability log — record policy ID and version, role, decision, authorization, model, timestamps, input references, and justification.

Human review workflow — record approve, reject, or escalate decisions with reviewer responsibility.

Deterministic output validator — detect changed numbers, altered logical operators, unsupported claims, invented evidence, and prohibited compliance language.

Proposed versus trusted state — keep AI suggestions separate from approved engineering artifacts.

Recovery demonstrator — inject a faulty advisory output, identify affected downstream artifacts, restore the last trusted state, and document re-review.

Empirical evaluation — evaluate usefulness, false claims, authorization burden, accountability completeness, and recovery effectiveness with practitioners.

19. Research scope

SafeTrace-AI investigates the following central question:

How can organizations define and operationalize boundaries for AI-assisted traceability while maintaining accountability and enabling recovery?

The current baseline demonstrates that AI-use boundaries can be represented as deterministic, machine-readable policies and enforced before model execution. It does not yet demonstrate complete organizational accountability or recovery. Those capabilities are explicit next-stage research work.

Potential evaluation areas include:

taxonomy of AI-use boundaries in traceability

policy expressiveness and usability

practitioner interpretation of authorization decisions

completeness of accountability and provenance records

factual and semantic validation of advisory output

detection and recovery after deliberately injected failures

comparison of deterministic-only and policy-governed AI-assisted workflows

20. Disclaimer

SafeTrace-AI is a research and demonstration prototype. It is not an ISO 26262 compliance tool, certification tool, production safety-analysis tool, or replacement for qualified engineering judgment.

All AI-generated explanations are advisory and require human engineering review.
