from pathlib import Path

from data_loader import load_yaml


def find_test_cases_for_requirement(
    requirement_id: str,
    test_cases: list[dict],
) -> list[dict]:
    """Return test cases that verify a requirement."""
    return [
        test_case
        for test_case in test_cases
        if test_case["verifies"] == requirement_id
    ]


def find_test_results_for_test_case(
    test_case_id: str,
    test_results: list[dict],
) -> list[dict]:
    """Return test results that belong to a test case."""
    return [
        test_result
        for test_result in test_results
        if test_result["test_case"] == test_case_id
    ]


if __name__ == "__main__":
    test_cases_data = load_yaml(
        Path("data/case_study/test_cases.yaml")
    )

    test_results_data = load_yaml(
        Path("data/case_study/test_results.yaml")
    )

    test_cases = test_cases_data["test_cases"]
    test_results = test_results_data["test_results"]

    requirement_id = "SSR-002"

    linked_test_cases = find_test_cases_for_requirement(
        requirement_id,
        test_cases,
    )

    print(f"Requirement: {requirement_id}")

    for test_case in linked_test_cases:
        print(f"  Test case: {test_case['id']}")

        linked_test_results = find_test_results_for_test_case(
            test_case["id"],
            test_results,
        )

        for test_result in linked_test_results:
            print(f"    Test result: {test_result['id']}")

            