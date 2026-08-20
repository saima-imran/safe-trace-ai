from pathlib import Path
import sys

import pytest

sys.path.insert(
    0,
    str(Path(__file__).resolve().parents[1] / "src"),
)

from governance_policy import (
    find_policy_for_activity,
    load_governance_policies,
)


def test_loads_three_governance_decisions() -> None:
    """The configuration should include all three AI-use decisions."""

    policies = load_governance_policies()

    decisions = {
        policy["decision"]
        for policy in policies
    }

    assert decisions == {
        "AI_PERMITTED",
        "HUMAN_AUTHORIZATION_REQUIRED",
        "AI_RESTRICTED",
    }


def test_safety_explanation_requires_authorization() -> None:
    """Safety-impact explanations should require prior authorization."""

    policies = load_governance_policies()

    policy = find_policy_for_activity(
        "explain_safety_requirement_impact",
        policies,
    )

    assert policy["id"] == "POL-AI-002"
    assert policy["decision"] == "HUMAN_AUTHORIZATION_REQUIRED"
    assert "safety_engineer" in policy["allowed_roles"]


def test_authoritative_trace_link_modification_restricts_ai() -> None:
    """AI must not modify authoritative traceability links."""

    policies = load_governance_policies()

    policy = find_policy_for_activity(
        "modify_authoritative_trace_link",
        policies,
    )

    assert policy["id"] == "POL-AI-003"
    assert policy["decision"] == "AI_RESTRICTED"
    assert policy["allowed_roles"] == []


def test_unknown_activity_is_rejected() -> None:
    """An activity without a policy must fail safely."""

    policies = load_governance_policies()

    with pytest.raises(
        ValueError,
        match="No governance policy exists",
    ):
        find_policy_for_activity(
            "unknown_activity",
            policies,
        )

        