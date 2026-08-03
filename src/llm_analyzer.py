"""
llm_analyzer.py

Purpose
-------
This module communicates with the local Ollama model to generate a
human-readable engineering explanation for a requirement change.

IMPORTANT:
The LLM DOES NOT make engineering decisions.

Python already determines:
    - which requirement changed
    - evidence status
    - deterministic reasoning

The LLM only explains those facts.
"""

from typing import Any

import requests

# -------------------------------------------------------------------
# Ollama Configuration
# -------------------------------------------------------------------

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3.2:3b"


# -------------------------------------------------------------------
# Prompt Builder
# -------------------------------------------------------------------

def build_prompt(
    old_requirement: str,
    new_requirement: str,
    evidence_status: str,
    deterministic_reason: str,
) -> str:
    """
    Create a constrained prompt for Ollama.

    The prompt supplies verified engineering facts and instructs the
    model to explain the change without inventing new information.
    """

    return f"""
You are assisting a software safety engineer.

Your role is ONLY to explain the engineering implications of the
requirement change.

You MUST NOT change or reinterpret the deterministic findings.

------------------------------------------------------------
Old Requirement
------------------------------------------------------------

{old_requirement}

------------------------------------------------------------
New Requirement
------------------------------------------------------------

{new_requirement}

------------------------------------------------------------
Deterministic Evidence Status
------------------------------------------------------------

{evidence_status}

------------------------------------------------------------
Deterministic Reason
------------------------------------------------------------

{deterministic_reason}

------------------------------------------------------------
Verified Facts
------------------------------------------------------------

- The previous maximum response time requirement was 500 ms.

- The updated maximum response time requirement is 200 ms.

- The previous measured response time was 420 ms.

- 420 ms satisfied the previous 500 ms requirement.

- 420 ms DOES NOT satisfy the updated 200 ms requirement.

------------------------------------------------------------
Your Task
------------------------------------------------------------

Explain:

1. What changed.

2. Why the existing verification evidence is affected.

3. Why re-verification is recommended.

------------------------------------------------------------
Rules
------------------------------------------------------------

- Preserve every verified fact exactly.

- Never state that 420 ms failed the previous
  500 ms requirement.

- Explain that 420 ms PASSED Version 1.

- Explain that 420 ms DOES NOT satisfy Version 2.

- Never change the deterministic evidence status.

- Never invent requirements.

- Never invent measurements.

- Never invent regulations.

- Never claim ISO 26262 compliance.

- Never claim certification.

- Treat your answer as engineering guidance.

------------------------------------------------------------
Output Format
------------------------------------------------------------

Change Type:

Semantic Impact:

Evidence Concern:

Suggested Review:
""".strip()


# -------------------------------------------------------------------
# Ollama Communication
# -------------------------------------------------------------------

def generate_explanation(prompt: str) -> str:
    """
    Send the prompt to Ollama and return the explanation.
    """

    payload: dict[str, Any] = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.2,
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
            "Unable to communicate with Ollama.\n"
            "Check that:\n"
            "1. Ollama is running.\n"
            "2. llama3.2:3b is installed.\n"
            "3. The Ollama API is reachable."
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


# -------------------------------------------------------------------
# Example
# -------------------------------------------------------------------

if __name__ == "__main__":

    old_requirement = (
        "When the seat-belt warning activation conditions "
        "are satisfied, the system shall activate the "
        "seat-belt warning within 500 ms."
    )

    new_requirement = (
        "When the seat-belt warning activation conditions "
        "are satisfied, the system shall activate the "
        "seat-belt warning within 200 ms."
    )

    evidence_status = "RE_VERIFICATION_REQUIRED"

    deterministic_reason = (
        "Previous measured response time was 420 ms, "
        "which exceeds the updated 200 ms requirement."
    )

    prompt = build_prompt(
        old_requirement,
        new_requirement,
        evidence_status,
        deterministic_reason,
    )

    explanation = generate_explanation(prompt)

    print("\n")
    print("=" * 70)
    print("LLM ENGINEERING EXPLANATION")
    print("=" * 70)
    print(explanation)
    print("=" * 70)

    


