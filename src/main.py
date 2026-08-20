from pathlib import Path

from data_loader import load_yaml
from evidence_assessor import assess_evidence
from governance_authorization import evaluate_ai_authorization
from governance_policy import (
    find_policy_for_activity,
    load_governance_policies,
)
from impact_analyzer import analyze_impacts
from llm_analyzer import build_prompt, generate_explanation


def find_requirement_by_id(
    requirement_id: str,
    requirements: list[dict],
) -> dict:
    """Return a requirement with the given ID."""

    for requirement in requirements:
        if requirement["id"] == requirement_id:
            return requirement

    raise ValueError(
        f"Requirement '{requirement_id}' was not found."
    )


def collect_evidence_ids(
    impact: dict,
) -> tuple[list[str], list[str]]:
    """Collect linked test-case and test-result IDs."""

    test_case_ids = []
    test_result_ids = []

    for evidence in impact["evidence"]:
        test_case = evidence["test_case"]
        test_case_ids.append(test_case["id"])

        for test_result in evidence["test_results"]:
            test_result_ids.append(test_result["id"])

    return test_case_ids, test_result_ids


def run_analysis(
    use_llm: bool = True,
    reviewer_role: str | None = None,
    authorization_granted: bool = False,
) -> list[dict]:
    """
    Run the SafeTrace-AI analysis pipeline.

    Governance policy is evaluated before any LLM call. The LLM can run
    only when the applicable policy and authorization permit execution.

    Returns structured analysis results that can be reused by
    the terminal application, Streamlit UI, or report generator.
    """

    policies = load_governance_policies()

    explanation_policy = find_policy_for_activity(
        "explain_safety_requirement_impact",
        policies,
    )

    if use_llm:
        authorization = evaluate_ai_authorization(
            explanation_policy,
            reviewer_role=reviewer_role,
            authorization_granted=authorization_granted,
        )
    else:
        authorization = {
            "policy_id": explanation_policy["id"],
            "status": "AI_NOT_REQUESTED",
            "ai_execution_allowed": False,
            "reviewer_role": reviewer_role,
            "reason": (
                "AI assistance was disabled for this analysis run."
            ),
        }

    requirements_v1_data = load_yaml(
        Path("data/case_study/requirements_v1.yaml")
    )

    requirements_v2_data = load_yaml(
        Path("data/case_study/requirements_v2.yaml")
    )

    test_cases_data = load_yaml(
        Path("data/case_study/test_cases.yaml")
    )

    test_results_data = load_yaml(
        Path("data/case_study/test_results.yaml")
    )

    requirements_v1 = requirements_v1_data["requirements"]
    requirements_v2 = requirements_v2_data["requirements"]
    test_cases = test_cases_data["test_cases"]
    test_results = test_results_data["test_results"]

    impacts = analyze_impacts(
        requirements_v1,
        requirements_v2,
        test_cases,
        test_results,
    )

    analysis_results = []

    for impact in impacts:
        requirement_id = impact["requirement_id"]

        old_requirement = find_requirement_by_id(
            requirement_id,
            requirements_v1,
        )

        new_requirement = find_requirement_by_id(
            requirement_id,
            requirements_v2,
        )

        assessment = assess_evidence(
            impact,
            requirements_v2,
        )

        test_case_ids, test_result_ids = collect_evidence_ids(
            impact
        )

        llm_explanation = None

        if (
            use_llm
            and authorization["ai_execution_allowed"]
        ):
            prompt = build_prompt(
                old_requirement=old_requirement["text"],
                new_requirement=new_requirement["text"],
                evidence_status=assessment["status"],
                deterministic_reason=assessment["reason"],
                test_case_ids=test_case_ids,
                test_result_ids=test_result_ids,
            )

            try:
                llm_explanation = generate_explanation(
                    prompt
                )

            except RuntimeError as exc:
                llm_explanation = (
                    "LLM explanation unavailable. "
                    f"Reason: {exc}"
                )

        analysis_results.append(
            {
                "requirement_id": requirement_id,
                "title": new_requirement["title"],
                "old_requirement": old_requirement["text"].strip(),
                "new_requirement": new_requirement["text"].strip(),
                "status": assessment["status"],
                "reason": assessment["reason"],
                "test_case_ids": test_case_ids,
                "test_result_ids": test_result_ids,
                "llm_explanation": llm_explanation,
                "policy_id": authorization["policy_id"],
                "governance_status": authorization["status"],
                "governance_reason": authorization["reason"],
                "reviewer_role": authorization["reviewer_role"],
                "ai_execution_allowed": authorization[
                    "ai_execution_allowed"
                ],
            }
        )

    return analysis_results


def print_analysis(
    results: list[dict],
) -> None:
    """Print analysis results to the terminal."""

    print()
    print("=" * 80)
    print("SAFETRACE-AI ANALYSIS")
    print("=" * 80)

    for result in results:
        print()
        print("-" * 80)
        print(
            f"Requirement: "
            f"{result['requirement_id']} - "
            f"{result['title']}"
        )
        print("-" * 80)

        print("\nOLD REQUIREMENT:")
        print(result["old_requirement"])

        print("\nNEW REQUIREMENT:")
        print(result["new_requirement"])

        print("\nDETERMINISTIC STATUS:")
        print(result["status"])

        print("\nDETERMINISTIC REASON:")
        print(result["reason"])

        print("\nAFFECTED EVIDENCE:")

        print(
            "Test cases: "
            + (
                ", ".join(result["test_case_ids"])
                if result["test_case_ids"]
                else "None"
            )
        )

        print(
            "Test results: "
            + (
                ", ".join(result["test_result_ids"])
                if result["test_result_ids"]
                else "None"
            )
        )

        print("\nGOVERNANCE POLICY:")
        print(result["policy_id"])

        print("\nGOVERNANCE STATUS:")
        print(result["governance_status"])

        print("\nGOVERNANCE REASON:")
        print(result["governance_reason"])

        print("\nAI EXECUTION ALLOWED:")
        print(result["ai_execution_allowed"])

        print("\nLLM ADVISORY EXPLANATION:")

        if result["llm_explanation"]:
            print(result["llm_explanation"])
        else:
            print(
                "No LLM explanation was generated because AI was "
                "disabled or governance authorization was not granted."
            )

    print()
    print("=" * 80)
    print("ANALYSIS COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    results = run_analysis(
        use_llm=False,
    )

    print_analysis(
        results
    )
    