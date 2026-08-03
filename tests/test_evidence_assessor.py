from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from data_loader import load_yaml
from evidence_assessor import assess_evidence
from impact_analyzer import analyze_impacts


def test_timing_change_requires_reverification() -> None:
    """SSR-002 should require reverification for the new 200 ms limit."""

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

    impacts = analyze_impacts(
        requirements_v1,
        requirements_v2,
        test_cases_data["test_cases"],
        test_results_data["test_results"],
    )

    ssr_002_impact = next(
        impact
        for impact in impacts
        if impact["requirement_id"] == "SSR-002"
    )

    assessment = assess_evidence(
        ssr_002_impact,
        requirements_v2,
    )

    assert assessment["status"] == "RE_VERIFICATION_REQUIRED"
    assert "420 ms" in assessment["reason"]
    assert "200 ms" in assessment["reason"]


    