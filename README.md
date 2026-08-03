# SafeTrace-AI

SafeTrace-AI is a research prototype for **AI-assisted requirement change-impact analysis and verification evidence review**.

The project combines a deterministic Python pipeline with a locally hosted Large Language Model (LLM) to analyze changes between requirement versions, identify affected verification evidence, and generate advisory engineering explanations.

The fundamental design principle is:

> **Deterministic logic determines engineering facts. The LLM explains those facts but does not make the engineering decision.**

---

## 1. Project Motivation

Safety-related software requirements evolve during development.

When a requirement changes, engineers need to understand:

- What changed?
- Which test cases are linked to the requirement?
- Which test results may be affected?
- Is existing verification evidence still relevant?
- Is re-verification required?
- How can the change be explained clearly to an engineer?

SafeTrace-AI explores how deterministic analysis and a local LLM can be combined to support this workflow.

The prototype uses a seat-belt warning system as its engineering case study.

---

## 2. System Architecture

SafeTrace-AI separates deterministic engineering analysis from generative AI explanation.

```text
Requirements V1
      |
      |
Requirements V2
      |
      v
+-----------------------+
|     Data Loader       |
+-----------------------+
      |
      v
+-----------------------+
|   Change Detector     |
+-----------------------+
      |
      v
Changed Requirements
      |
      v
+-----------------------+
|     Traceability      |
+-----------------------+
      |
      v
Requirement -> Test Case -> Test Result
      |
      v
+-----------------------+
|    Impact Analyzer    |
+-----------------------+
      |
      v
+-----------------------+
|   Evidence Assessor   |
+-----------------------+
      |
      v
Deterministic Engineering Finding
      |
      v
+-----------------------+
|     LLM Analyzer      |
+-----------------------+
      |
      v
Ollama / llama3.2:3b
      |
      v
Advisory Engineering Explanation
      |
      v
+-----------------------+
|     Human Review      |
+-----------------------+
```

The deterministic pipeline remains authoritative.

The LLM is used only as an advisory explanation layer.

---

## 3. Main Features

SafeTrace-AI currently provides:

- YAML-based engineering data
- Requirement version comparison
- Requirement change detection
- Requirement-to-test traceability
- Test-result traceability
- Verification impact analysis
- Deterministic evidence assessment
- Local LLM integration using Ollama
- Grounded engineering explanation prompts
- Streamlit user interface
- Automated testing using pytest
- Separation between deterministic decisions and AI-generated explanations

---

## 4. Requirement Versioning

The case study contains two versions of the same requirement set:

```text
requirements_v1.yaml
requirements_v2.yaml
```

These represent different revisions of the same requirements.

SafeTrace-AI compares the two versions and classifies each requirement as:

```text
modified
```

or:

```text
unchanged
```

The prototype does not treat V1 and V2 as different requirement categories.

They represent different versions of the same engineering baseline.

---

## 5. Traceability Model

SafeTrace-AI follows the relationship:

```text
Requirement
    |
    v
Test Case
    |
    v
Test Result
```

For example:

```text
SSR-002
   |
   v
TC-002
   |
   v
TR-002
```

This allows a requirement change to be connected to its existing verification evidence.

---

## 6. Deterministic Evidence Assessment

Engineering decisions are made by deterministic Python logic rather than by the LLM.

Example:

### Original requirement

```text
The seat-belt warning shall activate within 500 ms.
```

### Updated requirement

```text
The seat-belt warning shall activate within 200 ms.
```

### Existing verification result

```text
Measured response time = 420 ms
```

For the original requirement:

```text
420 ms <= 500 ms
```

The measurement satisfied the previous timing constraint.

For the updated requirement:

```text
420 ms > 200 ms
```

The existing measurement does not satisfy the updated timing constraint.

SafeTrace-AI therefore produces:

```text
RE_VERIFICATION_REQUIRED
```

with the deterministic reason:

```text
Previous measured response time was 420 ms,
which exceeds the new 200 ms requirement.
```

The LLM does not determine this status.

---

## 7. Evidence Status

The current prototype uses deterministic statuses including:

### REVIEW_REQUIRED

The requirement changed and its linked verification evidence should be reviewed.

### RE_VERIFICATION_REQUIRED

Existing deterministic evidence demonstrates that verification needs to be repeated or reconsidered against the updated requirement.

These statuses are generated before the LLM is called.

---

## 8. LLM Advisory Layer

SafeTrace-AI uses a locally hosted LLM through Ollama.

Current model:

```text
llama3.2:3b
```

The LLM receives verified information from the deterministic pipeline, including:

- old requirement
- new requirement
- deterministic evidence status
- deterministic reason
- linked test-case IDs
- linked test-result IDs

The model is asked to explain the change using four sections:

```text
Change Type

Semantic Impact

Evidence Concern

Suggested Review
```

The LLM is explicitly instructed not to:

- change the deterministic status
- invent measurements
- invent requirements
- invent tests
- invent traceability relationships
- perform hazard classification
- claim certification
- claim ISO 26262 compliance or non-compliance
- make authoritative safety-acceptance decisions

AI-generated explanations remain advisory and require human engineering review.

---

## 9. Example Semantic Change

Consider the following requirement.

### Previous version

```text
If the driver seat-belt status signal is unavailable,
the system shall report a seat-belt status fault.
```

### Updated version

```text
If the driver seat-belt status signal is unavailable or implausible,
the system shall report a seat-belt status fault and store a
diagnostic event.
```

The updated requirement introduces:

1. An additional condition: an **implausible** seat-belt status signal.
2. An additional required behavior: **store a diagnostic event**.

SafeTrace-AI identifies the linked verification evidence and recommends that it be reviewed against the expanded requirement.

---

## 10. Streamlit Interface

SafeTrace-AI includes a Streamlit interface for interactive analysis.

The interface presents:

- changed requirement count
- requirement ID and title
- old requirement
- new requirement
- deterministic evidence status
- deterministic reason
- linked test cases
- linked test results
- LLM advisory explanation

The interface also allows the LLM explanation layer to be enabled or disabled.

This makes it possible to run the deterministic pipeline independently of Ollama.

---

## 11. Project Structure

```text
safe-trace-ai/
|
+-- data/
|   |
|   +-- case_study/
|       |
|       +-- requirements_v1.yaml
|       +-- requirements_v2.yaml
|       +-- test_cases.yaml
|       +-- test_results.yaml
|
+-- src/
|   |
|   +-- data_loader.py
|   +-- change_detector.py
|   +-- traceability.py
|   +-- impact_analyzer.py
|   +-- evidence_assessor.py
|   +-- llm_analyzer.py
|   +-- main.py
|   +-- app.py
|
+-- tests/
|   |
|   +-- test_change_detector.py
|   +-- test_evidence_assessor.py
|   +-- test_llm_analyzer.py
|   +-- test_traceability.py
|
+-- requirements.txt
+-- README.md
```

---

## 12. Module Responsibilities

### `data_loader.py`

Loads YAML engineering data into Python data structures.

---

### `change_detector.py`

Compares requirement versions and identifies modified and unchanged requirements.

---

### `traceability.py`

Resolves traceability relationships between:

```text
Requirement -> Test Case -> Test Result
```

---

### `impact_analyzer.py`

Determines which verification evidence is associated with changed requirements.

---

### `evidence_assessor.py`

Applies deterministic engineering rules to determine evidence-review status.

---

### `llm_analyzer.py`

Builds a grounded prompt from verified deterministic facts and communicates with the local Ollama model.

The resulting explanation is advisory.

---

### `main.py`

Acts as the application orchestrator.

It coordinates the complete analysis pipeline and returns structured results that can be consumed by both the command-line interface and Streamlit.

---

### `app.py`

Provides the Streamlit user interface.

It calls the same analysis pipeline used by the command-line application rather than duplicating engineering logic.

---

## 13. Installation

Clone the repository:

```bash
git clone <repository-url>
cd safe-trace-ai
```

Create a virtual environment:

### Windows PowerShell

```powershell
python -m venv .venv
```

Activate it:

```powershell
.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
pip install -r requirements.txt
```

---

## 14. Ollama Setup

SafeTrace-AI currently uses Ollama for local LLM inference.

Check that Ollama is installed:

```powershell
ollama --version
```

Check installed models:

```powershell
ollama list
```

The current prototype expects:

```text
llama3.2:3b
```

If necessary, obtain the model through Ollama before running LLM-enabled analysis.

Ollama should be available locally at:

```text
http://localhost:11434
```

---

## 15. Running the Command-Line Analysis

From the project root:

```powershell
python src/main.py
```

The command-line application executes:

```text
Load engineering data
        |
        v
Detect requirement changes
        |
        v
Resolve traceability
        |
        v
Analyze verification impact
        |
        v
Assess evidence deterministically
        |
        v
Generate advisory LLM explanation
        |
        v
Display combined analysis
```

---

## 16. Running the Streamlit Application

Start the Streamlit application from the project root:

```powershell
streamlit run src/app.py
```

Streamlit normally opens the application in the browser at:

```text
http://localhost:8501
```

Use the sidebar to choose whether Ollama explanations should be generated.

Then select:

```text
Run SafeTrace-AI Analysis
```

To stop Streamlit, return to the terminal and press:

```text
Ctrl + C
```

---

## 17. Automated Testing

The project uses pytest.

Run the complete test suite:

```powershell
pytest -v
```

The current prototype includes tests for:

- requirement change detection
- deterministic evidence assessment
- requirement/test/result traceability
- LLM prompt construction
- Ollama response handling
- empty LLM response handling

The LLM integration tests mock the HTTP response and therefore do not require the real language model to generate a response during unit testing.

At the current development milestone:

```text
6 tests passed
```

---

## 18. Deterministic vs Generative Responsibilities

A central architectural boundary in SafeTrace-AI is:

```text
DETERMINISTIC PYTHON
        |
        +-- Detect changes
        +-- Resolve traceability
        +-- Analyze evidence
        +-- Assign evidence status
        |
        v
AUTHORITATIVE ENGINEERING FINDING
        |
        v
LOCAL LLM
        |
        +-- Explain the change
        +-- Explain evidence concern
        +-- Suggest items for human review
        |
        v
ADVISORY EXPLANATION
```

The LLM is not the authority for verification status.

This separation reduces the risk of using generative output as an uncontrolled engineering decision.

---

## 19. Current Limitations

SafeTrace-AI is a research prototype and has several limitations.

### Small case-study dataset

The current demonstration uses a small seat-belt warning requirement set.

### Rule-based deterministic assessment

Only a limited number of evidence-assessment rules are currently implemented.

### LLM output variability

Even with a strongly constrained prompt and low temperature, a language model can occasionally introduce wording or interpretations that are not explicitly supported by the engineering evidence.

For this reason, generated explanations are advisory and require human review.

### Local model capability

The current prototype uses `llama3.2:3b`, which provides a lightweight local inference solution but has more limited reasoning and instruction-following capability than larger models.

### No production lifecycle integration

The prototype does not currently integrate directly with industrial lifecycle-management platforms or requirements-management tools.

---

## 20. Future Work

Possible future extensions include:

### LLM Output Validation

Introduce a post-generation validation layer that checks LLM explanations for:

- unsupported claims
- prohibited compliance language
- certification claims
- changed numerical values
- altered logical operators
- invented evidence
- invented traceability relationships

Conceptually:

```text
Deterministic Finding
        |
        v
LLM Explanation
        |
        v
Output Validator
        |
        +-- acceptable -> present to engineer
        |
        +-- issue detected -> flag for review
```

### Expanded Deterministic Rules

Additional deterministic assessment rules could support more requirement-change categories.

### Larger Case Studies

The prototype could be evaluated using larger and more complex requirement baselines.

### Requirements-Management Integration

Future implementations could investigate integration with engineering lifecycle-management platforms such as SystemWeaver or similar tools.

### Report Generation

Analysis results could be exported into structured engineering change-impact reports.

### LLM Evaluation

Future research could systematically evaluate:

- factual grounding
- semantic accuracy
- hallucination rate
- logical-operator preservation
- numerical-value preservation
- usefulness to verification engineers

---

## 21. Research Scope

SafeTrace-AI investigates how generative AI can support requirement-change analysis while keeping authoritative engineering decisions within a deterministic and auditable pipeline.

The project does **not** attempt to replace:

- requirements engineers
- verification engineers
- safety engineers
- formal verification
- engineering review
- safety assessment
- certification processes

Instead, the LLM acts as an explanation and review-support component around deterministic engineering evidence.

---

## 22. Disclaimer

SafeTrace-AI is a research and demonstration prototype.

It is **not an ISO 26262 compliance tool**, certification tool, production safety-analysis tool, or replacement for qualified engineering judgement.

All AI-generated explanations are advisory and require human engineering review.
