"""
Generate advisory LLM explanations for deterministic SafeTrace-AI findings.

The LLM explains verified engineering facts supplied by the deterministic
pipeline. It does not determine evidence status, compliance, certification,
safety acceptance, or hazard classification.
"""

from typing import Any

import requests


OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3.2:3b"


def build_prompt(
    old_requirement: str,
    new_requirement: str,
    evidence_status: str,
    deterministic_reason: str,
    test_case_ids: list[str],
    test_result_ids: list[str],
) -> str:
    """Build a grounded prompt for requirement change-impact explanation."""

    test_cases_text = ", ".join(test_case_ids) or "None"
    test_results_text = ", ".join(test_result_ids) or "None"

    return f"""
You are assisting a software requirements and verification engineer.

Your role is limited to explaining verified information supplied by
SafeTrace-AI.

Do not make additional engineering, safety, compliance, or certification
judgements.

======================================================================
VERIFIED INPUT
======================================================================

OLD REQUIREMENT
{old_requirement}

NEW REQUIREMENT
{new_requirement}

DETERMINISTIC EVIDENCE STATUS
{evidence_status}

DETERMINISTIC REASON
{deterministic_reason}

LINKED TEST CASES
{test_cases_text}

LINKED TEST RESULTS
{test_results_text}

======================================================================
YOUR TASK
======================================================================

Compare the old and new requirement and explain:

1. What explicitly changed in the requirement text.

2. Which explicit conditions, thresholds, constraints, or required
   behaviours were added, removed, expanded, or made stricter.

3. Why the supplied linked verification evidence may need review.

4. What an engineer should inspect or verify next.

======================================================================
STRICT GROUNDING RULES
======================================================================

- Treat the deterministic status as authoritative.

- Treat the deterministic reason as authoritative.

- Preserve logical operators exactly.
  For example:
  "A OR B" must never be rewritten as "A AND B".

- Preserve numeric values exactly as supplied.

- Preserve requirement meaning exactly as supplied.

- Do not infer the designer's intention.

- Do not infer benefits such as:
  "safer",
  "more vigilant",
  "better",
  "improved safety",
  or similar claims unless explicitly provided.

- Do not invent requirements.

- Do not invent test cases.

- Do not invent test results.

- Do not invent measurements.

- Do not invent traceability links.

- Do not invent regulations.

- Do not claim ISO 26262 compliance or non-compliance.

- Do not use phrases such as:
  "ensure compliance",
  "prove compliance",
  or "certify compliance".

- Do not claim certification.

- Do not perform hazard analysis.

- Do not assign a safety risk.

- Do not claim that an earlier test failed unless the supplied
  deterministic evidence explicitly states this.

- Do not state that an existing test still passes the updated
  requirement unless the deterministic evidence explicitly proves it.

- Clearly distinguish between:
  a requirement change,
  existing evidence,
  and a suggested future review.

- Mention every clearly identifiable added condition or behaviour.

- Recommendations must use cautious language such as:
  "review",
  "verify",
  "inspect",
  "consider extending the test",
  or "determine whether additional verification is required".

- Treat the response as advisory and subject to human engineering review.

- Keep the response concise.

======================================================================
OUTPUT FORMAT
======================================================================

Use exactly these four headings:

Change Type:

Semantic Impact:

Evidence Concern:

Suggested Review:
""".strip()


def generate_explanation(prompt: str) -> str:
    """Send a prompt to Ollama and return the generated explanation."""

    payload: dict[str, Any] = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.1,
        },
    }

    try:
        response = requests.post(
            OLLAMA_URL,
            json=payload,
            timeout=120,
        )

        response.raise_for_status()

    except requests.RequestException as exc:
        raise RuntimeError(
            "Could not obtain an explanation from Ollama. "
            "Check that Ollama is running and that "
            f"the model '{MODEL_NAME}' is installed."
        ) from exc

    response_data = response.json()

    explanation = response_data.get(
        "response",
        "",
    ).strip()

    if not explanation:
        raise RuntimeError(
            "Ollama returned an empty response."
        )

    return explanation


if __name__ == "__main__":
    old_requirement = (
        "If the driver seat-belt status signal is unavailable, "
        "the system shall report a seat-belt status fault."
    )

    new_requirement = (
        "If the driver seat-belt status signal is unavailable or implausible, "
        "the system shall report a seat-belt status fault and store a "
        "diagnostic event."
    )

    prompt = build_prompt(
        old_requirement=old_requirement,
        new_requirement=new_requirement,
        evidence_status="REVIEW_REQUIRED",
        deterministic_reason=(
            "The requirement changed and its linked verification "
            "evidence should be reviewed."
        ),
        test_case_ids=["TC-003"],
        test_result_ids=["TR-003"],
    )

    explanation = generate_explanation(
        prompt
    )

    print()
    print("=" * 70)
    print("LLM ADVISORY EXPLANATION")
    print("=" * 70)
    print(explanation)
    print("=" * 70)
    