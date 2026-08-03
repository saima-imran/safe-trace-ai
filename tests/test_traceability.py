from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from data_loader import load_yaml
from traceability import (
    find_test_cases_for_requirement,
    find_test_results_for_test_case,
)


def test_resolves_requirement_to_test_case_and_result() -> None:
    """SSR-002 should resolve to TC-002 and then TR-002."""

    test_cases_data = load_yaml(
        Path("data/case_study/test_cases.yaml")
    )

    test_results_data = load_yaml(
        Path("data/case_study/test_results.yaml")
    )

    linked_test_cases = find_test_cases_for_requirement(
        "SSR-002",
        test_cases_data["test_cases"],
    )

    assert len(linked_test_cases) == 1
    assert linked_test_cases[0]["id"] == "TC-002"

    linked_test_results = find_test_results_for_test_case(
        "TC-002",
        test_results_data["test_results"],
    )

    assert len(linked_test_results) == 1
    assert linked_test_results[0]["id"] == "TR-002"

    