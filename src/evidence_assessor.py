from pathlib import Path

from data_loader import load_yaml
from impact_analyzer import analyze_impacts


def assess_evidence(
    impact: dict,
    requirements_v2: list[dict],
) -> dict:
    """Assign an evidence status to an impacted requirement."""

    requirement_id = impact["requirement_id"]

    current_requirement = next(
        requirement
        for requirement in requirements_v2
        if requirement["id"] == requirement_id
    )

    constraint = current_requirement.get("constraint")

    if constraint and constraint.get("type") == "timing":
        max_response_time = constraint.get("max_response_time_ms")

        for evidence in impact["evidence"]:
            for test_result in evidence["test_results"]:
                measurements = test_result.get("measurements", {})

                response_time = measurements.get("response_time_ms")

                if (
                    response_time is not None
                    and max_response_time is not None
                    and response_time > max_response_time
                ):
                    return {
                        "requirement_id": requirement_id,
                        "status": "RE_VERIFICATION_REQUIRED",
                        "reason": (
                            f"Previous measured response time was "
                            f"{response_time} ms, which exceeds the "
                            f"new {max_response_time} ms requirement."
                        ),
                    }

    return {
        "requirement_id": requirement_id,
        "status": "REVIEW_REQUIRED",
        "reason": (
            "The requirement changed and its linked verification "
            "evidence should be reviewed."
        ),
    }


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

    requirements_v1 = requirements_v1_data["requirements"]
    requirements_v2 = requirements_v2_data["requirements"]

    impacts = analyze_impacts(
        requirements_v1,
        requirements_v2,
        test_cases_data["test_cases"],
        test_results_data["test_results"],
    )

    for impact in impacts:
        assessment = assess_evidence(
            impact,
            requirements_v2,
        )

        print(
            f"{assessment['requirement_id']}: "
            f"{assessment['status']}"
        )

        print(
            f"  Reason: {assessment['reason']}"
        )

        

