from pathlib import Path
import sys

sys.path.insert(
    0,
    str(Path(__file__).resolve().parents[1] / "src"),
)

from governance_authorization import evaluate_ai_authorization
from governance_policy import (
    find_policy_for_activity,
    load_governance_policies,
)


def get_policy(activity: str) -> dict:
    """Load and return one policy for testing."""

    policies = load_governance_policies()

    return find_policy_for_activity(
        activity,
        policies,
    )


def test_permitted_activity_allows_ai() -> None:
    """A permitted low-consequence activity may use AI."""

    policy = get_policy(
        "summarize_low_consequence_change"
    )

    result = evaluate_ai_authorization(policy)

    assert result["status"] == "PERMITTED"
    assert result["ai_execution_allowed"] is True


def test_safety_activity_requires_explicit_authorization() -> None:
    """An allowed role must still explicitly authorize AI use."""

    policy = get_policy(
        "explain_safety_requirement_impact"
    )

    result = evaluate_ai_authorization(
        policy,
        reviewer_role="requirements_engineer",
        authorization_granted=False,
    )

    assert result["status"] == "AUTHORIZATION_REQUIRED"
    assert result["ai_execution_allowed"] is False


def test_allowed_role_can_authorize_safety_activity() -> None:
    """An allowed role may explicitly authorize bounded AI use."""

    policy = get_policy(
        "explain_safety_requirement_impact"
    )

    result = evaluate_ai_authorization(
        policy,
        reviewer_role="verification_engineer",
        authorization_granted=True,
    )

    assert result["status"] == "AUTHORIZED"
    assert result["ai_execution_allowed"] is True


def test_unknown_role_cannot_authorize_safety_activity() -> None:
    """A role outside the policy must not authorize AI use."""

    policy = get_policy(
        "explain_safety_requirement_impact"
    )

    result = evaluate_ai_authorization(
        policy,
        reviewer_role="guest",
        authorization_granted=True,
    )

    assert result["status"] == "UNAUTHORIZED_ROLE"
    assert result["ai_execution_allowed"] is False


def test_restricted_activity_blocks_ai() -> None:
    """No role may authorize AI to modify an authoritative trace link."""

    policy = get_policy(
        "modify_authoritative_trace_link"
    )

    result = evaluate_ai_authorization(
        policy,
        reviewer_role="safety_engineer",
        authorization_granted=True,
    )

    assert result["status"] == "RESTRICTED"
    assert result["ai_execution_allowed"] is False

    