from pathlib import Path

from data_loader import load_yaml
from evidence_assessor import assess_evidence
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
) -> list[dict]:
    """
    Run the SafeTrace-AI analysis pipeline.

    Returns structured analysis results that can be reused by
    the terminal application, Streamlit UI, or report generator.
    """

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

        if use_llm:
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

        print("\nLLM ADVISORY EXPLANATION:")

        if result["llm_explanation"]:
            print(result["llm_explanation"])
        else:
            print("LLM analysis disabled.")

    print()
    print("=" * 80)
    print("ANALYSIS COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    results = run_analysis(
        use_llm=True,
    )

    print_analysis(
        results
    )

    
