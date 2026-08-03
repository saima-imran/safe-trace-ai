from pathlib import Path

from change_detector import detect_changes
from data_loader import load_yaml
from traceability import (
    find_test_cases_for_requirement,
    find_test_results_for_test_case,
)


def analyze_impacts(
    requirements_v1: list[dict],
    requirements_v2: list[dict],
    test_cases: list[dict],
    test_results: list[dict],
) -> list[dict]:
    """Find verification evidence linked to changed requirements."""

    changes = detect_changes(
        requirements_v1,
        requirements_v2,
    )

    impacts = []

    for change in changes:
        if change["change_type"] != "modified":
            continue

        requirement_id = change["id"]

        linked_test_cases = find_test_cases_for_requirement(
            requirement_id,
            test_cases,
        )

        linked_evidence = []

        for test_case in linked_test_cases:
            linked_test_results = find_test_results_for_test_case(
                test_case["id"],
                test_results,
            )

            linked_evidence.append(
                {
                    "test_case": test_case,
                    "test_results": linked_test_results,
                }
            )

        impacts.append(
            {
                "requirement_id": requirement_id,
                "change": change,
                "evidence": linked_evidence,
            }
        )

    return impacts


if __name__ == "__main__":
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

    impacts = analyze_impacts(
        requirements_v1_data["requirements"],
        requirements_v2_data["requirements"],
        test_cases_data["test_cases"],
        test_results_data["test_results"],
    )

    for impact in impacts:
        print(f"Requirement: {impact['requirement_id']}")

        for evidence in impact["evidence"]:
            test_case = evidence["test_case"]

            print(f"  Test case: {test_case['id']}")

            for test_result in evidence["test_results"]:
                print(f"    Test result: {test_result['id']}")

                