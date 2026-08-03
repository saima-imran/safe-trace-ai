"""Generate downloadable reports from SafeTrace-AI analysis results."""


def build_text_report(results: list[dict]) -> str:
    """Convert SafeTrace-AI analysis results into a text report."""

    lines = []

    # ---------------------------------------------------------
    # Report header
    # ---------------------------------------------------------

    lines.append("SafeTrace-AI Analysis Report")
    lines.append("=" * 70)
    lines.append("")

    lines.append(
        "This report combines deterministic requirement-change analysis "
        "with advisory LLM-generated explanations."
    )

    lines.append("")

    lines.append(
        "Important: AI-generated explanations are advisory and require "
        "human engineering review."
    )

    lines.append("")

    lines.append(
        f"Changed requirements analyzed: {len(results)}"
    )

    lines.append("")

    # ---------------------------------------------------------
    # Requirement results
    # ---------------------------------------------------------

    for result in results:
        lines.append("-" * 70)

        lines.append(
            f"{result['requirement_id']} - {result['title']}"
        )

        lines.append("-" * 70)
        lines.append("")

        # Status
        lines.append("STATUS")
        lines.append(result["status"])
        lines.append("")

        # Old requirement
        lines.append("OLD REQUIREMENT")
        lines.append(result["old_requirement"])
        lines.append("")

        # New requirement
        lines.append("NEW REQUIREMENT")
        lines.append(result["new_requirement"])
        lines.append("")

        # Deterministic finding
        lines.append("DETERMINISTIC FINDING")
        lines.append(result["reason"])
        lines.append("")

        # Verification evidence
        lines.append("AFFECTED VERIFICATION EVIDENCE")

        test_cases = (
            ", ".join(result["test_case_ids"])
            if result["test_case_ids"]
            else "None"
        )

        test_results = (
            ", ".join(result["test_result_ids"])
            if result["test_result_ids"]
            else "None"
        )

        lines.append(
            f"Test Cases: {test_cases}"
        )

        lines.append(
            f"Test Results: {test_results}"
        )

        lines.append("")

        # LLM explanation
        lines.append("LLM ADVISORY EXPLANATION")

        if result["llm_explanation"]:
            lines.append(
                result["llm_explanation"]
            )
        else:
            lines.append(
                "LLM analysis was disabled for this run."
            )

        lines.append("")

        lines.append(
            "AI-generated explanations are advisory and require "
            "human engineering review."
        )

        lines.append("")

    # ---------------------------------------------------------
    # Report footer
    # ---------------------------------------------------------

    lines.append("=" * 70)
    lines.append("END OF REPORT")
    lines.append("=" * 70)

    return "\n".join(lines)

